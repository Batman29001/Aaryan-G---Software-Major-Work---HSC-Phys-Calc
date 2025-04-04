from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import numpy as np
from core.kinematics import solve_kinematics

class KinematicsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.last_result = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Input Panel
        input_panel = QGroupBox("Kinematics Calculator")
        input_layout = QFormLayout()
        
        # Create input fields with units
        self.inputs = {}
        units = {
            'u': ["m/s", "km/h", "ft/s"],
            'v': ["m/s", "km/h", "ft/s"],
            'a': ["m/s²", "ft/s²"],
            's': ["m", "km", "ft"],
            't': ["s", "min", "h"]
        }
        
        for var, label in [('u',"Initial velocity"), ('v',"Final velocity"), 
                          ('a',"Acceleration"), ('s',"Displacement"), ('t',"Time")]:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            input_layout.addRow(f"{label}:", hbox)

        # Buttons
        self.calculate_btn = QPushButton("🚀 Calculate")
        self.clear_btn = QPushButton("🧹 Clear")
        self.plot_btn = QPushButton("📈 Plot Motion")
        self.theme_btn = QPushButton("🌙 Dark Mode")
        
        # Connect buttons
        self.calculate_btn.clicked.connect(self.calculate)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.plot_btn.clicked.connect(self.plot_motion)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Results display
        self.result_display = QLabel("Results will appear here...")
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.result_display.setWordWrap(True)
        self.formula_label = QLabel("Used formula: -")
        
        # Add widgets
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.plot_btn)
        button_layout.addWidget(self.theme_btn)
        
        input_layout.addRow(button_layout)
        input_layout.addRow(self.formula_label)
        input_layout.addRow(self.result_display)
        input_panel.setLayout(input_layout)
        
        # Plot area
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Final layout
        main_layout.addWidget(input_panel, 1)
        main_layout.addWidget(self.canvas, 1)
        self.setLayout(main_layout)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget { background-color: #333; color: #EEE; }
                QLineEdit, QComboBox { background-color: #555; color: #FFF; }
                QPushButton { background-color: #666; }
                QLabel { color: #EEE; }
            """)
            self.theme_btn.setText("☀️ Light Mode")
            self.ax.set_facecolor('#444')
            self.figure.set_facecolor('#333')
            for text in self.ax.texts + [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label]:
                text.set_color('white')
        else:
            self.setStyleSheet("")
            self.theme_btn.setText("🌙 Dark Mode")
            self.ax.set_facecolor('white')
            self.figure.set_facecolor('white')
            for text in self.ax.texts + [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label]:
                text.set_color('black')
        self.canvas.draw()
    
    def get_input_values(self):
        values = {}
        for var, field in self.inputs.items():
            text = field.text().strip()
            try:
                values[var] = float(text) if text else None
            except ValueError:
                values[var] = None
        return values
    
    def calculate(self):
        values = self.get_input_values()
        provided = sum(1 for v in values.values() if v is not None)
    
        if provided < 3:
            QMessageBox.warning(self, "Insufficient Data", 
                          "At least 3 variables are required!")
            return
    
        result = solve_kinematics(**values)
        self.last_result = result
    
        # Display results
        result_text = "📊 Results:\n"
        for var, val in result.items():
            if val is None:
                result_text += f"• {var}: ❓ (missing data)\n"
            else:
                try:
                    result_text += f"• {var}: {float(val):.3f}\n"
                except (TypeError, ValueError):
                    result_text += f"• {var}: {val}\n"
        
            self.result_display.setText(result_text)
            
            # Determine which formula was used
            formula_text = self.determine_used_formula(result, values)
            self.formula_label.setText(f"Used formula: {formula_text}")

    def determine_used_formula(self, result, original_inputs):
        """Simple heuristic to determine which formula was likely used"""
        # This is a simplified version - you can expand it based on your needs
        if result['v'] is not None and original_inputs.get('v') is None:
            if all(k in original_inputs for k in ['u', 'a', 't']):
                return "v = u + a·t"
        elif result['s'] is not None and original_inputs.get('s') is None:
            if all(k in original_inputs for k in ['u', 'v', 't']):
                return "s = ½(u + v)t"
        return "Multiple steps used"
    
    def clear_fields(self):
        for field in self.inputs.values():
            field.clear()
        self.result_display.setText("Results will appear here...")
        self.formula_label.setText("Used formula: -")
        self.ax.clear()
        self.canvas.draw()
    
    def plot_motion(self):
        if not hasattr(self, 'last_result') or not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting!")
            return
            
        result = self.last_result
        required = ['u', 'a', 't']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need u, a, and t to plot motion!")
            return
            
        u, a, t = result['u'], result['a'], result['t']
        
        # Handle case where time is zero or very small
        if t <= 0.001:  # Threshold for "zero" time
            QMessageBox.warning(self, "Invalid Time", "Time must be positive to plot motion!")
            return
        
        # Create time array with at least 10 points
        time_points = max(10, int(t * 10))  # Ensure enough points for plotting
        time = np.linspace(0, t, time_points)
        
        # Calculate position and velocity
        s = u * time + 0.5 * a * time**2
        v = u + a * time
        
        # Clear previous plot
        self.ax.clear()
        
        # Set dynamic axis limits with padding
        x_padding = t * 0.1  # 10% padding
        y_min = min(min(s), min(v)) - 1
        y_max = max(max(s), max(v)) + 1
        
        self.ax.set_xlim(0 - x_padding, t + x_padding)
        self.ax.set_ylim(y_min, y_max)
        
        # Plot curves
        self.ax.plot(time, s, 'b', label='Displacement (s)')
        self.ax.plot(time, v, 'r', label='Velocity (v)')
        
        # Add labels and legend
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Motion Graphs')
        self.ax.legend()
        self.ax.grid(True)
        
        # Apply dark mode if active
        if hasattr(self, 'dark_mode') and self.dark_mode:
            self.ax.set_facecolor('#444')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label]:
                text.set_color('white')
        
        self.canvas.draw()