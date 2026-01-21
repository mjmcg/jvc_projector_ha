# JVC Projector HA – Home Assistant Integration

A custom Home Assistant integration for JVC projectors using the [**2024 External Command Communication Specification**](https://www.jvc.com/usa/projectors/installers-calibrators/external-command-communication-specification/).

## Supported Models

The integration was built and tested using the DLA-NZ500, but should work with other models that implement the same API:

- DLA-NZ500, DLA-NZ700, DLA-NZ800, DLA-NZ900
- DLA-RS1200, DLA-RS2200, DLA-RS3200, DLA-RS4200
- DLA-N788, DLA-N799, DLA-N888, DLA-N899, DLA-N988
- DLA-N700, DLA-N800, DLA-N1188
- DLA-V800R, DLA-V900R
- DLA-Z5, DLA-Z7

There is a newer [**2025 External Command Communication Specification**](https://www.jvc.com/usa/projectors/installers-calibrators/external_command_dlanz900_series/) for the DLA-NZ800 and DLA-NZ900 models. Since the API is the same, the integration should work so I've included them in the supported models. 


---

## Included Entities

**Controls**
- Power On/Off
- Input source (HDMI 1/2)
- Picture mode selection (Cinema, Natural, HDR, etc.)
- LD Power (laser diode current value: 0-100)
- Dynamic Control (Off/Low/High/Balanced)

**Sensors**
- Power state (On/Standby/Warming/Cooling/Error)
- Light source usage time (hours)
- HDMI signal present (binary sensor)
- Source display resolution (e.g., 4K60, 1080p60, No Signal)
- Input display (HDMI 1/2)
- Content type (SDR/HDR10/HDR10+/HLG)
- Colorimetry (BT.709, BT.2020, DCI-P3, etc.)
- Model (projector model name)
- LD Current Value (current laser diode power level)

**IR Remote Commands**
- Power On/Off toggle
- Virtual remote with IR remote buttons accessible via `remote.send_command` service calls
- Lovelace button cards (example provided in `lovelace/jvc_remote_card.yaml`)
- Available remote buttons: menu, up, down, left, right, ok, back, info, hide, input, picture_mode, lens_control, mpc, hdmi_1, hdmi_2, mode_1, mode_2, mode_3, and more

---

## Installation

### HACS (Recommended)

### Home Assistant Community Store (HACS)

*Recommended because you get notified of updates.*

> HACS is a third-party downloader for Home Assistant to easily install and update custom integrations made by the community. See <https://hacs.xyz/> for more details.

You can add the repository to HACS on your Home Assistant instance with the button below

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mjmcg&repository=jvc_projector_ha&category=integration)

If the button does not work, or you don't want to use it, follow these steps to add the integration to HACS manually.

### Manual Installation

1. Copy the directory: custom_components/jvc_projectors_ha into: config/custom_components/
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services**

---

## Configuration

Configuration is performed in the Home Assistant UI.

### You will need:
- Network connectivity between Home Assistant and the projector
- Projector IP address
- Projector Port (default is 20554)
- Hashed network password (see below)


### Generating your hashed network password

1. Using the remote, set a Network Password for your projector. It must be between 8 and 10 characters long, e.g. "MyPassword"
2. Append "JVCKWPJ" to that password, e.g. "MyPasswordJVCKWPJ"
3. Generate the MD5 hash of that string. You can use an online tool like https://codebeautify.org/sha256-hash-generator or a command line tool.
4. Use the resulting hash string as your password when configuring the integration in Home Assistant, e.g. "98c75d723b5bc9d638c87618bdfde6d6dffe2a5cfebf3d2f918c95e1ea2f3b40".

### Note on network connectivity
If your JVC projector only has a wired network connection, you can use a travel router like the [TP-Link AC750 Wireless Portable Nano Travel Router (TL-WR902AC)](https://www.tp-link.com/us/home-networking/wifi-router/tl-wr902ac/) in client mode to connect it to your network. This is how I have mine set up and it has worked perfectly.

---

## Status

This is my first Home Assistant integration so there may be bugs or missing features.

Testing feedback and issue reports are welcome.

---

## Credits & Acknowledgments

This integration is based on the excellent [pyjvcprojector](https://github.com/SteveEasley/pyjvcprojector) Python library by [Steve Easley](https://github.com/SteveEasley). The library provides the core communication protocol implementation for JVC D-ILA projectors over LAN. The device communication code derived from pyjvcprojector is licensed under the MIT License.

This project was inspired by the community-maintained JVC Home Assistant integration: https://github.com/iloveicedgreentea/jvc_homeassistant

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.