from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QScrollArea, QHBoxLayout)
from PyQt6.QtCore import Qt
from core.ai_solver import AISolver

class AIAssistantTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.solver = AISolver()  
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
    
        # Create return button at the top
        return_btn = QPushButton("← Return to Main Menu")
        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        return_btn.clicked.connect(self.return_to_menu)
        layout.addWidget(return_btn)
    
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
        self.solve_btn.clicked.connect(self.solve_problem)
    
        # Result display
        self.result_label = QLabel()
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.result_label.setWordWrap(True)
    
        layout.addWidget(self.input_box)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def solve_problem(self):
        problem_text = self.input_box.toPlainText().strip()
        if not problem_text:
            self.result_label.setText("Please enter a physics problem")
            return
            
        self.solve_btn.setEnabled(False)
        self.solve_btn.setText("Solving...")
        
        try:
            result = self.solver.solve(problem_text)
            if "error" in result:
                self.result_label.setText(f"Error: {result['error']}")
            else:
                response = f"Topic: {result['topic']}\n"
                response += f"Inputs: {result['inputs']}\n"
                response += f"Result: {result.get('result', 'No result found')}"
                self.result_label.setText(response)
        except Exception as e:
            self.result_label.setText(f"An error occurred: {str(e)}")
        finally:
            self.solve_btn.setEnabled(True)
            self.solve_btn.setText("🔍 Solve with AI")

    def return_to_menu(self):
        self.parent().parent().return_to_menu()