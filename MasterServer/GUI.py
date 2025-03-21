import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QMessageBox, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

class ServerCard(QFrame):
    def __init__(self, name, config, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ServerCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 10px;
            }
            ServerCard:hover {
                border: 1px solid #0078d4;
            }
            QLabel#titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            QLabel#descriptionLabel {
                color: #666;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Icon (placeholder for now)
        icon_label = QLabel()
        icon_pixmap = QPixmap(32, 32)
        icon_pixmap.fill(Qt.GlobalColor.blue)
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title_label = QLabel(name)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        description = "MCP Server for " + name
        desc_label = QLabel(description)
        desc_label.setObjectName("descriptionLabel")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Enable button
        self.enable_button = QPushButton("Enable Server")
        layout.addWidget(self.enable_button)
        
        layout.addStretch()
        self.setMinimumSize(200, 250)

class MCPServerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Server Manager")
        self.setMinimumSize(800, 600)
        
        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header = QLabel("MCP Server Manager")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Scroll area for server grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Initialize servers
        self.servers = {
            "Python Server": {
                "command": "python",
                "args": ["mcp-server.py"],
                "env": {
                    "API_KEY": "value"
                }
            },
            "Filesystem Server": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/Users/username/Desktop",
                    "/Users/username/Downloads"
                ]
            }
        }
        
        # Populate server grid
        self.populate_server_grid()
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def populate_server_grid(self):
        row = 0
        col = 0
        max_cols = 3  # Number of cards per row
        
        for server_name, server_config in self.servers.items():
            card = ServerCard(server_name, server_config)
            card.enable_button.clicked.connect(lambda checked, name=server_name: self.enable_server(name))
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def enable_server(self, server_name):
        server_config = self.servers[server_name]
        
        try:
            # Handle Claude config
            claude_config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
            os.makedirs(os.path.dirname(claude_config_path), exist_ok=True)
            
            # Load existing Claude config or create new one
            existing_claude_config = {}
            if os.path.exists(claude_config_path):
                try:
                    with open(claude_config_path, 'r') as f:
                        existing_claude_config = json.load(f)
                except json.JSONDecodeError:
                    pass  # Use empty config if file is corrupted
            
            # Initialize mcpServers if it doesn't exist
            if "mcpServers" not in existing_claude_config:
                existing_claude_config["mcpServers"] = {}
            
            # Update the specific server config
            existing_claude_config["mcpServers"][server_name] = server_config
            
            # Save updated Claude config
            with open(claude_config_path, 'w') as f:
                json.dump(existing_claude_config, f, indent=2)
                
            # Handle Cursor config
            cursor_config_path = os.path.expanduser("~/.cursor/mcp.json")
            os.makedirs(os.path.dirname(cursor_config_path), exist_ok=True)
            
            # Load existing Cursor config or create new one
            existing_cursor_config = {}
            if os.path.exists(cursor_config_path):
                try:
                    with open(cursor_config_path, 'r') as f:
                        existing_cursor_config = json.load(f)
                except json.JSONDecodeError:
                    pass  # Use empty config if file is corrupted
            
            # Initialize mcpServers if it doesn't exist
            if "mcpServers" not in existing_cursor_config:
                existing_cursor_config["mcpServers"] = {}
            
            # Update the specific server config
            existing_cursor_config["mcpServers"][server_name] = server_config
            
            # Save updated Cursor config
            with open(cursor_config_path, 'w') as f:
                json.dump(existing_cursor_config, f, indent=2)
                
            QMessageBox.information(self, "Success", 
                                  f"Server '{server_name}' has been enabled!\n"
                                  "Please restart Claude and Cursor for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MCPServerManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
