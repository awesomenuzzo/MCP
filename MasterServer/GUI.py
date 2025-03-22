import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QMessageBox, QGridLayout, QFrame, QScrollArea,
                            QGraphicsDropShadowEffect, QDialog, QLineEdit,
                            QFormLayout, QDialogButtonBox, QStackedWidget,
                            QMenu, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint, QRect, QFileSystemWatcher, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QLinearGradient, QFont, QGradient
from PyQt6.QtSvg import QSvgRenderer
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
        
        # Set size policy to expand horizontally and vertically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Set minimum width to ensure cards don't get too small
        self.setMinimumWidth(500)
        
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
                padding: 8px 16px;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: 500;
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
        icon_layout = QHBoxLayout(icon_container)  # Changed to QHBoxLayout for better centering
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(config.CARD_STYLES["icon_size"], config.CARD_STYLES["icon_size"])
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the content in the label
        
        # Try to find an icon file (first PNG, then SVG)
        icon_path = os.path.join(server_path, "icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(server_path, "icon.svg")
            if not os.path.exists(icon_path):
                # Use default logo if no icon exists
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_icon.png")
        
        def create_scaled_pixmap(source_width, source_height, device_pixel_ratio, container_size, render_func):
            """Common scaling function for both SVG and PNG images"""
            # Calculate the scaling factor while preserving aspect ratio
            scale_factor = min(container_size / source_width, container_size / source_height)
            new_width = int(source_width * scale_factor)
            new_height = int(source_height * scale_factor)
            
            # Create a transparent background with device pixel ratio awareness
            final_pixmap = QPixmap(
                int(container_size * device_pixel_ratio),
                int(container_size * device_pixel_ratio)
            )
            final_pixmap.setDevicePixelRatio(device_pixel_ratio)
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Calculate position to center the scaled image
            x = int((container_size * device_pixel_ratio - new_width * device_pixel_ratio) // 2)
            y = int((container_size * device_pixel_ratio - new_height * device_pixel_ratio) // 2)
            
            # Draw the scaled image onto the transparent background
            painter = QPainter(final_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # Call the provided render function with calculated dimensions
            render_func(painter, x, y, new_width, new_height, device_pixel_ratio)
            painter.end()
            
            return final_pixmap
        
        # Load the image based on its type
        original_pixmap = None
        if icon_path.lower().endswith('.svg'):
            # Handle SVG files
            renderer = QSvgRenderer(icon_path)
            if renderer.isValid():
                device_pixel_ratio = self.devicePixelRatio()
                container_size = config.CARD_STYLES["icon_size"]
                
                def svg_render(painter, x, y, width, height, dpr):
                    from PyQt6.QtCore import QRectF
                    # Render SVG directly at the target size
                    renderer.render(painter, QRectF(x/dpr, y/dpr, width, height))
                
                original_pixmap = create_scaled_pixmap(
                    container_size,  # Use container size as source size
                    container_size,  # Use container size as source size
                    device_pixel_ratio,
                    container_size,
                    svg_render
                )
        else:
            # Handle PNG and other bitmap formats
            temp_pixmap = QPixmap(icon_path)
            if not temp_pixmap.isNull():
                device_pixel_ratio = self.devicePixelRatio()
                container_size = config.CARD_STYLES["icon_size"]
                
                def png_render(painter, x, y, width, height, dpr):
                    from PyQt6.QtCore import QPoint
                    scaled_pixmap = temp_pixmap.scaled(
                        int(width * dpr),
                        int(height * dpr),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    scaled_pixmap.setDevicePixelRatio(dpr)
                    painter.drawPixmap(QPoint(int(x), int(y)), scaled_pixmap)
                
                original_pixmap = create_scaled_pixmap(
                    temp_pixmap.width(),
                    temp_pixmap.height(),
                    device_pixel_ratio,
                    container_size,
                    png_render
                )
        
        # Check if the image loaded successfully
        if original_pixmap is None or original_pixmap.isNull() or original_pixmap.width() == 0 or original_pixmap.height() == 0:
            # Create a fallback pixmap with the first letter of the server name
            container_size = config.CARD_STYLES["icon_size"]
            device_pixel_ratio = self.devicePixelRatio()
            final_pixmap = QPixmap(
                int(container_size * device_pixel_ratio),
                int(container_size * device_pixel_ratio)
            )
            final_pixmap.setDevicePixelRatio(device_pixel_ratio)
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Draw the first letter
            painter = QPainter(final_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Set up the font
            font = QFont()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            
            # Draw the letter
            text = name[0].upper() if name else "M"
            text_rect = painter.fontMetrics().boundingRect(text)
            x = (container_size * device_pixel_ratio - text_rect.width()) // 2
            y = (container_size * device_pixel_ratio + text_rect.height()) // 2
            painter.setPen(QColor(config.COLORS["text_primary"]))
            painter.drawText(x, y, text)
            painter.end()
        else:
            final_pixmap = original_pixmap
        
        icon_label.setPixmap(final_pixmap)
        icon_label.setScaledContents(False)  # Don't let the label scale the contents
        
        icon_layout.addWidget(icon_label)
        
        # Add icon container to main layout
        layout.addWidget(icon_container)
        
        # Content container (middle)
        content_container = QWidget()
        content_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
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
        layout.addWidget(content_container, 1)  # Takes up available space
        
        # Button container (right side)
        button_container = QWidget()
        button_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        # Button and menu container
        button_menu_container = QWidget()
        button_menu_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        button_menu_layout = QHBoxLayout(button_menu_container)
        button_menu_layout.setContentsMargins(0, 0, 0, 0)
        button_menu_layout.setSpacing(4)
        
        # Enable/Disable buttons container
        toggle_button_container = QWidget()
        toggle_button_container.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        toggle_button_layout = QVBoxLayout(toggle_button_container)
        toggle_button_layout.setContentsMargins(0, 0, 0, 0)
        toggle_button_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Enable button
        self.enable_button = QPushButton("Enable Server")
        self.enable_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.enable_button.setObjectName("enableButton")
        toggle_button_layout.addWidget(self.enable_button)
        
        # Disable button
        self.disable_button = QPushButton("Disable Server")
        self.disable_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
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
        
        # Add containers to main layout with appropriate stretches
        layout.addWidget(icon_container, 0)  # No stretch
        layout.addWidget(content_container, 1)  # Takes up available space
        layout.addWidget(button_container, 0)  # No stretch
        
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
            QScrollBar:vertical {{
                border: none;
                background-color: {config.COLORS["background"]};
                width: 12px;
                margin: 0px 2px 0px 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {config.COLORS["border"]};
                min-height: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {config.COLORS["text_secondary"]};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
                border: none;
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
            
            # Add the MCP to the servers dictionary and installed list
            self.parent_window.servers[mcp_name] = mcp_info
            self.parent_window.installed_mcps.add(mcp_name)
            self.parent_window.save_installed_mcps()
            
            # Update both the app store and main window
            self.parent_window.update_app_store()
            self.parent_window.populate_server_grid()
            
            # Show success message
            self.parent_window.notification_manager.show_notification(
                self.parent_window,
                f"MCP '{mcp_name}' has been installed!\n"
                f"You can now enable it from the main window."
            )
            
        except Exception as e:
            self.parent_window.notification_manager.show_notification(
                self.parent_window,
                f"Failed to install MCP: {str(e)}",
                duration=5000
            )

class ToastNotification(QFrame):
    def __init__(self, parent=None, message="", duration=3000):
        super().__init__(parent)
        
        # Set up the frame
        self.setFixedWidth(300)
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {config.COLORS["card_background"]};
                border-radius: 8px;
                border: 1px solid {config.COLORS["border"]};
            }}
            QLabel {{
                color: {config.COLORS["text_primary"]};
                font-size: 14px;
                padding: 0px;
                background: transparent;
            }}
        """)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Add message
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Size the frame based on content
        self.adjustSize()
        
        # Set up animations
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Show animation
        self.setWindowOpacity(0.0)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        
        # Set up timer for auto-hide
        QTimer.singleShot(duration, self.hide_animation)
    
    def hide_animation(self):
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.on_fade_out_finished)
        self.fade_anim.start()
    
    def on_fade_out_finished(self):
        # Notify parent of removal before deletion
        if hasattr(self.parent(), 'on_notification_removed'):
            self.parent().on_notification_removed(self)
        self.deleteLater()

class NotificationManager:
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = NotificationManager()
        return cls._instance
    
    def __init__(self):
        self.notifications = []
        self.margin = 20
        self.spacing = 10
    
    def show_notification(self, parent, message, duration=3000):
        # Create new notification
        notification = ToastNotification(parent, message, duration)
        
        # Remove any deleted notifications from the list
        self.notifications = [n for n in self.notifications if n and not n.isHidden()]
        
        # Calculate position (top right with margin)
        x = parent.width() - notification.width() - self.margin
        
        # Calculate y position based on existing notifications
        y = self.margin
        for existing in self.notifications:
            if existing and not existing.isHidden():
                y += existing.height() + self.spacing
        
        notification.move(x, y)
        notification.show()
        
        # Add to notifications list
        self.notifications.append(notification)
    
    def on_notification_removed(self, notification):
        """Called when a notification is about to be removed"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            
        # Reposition remaining notifications
        if not self.notifications:
            return
            
        y = self.margin
        for n in self.notifications:
            if n and not n.isHidden():
                n.move(n.x(), y)
                y += n.height() + self.spacing

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
        self.installed_mcps = set()  # Track installed MCPs
        
        # Initialize notification manager first
        self.notification_manager = NotificationManager.instance()
        
        # Add method to handle notification removal
        def on_notification_removed(notification):
            self.notification_manager.on_notification_removed(notification)
        
        # Add the method to the instance
        self.on_notification_removed = on_notification_removed
        
        # Initialize file watcher
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.handle_config_change)
        self.config_update_timer = QTimer(self)
        self.config_update_timer.setSingleShot(True)
        self.config_update_timer.timeout.connect(self.process_config_changes)
        self.pending_changes = set()
        
        # Initialize the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)  # Changed to QHBoxLayout for sidebar
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(48)  # Narrow sidebar
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {config.COLORS["card_background"]};
                border-right: 1px solid {config.COLORS["border"]};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 0)  # Only top margin
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)  # Top center alignment
        
        # Add button in sidebar
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(32, 32)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {config.COLORS["text_primary"]};
                border: none;
                border-radius: 16px;
                font-size: 20px;
                font-weight: normal;
                padding: 0;
                text-align: center;
                line-height: 30px;  /* Slightly reduced to account for font metrics */
                margin: 0;
                vertical-align: middle;
            }}
            QPushButton:hover {{
                background-color: {config.COLORS["border"]};
            }}
            QPushButton:pressed {{
                margin-top: 2px;
                margin-bottom: -2px;
            }}
        """)
        self.add_button.clicked.connect(self.show_app_store)
        sidebar_layout.addWidget(self.add_button)
        
        # Add sidebar to main layout
        main_layout.addWidget(sidebar)
        
        # Create content container
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create home page
        self.home_page = QWidget()
        self.setup_home_page()
        content_layout.addWidget(self.home_page)
        
        # Add content container to main layout
        main_layout.addWidget(content_container)
        
        # Create app store window (but don't show it yet)
        self.app_store_window = None
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {config.COLORS["background"]};
            }}
        """)
        
        # Load initial data and start monitoring
        self.load_all_data()
        self.setup_file_monitoring()
        
        # Add method to handle notification removal
        def on_notification_removed(notification):
            pass
        
        # Add the method to the instance
        self.on_notification_removed = on_notification_removed
    
    def setup_file_monitoring(self):
        """Set up monitoring for all server config files"""
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Scan for server config files
        for item in os.listdir(parent_dir):
            if item.startswith('.') or item == "MasterServer":
                continue
                
            full_path = os.path.join(parent_dir, item)
            if not os.path.isdir(full_path):
                continue
                
            config_path = os.path.join(full_path, "config.json")
            if os.path.exists(config_path):
                self.file_watcher.addPath(config_path)
    
    def handle_config_change(self, path):
        """Handle a config file change event"""
        # Add the changed file to pending changes
        self.pending_changes.add(path)
        
        # Restart the timer to process changes
        self.config_update_timer.start(1000)  # Wait 1 second before processing changes
        
        # Re-add the file to the watcher (some systems remove it after a change)
        if os.path.exists(path):
            self.file_watcher.addPath(path)
    
    def process_config_changes(self):
        """Process all pending server config changes"""
        if not self.pending_changes:
            return
            
        try:
            # Track which applications need to be updated
            apps_with_changes = set()
            
            # Process each changed server config file
            for path in self.pending_changes:
                try:
                    # Get the server name from the path
                    server_dir = os.path.dirname(path)
                    server_name = os.path.basename(server_dir)
                    
                    # Load the updated server config
                    try:
                        with open(path, 'r') as f:
                            server_config = json.load(f)
                    except json.JSONDecodeError as je:
                        # Get the line content where the error occurred
                        with open(path, 'r') as f:
                            lines = f.readlines()
                            error_line = lines[je.lineno - 1] if je.lineno <= len(lines) else ""
                            
                        self.notification_manager.show_notification(
                            self,
                            f"Invalid JSON in config file for {server_name}:\n"
                            f"Line {je.lineno}: {error_line.strip()}\n"
                            f"Error: {str(je)}",
                            duration=5000
                        )
                        continue
                    except Exception as e:
                        self.notification_manager.show_notification(
                            self,
                            f"Failed to read config file for {server_name}:\n{str(e)}",
                            duration=5000
                        )
                        continue
                    
                    # Update the server in our servers dictionary
                    if server_name in self.servers:
                        # Update the config while preserving the path
                        self.servers[server_name]["config"] = server_config
                        
                        # If this server is enabled, update all application configs
                        if server_name in self.enabled_servers:
                            for app_id, app_config in config.APPLICATIONS.items():
                                try:
                                    with open(app_config["config_path"], 'r') as f:
                                        app_data = json.load(f)
                                        if app_config["config_key"] in app_data and server_name in app_data[app_config["config_key"]]:
                                            # Get the current server config from the app
                                            current_app_config = app_data[app_config["config_key"]][server_name]
                                            
                                            # Create a new config that preserves required fields
                                            new_config = {
                                                "command": current_app_config.get("command", server_config.get("command", "")),
                                                "args": server_config.get("args", []),
                                                "env": current_app_config.get("env", {})
                                            }
                                            
                                            # Update any other fields from the server config
                                            for key, value in server_config.items():
                                                if key not in ["command", "args", "env"]:
                                                    new_config[key] = value
                                            
                                            # Update the server config in the app
                                            app_data[app_config["config_key"]][server_name] = new_config
                                            with open(app_config["config_path"], 'w') as f:
                                                json.dump(app_data, f, indent=2)
                                            apps_with_changes.add(app_config["name"])
                                except Exception as e:
                                    self.notification_manager.show_notification(
                                        self,
                                        f"Failed to update config for {app_config['name']}:\n{str(e)}",
                                        duration=5000
                                    )
                                    continue
                    
                except Exception as e:
                    self.notification_manager.show_notification(
                        self,
                        f"Error processing config change for {os.path.basename(path)}:\n{str(e)}",
                        duration=5000
                    )
                    continue
            
            # Clear pending changes
            self.pending_changes.clear()
            
            # Update the UI
            self.populate_server_grid()
            
            # Notify user about changes
            if apps_with_changes:
                apps_list = ", ".join(sorted(apps_with_changes))
                self.notification_manager.show_notification(
                    self,
                    f"Server configurations have been updated for: {apps_list}\n"
                    f"Please restart these applications for the changes to take effect."
                )
                
        except Exception as e:
            self.notification_manager.show_notification(
                self,
                f"Error syncing configurations:\n{str(e)}",
                duration=5000
            )
    
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
            QScrollBar:vertical {{
                border: none;
                background-color: {config.COLORS["background"]};
                width: 12px;
                margin: 0px 2px 0px 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {config.COLORS["border"]};
                min-height: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {config.COLORS["text_secondary"]};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
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
            
            # Remove from enabled servers, installed MCPs, and servers dictionary
            self.enabled_servers.discard(server_name)
            self.installed_mcps.discard(server_name)
            if server_name in self.servers:
                del self.servers[server_name]
            
            # Add to deleted MCPs list
            self.deleted_mcps.add(server_name)
            self.save_deleted_mcps()
            self.save_installed_mcps()
            
            # Update both main window and app store
            self.populate_server_grid()
            if self.app_store_window and self.app_store_window.isVisible():
                self.app_store_window.hide()  # Hide and show to force a refresh
                self.update_app_store()
                self.app_store_window.show()
            
            # Show success message
            app_names = [app["name"] for app in config.APPLICATIONS.values()]
            self.notification_manager.show_notification(
                self,
                f"MCP '{server_name}' has been removed!\n"
                f"Please restart {', '.join(app_names)} for changes to take effect."
            )
            
        except Exception as e:
            self.notification_manager.show_notification(
                self,
                f"Failed to remove MCP: {str(e)}",
                duration=5000
            )

    def populate_server_grid(self):
        """Populate the main window grid with installed MCPs"""
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # Calculate number of columns based on window width
        window_width = self.width()
        if window_width >= 1500:  # Very wide window - 3 columns
            num_columns = 3
        elif window_width >= 1000:  # Medium window - 2 columns
            num_columns = 2
        else:  # Narrow window - 1 column
            num_columns = 1
        
        # Add cards in a grid
        sorted_servers = sorted(self.servers.items())
        for idx, (server_name, server_info) in enumerate(sorted_servers):
            row = idx // num_columns
            col = idx % num_columns
            
            is_enabled = server_name in self.enabled_servers
            card = ServerCard(server_name, server_info["config"], server_info["path"], is_enabled)
            card.enable_button.clicked.connect(lambda checked, name=server_name: self.enable_server(name))
            card.disable_button.clicked.connect(lambda checked, name=server_name: self.disable_server(name))
            
            # Create and connect menu
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda checked, name=server_name: self.delete_mcp(name))
            card.menu_button.clicked.connect(lambda checked, m=menu, b=card.menu_button: m.exec(b.mapToGlobal(b.rect().bottomLeft())))
            
            self.grid_layout.addWidget(card, row, col)
        
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
            self.notification_manager.show_notification(
                self,
                f"Server '{server_name}' has been disabled!\n"
                f"Please restart {', '.join(app_names)} for changes to take effect."
            )
            
        except Exception as e:
            self.notification_manager.show_notification(
                self,
                f"Failed to disable server: {str(e)}",
                duration=5000
            )
    
    def enable_server(self, server_name):
        server_info = self.servers[server_name]
        server_config = server_info["config"]
        
        # Check if server has environment variables
        env_vars = server_config.get("env", {})
        if env_vars:
            # Get existing values or defaults
            existing_vars = self.env_vars.get(server_name, {})
            
            # Only include variables that are actually defined in the server's config.json
            filtered_vars = {}
            for var_name in env_vars:
                if var_name not in existing_vars:
                    filtered_vars[var_name] = env_vars[var_name]
                else:
                    filtered_vars[var_name] = existing_vars[var_name]
            
            # Show dialog for environment variables
            dialog = EnvironmentVariablesDialog(server_name, filtered_vars, self)
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
            self.notification_manager.show_notification(
                self,
                f"Server '{server_name}' has been enabled!\n"
                f"Please restart {', '.join(app_names)} for changes to take effect."
            )
            
        except Exception as e:
            self.notification_manager.show_notification(
                self,
                f"Failed to save configuration: {str(e)}",
                duration=5000
            )
    
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
        self.load_installed_mcps()  # Load installed MCPs before loading servers
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

    def load_installed_mcps(self):
        """Load the list of installed MCPs"""
        self.installed_mcps = set()
        if os.path.exists(config.INSTALLED_MCPS_PATH):
            try:
                with open(config.INSTALLED_MCPS_PATH, 'r') as f:
                    self.installed_mcps = set(json.load(f))
            except:
                pass
    
    def save_installed_mcps(self):
        """Save the current list of installed MCPs"""
        os.makedirs(os.path.dirname(config.INSTALLED_MCPS_PATH), exist_ok=True)
        with open(config.INSTALLED_MCPS_PATH, 'w') as f:
            json.dump(list(self.installed_mcps), f, indent=2)

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
                    
                # Load servers that are either installed or enabled
                for server_name, server_data in server_config.items():
                    # Skip deleted MCPs
                    if server_name in self.deleted_mcps:
                        continue
                        
                    # Only load if installed or enabled
                    if server_name not in self.installed_mcps and server_name not in enabled_servers:
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
            # Track which applications had config changes
            apps_with_changes = set()
            
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
                                    apps_with_changes.add(app_config["name"])
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
                                
                                # Check if config needs updating
                                needs_update = False
                                if server_name not in app_data[app_config["config_key"]]:
                                    needs_update = True
                                else:
                                    current_config = app_data[app_config["config_key"]][server_name]
                                    # Compare configs excluding env vars
                                    current_without_env = current_config.copy()
                                    current_without_env.pop("env", None)
                                    server_without_env = server_data.copy()
                                    server_without_env.pop("env", None)
                                    if current_without_env != server_without_env:
                                        needs_update = True
                                
                                if needs_update:
                                    # Preserve environment variables if they exist
                                    env_vars = app_data[app_config["config_key"]].get(server_name, {}).get("env", {})
                                    server_data_with_env = server_data.copy()
                                    if env_vars:
                                        server_data_with_env["env"] = env_vars
                                    app_data[app_config["config_key"]][server_name] = server_data_with_env
                                    with open(app_config["config_path"], 'w') as f:
                                        json.dump(app_data, f, indent=2)
                                    apps_with_changes.add(app_config["name"])
                        except:
                            continue

            # Update our enabled servers set to match the actual state
            self.enabled_servers = all_enabled_servers.intersection(self.servers.keys())
            
            # If there were any changes, notify the user
            if apps_with_changes:
                apps_list = ", ".join(sorted(apps_with_changes))
                self.notification_manager.show_notification(
                    self,
                    f"MCP configurations have been updated for: {apps_list}\n"
                    f"Please restart these applications for the changes to take effect."
                )
            
        except Exception as e:
            print(f"Error syncing application configs: {e}")
            self.notification_manager.show_notification(
                self,
                f"Error syncing configurations: {str(e)}",
                duration=5000
            )

def main():
    app = QApplication(sys.argv)
    window = MCPServerManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
