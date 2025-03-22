import os

# Paths
HOME_DIR = os.path.expanduser("~")
CLAUDE_CONFIG_PATH = os.path.join(HOME_DIR, "Library/Application Support/Claude/claude_desktop_config.json")
CURSOR_CONFIG_PATH = os.path.join(HOME_DIR, ".cursor/mcp.json")
ENV_VARS_PATH = os.path.join(HOME_DIR, ".mcp_servers/env_vars.json")
WINDSURF_CONFIG_PATH = os.path.join(HOME_DIR, ".codeium/windsurf/mcp_config.json")
DELETED_MCPS_PATH = os.path.join(HOME_DIR, ".mcp_servers/deleted_mcps.json")

# Application Configurations
APPLICATIONS = {
    "claude": {
        "name": "Claude",
        "config_path": os.path.join(HOME_DIR, "Library/Application Support/Claude/claude_desktop_config.json"),
        "config_key": "mcpServers"
    },
    "cursor": {
        "name": "Cursor",
        "config_path": os.path.join(HOME_DIR, ".cursor/mcp.json"),
        "config_key": "mcpServers"
    },
    "windsurf": {
        "name": "Windsurf",
        "config_path": os.path.join(HOME_DIR, ".codeium/windsurf/mcp_config.json"),
        "config_key": "mcpServers"
    }
}

# UI Settings
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 600
WINDOW_TITLE = "MCP Server Manager"

# Style Constants
COLORS = {
    "primary": "#0078d4",
    "primary_hover": "#006cbd",
    "danger": "#d83b01",
    "danger_hover": "#a92d01",
    "background": "#f5f5f5",
    "card_background": "#ffffff",
    "border": "#e0e0e0",
    "text_primary": "#1f1f1f",
    "text_secondary": "#666666",
}

# Server Card Settings
CARD_STYLES = {
    "border_radius": 12,
    "padding": 24,
    "icon_size": 80,
    "button_min_width": 140,
}

# Environment Variables Dialog Settings
ENV_DIALOG = {
    "min_width": 600,
    "min_height": 200,
    "padding": 32,
    "label_min_width": 150,
}

# File patterns
IGNORED_DIRECTORIES = [".git", ".svn", "__pycache__", "MasterServer"]
REQUIRED_SERVER_FILES = ["config.json"] 