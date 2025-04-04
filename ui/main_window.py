from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .kinematics_tab import KinematicsTab

class PhysicsCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Physics Calculator")
        self.setGeometry(100, 100, 800, 600)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.kinematics_tab = KinematicsTab()
        self.tabs.addTab(self.kinematics_tab, "Kinematics")
        
        # Add more tabs here as needed
        self.setCentralWidget(self.tabs)