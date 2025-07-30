import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from ui.particle_background import ParticleBackground
from ui.qr_code_dialog import QRCodeDialog


class SignupDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("Create Account")
        self.setMinimumSize(400, 420)
        self.setMaximumWidth(400)
        self.setStyleSheet("background: transparent;")
        self.setup_ui()

    def setup_ui(self):
        self.background = ParticleBackground(self)
        self.background.resize(self.size())

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        title = QLabel("Create Your Phys Calc Account")
        title.setFont(QFont("Segoe UI", 14))
        title.setStyleSheet("color: #4FC3F7;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit(placeholderText="Username")
        self.email_input = QLineEdit(placeholderText="Email")
        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in [self.username_input, self.email_input, self.password_input]:
            field.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    background-color: #1E2A38;
                    border: 1px solid rgba(79, 195, 247, 0.35);
                    border-radius: 6px;
                    color: #CFD8DC;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #4FC3F7;
                }
            """)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38;
                color: #4FC3F7;
                border: 1px solid #4FC3F7;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #263646;
            }
        """)
        self.signup_btn.clicked.connect(self.handle_signup)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF9A9A; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.signup_btn)
        main_layout.addWidget(self.error_label)

    def handle_signup(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not all([username, email, password]):
            self.error_label.setText("All fields are required.")
            return

        if len(username) < 3 or not re.match(r'^[a-zA-Z0-9_.]+$', username):
            self.error_label.setText("Username must be 3+ chars (letters, numbers, _, . only).")
            return

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            self.error_label.setText("Invalid email format.")
            return

        if len(password) < 8 or not (
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password)
        ):
            self.error_label.setText("Password must be 8+ chars, upper, lower, digit & symbol.")
            return

        # SIGNUP + GET 2FA SECRET + URI
        result = self.auth_manager.signup(username, email, password)

        if result:
            secret = result["secret"]
            uri = result["uri"]

            qr_dialog = QRCodeDialog(uri)
            qr_dialog.exec()

            self.signup_btn.setDisabled(True)
            self.signup_btn.setText("Check your Email to verify your account ✅")


