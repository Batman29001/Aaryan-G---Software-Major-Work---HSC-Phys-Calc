from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QScrollArea)
from PyQt6.QtCore import Qt
from core.ai_solver import AISolver

class AIAssistantTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.solver = AISolver()  
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
    
        # Input
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("""Example problems:
            1. "Find range of projectile at 20 m/s, 30°"
            2. "3kg mass in 2m radius circle at 4m/s. Find force"
            3. "5μC charge in 200N/C field. Find force\"""")
    
    # Button with loading state
        self.solve_btn = QPushButton("🔍 Solve with AI")
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
    
    # Result display
        self.result_label = QLabel()
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
    
        layout.addWidget(self.input_box)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.result_label)
        self.setLayout(layout)