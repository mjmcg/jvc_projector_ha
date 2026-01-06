# JVC Projector HA – Home Assistant Integration

A custom Home Assistant integration for JVC projectors using the [**2024 External Command Communication Specification**](https://www.jvc.com/usa/projectors/installers-calibrators/external-command-communication-specification/).

## Supported Models

The following projectors are supported:

- DLA-NZ500, DLA-NZ700, DLA-NZ900
- DLA-RS1200, DLA-RS2200
- DLA-N788, DLA-N799, DLA-N888, DLA-N899
- DLA-N700, DLA-N800
- DLA-Z5, DLA-Z7

Additional JVC models that implement the 2024 External Command Communication Specification may also work.

---

## Included Entities

**Controls**
- Power On/Off control
- Input source
- Picture mode selection

**Sensors**
- Content type (SDR/HDR)
- Light source usage time (hours)
- Power State (Warming Up/Cooling Down/On/Off)
- HDMI Signal Present (Yes/No)
- Source Display Resolution (e.g., 4K60, 1080p60)

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

1. Using the remote, set a Network Password for your projector, e.g. "MyPassword"
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

## Project Inspiration and Credit

This project was inspired by the community-maintained JVC Home Assistant integration:

https://github.com/iloveicedgreentea/jvc_homeassistant

Thanks to @iloveicedgreentea for their work on JVC projectors in Home Assistant.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.