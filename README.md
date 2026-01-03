# JVC Projectors – Home Assistant Integration

A custom Home Assistant integration for JVC projectors using the **2024 External Command Communication Specification**, with an initial focus on **JVC NZ-series** projectors.

This project is a ground-up rewrite designed to support modern Home Assistant architecture, improved reliability, and the newer JVC command protocol.

---

## Features

- Native Home Assistant custom integration
- Support for JVC projectors using the 2024 external command protocol
- Initial focus on NZ-series models
- Asynchronous, non-blocking communication model
- Clean config flow UI
- Sensors, remote entities, and services aligned with Home Assistant best practices
- Designed for long-term maintainability and future expansion

---

## Supported Models

This integration is currently developed and tested with **JVC NZ-series projectors**.

Other JVC models that implement the 2024 External Command Communication Specification may work but are not yet officially supported.

---

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Add this repository as a **Custom Repository**
   - Repository: `https://github.com/mjmcg/jvc-projectors-ha`
   - Category: *Integration*
3. Install **JVC Projectors**
4. Restart Home Assistant
5. Add the integration via **Settings → Devices & Services**

### Manual Installation

1. Copy the directory: custom_components/jvc_projectors_ha into: config/custom_components/
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services**

---

## Configuration

Configuration is performed entirely through the Home Assistant UI.

You will need:
- Projector IP address
- Network connectivity between Home Assistant and the projector

---

## Project Origin and Credit

This project was inspired by and conceptually derived from the community-maintained JVC Home Assistant integration:

https://github.com/iloveicedgreentea/jvc_homeassistant

The current codebase has been **fully rewritten** to support the 2024 External Command Communication Specification, modern Home Assistant patterns, and NZ-series projectors.  
No code has been directly reused.

---

## Status

This project is under active development.

Expect ongoing improvements, expanded model support, and additional entities and services.

Testing feedback and issue reports are welcome.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.