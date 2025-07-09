from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

class SignupDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setWindowTitle("Sign Up")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit(placeholderText="Username")
        self.email_input = QLineEdit(placeholderText="Email")
        self.password_input = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)
        self.signup_btn = QPushButton("Sign Up")
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        
        self.signup_btn.clicked.connect(self.handle_signup)
        
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

    def handle_signup(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not all([username, email, password]):
            self.error_label.setText("All fields are required!")
            return
        
        if self.auth_manager.signup(username, email, password):
            self.accept()  # Close on success
        else:
            self.error_label.setText("Username/email already exists.")