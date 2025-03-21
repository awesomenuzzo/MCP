import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QMessageBox, QGridLayout, QFrame, QScrollArea,
                            QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter

class ServerCard(QFrame):
    def __init__(self, name, config, server_path, is_enabled=False, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            ServerCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            ServerCard:hover {
                border: 1px solid #0078d4;
                background-color: #ffffff;
            }
            QLabel#titleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1f1f1f;
                background: transparent;
            }
            QLabel#descriptionLabel {
                color: #666;
                font-size: 14px;
                background: transparent;
            }
            QPushButton {
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: 500;
                min-width: 140px;
            }
            QPushButton#enableButton {
                background-color: #0078d4;
            }
            QPushButton#enableButton:hover {
                background-color: #006cbd;
            }
            QPushButton#disableButton {
                background-color: #d83b01;
            }
            QPushButton#disableButton:hover {
                background-color: #a92d01;
            }
            QWidget {
                background: transparent;
            }
        """)
        
        # Add shadow effect to the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Icon container (left side)
        icon_container = QWidget()
        icon_container.setFixedSize(80, 80)  # Fix the container size
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(80, 80)
        icon_path = os.path.join(server_path, "icon.png")
        if os.path.exists(icon_path):
            original_pixmap = QPixmap(icon_path)
            # Create a square container size
            container_size = 80
            
            # Calculate the scaling factor while preserving aspect ratio
            width = original_pixmap.width()
            height = original_pixmap.height()
            scale_factor = min(container_size / width, container_size / height) * 0.9  # Scale to 90% of container
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Create a transparent background
            final_pixmap = QPixmap(container_size, container_size)
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Scale the original image
            scaled_pixmap = original_pixmap.scaled(
                new_width, new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Calculate position to center the scaled image
            x = (container_size - new_width) // 2
            y = (container_size - new_height) // 2
            
            # Draw the scaled image onto the transparent background
            painter = QPainter(final_pixmap)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            icon_label.setPixmap(final_pixmap)
            icon_label.setScaledContents(False)  # Don't let the label scale the contents
        else:
            # Use default blue placeholder
            pixmap = QPixmap(80, 80)
            pixmap.fill(Qt.GlobalColor.blue)
            icon_label.setPixmap(pixmap)
        
        icon_layout.addWidget(icon_label)
        
        # Add icon container to main layout
        layout.addWidget(icon_container)
        
        # Content container (middle)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Title
        title_label = QLabel(name)
        title_label.setObjectName("titleLabel")
        content_layout.addWidget(title_label)
        
        # Description
        readme_path = os.path.join(server_path, "README.md")
        description = ""
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r') as f:
                    description = f.readline().strip()  # Get first line of README
            except:
                pass
        
        if not description:
            description = "MCP Server"
            
        desc_label = QLabel(description)
        desc_label.setObjectName("descriptionLabel")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        # Add content container to main layout with stretch
        layout.addWidget(content_container, stretch=1)
        
        # Button container (right side)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        # Enable button
        self.enable_button = QPushButton("Enable Server")
        self.enable_button.setObjectName("enableButton")
        button_layout.addWidget(self.enable_button)
        
        # Disable button
        self.disable_button = QPushButton("Disable Server")
        self.disable_button.setObjectName("disableButton")
        button_layout.addWidget(self.disable_button)
        
        # Add button container to main layout
        layout.addWidget(button_container)
        
        # Update button visibility based on enabled state
        self.update_button_state(is_enabled)
        
        # Set fixed height but allow width to be flexible
        self.setFixedHeight(120)
        
    def update_button_state(self, is_enabled):
        self.enable_button.setVisible(not is_enabled)
        self.disable_button.setVisible(is_enabled)

class MCPServerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Server Manager")
        self.setMinimumSize(1000, 600)
        
        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # Header
        header = QLabel("MCP Server Manager")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #1f1f1f;
            margin-bottom: 12px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Scroll area for server grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        
        scroll_content = QWidget()
        self.grid_layout = QVBoxLayout(scroll_content)  # Changed to VBoxLayout for single column
        self.grid_layout.setSpacing(16)  # Space between cards
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Load servers from directories
        self.load_servers()
        
        # Load current configurations
        self.load_current_configs()
        
        # Populate server grid
        self.populate_server_grid()
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def load_servers(self):
        self.servers = {}
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Scan for directories that might be servers
        for item in os.listdir(parent_dir):
            if item.startswith('.'):
                continue
                
            full_path = os.path.join(parent_dir, item)
            if not os.path.isdir(full_path):
                continue
                
            # Skip the MasterServer directory
            if item == "MasterServer":
                continue
                
            config_path = os.path.join(full_path, "config.json")
            if not os.path.exists(config_path):
                continue
                
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                # Store server info with its path
                for server_name, server_config in config.items():
                    # Update the command path if it's relative
                    if "args" in server_config:
                        for i, arg in enumerate(server_config["args"]):
                            if isinstance(arg, str) and arg.startswith("./"):
                                server_config["args"][i] = os.path.join(full_path, arg[2:])
                    
                    self.servers[server_name] = {
                        "config": server_config,
                        "path": full_path
                    }
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
    
    def load_current_configs(self):
        self.enabled_servers = set()
        
        # Check Claude config
        claude_config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        if os.path.exists(claude_config_path):
            try:
                with open(claude_config_path, 'r') as f:
                    config = json.load(f)
                    if "mcpServers" in config:
                        self.enabled_servers.update(config["mcpServers"].keys())
            except:
                pass
        
        # Check Cursor config
        cursor_config_path = os.path.expanduser("~/.cursor/mcp.json")
        if os.path.exists(cursor_config_path):
            try:
                with open(cursor_config_path, 'r') as f:
                    config = json.load(f)
                    if "mcpServers" in config:
                        self.enabled_servers.update(config["mcpServers"].keys())
            except:
                pass
    
    def populate_server_grid(self):
        # Add cards in a single column
        for server_name, server_info in self.servers.items():
            is_enabled = server_name in self.enabled_servers
            card = ServerCard(server_name, server_info["config"], server_info["path"], is_enabled)
            card.enable_button.clicked.connect(lambda checked, name=server_name: self.enable_server(name))
            card.disable_button.clicked.connect(lambda checked, name=server_name: self.disable_server(name))
            self.grid_layout.addWidget(card)
            
            # Add a small spacer after each card except the last one
            if server_name != list(self.servers.keys())[-1]:
                spacer = QWidget()
                spacer.setFixedHeight(1)  # 1 pixel high spacer
                self.grid_layout.addWidget(spacer)
    
    def disable_server(self, server_name):
        try:
            # Handle Claude config
            claude_config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
            if os.path.exists(claude_config_path):
                try:
                    with open(claude_config_path, 'r') as f:
                        config = json.load(f)
                        if "mcpServers" in config and server_name in config["mcpServers"]:
                            del config["mcpServers"][server_name]
                            with open(claude_config_path, 'w') as f:
                                json.dump(config, f, indent=2)
                except:
                    pass
            
            # Handle Cursor config
            cursor_config_path = os.path.expanduser("~/.cursor/mcp.json")
            if os.path.exists(cursor_config_path):
                try:
                    with open(cursor_config_path, 'r') as f:
                        config = json.load(f)
                        if "mcpServers" in config and server_name in config["mcpServers"]:
                            del config["mcpServers"][server_name]
                            with open(cursor_config_path, 'w') as f:
                                json.dump(config, f, indent=2)
                except:
                    pass
            
            # Update UI
            self.enabled_servers.discard(server_name)
            self.refresh_server_states()
            
            QMessageBox.information(self, "Success", 
                                  f"Server '{server_name}' has been disabled!\n"
                                  "Please restart Claude and Cursor for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to disable server: {str(e)}")
    
    def enable_server(self, server_name):
        server_info = self.servers[server_name]
        server_config = server_info["config"]
        
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
                    pass
            
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
                    pass
            
            # Initialize mcpServers if it doesn't exist
            if "mcpServers" not in existing_cursor_config:
                existing_cursor_config["mcpServers"] = {}
            
            # Update the specific server config
            existing_cursor_config["mcpServers"][server_name] = server_config
            
            # Save updated Cursor config
            with open(cursor_config_path, 'w') as f:
                json.dump(existing_cursor_config, f, indent=2)
            
            # Update UI
            self.enabled_servers.add(server_name)
            self.refresh_server_states()
                
            QMessageBox.information(self, "Success", 
                                  f"Server '{server_name}' has been enabled!\n"
                                  "Please restart Claude and Cursor for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def refresh_server_states(self):
        # Update all server cards' button states
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, ServerCard):
                server_name = widget.findChild(QLabel, "titleLabel").text()
                widget.update_button_state(server_name in self.enabled_servers)

def main():
    app = QApplication(sys.argv)
    window = MCPServerManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
