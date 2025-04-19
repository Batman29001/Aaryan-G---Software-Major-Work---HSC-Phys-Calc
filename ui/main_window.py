from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.kinematics_tab import KinematicsTab
from ui.dynamics_tab import DynamicsTab
from ui.waves_tab import WavesTab  # Add this import

class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HSC Physics Calculator")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Calculator buttons
        self.kinematics_btn = QPushButton("Kinematics Calculator")
        self.dynamics_btn = QPushButton("Dynamics Calculator")
        self.waves_btn = QPushButton("Waves Calculator")  
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #3A7CA5;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                margin: 10px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2F6690;
            }
        """
        self.kinematics_btn.setStyleSheet(button_style)
        self.dynamics_btn.setStyleSheet(button_style)
        self.waves_btn.setStyleSheet(button_style)  
        
        layout.addWidget(self.kinematics_btn)
        layout.addWidget(self.dynamics_btn)
        layout.addWidget(self.waves_btn)  
        layout.addStretch()
        
        self.setLayout(layout)

class PhysicsCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HSC Physics Calculator")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Create main menu
        self.main_menu = MainMenu()
        
        # Create calculator tabs
        self.kinematics_tab = KinematicsTab()
        self.dynamics_tab = DynamicsTab()
        self.waves_tab = WavesTab()  
        
        # Add all widgets to stacked widget
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.kinematics_tab)
        self.stacked_widget.addWidget(self.dynamics_tab)
        self.stacked_widget.addWidget(self.waves_tab) 
        
        # Connect menu buttons to switch views
        self.main_menu.kinematics_btn.clicked.connect(lambda: self.switch_to_calculator(1))
        self.main_menu.dynamics_btn.clicked.connect(lambda: self.switch_to_calculator(2))
        self.main_menu.waves_btn.clicked.connect(lambda: self.switch_to_calculator(3))  
        
        # Set central widget
        self.setCentralWidget(self.stacked_widget)
        
        # Show main menu by default
        self.stacked_widget.setCurrentIndex(0)
    
    def switch_to_calculator(self, index):
        self.stacked_widget.setCurrentIndex(index)
    
    def return_to_menu(self):
        self.stacked_widget.setCurrentIndex(0)