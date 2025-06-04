from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QScrollArea, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.ai_solver import AISolver

class AIWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, solver, problem_text):
        super().__init__()
        self.solver = solver
        self.problem_text = problem_text

    def run(self):
        try:
            result = self.solver.solve(self.problem_text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AIAssistantTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.solver = AISolver()  
        self.worker = None
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
        print(f"DEBUG: Button clicked. Text: '{problem_text}'") 
        # Check if problem text is empty
        if not problem_text:
            self.result_label.setText("Please enter a physics problem")
            return
            
        self.solve_btn.setEnabled(False)
        self.solve_btn.setText("Solving...")
        QApplication.processEvents()
        
        # Cancel any existing worker
        if self.worker and self.worker.isRunning():
            self.worker.terminate()

        print("DEBUG: Starting worker...")    
        self.worker = AIWorker(self.solver, problem_text)
        self.worker.finished.connect(self.on_solution_finished)
        self.worker.error.connect(self.on_solution_error)
        self.worker.start()
        print("DEBUG: Worker started")

    def on_solution_finished(self, result):
        print(f"DEBUG: Finished signal received. Result: {result}")
        if "error" in result:
            self.result_label.setText(f"Error: {result['error']}")
        else:
            response = f"<b>Topic:</b> {result['topic']}<br>"
            response += f"<b>Inputs:</b> {result['inputs']}<br>"
            response += f"<b>Result:</b> {result.get('result', 'No result found')}"
            self.result_label.setText(response)
            
        self.solve_btn.setEnabled(True)
        self.solve_btn.setText("🔍 Solve with AI")

    def on_solution_error(self, error):
        print(f"DEBUG: Error signal received: {error}")
        self.result_label.setText(f"An error occurred: {error}")
        self.solve_btn.setEnabled(True)
        self.solve_btn.setText("🔍 Solve with AI")

    def return_to_menu(self):
        self.parent().parent().return_to_menu()