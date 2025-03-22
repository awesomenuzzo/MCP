import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QMessageBox, QGridLayout, QFrame, QScrollArea,
                            QGraphicsDropShadowEffect, QDialog, QLineEdit,
                            QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
import config

class EnvironmentVariablesDialog(QDialog):
    def __init__(self, server_name, env_vars, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Environment Variables - {server_name}")
        self.setMinimumWidth(config.ENV_DIALOG["min_width"])
        self.setMinimumHeight(config.ENV_DIALOG["min_height"])
        
        # Set dialog style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {config.COLORS["card_background"]};
            }}
            QLabel {{
                font-size: 14px;
                color: {config.COLORS["text_primary"]};
                padding: 4px 0;
            }}
            QLineEdit {{
                padding: 12px;
                border: 2px solid {config.COLORS["border"]};
                border-radius: 8px;
                background-color: {config.COLORS["background"]};
                font-size: 14px;
                color: {config.COLORS["text_primary"]};
                selection-background-color: {config.COLORS["primary"]};
            }}
            QLineEdit:focus {{
                border: 2px solid {config.COLORS["primary"]};
                background-color: {config.COLORS["card_background"]};
            }}
            QLineEdit:hover {{
                background-color: {config.COLORS["card_background"]};
                border: 2px solid #ccc;
            }}
            QPushButton {{
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                border: none;
            }}
            QPushButton#okButton {{
                background-color: {config.COLORS["primary"]};
                color: white;
            }}
            QPushButton#okButton:hover {{
                background-color: {config.COLORS["primary_hover"]};
            }}
            QPushButton#cancelButton {{
                background-color: {config.COLORS["background"]};
                color: {config.COLORS["text_primary"]};
            }}
            QPushButton#cancelButton:hover {{
                background-color: {config.COLORS["border"]};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(config.ENV_DIALOG["padding"], config.ENV_DIALOG["padding"], 
                                config.ENV_DIALOG["padding"], config.ENV_DIALOG["padding"])
        
        # Header
        header = QLabel("Configure Environment Variables")
        header.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {config.COLORS["text_primary"]};
            margin-bottom: 8px;
        """)
        layout.addWidget(header)
        
        # Description
        description = QLabel("These values will be securely stored and used when the server is enabled.")
        description.setStyleSheet(f"""
            font-size: 14px;
            color: {config.COLORS["text_secondary"]};
            margin-bottom: 16px;
        """)
        layout.addWidget(description)
        
        # Form layout for environment variables
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        self.env_inputs = {}
        
        for var_name, var_value in env_vars.items():
            # Create a container for each row
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(16)
            
            # Label
            label = QLabel(var_name + ":")
            label.setMinimumWidth(config.ENV_DIALOG["label_min_width"])
            
            # Input field
            input_field = QLineEdit(var_value)
            input_field.setPlaceholderText(f"Enter value for {var_name}")
            
            row_layout.addWidget(label)
            row_layout.addWidget(input_field, 1)
            
            form_layout.addRow(row_widget)
            self.env_inputs[var_name] = input_field
        
        layout.addWidget(form_widget)
        layout.addStretch()
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("Save Changes")
        ok_btn.setObjectName("okButton")
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addWidget(button_container)
    
    def get_environment_variables(self):
        return {
            var_name: input_field.text()
            for var_name, input_field in self.env_inputs.items()
        }

class ServerCard(QFrame):
    def __init__(self, name, config_data, server_path, is_enabled=False, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            ServerCard {{
                background: {config.COLORS["card_background"]};
                border-radius: {config.CARD_STYLES["border_radius"]}px;
                border: 1px solid {config.COLORS["border"]};
            }}
            ServerCard:hover {{
                border: 1px solid {config.COLORS["primary"]};
                background-color: {config.COLORS["card_background"]};
            }}
            QLabel#titleLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {config.COLORS["text_primary"]};
                background: transparent;
            }}
            QLabel#descriptionLabel {{
                color: {config.COLORS["text_secondary"]};
                font-size: 14px;
                background: transparent;
            }}
            QPushButton {{
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: 500;
                min-width: {config.CARD_STYLES["button_min_width"]}px;
            }}
            QPushButton#enableButton {{
                background-color: {config.COLORS["primary"]};
            }}
            QPushButton#enableButton:hover {{
                background-color: {config.COLORS["primary_hover"]};
            }}
            QPushButton#disableButton {{
                background-color: {config.COLORS["danger"]};
            }}
            QPushButton#disableButton:hover {{
                background-color: {config.COLORS["danger_hover"]};
            }}
            QWidget {{
                background: transparent;
            }}
        """)
        
        # Add shadow effect to the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Main horizontal layout
        layout = QHBoxLayout(self)
        padding = config.CARD_STYLES["padding"]
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(24)
        
        # Icon container
        icon_container = QWidget()
        icon_container.setFixedSize(config.CARD_STYLES["icon_size"], config.CARD_STYLES["icon_size"])
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(config.CARD_STYLES["icon_size"], config.CARD_STYLES["icon_size"])
        icon_path = os.path.join(server_path, "icon.png")
        if os.path.exists(icon_path):
            original_pixmap = QPixmap(icon_path)
            # Create a square container size
            container_size = config.CARD_STYLES["icon_size"]
            
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
            pixmap = QPixmap(config.CARD_STYLES["icon_size"], config.CARD_STYLES["icon_size"])
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
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # Header
        header = QLabel(config.WINDOW_TITLE)
        header.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {config.COLORS["text_primary"]};
            margin-bottom: 12px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Scroll area for server grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget {{
                background-color: {config.COLORS["background"]};
            }}
        """)
        
        scroll_content = QWidget()
        self.grid_layout = QVBoxLayout(scroll_content)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Load initial data
        self.load_all_data()
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {config.COLORS["background"]};
            }}
        """)
    
    def load_all_data(self):
        """Load all data needed for the UI"""
        self.load_servers()
        self.load_current_configs()
        self.load_environment_variables()
        self.sync_application_configs()
        self.populate_server_grid()
    
    def load_servers(self):
        self.servers = {}
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # First load current enabled servers to check for changes
        enabled_servers = set()
        for app_id, app_config in config.APPLICATIONS.items():
            if os.path.exists(app_config["config_path"]):
                try:
                    with open(app_config["config_path"], 'r') as f:
                        app_data = json.load(f)
                        if app_config["config_key"] in app_data:
                            enabled_servers.update(app_data[app_config["config_key"]].keys())
                except:
                    pass
        
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
                    server_config = json.load(f)
                    
                # Store server info with its path
                for server_name, server_data in server_config.items():
                    # Update the command path if it's relative
                    if "args" in server_data:
                        for i, arg in enumerate(server_data["args"]):
                            if isinstance(arg, str) and arg.startswith("./"):
                                server_data["args"][i] = os.path.join(full_path, arg[2:])
                    
                    self.servers[server_name] = {
                        "config": server_data,
                        "path": full_path
                    }
                    
                    # If this server is enabled, update its configuration
                    if server_name in enabled_servers:
                        self.update_server_config(server_name, server_data)
                            
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")

    def update_server_config(self, server_name, server_data):
        """Update server configuration across all applications"""
        try:
            for app_id, app_config in config.APPLICATIONS.items():
                if os.path.exists(app_config["config_path"]):
                    with open(app_config["config_path"], 'r') as f:
                        app_config_data = json.load(f)
                        if app_config["config_key"] in app_config_data and server_name in app_config_data[app_config["config_key"]]:
                            # Preserve environment variables if they exist
                            env_vars = app_config_data[app_config["config_key"]][server_name].get("env", {})
                            server_data_with_env = server_data.copy()
                            server_data_with_env["env"] = env_vars
                            app_config_data[app_config["config_key"]][server_name] = server_data_with_env
                            with open(app_config["config_path"], 'w') as f:
                                json.dump(app_config_data, f, indent=2)
        except Exception as e:
            print(f"Error updating enabled server {server_name}: {e}")

    def load_environment_variables(self):
        self.env_vars = {}
        if os.path.exists(config.ENV_VARS_PATH):
            try:
                with open(config.ENV_VARS_PATH, 'r') as f:
                    self.env_vars = json.load(f)
            except:
                pass
                
        # Check Windsurf config
        if os.path.exists(config.WINDSURF_CONFIG_PATH):
            try:
                with open(config.WINDSURF_CONFIG_PATH, 'r') as f:
                    windsurf_config = json.load(f)
                    if "mcpServers" in windsurf_config:
                        self.enabled_servers.update(windsurf_config["mcpServers"].keys())
            except:
                pass
    
    def ensure_config_exists(self, app_config):
        """Ensure the config file exists and has the correct structure"""
        try:
            os.makedirs(os.path.dirname(app_config["config_path"]), exist_ok=True)
            
            # If file doesn't exist, create it with empty mcpServers object
            if not os.path.exists(app_config["config_path"]):
                with open(app_config["config_path"], 'w') as f:
                    json.dump({app_config["config_key"]: {}}, f, indent=2)
            
            # If file exists but doesn't have mcpServers, add it
            else:
                try:
                    with open(app_config["config_path"], 'r') as f:
                        app_data = json.load(f)
                        if app_config["config_key"] not in app_data:
                            app_data[app_config["config_key"]] = {}
                            with open(app_config["config_path"], 'w') as f:
                                json.dump(app_data, f, indent=2)
                except json.JSONDecodeError:
                    # If file is corrupted, create new one
                    with open(app_config["config_path"], 'w') as f:
                        json.dump({app_config["config_key"]: {}}, f, indent=2)
        except Exception as e:
            print(f"Error ensuring config exists for {app_config['name']}: {e}")

    def load_current_configs(self):
        self.enabled_servers = set()
        
        # Check all application configs
        for app_id, app_config in config.APPLICATIONS.items():
            self.ensure_config_exists(app_config)
            try:
                with open(app_config["config_path"], 'r') as f:
                    app_data = json.load(f)
                    if app_config["config_key"] in app_data:
                        self.enabled_servers.update(app_data[app_config["config_key"]].keys())
            except:
                pass

    def sync_application_configs(self):
        """Ensure all application configs are in sync with enabled servers"""
        try:
            # Get all currently enabled servers from all applications
            all_enabled_servers = set()
            for app_id, app_config in config.APPLICATIONS.items():
                self.ensure_config_exists(app_config)
                try:
                    with open(app_config["config_path"], 'r') as f:
                        app_data = json.load(f)
                        if app_config["config_key"] in app_data:
                            all_enabled_servers.update(app_data[app_config["config_key"]].keys())
                except:
                    continue

            # For each enabled server, ensure it exists in all application configs
            for server_name in all_enabled_servers:
                if server_name not in self.servers:
                    # If server doesn't exist anymore, remove it from all configs
                    for app_id, app_config in config.APPLICATIONS.items():
                        self.ensure_config_exists(app_config)
                        try:
                            with open(app_config["config_path"], 'r') as f:
                                app_data = json.load(f)
                                if app_config["config_key"] in app_data and server_name in app_data[app_config["config_key"]]:
                                    del app_data[app_config["config_key"]][server_name]
                                    with open(app_config["config_path"], 'w') as f:
                                        json.dump(app_data, f, indent=2)
                        except:
                            continue
                else:
                    # If server exists, ensure it's properly configured in all apps
                    server_data = self.servers[server_name]["config"]
                    for app_id, app_config in config.APPLICATIONS.items():
                        self.ensure_config_exists(app_config)
                        try:
                            with open(app_config["config_path"], 'r') as f:
                                app_data = json.load(f)
                                if app_config["config_key"] not in app_data:
                                    app_data[app_config["config_key"]] = {}
                                
                                # Preserve environment variables if they exist
                                if server_name in app_data[app_config["config_key"]]:
                                    env_vars = app_data[app_config["config_key"]][server_name].get("env", {})
                                    server_data_with_env = server_data.copy()
                                    server_data_with_env["env"] = env_vars
                                    app_data[app_config["config_key"]][server_name] = server_data_with_env
                                else:
                                    app_data[app_config["config_key"]][server_name] = server_data
                                
                                with open(app_config["config_path"], 'w') as f:
                                    json.dump(app_data, f, indent=2)
                        except:
                            continue

            # Update our enabled servers set to match the actual state
            self.enabled_servers = all_enabled_servers.intersection(self.servers.keys())
            
        except Exception as e:
            print(f"Error syncing application configs: {e}")

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
            # Update all application configs
            for app_id, app_config in config.APPLICATIONS.items():
                if os.path.exists(app_config["config_path"]):
                    try:
                        with open(app_config["config_path"], 'r') as f:
                            app_data = json.load(f)
                            if app_config["config_key"] in app_data and server_name in app_data[app_config["config_key"]]:
                                del app_data[app_config["config_key"]][server_name]
                                with open(app_config["config_path"], 'w') as f:
                                    json.dump(app_data, f, indent=2)
                    except:
                        pass
            
            # Update UI
            self.enabled_servers.discard(server_name)
            self.refresh_server_states()
            
            app_names = [app["name"] for app in config.APPLICATIONS.values()]
            QMessageBox.information(self, "Success", 
                                  f"Server '{server_name}' has been disabled!\n"
                                  f"Please restart {', '.join(app_names)} for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to disable server: {str(e)}")
    
    def enable_server(self, server_name):
        server_info = self.servers[server_name]
        server_config = server_info["config"]
        
        # Check if server has environment variables
        env_vars = server_config.get("env", {})
        if env_vars:
            # Get existing values or defaults
            existing_vars = self.env_vars.get(server_name, {})
            for var_name in env_vars:
                if var_name not in existing_vars:
                    existing_vars[var_name] = env_vars[var_name]
            
            # Show dialog for environment variables
            dialog = EnvironmentVariablesDialog(server_name, existing_vars, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Save the environment variables
                self.env_vars[server_name] = dialog.get_environment_variables()
                self.save_environment_variables()
            else:
                return  # User cancelled
        
        try:
            # Update all application configs
            for app_id, app_config in config.APPLICATIONS.items():
                os.makedirs(os.path.dirname(app_config["config_path"]), exist_ok=True)
                
                # Load existing config or create new one
                app_data = {}
                if os.path.exists(app_config["config_path"]):
                    try:
                        with open(app_config["config_path"], 'r') as f:
                            app_data = json.load(f)
                    except json.JSONDecodeError:
                        pass
                
                # Initialize mcpServers if it doesn't exist
                if app_config["config_key"] not in app_data:
                    app_data[app_config["config_key"]] = {}
                
                # Update the specific server config with environment variables
                server_config_with_env = server_config.copy()
                if env_vars and server_name in self.env_vars:
                    server_config_with_env["env"] = self.env_vars[server_name]
                
                # Update the specific server config
                app_data[app_config["config_key"]][server_name] = server_config_with_env
                
                # Save updated config
                with open(app_config["config_path"], 'w') as f:
                    json.dump(app_data, f, indent=2)
            
            # Update UI
            self.enabled_servers.add(server_name)
            self.refresh_server_states()
                
            app_names = [app["name"] for app in config.APPLICATIONS.values()]
            QMessageBox.information(self, "Success", 
                                  f"Server '{server_name}' has been enabled!\n"
                                  f"Please restart {', '.join(app_names)} for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def refresh_server_states(self):
        # Update all server cards' button states
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, ServerCard):
                server_name = widget.findChild(QLabel, "titleLabel").text()
                widget.update_button_state(server_name in self.enabled_servers)

    def save_environment_variables(self):
        os.makedirs(os.path.dirname(config.ENV_VARS_PATH), exist_ok=True)
        with open(config.ENV_VARS_PATH, 'w') as f:
            json.dump(self.env_vars, f, indent=2)

def main():
    app = QApplication(sys.argv)
    window = MCPServerManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
