from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.qr_code_dialog import QRCodeDialog
from ui.particle_background import ParticleBackground

class UserSettingsTab(QWidget):
    def __init__(self, auth_manager, return_callback):
        super().__init__()
        self.auth_manager = auth_manager
        self.return_callback = return_callback
        self.user_id, self.username = self.auth_manager.current_user

        self.setStyleSheet("background: transparent;")
        self.background = ParticleBackground(self)
        self.background.resize(self.size())
        self.init_ui()
        self.load_user_data()

    def resizeEvent(self, event):
        self.background.resize(self.size())
        super().resizeEvent(event)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(60, 40, 60, 40)
        self.layout.setSpacing(20)

        self.title = QLabel("User Account Settings")
        self.title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #4FC3F7;")
        self.layout.addWidget(self.title)

        self.username_field = self._create_field("Username")
        self.email_field = self._create_field("Email")
        self.password_field = self._create_field("Password (hidden)", echo_mode=True)

        self.qr_btn = QPushButton("View 2FA QR Code")
        self.qr_btn.clicked.connect(self.show_qr_code)
        self._style_button(self.qr_btn)
        self.layout.addWidget(self.qr_btn)

        btn_row = QHBoxLayout()

        self.edit_btn = QPushButton("Edit Info")
        self.edit_btn.clicked.connect(self.attempt_edit)
        self._style_button(self.edit_btn)
        btn_row.addWidget(self.edit_btn)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.return_callback)
        self._style_button(self.back_btn)
        btn_row.addWidget(self.back_btn)

        self.layout.addLayout(btn_row)

    def _create_field(self, label_text, echo_mode=False):
        label = QLabel(label_text)
        label.setStyleSheet("color: #B0BEC5; font-weight: bold;")
        field = QLineEdit()
        field.setReadOnly(True)
        field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                background-color: #1E2A38;
                border: 1px solid #4FC3F7;
                border-radius: 6px;
                color: #CFD8DC;
            }
        """)
        if echo_mode:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(label)
        self.layout.addWidget(field)
        return field

    def _style_button(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38;
                color: #4FC3F7;
                border: 1px solid #4FC3F7;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #263646;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

    def load_user_data(self):
        user_data = self.auth_manager.get_user_details(self.user_id)
        if not user_data:
            return

        self.username_field.setText(user_data["username"])
        self.email_field.setText(user_data["email"])
        self.password_field.setText("********")  # Placeholder

        self.totp_uri = user_data["totp_uri"]

    def show_qr_code(self):
        dlg = QRCodeDialog(self.totp_uri)
        dlg.exec()

    def attempt_edit(self):
        password, ok = QInputDialog.getText(self, "Confirm Identity", "Enter current password:", QLineEdit.EchoMode.Password)
        if not ok or not password:
            return

        if not self.auth_manager.verify_password(self.user_id, password):
            QMessageBox.critical(self, "Error", "Incorrect password.")
            return

        # Enable editing
        self.username_field.setReadOnly(False)
        self.email_field.setReadOnly(False)
        self.password_field.setReadOnly(False)

        self.edit_btn.setText("Save Changes")
        self.edit_btn.clicked.disconnect()
        self.edit_btn.clicked.connect(self.save_changes)

    def save_changes(self):
        new_username = self.username_field.text().strip()
        new_email = self.email_field.text().strip()
        new_password = self.password_field.text().strip()

        if not new_username or not new_email:
            QMessageBox.warning(self, "Invalid Input", "Username and Email cannot be empty.")
            return

        success = self.auth_manager.update_user_details(
            self.user_id,
            username=new_username,
            email=new_email,
            password=new_password if new_password != "********" else None
        )

        if success:
            QMessageBox.information(self, "Updated", "User info updated.")
            self.edit_btn.setText("Edit Info")
            self.username_field.setReadOnly(True)
            self.email_field.setReadOnly(True)
            self.password_field.setReadOnly(True)
            self.edit_btn.clicked.disconnect()
            self.edit_btn.clicked.connect(self.attempt_edit)
        else:
            QMessageBox.critical(self, "Error", "Update failed.")
