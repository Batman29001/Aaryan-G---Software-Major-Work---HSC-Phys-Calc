from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import re

from ui.main_window import ParticleBackground

class SignupDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("Create Account")
        self.setFixedSize(400, 420)
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

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.error_label)

        main_layout.addWidget(container)

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

        # 2FA: Sign up and get TOTP secret
        secret = self.auth_manager.signup(username, email, password)
        if secret:
            self.display_2fa_qr(secret)
            self.accept()
        else:
            self.error_label.setText("Email or username already exists.")

    def display_2fa_qr(self, secret):
        import pyotp, qrcode
        from io import BytesIO
        from PyQt6.QtGui import QPixmap

        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=self.email_input.text(),
            issuer_name="Phys Calc"
        )
        qr = qrcode.make(totp_uri)
        buf = BytesIO()
        qr.save(buf, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())

        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(qr_label)

