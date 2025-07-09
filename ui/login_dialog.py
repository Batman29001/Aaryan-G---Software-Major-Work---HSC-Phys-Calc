from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

class LoginDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("Login")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.email_input = QLineEdit(placeholderText="Email")
        self.password_input = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton("Login")
        self.signup_btn = QPushButton("Create Account")
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        
        self.login_btn.clicked.connect(self.handle_login)
        self.signup_btn.clicked.connect(self.handle_signup)
        
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        user = self.auth_manager.login(email, password)
        if user:
            self.user_id, self.username = user  # Store for later
            self.accept()  # Close dialog on success
        else:
            self.error_label.setText("Invalid email or password.")

    def handle_signup(self):
        from ui.signup_dialog import SignupDialog  # Avoid circular import
        signup_dialog = SignupDialog(self.auth_manager)
        if signup_dialog.exec():
            self.email_input.setText(signup_dialog.email_input.text())