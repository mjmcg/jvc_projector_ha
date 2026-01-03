"""Constants for the jvc_projector Home Assistant integration."""

from .jvcprojector import const as pj

NAME = "JVC Projector"
DOMAIN = "jvc_projector"
MANUFACTURER = "JVC"

# ---- 2024 spec additions ----
KEY_LIGHT_SOURCE_TIME = "light_source_time"

# Remote buttons exposed to Home Assistant.
# These are IR-equivalent commands confirmed in the 2024 LAN spec.
REMOTE_COMMANDS = {
    "menu": pj.REMOTE_MENU,
    "up": pj.REMOTE_UP,
    "down": pj.REMOTE_DOWN,
    "left": pj.REMOTE_LEFT,
    "right": pj.REMOTE_RIGHT,
    "ok": pj.REMOTE_OK,
    "back": pj.REMOTE_BACK,

    "info": pj.REMOTE_INFO,
    "input": pj.REMOTE_INPUT,

    # Picture / mode related
    "picture_mode": pj.REMOTE_PICTURE_MODE,
    "color_profile": pj.REMOTE_COLOR_PROFILE,
    "gamma": pj.REMOTE_GAMMA,
    "color_temp": pj.REMOTE_COLOR_TEMP,

    # Lens & installation
    "lens_control": pj.REMOTE_LENS_CONTROL,
    "lens_ap": pj.REMOTE_LENS_AP,
    "anamo": pj.REMOTE_ANAMO,

    # HDMI shortcuts
    "hdmi_1": pj.REMOTE_HDMI_1,
    "hdmi_2": pj.REMOTE_HDMI_2,

    # Mode shortcuts (still supported in 2024)
    "mode_1": pj.REMOTE_MODE_1,
    "mode_2": pj.REMOTE_MODE_2,
    "mode_3": pj.REMOTE_MODE_3,

    # Less common but confirmed
    "hide": pj.REMOTE_HIDE,
    "mpc": pj.REMOTE_MPC,
    "advanced_menu": pj.REMOTE_ADVANCED_MENU,
    "setting_memory": pj.REMOTE_SETTING_MEMORY,
    "gamma_settings": pj.REMOTE_GAMMA_SETTINGS,
    "cmd": pj.REMOTE_CMD,
    "3d_format": pj.REMOTE_3D_FORMAT,
}