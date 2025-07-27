from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QInputDialog
from ui.particle_background import ParticleBackground
from ui.signup_dialog import SignupDialog

class LoginDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("Login")
        self.setFixedSize(400, 380)
        self.setStyleSheet("background: transparent;")
        self.setup_ui()

    def setup_ui(self):
        self.background = ParticleBackground(self)
        self.background.resize(self.size())

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(16)

        title = QLabel("Welcome Back to Phys Calc!")
        title.setFont(QFont("Segoe UI", 14))
        title.setStyleSheet("color: #4FC3F7;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit(placeholderText="Email")
        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in [self.email_input, self.password_input]:
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

        self.login_btn = QPushButton("Log In")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
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
        self.login_btn.clicked.connect(self.handle_login)

        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signup_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #90A4AE;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
                color: #CFD8DC;
            }
        """)
        self.signup_btn.clicked.connect(self.handle_signup)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF9A9A; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.login_btn)
        main_layout.addWidget(self.signup_btn)
        main_layout.addWidget(self.error_label)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.error_label.setText("Enter both email and password.")
            return

        # Ask for 2FA code (always, for simplicity — or you could only ask after password passes)
        totp_code, ok = QInputDialog.getText(
            self,
            "Two-Factor Authentication",
            "Enter your 2FA code from Authenticator app:"
        )

        if not ok or not totp_code.strip():
            self.error_label.setText("2FA code required.")
            return

        # Call login with 2FA code
        user = self.auth_manager.login(email, password, totp_code.strip())

        if user:
            self.user_id, self.username = user["id"], user["username"]
            self.accept()
        else:
            self.error_label.setText("Invalid credentials or 2FA code.")

    def handle_signup(self):
        signup_dialog = SignupDialog(self.auth_manager)
        if signup_dialog.exec():
            self.email_input.setText(signup_dialog.email_input.text())
