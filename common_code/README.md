# Shared Code Folder

This folder contains shared code that is reused across multiple modules within the project. The purpose of this directory is to centralize common functionality, reduce redundancy, and ensure consistency across the codebase.

**Note:** This folder uses **Python 3.10**. Ensure you are using this version (or a compatible version) to avoid compatibility issues with syntax or dependencies.

`paths.py` is a script for managing common paths dynamically. It calculates key directories, allowing modules to reference shared resources without hardcoding paths.

- **`PATH_ROOT`**: Root directory of the project.
- **`PATH_COMMON_CODE`**: Directory containing shared code (`common_code`).
