# -*- coding: utf-8 -*-
import os
import re
import socket
import subprocess
import psutil

from libqtile.config import (
    KeyChord,
    Key,
    Screen,
    Group,
    Drag,
    Click,
    ScratchPad,
    DropDown,
    Match,
)
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.lazy import lazy
from libqtile import qtile
from typing import List  # noqa: F401
from custom.bsp import Bsp as CustomBsp
from custom.pomodoro import Pomodoro as CustomPomodoro
from custom.zoomy import Zoomy as CustomZoomy
from custom.stack import Stack as CustomStack
from custom.windowname import WindowName as CustomWindowName

mod = "mod4"
terminal = "urxvt"
myconfig = "/home/uriel/.config/qtile/config.py"

################################################
## Resize functions for bsp layout #############
################################################

def resize(qtile, direction):
    layout = qtile.current_layout
    child = layout.current
    parent = child.parent

    while parent:
        if child in parent.children:
            layout_all = False

            if (direction == "left" and parent.split_horizontal) or (
                direction == "up" and not parent.split_horizontal
            ):
                parent.split_ratio = max(5, parent.split_ratio - layout.grow_amount)
                layout_all = True
            elif (direction == "right" and parent.split_horizontal) or (
                direction == "down" and not parent.split_horizontal
            ):
                parent.split_ratio = min(95, parent.split_ratio + layout.grow_amount)
                layout_all = True

            if layout_all:
                layout.group.layout_all()
                break

        child = parent
        parent = child.parent


@lazy.function
def resize_left(qtile):
    resize(qtile, "left")


@lazy.function
def resize_right(qtile):
    resize(qtile, "right")


@lazy.function
def resize_up(qtile):
    resize(qtile, "up")


@lazy.function
def resize_down(qtile):
    resize(qtile, "down")


