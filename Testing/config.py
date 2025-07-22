from datetime import datetime
import os

class Config:
    """
    Configuration class for the OSMOSE extraction script.
    All user-configurable settings are centralized here.
    """
    MISSION_ID = "25GBIASIJAP002"
    START_DATE = datetime.strptime('01/01/2024', '%d/%m/%Y')
    END_DATE = datetime.strptime('11/07/2025', '%d/%m/%Y')
    OSMOSE_BASE_URL = "https://osmose-sba.safe.socgen/"
    
    # Input/Output Files and Directories
    WORKSPACE_DIR = os.getcwd()
    INPUT_FILE_METADATA = 'Input/0-OSMOSE_auto_search_input_Email - Voice.xlsx'
    INPUT_FILE_CONTENT = "C:/Users/a112524/github/tool_osmose_AutoSearch_Filtering/2501A51HKG010/OSMOSE_PROJECT/Autosearch Charles/Charles_Osmose_Metadata_All.csv"
    OSMOSE_PROJECT_PATH = os.path.join(WORKSPACE_DIR, MISSION_ID, "OSMOSE_PROJECT")
    OUTPUT_PATH_METADATA = os.path.join(OSMOSE_PROJECT_PATH, "Autosearch Voice")
    OUTPUT_PATH_CONTENT = "Other Metadata for LLM/Charles content"

    LOG_FILENAME = "fetch_requests.log"
    
    # Performance and Rate Limiting
    MAX_CONCURRENT_REQUESTS = 10
    RATE_LIMIT_MAX_CALLS = 360
    RATE_LIMIT_PERIOD_SECONDS = 60

    REQUEST_HEADERS = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "Host": "osmose-sba.safe.socgen",
        "Referer": "https://osmose-sba.safe.socgen/demo/search?n=10&sort=rel-desc",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "X-Dev-Client": "osmose-app"
    }

    def __init__(self):
        """Create output directories if they don't exist."""
        os.makedirs(self.OSMOSE_PROJECT_PATH, exist_ok=True)
        os.makedirs(self.OUTPUT_PATH_METADATA, exist_ok=True)
        os.makedirs(self.OUTPUT_PATH_CONTENT, exist_ok=True)

config = Config() 