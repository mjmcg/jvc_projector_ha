# JVC Projectors – Home Assistant Integration

A custom Home Assistant integration for JVC projectors using the **2024 External Command Communication Specification**, with a focus on **JVC NZ-series** projectors.

This project uses the [2024 JVC LAN specification](https://www.jvc.com/usa/projectors/installers-calibrators/external-command-communication-specification/) and is designed to support the newer JVC command protocol.


---

## Features

- Home Assistant custom integration
- Support for JVC projectors using the 2024 external command protocol
- Initial focus is on the JVC DLA-NZ500
- Asynchronous, non-blocking communication model
- Clean config flow UI
- Sensors, remote entities, and services aligned with Home Assistant best practices
- Designed for long-term maintainability and future expansion

---

## Supported Models

This integration is currently developed and tested with a **JVC DLA-NZ500 projector**.

Other JVC models that implement the 2024 External Command Communication Specification may work but are not yet officially supported.

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

Configuration is performed entirely through the Home Assistant UI.

You will need:
- Projector IP address
- Hashed password for the projector login
- Network connectivity between Home Assistant and the projector

---

## Status

This project is under active development.

Expect ongoing improvements, expanded model support, and additional entities and services.

Testing feedback and issue reports are welcome.

---

## Project Inspiration and Credit

This project was inspired by the community-maintained JVC Home Assistant integration:

https://github.com/iloveicedgreentea/jvc_homeassistant

The current codebase has been rewritten to support the 2024 External Command Communication Specification and NZ-series projectors.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.