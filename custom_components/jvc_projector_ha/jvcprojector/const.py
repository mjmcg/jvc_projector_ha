"""Device constants for a JVC Projector."""

from typing import Final

POWER: Final = "power"
OFF: Final = "off"
STANDBY: Final = "standby"
ON: Final = "on"
WARMING: Final = "warming"
COOLING: Final = "cooling"
ERROR: Final = "error"

INPUT: Final = "input"
HDMI1 = "hdmi1"
HDMI2 = "hdmi2"

SOURCE: Final = "source"
NOSIGNAL: Final = "nosignal"
SIGNAL: Final = "signal"

# ---- 2024 D-ILA LAN spec (raw command names) ----
IFLT: Final = "IFLT"  # Light Source Time (numeric, hours)
IFIN: Final = "IFIN"  # Input Display (diagnostic)
IFIS: Final = "IFIS"  # Source Display (on/off)
IFCM: Final = "IFCM"  # Colorimetry
MODEL: Final = "model"  # Projector model
PMPM: Final = "PMPM"  # Picture Mode
PMCT: Final = "PMCT"  # Content Type
PMAT: Final = "PMAT"  # Auto transition value for Content Type
PMCV: Final = "PMCV"  # LD Current Value
PMDC: Final = "PMDC"  # Dynamic Control

# Internal keys (for entity IDs)
auto_content_type: Final = "auto_content_type"  # Maps to PMAT

# Remote Control Codes (IR pass-through)
REMOTE_STANDBY: Final = "7306"
REMOTE_ON: Final = "7305"
REMOTE_MENU: Final = "732E"
REMOTE_UP: Final = "7301"
REMOTE_DOWN: Final = "7302"
REMOTE_LEFT: Final = "7336"
REMOTE_RIGHT: Final = "7334"
REMOTE_OK: Final = "732F"
REMOTE_BACK: Final = "7303"
REMOTE_MPC: Final = "73F0"
REMOTE_HIDE: Final = "731D"
REMOTE_INFO: Final = "7374"
REMOTE_INPUT: Final = "7308"
REMOTE_ADVANCED_MENU: Final = "7373"
REMOTE_PICTURE_MODE: Final = "73F4"
REMOTE_COLOR_PROFILE: Final = "7388"
REMOTE_LENS_CONTROL: Final = "7330"
REMOTE_SETTING_MEMORY: Final = "73D4"
REMOTE_GAMMA_SETTINGS: Final = "73F5"
REMOTE_CMD: Final = "738A"
REMOTE_MODE_1: Final = "73D8"
REMOTE_MODE_2: Final = "73D9"
REMOTE_MODE_3: Final = "73DA"
REMOTE_HDMI_1: Final = "7370"
REMOTE_HDMI_2: Final = "7371"
REMOTE_LENS_AP: Final = "7320"
REMOTE_ANAMO: Final = "73C5"
REMOTE_GAMMA: Final = "7375"
REMOTE_COLOR_TEMP: Final = "7376"
REMOTE_3D_FORMAT: Final = "73D6"
REMOTE_PIC_ADJ: Final = "7372"
REMOTE_NATURAL: Final = "736A"
REMOTE_CINEMA: Final = "7368"

# Mapping of user-friendly button names to remote codes
REMOTE_BUTTON_MAP: Final = {
    "standby": REMOTE_STANDBY,
    "on": REMOTE_ON,
    "menu": REMOTE_MENU,
    "up": REMOTE_UP,
    "down": REMOTE_DOWN,
    "left": REMOTE_LEFT,
    "right": REMOTE_RIGHT,
    "ok": REMOTE_OK,
    "back": REMOTE_BACK,
    "mpc": REMOTE_MPC,
    "hide": REMOTE_HIDE,
    "info": REMOTE_INFO,
    "input": REMOTE_INPUT,
    "advanced_menu": REMOTE_ADVANCED_MENU,
    "picture_mode": REMOTE_PICTURE_MODE,
    "color_profile": REMOTE_COLOR_PROFILE,
    "lens_control": REMOTE_LENS_CONTROL,
    "setting_memory": REMOTE_SETTING_MEMORY,
    "gamma_settings": REMOTE_GAMMA_SETTINGS,
    "cmd": REMOTE_CMD,
    "mode_1": REMOTE_MODE_1,
    "mode_2": REMOTE_MODE_2,
    "mode_3": REMOTE_MODE_3,
    "hdmi_1": REMOTE_HDMI_1,
    "hdmi_2": REMOTE_HDMI_2,
    "lens_ap": REMOTE_LENS_AP,
    "anamo": REMOTE_ANAMO,
    "gamma": REMOTE_GAMMA,
    "color_temp": REMOTE_COLOR_TEMP,
    "3d_format": REMOTE_3D_FORMAT,
    "pic_adj": REMOTE_PIC_ADJ,
    "natural": REMOTE_NATURAL,
    "cinema": REMOTE_CINEMA,
}
