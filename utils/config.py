# Configuration settings for the application
from utils.config_loader import load_config

# Load configuration from YAML
config = load_config()

# File paths
DATA_PATH = config['paths']['data']
LOGO_PATH = config['paths']['logo']
TEAMS_PATH = config['paths']['teams']

# Position mapping
POSITION_MAP = config['position_map']

# Column configurations
DISPLAY_COLUMNS = config['display_columns']
COLUMN_RENAME_MAP = config['column_rename_map']

# Styling configurations
HIGH_RISK_COLOR = config['colors']['high_risk']
LOW_RISK_COLOR = config['colors']['low_risk']