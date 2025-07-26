import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication
from ui.main_window import PhysicsCalculator
from core.auth import AuthManager
from ui.login_dialog import LoginDialog
from PyQt6.QtWidgets import QDialog
from dotenv import load_dotenv
import subprocess


load_dotenv()

subprocess.Popen([sys.executable, "verify_server.py"])


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Catch all unhandled exceptions"""
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

sys.excepthook = handle_exception


def main():
    try:
        logging.info("STARTING DEBUG SESSION")
        
        logging.info("Creating QApplication")
        app = QApplication(sys.argv)
        
        logging.info("Creating AuthManager")
        auth = AuthManager()
        
        logging.info("Creating LoginDialog")
        login_dialog = LoginDialog(auth)
        logging.info(f"LoginDialog object: {hex(id(login_dialog))}")
        
        print("Starting login dialog")
        result = login_dialog.exec()
        print(f"Login dialog result: {result}")
        
        if result == QDialog.DialogCode.Accepted: 
            email = login_dialog.email_input.text()
            password = login_dialog.password_input.text()
            
            # Actually verify credentials
            user = auth.login(email, password)  # This sets auth.current_user
            
            if user:  # Only proceed if login succeeded
                logging.info(f"User {user['username']} logged in (ID: {user['id']})")
                calculator = PhysicsCalculator(auth)
                calculator.show()
                sys.exit(app.exec())
            else:
                logging.warning("Invalid credentials")
                sys.exit(1)
            
    except Exception as e:
        logging.critical(f"CRASH: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 