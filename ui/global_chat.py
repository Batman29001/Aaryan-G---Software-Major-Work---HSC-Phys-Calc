from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import QTimer, Qt

class GlobalChatTab(QWidget):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setup_ui()
        self.load_messages()
        
        # Auto-refresh every 3 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(3000)

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Message display
        self.chat_display = QTextEdit(readOnly=True)
        self.chat_display.setStyleSheet("""
            font-size: 14px;
            background-color: #f0f0f0;
            padding: 10px;
        """)
        
        # Input area
        self.message_input = QLineEdit(placeholderText="Type your message...")
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A7CA5;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2F6690;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        layout.addWidget(QLabel("Global Chat"))
        layout.addWidget(self.chat_display)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)
        self.setLayout(layout)

    def send_message(self):
        if not hasattr(self.auth_manager, 'current_user'):
            return  # Safety check
            
        message = self.message_input.text().strip()
        if message and hasattr(self.auth_manager, 'current_user'):
            user = self.auth_manager.current_user  # (user_id, username)
            self.auth_manager.save_global_message(user[0], user[1], message)

    def load_messages(self):
        messages = self.auth_manager.get_global_messages()
        self.chat_display.clear()
        for msg in reversed(messages):  # Newest at bottom
            self.chat_display.append(
                f"<b>{msg['username']}</b> <i>({msg['timestamp']})</i>\n"
                f"{msg['message']}\n"
            )