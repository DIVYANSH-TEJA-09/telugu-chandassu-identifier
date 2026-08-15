# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-15

### Changed
- Renamed the Python package and public engine API from `telugu_chandas` / `ChandasEngine` to `telugu_chandassu` / `ChandassuEngine`.
- Renamed the demo and Chandassu rules module to use the standardized spelling.

## [0.1.0] - 2026-08-15

### Added
- Rule-based prosody engine for identifying Telugu meters (Chandassu).
- Support for **Vritta** meters: Utpalamala, Champakamala, Shardulam, Mattebham.
- Support for **Jati** meters: Dwipada, Taruvoja, Kandam.
- Support for **Upajati** meters: Ataveladi, Tetagiti, Sisam.
- Laghu/Guru weight classification with full Telugu prosody rules (onset clusters, positional guru, pollu, sunna, visarga, wall rule, and hyphen handling).
- Gana classification (3-akshara ganas, Surya ganas, Indra ganas, Kandam ganas).
- Yati (యతి) harmony validation and Prasa (ప్రాస) consonant matching.
- Streamlit interactive UI application.
- Modern packaging configuration via PEP 621 (`pyproject.toml`) for PyPI release.
