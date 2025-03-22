import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QMessageBox, QGridLayout, QFrame, QScrollArea,
                            QGraphicsDropShadowEffect, QDialog, QLineEdit,
                            QFormLayout, QDialogButtonBox, QStackedWidget,
                            QMenu)
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QLinearGradient, QFont, QGradient
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
        self.setGraphicsEffect(None)  # Explicitly remove any graphics effects
        
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
                background-color: transparent;
            }}
            QPushButton#enableButton {{
                background-color: {config.COLORS["primary"]};
                color: white;
            }}
            QPushButton#enableButton:hover {{
                background-color: {config.COLORS["primary_hover"]};
            }}
            QPushButton#disableButton {{
                background-color: {config.COLORS["danger"]};
                color: white;
            }}
            QPushButton#disableButton:hover {{
                background-color: {config.COLORS["danger_hover"]};
            }}
            QPushButton#menuButton {{
                background-color: transparent;
                color: {config.COLORS["text_secondary"]};
                padding: 4px;
                min-width: 32px;
                max-width: 32px;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton#menuButton:hover {{
                background-color: {config.COLORS["border"]};
                color: {config.COLORS["text_primary"]};
            }}
            QMenu {{
                background-color: {config.COLORS["card_background"]};
                border: 1px solid {config.COLORS["border"]};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                color: {config.COLORS["text_primary"]};
                font-size: 14px;
            }}
            QMenu::item:selected {{
                background-color: {config.COLORS["border"]};
                color: {config.COLORS["text_primary"]};
            }}
            QWidget {{
                background: transparent;
            }}
        """)
        
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
            # Create default MCP text icon
            container_size = config.CARD_STYLES["icon_size"]
            pixmap = QPixmap(container_size, container_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw white background with rounded corners
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("white"))
            painter.drawRoundedRect(0, 0, container_size, container_size, 12, 12)
            
            # Draw text
            font = QFont("Arial", 24)
            font.setBold(True)
            painter.setFont(font)
            
            # Draw text in primary color
            painter.setPen(QColor(config.COLORS["primary"]))
            painter.drawText(QRect(0, 0, container_size, container_size), 
                           Qt.AlignmentFlag.AlignCenter, "M.C.P.")
            
            painter.end()
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
        
        # Title container
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # Title
        title_label = QLabel(name)
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        content_layout.addWidget(title_container)
        
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
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        # Button and menu container
        button_menu_container = QWidget()
        button_menu_layout = QHBoxLayout(button_menu_container)
        button_menu_layout.setContentsMargins(0, 0, 0, 0)
        button_menu_layout.setSpacing(4)
        
        # Enable/Disable buttons container
        toggle_button_container = QWidget()
        toggle_button_layout = QVBoxLayout(toggle_button_container)
        toggle_button_layout.setContentsMargins(0, 0, 0, 0)
        toggle_button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Enable button
        self.enable_button = QPushButton("Enable Server")
        self.enable_button.setObjectName("enableButton")
        toggle_button_layout.addWidget(self.enable_button)
        
        # Disable button
        self.disable_button = QPushButton("Disable Server")
        self.disable_button.setObjectName("disableButton")
        toggle_button_layout.addWidget(self.disable_button)
        
        button_menu_layout.addWidget(toggle_button_container)
        
        # Menu button
        self.menu_button = QPushButton("⋮")  # Using vertical ellipsis character
        self.menu_button.setObjectName("menuButton")
        self.menu_button.setFixedSize(32, 32)
        self.menu_button.setGraphicsEffect(None)  # Explicitly remove any shadow effect
        self.menu_button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Make background truly transparent
        button_menu_layout.addWidget(self.menu_button)
        
        # Ensure the menu button's container is also shadow-free
        button_menu_container.setGraphicsEffect(None)
        button_menu_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        button_layout.addWidget(button_menu_container)
        
        # Add button container to main layout
        layout.addWidget(button_container)
        
        # Update button visibility based on enabled state
        self.update_button_state(is_enabled)
        
        # Set fixed height but allow width to be flexible
        self.setFixedHeight(120)
        
    def update_button_state(self, is_enabled):
        self.enable_button.setVisible(not is_enabled)
        self.disable_button.setVisible(is_enabled)

class AppStorePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Store parent reference
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("MCP Store")
        header.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {config.COLORS["text_primary"]};
            margin-bottom: 12px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        description = QLabel("Browse and install MCPs to give your LLM new capabilities")
        description.setStyleSheet(f"""
            font-size: 16px;
            color: {config.COLORS["text_secondary"]};
            margin-bottom: 24px;
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Scroll area for MCP grid
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
        layout.addWidget(scroll)
        
    def populate_grid(self, available_mcps):
        """Populate the app store grid with available MCPs"""
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # Add cards for available MCPs
        for mcp_name, mcp_info in sorted(available_mcps.items()):
            card = ServerCard(mcp_name, mcp_info["config"], mcp_info["path"], is_enabled=False)
            card.enable_button.setText("Install")
            card.enable_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {config.COLORS["primary"]};
                    color: white;
                    border: none;
                    padding: 8px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    min-width: {config.CARD_STYLES["button_min_width"]}px;
                }}
                QPushButton:hover {{
                    background-color: {config.COLORS["primary_hover"]};
                }}
            """)
            card.disable_button.setVisible(False)
            card.menu_button.setVisible(False)  # Hide menu button in app store
            card.enable_button.clicked.connect(lambda checked, name=mcp_name, info=mcp_info: self.install_mcp(name, info))
            self.grid_layout.addWidget(card)
            
            # Add a small spacer after each card except the last one
            if mcp_name != list(available_mcps.keys())[-1]:
                spacer = QWidget()
                spacer.setFixedHeight(1)
                self.grid_layout.addWidget(spacer)
        
        # Force layout update
        self.grid_layout.update()
        if self.parent_window:
            self.parent_window.update()

    def install_mcp(self, mcp_name, mcp_info):
        """Install an MCP from the app store"""
        try:
            # Remove from deleted MCPs if it was previously deleted
            self.parent_window.deleted_mcps.discard(mcp_name)
            self.parent_window.save_deleted_mcps()
            
            # Add the MCP to the servers dictionary
            self.parent_window.servers[mcp_name] = mcp_info
            
            # Enable the MCP
            self.parent_window.enable_server(mcp_name)
            
            # Update both the app store and main window
            self.parent_window.update_app_store()
            self.parent_window.populate_server_grid()
            
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"MCP '{mcp_name}' has been installed and enabled!\n"
                                  f"Please restart your applications for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to install MCP: {str(e)}")

class MCPServerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Initialize data structures
        self.servers = {}
        self.enabled_servers = set()
        self.env_vars = {}
        self.deleted_mcps = set()
        
        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create home page
        self.home_page = QWidget()
        self.setup_home_page()
        main_layout.addWidget(self.home_page)
        
        # Create app store window (but don't show it yet)
        self.app_store_window = None
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {config.COLORS["background"]};
            }}
        """)
        
        # Add floating button after everything else is set up
        self.setup_floating_button()
        
        # Load initial data
        self.load_all_data()
    
    def setup_floating_button(self):
        """Set up the floating add button in the bottom right corner"""
        # Floating add button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(56, 56)
        self.add_button.setGraphicsEffect(None)  # Explicitly remove any shadow effect
        self.add_button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Make background truly transparent
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #000000;
                border: none;
                border-radius: 28px;  /* Half of width/height for perfect circle */
                font-size: 24px;  /* Reduced font size for better centering */
                font-weight: normal;  /* Normal weight for cleaner look */
                margin: 16px;
                text-align: center;
                padding: 0px;  /* Remove padding to ensure perfect circle */
                line-height: 52px;  /* Center the plus sign vertically */
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
                margin-top: 18px;
                margin-bottom: 14px;
            }}
        """)
        self.add_button.clicked.connect(self.show_app_store)
        
        # Create a container for the add button that stays on top
        self.button_container = QWidget(self)
        self.button_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.button_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Make background truly transparent
        self.button_container.setGraphicsEffect(None)  # Ensure no shadow on container
        self.button_container.setFixedSize(88, 88)
        self.button_container.setStyleSheet("background: transparent;")
        
        button_layout = QVBoxLayout(self.button_container)
        button_layout.addWidget(self.add_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ensure the button container stays on top
        self.button_container.raise_()
        
        # Initial position
        self.update_button_position()
    
    def update_button_position(self):
        """Update the floating button position"""
        if hasattr(self, 'button_container'):
            self.button_container.move(
                self.width() - self.button_container.width(),
                self.height() - self.button_container.height()
            )
            self.button_container.raise_()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.update_button_position()
    
    def setup_home_page(self):
        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QLabel(config.WINDOW_TITLE)
        header.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {config.COLORS["text_primary"]};
            margin-bottom: 12px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
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
        layout.addWidget(scroll)
        
        # Empty state message
        self.empty_state = QLabel("No MCPs installed. Visit the MCP Store to install some!")
        self.empty_state.setStyleSheet(f"""
            font-size: 18px;
            color: {config.COLORS["text_secondary"]};
        """)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_state)
        self.empty_state.hide()
    
    def show_app_store(self):
        """Show MCP Store in a new window"""
        if not self.app_store_window:
            self.app_store_window = QMainWindow(self)
            self.app_store_window.setWindowTitle("MCP Store")
            self.app_store_window.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            
            # Create and set up app store page
            self.app_store_page = AppStorePage(self)
            self.app_store_window.setCentralWidget(self.app_store_page)
            
            # Position the new window relative to the main window
            self.app_store_window.move(
                self.x() + 50,
                self.y() + 50
            )
        
        # Update available MCPs and show the window
        self.update_app_store()
        self.app_store_window.show()
        self.app_store_window.raise_()
        self.app_store_window.activateWindow()
    
    def update_app_store(self):
        # Get all available MCPs
        available_mcps = {}
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        for item in os.listdir(parent_dir):
            if item.startswith('.') or item == "MasterServer":
                continue
                
            full_path = os.path.join(parent_dir, item)
            if not os.path.isdir(full_path):
                continue
                
            config_path = os.path.join(full_path, "config.json")
            if not os.path.exists(config_path):
                continue
                
            try:
                with open(config_path, 'r') as f:
                    server_config = json.load(f)
                    
                # Only include MCPs that aren't already installed
                for server_name, server_data in server_config.items():
                    if server_name not in self.servers:
                        # Update the command path if it's relative
                        if "args" in server_data:
                            for i, arg in enumerate(server_data["args"]):
                                if isinstance(arg, str) and arg.startswith("./"):
                                    server_data["args"][i] = os.path.join(full_path, arg[2:])
                        
                        available_mcps[server_name] = {
                            "config": server_data,
                            "path": full_path
                        }
                            
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
        
        self.app_store_page.populate_grid(available_mcps)
    
    def delete_mcp(self, server_name):
        """Remove an MCP from all application configs and update the UI"""
        try:
            # Remove from all application configs
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
            
            # Remove from enabled servers and servers dictionary
            self.enabled_servers.discard(server_name)
            if server_name in self.servers:
                del self.servers[server_name]
            
            # Add to deleted MCPs list
            self.deleted_mcps.add(server_name)
            self.save_deleted_mcps()
            
            # Update both main window and app store
            self.populate_server_grid()
            if self.app_store_window and self.app_store_window.isVisible():
                self.app_store_window.hide()  # Hide and show to force a refresh
                self.update_app_store()
                self.app_store_window.show()
            
            # Show success message
            app_names = [app["name"] for app in config.APPLICATIONS.values()]
            QMessageBox.information(self, "Success", 
                                  f"MCP '{server_name}' has been removed!\n"
                                  f"Please restart {', '.join(app_names)} for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove MCP: {str(e)}")

    def populate_server_grid(self):
        """Populate the main window grid with installed MCPs"""
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # Add cards in a single column
        for server_name, server_info in sorted(self.servers.items()):
            is_enabled = server_name in self.enabled_servers
            card = ServerCard(server_name, server_info["config"], server_info["path"], is_enabled)
            card.enable_button.clicked.connect(lambda checked, name=server_name: self.enable_server(name))
            card.disable_button.clicked.connect(lambda checked, name=server_name: self.disable_server(name))
            
            # Create and connect menu
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda checked, name=server_name: self.delete_mcp(name))
            card.menu_button.clicked.connect(lambda checked, m=menu, b=card.menu_button: m.exec(b.mapToGlobal(b.rect().bottomLeft())))
            
            self.grid_layout.addWidget(card)
            
            # Add a small spacer after each card except the last one
            if server_name != list(self.servers.keys())[-1]:
                spacer = QWidget()
                spacer.setFixedHeight(1)
                self.grid_layout.addWidget(spacer)
        
        # Show/hide empty state message
        self.empty_state.setVisible(len(self.servers) == 0)
        
        # Force layout update
        self.grid_layout.update()
        self.home_page.update()

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

    def load_all_data(self):
        """Load all data needed for the UI"""
        self.load_deleted_mcps()
        self.load_servers()
        self.load_current_configs()
        self.load_environment_variables()
        self.sync_application_configs()
        self.populate_server_grid()
    
    def load_deleted_mcps(self):
        """Load the list of deleted MCPs"""
        self.deleted_mcps = set()
        if os.path.exists(config.DELETED_MCPS_PATH):
            try:
                with open(config.DELETED_MCPS_PATH, 'r') as f:
                    self.deleted_mcps = set(json.load(f))
            except:
                pass
    
    def save_deleted_mcps(self):
        """Save the current list of deleted MCPs"""
        os.makedirs(os.path.dirname(config.DELETED_MCPS_PATH), exist_ok=True)
        with open(config.DELETED_MCPS_PATH, 'w') as f:
            json.dump(list(self.deleted_mcps), f, indent=2)

    def load_servers(self):
        """Load all installed MCPs"""
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
            if item.startswith('.') or item == "MasterServer":
                continue
                
            full_path = os.path.join(parent_dir, item)
            if not os.path.isdir(full_path):
                continue
                
            config_path = os.path.join(full_path, "config.json")
            if not os.path.exists(config_path):
                continue
                
            try:
                with open(config_path, 'r') as f:
                    server_config = json.load(f)
                    
                # Store server info with its path
                for server_name, server_data in server_config.items():
                    # Skip deleted MCPs
                    if server_name in self.deleted_mcps:
                        continue
                        
                    # Update the command path if it's relative
                    if "args" in server_data:
                        for i, arg in enumerate(server_data["args"]):
                            if isinstance(arg, str) and arg.startswith("./"):
                                server_data["args"][i] = os.path.join(full_path, arg[2:])
                    
                    self.servers[server_name] = {
                        "config": server_data,
                        "path": full_path
                    }
                            
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")

    def load_current_configs(self):
        """Load current enabled servers from all application configs"""
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

    def load_environment_variables(self):
        """Load environment variables from the config file"""
        self.env_vars = {}
        if os.path.exists(config.ENV_VARS_PATH):
            try:
                with open(config.ENV_VARS_PATH, 'r') as f:
                    self.env_vars = json.load(f)
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

def main():
    app = QApplication(sys.argv)
    window = MCPServerManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
