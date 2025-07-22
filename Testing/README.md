# OSMOSE Data Extraction Tool

This tool is designed to extract metadata and content from the OSMOSE platform. It is a refactored and merged version of two original scripts, providing a more structured and maintainable codebase.

## Project Structure

```
.
├── config.py               # All configuration settings
├── main.py                 # Main entry point for the application
├── requirements.txt        # Python package dependencies
├── src                     # Source code
│   ├── osmose              # Modules related to OSMOSE interaction
│   │   ├── client.py
│   │   ├── content_extractor.py
│   │   └── metadata_extractor.py
│   └── utils               # Utility modules
│       ├── cookie_manager.py
│       ├── data_handler.py
│       └── rate_limiter.py
└── README.md
```

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

3.  **Configure the application:**
    Open `config.py` and modify the settings as needed. You will need to provide the correct `MISSION_ID`, input file paths, and other relevant parameters.

## Usage

You can run the application from the command line using `main.py`. You need to specify which task you want to perform.

### Extract Metadata

```bash
python main.py metadata
```

### Extract Content

```bash
python main.py content
```

### Extract Both Metadata and Content

```bash
python main.py all
``` 