# Fog-of-War Chess

Fog-of-War Chess - a single-player chess variant with limited visibility.

## Requirements

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (for environment and package management)

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd fog-of-war-chess
    ```

2.  Create a virtual environment using `uv`:
    ```bash
    uv venv
    ```

3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

4.  Install the project dependencies from `pyproject.toml`:
    ```bash
    uv pip install -e .
    ```


## Running the Application

1.  Ensure the virtual environment is activated.

2.  Run the application:
    ```bash
    python run.py
    ```

3.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Running Tests

1.  Ensure the virtual environment is activated.

2.  Run the tests:
    ```bash
    pytest
    ```
