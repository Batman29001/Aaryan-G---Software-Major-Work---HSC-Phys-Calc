import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import PhysicsCalculator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = PhysicsCalculator()
    calculator.show()
    sys.exit(app.exec())