# Inbudex API

## Overview

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLAlchemy](https://www.sqlalchemy.org) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
- 📦 [**Poetry**](https://python-poetry.org/) to manage the dependencies and enviroment needed for the project.

## 📈 Project Status

> **Current Phase:** In Development

## ⚙️ Installation & Setup

### Requirements

- Python 3.12+
- Docker (for containerized environments)

### Local Setup

1. Install Poetry
   - Mac/Linux

   ```bash
   brew install pipx
   pipx install poetry --python python3.12
   ```

   - Windows

   ```
   winget install Python.Python.3.12
   pip install --user pipx
   pipx ensurepath
   pipx install poetry --python python
   ```

2. Install dependecies

   ```bash
   poetry install
   ```

3. Activate the virtual enviroment
   1. find the environment path:

   ```bash
   poetry env info --path
   ```

   2. Then, activate:
      - Mac/Linux

      ```bash
      source <POETRYPATH>/bin/activate
      ```

      - Windows

      ```bash
      <POETRYPATH>\Scripts\Activate.ps1
      ```

4. Run the API (not yet possible)

```bash
poetry run uvicorn inbudex.main:app --reload
```
