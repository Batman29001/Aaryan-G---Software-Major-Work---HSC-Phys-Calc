from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.main_window import ParticleBackground
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

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 40, 50, 0.92);
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 150))
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title = QLabel("Welcome to Phys Calc")
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

        layout.addWidget(title)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.error_label)

        main_layout.addWidget(container)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        if not email or not password:
            self.error_label.setText("Enter both email and password.")
            return

        user = self.auth_manager.login(email, password)
        if user:
            self.user_id, self.username = user
            self.accept()
        else:
            self.error_label.setText("Invalid email or password.")

    def handle_signup(self):
        signup_dialog = SignupDialog(self.auth_manager)
        if signup_dialog.exec():
            self.email_input.setText(signup_dialog.email_input.text())