keys = [
    ########################
    ### The essentials #####
    ########################
    Key([mod], "Return", lazy.spawn(terminal), desc="Launches My Terminal"),
    Key(
        [mod],
        "d",
        lazy.spawn("rofi -modi run,drun,window -lines 12 -padding 18 -width 60 -location 0 -show drun -sidebar-mode -columns 3"),
        desc="rofi ",
    ),
    Key(
        [mod, "shift"],
        "d",
        lazy.spawn("instantmenu_run"),
        desc="instantos_menu ",
    ),
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle through layouts"),
    Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill active window"),
    Key([mod, "shift"], "c", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod, "shift"], "r", lazy.restart(), desc="Restart Qtile"),

    ############################
    ### Window controls ########
    ############################
    Key(
        [mod], "Down", lazy.layout.down(), desc="Move focus down in current stack pane"
    ),
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up in current stack pane"),
    Key(
        [mod],
        "Left",
        lazy.layout.left(),
        lazy.layout.next(),
        desc="Move focus left in current stack pane",
    ),
    Key(
        [mod],
        "Right",
        lazy.layout.right(),
        lazy.layout.previous(),
        desc="Move focus right in current stack pane",
    ),
    Key(
        [mod, "shift"],
        "Down",
        lazy.layout.shuffle_down(),
        desc="Move windows down in current stack",
    ),
    Key(
        [mod, "shift"],
        "Up",
        lazy.layout.shuffle_up(),
        desc="Move windows up in current stack",
    ),
    Key(
        [mod, "shift"],
        "Left",
        lazy.layout.shuffle_left(),
        lazy.layout.swap_left(),
        lazy.layout.client_to_previous(),
        desc="Move windows left in current stack",
    ),
    Key(
        [mod, "shift"],
        "Right",
        lazy.layout.shuffle_right(),
        lazy.layout.swap_right(),
        lazy.layout.client_to_next(),
        desc="Move windows right in the current stack",
    ),
    Key(
        [mod, "mod1"],
        "Left",
        resize_left,
        desc="Resize window left",
    ),
    Key([mod], "n", lazy.layout.normalize(), desc="Normalize window size ratios"),
    Key(
        [mod],
        "m",
        lazy.window.toggle_maximize(),
        desc="Toggle window between minimum and maximum sizes",
    ),
    Key([mod, "shift"], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
    Key([mod], "equal", lazy.layout.grow(), desc="Grow in monad tall"),
    Key([mod], "minus", lazy.layout.shrink(), desc="Shrink in monad tall"),
    Key(
        [mod],
        "t",
        lazy.window.toggle_floating(),
        desc="Toggle floating on focused window",
    ),
    Key(
        [mod],
        "h",
        lazy.window.toggle_minimize(),
        desc="Toggle minimization on focused window",
    ),
    Key(
        [mod, "shift"],
        "h",
        lazy.group.unminimize_all(),
        desc="Unminimize all windows on current group",
    ),
    ########################
    ### Stack controls #####
    ########################
    Key(
        [mod],
        "f",
        lazy.spawn("thunar"),
        desc="launch thunar",
    ),
    Key(
        [mod],
        "s",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    ########################
    ### Misc. Commands #####
    ########################
    Key(
        [mod],
        "b",
        lazy.spawn("./.config/qtile/toggle_eww.sh"),
        desc="Toggle bottom eww bar visibility",
    ),
    Key(
        [mod, "shift"],
        "Return",
        lazy.spawn("terminator"),
        desc="Launch terminal",
    ),
    Key([mod, "shift"], "m", lazy.spawn("splatmoji copy"), desc="*moji selector"),

    Key(
        [mod],
        "w",
        lazy.spawn("firefox"),
        desc="launch firefox",
    ),
    Key(
        [mod],
        "n",
        lazy.spawn("nitrogen"),
        desc="choose wallpaper",
    ),
    Key(
        [mod],
        "x",
        lazy.spawn("hefflogout"),
        desc="powermenu",
    ),
    Key(
        [],
        "Print",
        lazy.spawn("scrot '%S.png' -e -d 5'mv $f $$(xdg-user-dir PICTURES)/Ubuntu-%S-$wx$h.png ; feh $$(xdg-user-dir PICTURES)/Ubuntu-%S-$wx$h.png'"),
        desc="Print Screen",
    ),

]


def show_keys():
    key_help = ""
    for k in keys:
        mods = ""

        for m in k.modifiers:
            if m == "mod4":
                mods += "Super + "
            else:
                mods += m.capitalize() + " + "

        if len(k.key) > 1:
            mods += k.key.capitalize()
        else:
            mods += k.key

        key_help += "{:<30} {}".format(mods, k.desc + "\n")

    return key_help


keys.extend(
    []
)

workspaces = [
    {"name": "WWW", "key": "1", "matches": [Match(wm_class="firefox")]},
    {
        "name": "WEB",
        "key": "2",
        "matches": [
            Match(wm_class="Thunderbird"),
            Match(wm_class="transmission"),
            Match(wm_class="gnome-calendar"),
        ],
    },
    {
        "name": "TERM",
        "key": "3",
        "matches": [
            Match(wm_class="joplin"),
            Match(wm_class="libreoffice"),
            Match(wm_class="org.pwmt.zathura"),
        ],
    },
    {"name": "TXT", "key": "4", "matches": [Match(wm_class="geany")]},
    {"name": "FILES", "key": "5", "matches": [Match(wm_class="thunar")]},

    {
        "name": "EDIT",
        "key": "6",
        "matches": [
            Match(wm_class="slack"),
            Match(wm_class="lightcord"),
            Match(wm_class="polari"),
        ],
    },
    {"name": "SYS", "key": "7", "matches": [Match(wm_class="spotify")]},
    {"name": "MEET", "key": "8", "matches": [Match(wm_class="gimp")]},
    {"name": "MUS", "key": "9", "matches": []},
    {
        "name": "MP4",
        "key": "0",
        "matches": [
            Match(wm_class="lxappearance"),
            Match(wm_class="pavucontrol"),
            Match(wm_class="connman-gtk"),
        ],
    },
]

groups = [
    ScratchPad(
        "scratchpad",
        [
            # define a drop down terminal.
            # it is placed in the upper third of screen by default.
            DropDown(
                "term",
                "alacritty --class dropdown -e tmux_startup.sh",
                height=0.6,
                on_focus_lost_hide=False,
                opacity=1,
                warp_pointer=False,
            ),
        ],
    ),
]

for workspace in workspaces:
    matches = workspace["matches"] if "matches" in workspace else None
    groups.append(Group(workspace["name"], matches=matches, layout="bsp"))
    keys.append(
        Key(
            [mod],
            workspace["key"],
            lazy.group[workspace["name"]].toscreen(),
            desc="Focus this desktop",
        )
    )
    keys.append(
        Key(
            [mod, "shift"],
            workspace["key"],
            lazy.window.togroup(workspace["name"]),
            desc="Move focused window to another group",
        )
    )

########################
# Define colors ########
########################

colors = [
    ["#1c2023", "#1c2023"],  # background 0
    ["#d8dee9", "#d8dee9"],  # foreground 1
    ["#3b4252", "#3b4252"],  # background lighter 2
    ["#bf616a", "#bf616a"],  # red 3
    ["#a3be8c", "#a3be8c"],  # green 4
    ["#ebcb8b", "#ebcb8b"],  # yellow 5
    ["#81a1c1", "#81a1c1"],  # blue 6
    ["#b48ead", "#b48ead"],  # magenta 7
    ["#88c0d0", "#88c0d0"],  # cyan 8
    ["#e5e9f0", "#e5e9f0"],  # white 9
    ["#4c566a", "#4c566a"],  # grey 10
    ["#d08770", "#d08770"],  # orange 11
    ["#8fbcbb", "#8fbcbb"],  # super cyan 12
    ["#5e81ac", "#5e81ac"],  # super blue 13
    ["#242831", "#242831"],  # super dark background 14
]

layout_theme = {
    "border_width": 3,
    "margin": 9,
    "border_focus": "66c31b",
    "border_normal": "1c1c1c",
    "font": "FiraCode Nerd Font",
    "grow_amount": 2,
}

layouts = [
    CustomBsp(**layout_theme, fair=False),
    layout.Max(**layout_theme),
    layout.Stack(num_stacks=2, **layout_theme),
    layout.Floating(**layout_theme, fullscreen_border_width=3, max_border_width=3),
]

########################
# Setup bar ############
########################

widget_defaults = dict(
    font="novamono for powerline bold", fontsize=11, padding=3, background=colors[14]
)
extension_defaults = widget_defaults.copy()

group_box_settings = {
    "padding" : 5,
                    "borderwidth" : 3,
                    "active" : colors[9],
                    "inactive" : colors[10],
                    "disable_drag" : True,
                    "rounded" : True,
                    "margin_y" : 3,
                    "margin_x" : 2,
                    "padding_y" : 5,
                    "padding_x" : 4,
                    #hide_unused" :True,
                    "highlight_color" : colors[1],
                    "highlight_method" : "block",
                    "this_current_screen_border" : colors[3],
                    "this_screen_border" : colors [1],
                    "other_current_screen_border" : colors[1],
                    "other_screen_border" : colors[1],
                    "foreground" : colors[8],
                    "background" : colors[14],
}


### Mouse_callback functions
def open_pavu():
    qtile.cmd_spawn("pavucontrol")

def open_powermenu():
    qtile.cmd_spawn("betterlockscreen -l dim")

def open_instantstartmenu():
    qtile.cmd_spawn("appmenu")


screens = [
    Screen(
        wallpaper="~/Imágenes/girl.jpg",
        wallpaper_mode="fill",
        top=bar.Bar(
            [
                 widget.Sep(
                    linewidth=2,
                    foreground=colors[14],
                    padding=6,
                    size_percent=50,
                 ),
                 widget.TextBox(
                    text="",
                    foreground =colors[1],
                    font = "feather",
                    fontsize = 12,
                    padding = 5,
                    mouse_callbacks = {"Button1": open_instantstartmenu},
                 ),
                 widget.Sep(
                    linewidth=2,
                    foreground=colors[2],
                    padding=25,
                    size_percent=50,
                 ),
                widget.GroupBox(
                    font="trebuchet ms",
                    fontsize = 11,
                    visible_groups=["WWW"],
                    **group_box_settings,
                ),
                widget.GroupBox(
                    font="trebuchet ms",
                    fontsize = 11,
                    visible_groups=["WEB", "TERM", "TXT", "FILES", "EDIT"],
                    **group_box_settings,
                ),
                widget.GroupBox(
                    font="trebuchet ms",
                    fontsize = 11,
                    visible_groups=["SYS"],
                    **group_box_settings,
                ),
                widget.GroupBox(
                    font="trebuchet ms",
                    fontsize = 11,
                    visible_groups=["MEET", "MUS", "MP4"],
                    **group_box_settings,
                ),
                widget.Sep(
                    linewidth=0,
                    foreground=colors[14],
                    background=colors[14],
                    padding=10,
                    size_percent=40,
                ),
                widget.Sep(
                    linewidth=0,
                    foreground=colors[14],
                    background=colors[14],
                    padding=10,
                    size_percent=50,
                ),
                widget.Spacer(),
                widget.TextBox(
                    text=" ",
                    foreground=colors[14],
                    background=colors[14],
                    font="Font Awesome 5 Free Solid",
                ),
                widget.Spacer(),
                widget.TextBox(
                    text=" ",
                    foreground=colors[14],
                    background=colors[14],
                    fontsize=28,
                    padding=0,
                ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                widget.TextBox(
                       text = "   ",
                       font = "feather",
                    fontsize = 15,
                       background = colors[7],
                       foreground = colors[0],
                       padding = 0,
                       ),
                widget.Net(
                       background = colors[6],
                       foreground = colors[0],
                       padding = 5,
                       interface="wlan0",
                       format = '↓{down} ↑{up} ',
                       ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                widget.TextBox(
                       text = "  ",
                       font = "feather",
                    fontsize = 15,
                       background = colors[6],
                       foreground = colors[0],
                       padding = 0,
                       ),

                widget.Memory(
                        background=colors[5],
                        foreground=colors[0],
                        format='{MemUsed: .0f} MB ',
                        ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                widget.TextBox(
                       text = "  ",
                       font = "feather",
                       fontsize = 15,
                       foreground = colors[0],
                       background = colors[5],
                       padding = 0
                       ),
                widget.CurrentLayout(
                foreground = colors[0],
                background = colors[4],
                padding = 4
                ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                 widget.TextBox(
                       text = "  ",
                       font = "feather",
                       fontsize = 15,
                       foreground = colors[0],
                       background = colors[4],
                       padding = 0
                       ),
                 widget.PulseVolume(
                    foreground = colors[0],
                    background = colors[3],
                    limit_max_volume="True",
                    mouse_callbacks={"Button3": open_pavu},
                ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                widget.TextBox(
                    text="  ",
                    font = "feather",
                    fontsize = 15,
                    foreground=colors[0],  # fontsize=38
                    background=colors[3],
                ),
                widget.Clock(
                    format="%a, %b %d ",
                    background=colors[9],
                    foreground=colors[0],
                ),
                widget.Sep(linewidth = 0,
                           padding = 4,
                           foreground = colors[14],
                           background=colors[14],
                           ),
                widget.Sep(
                    linewidth = 0,
                    padding = 4,
                    foreground = colors[14],
                    background = colors[14],
                ),
                    widget.TextBox(
                       text = "  ",
                       font = "feather",
                       fontsize = 15,
                       background = colors[9],
                       foreground = colors[0],
                       padding = 0
                       ),
                    widget.Clock(
                        background=colors[14],
                        icons_size=20,
                        padding=8
                        ),
                widget.Sep(
                    padding = 6,
                    linewidth = 0,
                    background = colors[14],
                    foreground = colors[14],
                ),
                    widget.Sep(
                    padding = 6,
                    linewidth = 0,
                    background = colors[14],
                    foreground = colors[14],
                ),
            ],
            31,
            margin=[10, 15, 5, 15],
        ),
        bottom=bar.Gap(18),
        left=bar.Gap(18),
        right=bar.Gap(18),
    ),
]

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = "floating_only"
cursor_warp = False
floating_layout = layout.Floating(
    **layout_theme,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        Match(wm_type="utility"),
        Match(wm_type="notification"),
        Match(wm_type="toolbar"),
        Match(wm_type="splash"),
        Match(wm_type="dialog"),
        Match(wm_class="confirm"),
        Match(wm_class="dialog"),
        Match(wm_class="download"),
        Match(wm_class="error"),
        Match(wm_class="file_progress"),
        Match(wm_class="notification"),
        Match(wm_class="splash"),
        Match(wm_class="toolbar"),
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="pomotroid"),
        Match(wm_class="cmatrixterm"),
        Match(title="Farge"),
        Match(wm_class="org.gnome.Nautilus"),
        Match(wm_class="feh"),
        Match(wm_class="gnome-calculator"),
        Match(wm_class="blueberry"),
    ],
)
auto_fullscreen = True
focus_on_window_activation = "focus"

# Startup scripts
@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser("~")
    subprocess.call([home + "/.config/qtile/autostart.sh"])


# Window swallowing ;)
@hook.subscribe.client_new
def _swallow(window):
    pid = window.window.get_net_wm_pid()
    ppid = psutil.Process(pid).ppid()
    cpids = {
        c.window.get_net_wm_pid(): wid for wid, c in window.qtile.windows_map.items()
    }
    for i in range(5):
        if not ppid:
            return
        if ppid in cpids:
            parent = window.qtile.windows_map.get(cpids[ppid])
            parent.minimized = True
            window.parent = parent
            return
        ppid = psutil.Process(ppid).ppid()


@hook.subscribe.client_killed
def _unswallow(window):
    if hasattr(window, "parent"):
        window.parent.minimized = False


# Go to group when app opens on matched group
@hook.subscribe.client_new
def modify_window(client):
    # if (client.window.get_wm_transient_for() or client.window.get_wm_type() in floating_types):
    #    client.floating = True

    for group in groups:  # follow on auto-move
        match = next((m for m in group.matches if m.compare(client)), None)
        if match:
            targetgroup = client.qtile.groups_map[
                group.name
            ]  # there can be multiple instances of a group
            targetgroup.cmd_toscreen(toggle=False)
            break

wmname = "qtile"
