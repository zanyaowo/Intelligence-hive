# Third-Party Software Attribution

This project includes and modifies open-source software components. Below is a list of all third-party software, their licenses, and modifications made.

## Snare Honeypot

**Project**: Snare - Super Next generation Advanced Reactive honEypot
**Source**: https://github.com/mushorg/snare
**License**: GNU General Public License v3.0
**License File**: `honeypot_configs/snare_tanner/snare/LICENSE`

### Modifications Made:
- Removed Chinese language comments from source files
- Modified Docker configuration for integration with data platform
- Customized docker-compose.yml for deployment setup

---

## Tanner

**Project**: Tanner - Remote data analysis and classification service
**Source**: https://github.com/mushorg/tanner
**License**: GNU General Public License v3.0
**License File**: `honeypot_configs/snare_tanner/tanner/LICENSE`

### Modifications Made:
- **sessions_session.py**: Removed Chinese language comments from code
- **docker-compose.yml**:
  - Changed healthcheck command from `curl` to `wget` for Alpine Linux compatibility
  - Removed redundant Chinese comments
  - Modified port mappings for integration

---

## License Compliance

This project, including all modifications to the above components, is released under the **GNU General Public License v3.0** to comply with the copyleft requirements of the included software.

### Source Code Availability

All source code, including modifications, is available in this repository. The complete and unmodified license texts for Snare and Tanner are preserved in their respective directories.

### Original Authors

All credit for the core functionality of Snare and Tanner goes to their original authors and the [mushorg](https://github.com/mushorg) organization.

---

## Contact

If you have questions about the licensing or modifications, please open an issue in this repository.

---

*Last Updated: 2025-10-23*
