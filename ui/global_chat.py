from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor

class GlobalChatTab(QWidget):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setup_ui()
        self.load_messages()
        
        # Auto-refresh every 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(2000)

    def setup_ui(self):
        # Main layout with tight spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Global Physics Chat")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A7CA5, stop:1 #2F6690);
                border-radius: 6px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Message display
        self.chat_display = QTextEdit(readOnly=True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #2D3748;
                color: #E2E8F0;
                padding: 10px;
                border: 1px solid #4A5568;
                border-radius: 6px;
            }
        """)
        self.chat_display.setMinimumHeight(400)
        
        # Input area (compact)
        input_card = QWidget()
        input_card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        input_layout = QVBoxLayout(input_card)
        input_layout.setSpacing(6)
        
        # Message input with dark text for visibility
        self.message_input = QLineEdit(placeholderText="Type your message...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #1A202C;  /* Dark text for visibility */
            }
            QLineEdit:focus {
                border: 1px solid #4299E1;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        
        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4299E1, stop:1 #3182CE);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3182CE, stop:1 #2B6CB0);
            }
            QPushButton:pressed {
                background: #2C5282;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(self.chat_display)
        layout.addWidget(input_card)
        self.setLayout(layout)

    def send_message(self):
        if not hasattr(self.auth_manager, 'current_user') or not self.auth_manager.current_user:
            self.append_system_message("Please login to send messages")
            return
            
        message = self.message_input.text().strip()
        if message:
            try:
                user = self.auth_manager.current_user
                self.auth_manager.save_global_message(user[0], user[1], message)
                self.message_input.clear()
                self.load_messages()
            except Exception as e:
                self.append_system_message(f"Error sending message: {str(e)}")

    def append_system_message(self, text):
        self.chat_display.append(
            f'<div style="color: #A0AEC0; font-style: italic; margin: 2px 0;">{text}</div>'
        )

    def load_messages(self):
        try:
            messages = self.auth_manager.get_global_messages()
            current_scroll = self.chat_display.verticalScrollBar().value()
            at_bottom = self.chat_display.verticalScrollBar().value() == self.chat_display.verticalScrollBar().maximum()
            
            self.chat_display.clear()
            for msg in messages:
                self.chat_display.append(
                    f'<div style="margin: 4px 0;">'
                    f'<span style="font-weight: bold; color: #63B3ED;">{msg["username"]}</span>'
                    f'<span style="color: #718096; font-size: 12px; margin-left: 6px;">{msg["timestamp"]}</span>'
                    f'<div style="color: #E2E8F0; margin-top: 2px;">{msg["message"]}</div>'
                    f'</div>'
                )
                
            if at_bottom:
                self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            else:
                self.chat_display.verticalScrollBar().setValue(current_scroll)
                
        except Exception as e:
            self.append_system_message(f"Error loading messages: {str(e)}")