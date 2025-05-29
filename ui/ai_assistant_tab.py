import json  
import openai 
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QScrollArea)
from PyQt6.QtCore import Qt
from core.ai_solver import AISolver

class AIAssistantTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.solver = AISolver("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")  # Replace with your key
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Problem input
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Enter your physics problem...")
        
        # Solve button
        self.solve_btn = QPushButton("Solve with AI")
        self.solve_btn.clicked.connect(self.solve_problem)
        
        # Result display
        self.result_area = QScrollArea()
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.result_area.setWidget(self.result_label)
        
        layout.addWidget(self.input_box)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.result_area)
        self.setLayout(layout)

    def solve_problem(self):
        problem = self.input_box.toPlainText().strip()
        if not problem:
            self.result_label.setText("⚠️ Please enter a physics problem")
            return

        try:
            solution = self.solver.solve(problem)
            result_text = f"""
            🎯 Topic: {solution.get('topic', 'Unknown').upper()}
            📥 Inputs: {solution.get('inputs', {})}
            📤 Result: {solution.get('result', 'Unavailable')}
            """
            self.result_label.setText(result_text)
        except json.JSONDecodeError:
            self.result_label.setText("⚠️ AI returned invalid data. Try a clearer problem.")
        except openai.error.AuthenticationError:
            self.result_label.setText("⚠️ Invalid API key. Check your OpenAI key.")
        except Exception as e:
            self.result_label.setText(f"⚠️ Error: {str(e)}")