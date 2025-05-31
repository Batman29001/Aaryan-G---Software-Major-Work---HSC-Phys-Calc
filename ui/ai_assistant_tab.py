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
        self.input_box.setPlaceholderText("e.g., 'A 2kg mass moves at 5 m/s in a 3m circle. Find centripetal force.'")
        
        # Button
        self.solve_btn = QPushButton("Solve with AI")
        self.solve_btn.clicked.connect(self.solve_problem)
        
        # Output
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        
        layout.addWidget(self.input_box)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def solve_problem(self):
        problem = self.input_box.toPlainText().strip()
        if not problem:
            self.result_label.setText("⚠️ Please enter a physics problem")
            return

        try:
            solution = self.solver.solve(problem)
            if "error" in solution:
                self.result_label.setText(f"⚠️ {solution['error']}")
            else:
                self.result_label.setText(
                    f"🔍 Topic: {solution['topic'].upper()}\n"
                    f"📥 Inputs: {solution['inputs']}\n"
                    f"🎯 Target: {solution.get('target', 'Unknown')}\n"
                    f"📤 Result: {solution['result']}"
                )
        except Exception as e:
            self.result_label.setText(f"⚠️ Error: {str(e)}")