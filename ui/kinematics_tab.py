from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import numpy as np
from core.kinematics import solve_kinematics
from PyQt6.QtGui import QFont, QColor
from matplotlib.patches import ArrowStyle

class KinematicsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False  # Start in light mode (for plot only)
        self.last_result = None
        self.inputs = {}
        self.unit_combos = {}
        self.initUI()

    def initUI(self):
        # Main layout - set directly on the widget
        main_layout = QVBoxLayout(self)
        
        # Create return button
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
        main_layout.addWidget(return_btn)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
        
        # Calculator layout
        calculator_layout = QHBoxLayout()
        
        # Input Panel - ALWAYS DARK
        input_panel = QGroupBox("Kinematics Calculator")
        input_layout = QFormLayout()
        
        # Create input fields with units
        units = {
            'u': ["m/s", "km/h", "ft/s"],
            'v': ["m/s", "km/h", "ft/s"],
            'a': ["m/s²", "ft/s²"],
            's': ["m", "km", "ft"],
            't': ["s", "min", "h"]
        }

        # Physics symbols for labels
        symbols = {
            'u': "v₀ (Initial velocity)",
            'v': "v (Final velocity)",
            'a': "a (Acceleration)",
            's': "Δx (Displacement)",
            't': "t (Time)"
        }

        for var in ['u', 'v', 'a', 's', 't']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            input_layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo

        # Buttons
        self.calculate_btn = QPushButton("🚀 Calculate")
        self.clear_btn = QPushButton("🔄 Reset")
        self.plot_btn = QPushButton("📊 Motion Graphs")
        self.theme_btn = QPushButton("🌙 Toggle Plot Theme")
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.plot_btn)
        button_layout.addWidget(self.theme_btn)
        
        # Results display
        self.result_display = QLabel("Results will appear here...")
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.result_display.setWordWrap(True)
        self.formula_label = QLabel("Used formula: -")
        
        # Add widgets to input layout
        input_layout.addRow(button_layout)
        input_layout.addRow(self.formula_label)
        input_layout.addRow(self.result_display)
        
        # Set layout for input panel
        input_panel.setLayout(input_layout)
        
        # Plot area - will toggle between light/dark
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Add to calculator layout
        calculator_layout.addWidget(input_panel, 1)
        calculator_layout.addWidget(self.canvas, 1)
        
        # Add calculator layout to main layout
        main_layout.addLayout(calculator_layout)
        
        # Apply styling and connect signals
        self.apply_style()
        self.connect_signals()
    
    def return_to_menu(self):
        """Return to the main menu"""
        self.parent().parent().return_to_menu()
    
    def apply_style(self):
        """Apply dark mode to input area and initialize plot theme"""
        # Permanent dark styling for input area
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
                color: #EEEEEE;
                font-family: Segoe UI, Arial;
            }
            QGroupBox {
                font: bold 14px;
                border: 2px solid #3A7CA5;
                border-radius: 5px;
                margin-top: 1ex;
                background-color: #333333;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #3A7CA5;
            }
            QPushButton {
                background-color: #3A7CA5;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2F6690;
            }
            QLineEdit, QComboBox {
                border: 1px solid #3A7CA5;
                padding: 5px;
                border-radius: 3px;
                background-color: #444444;
                color: white;
                selection-background-color: #3A7CA5;
            }
            QLabel {
                color: #EEEEEE;
                font-size: 13px;
            }
        """)
        
        # Initialize plot with light mode
        self.update_plot_theme()
    
    def update_plot_theme(self):
        """Only update the plot colors based on current theme"""
        if self.dark_mode:
            # Dark plot styling
            self.ax.set_facecolor('#2F2F2F')
            self.figure.set_facecolor('#2F2F2F')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#EEEEEE')
            self.ax.grid(color='#444444')
        else:
            # Light plot styling
            self.ax.set_facecolor('#F8F9FA')
            self.figure.set_facecolor('#F8F9FA')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#333333')
            self.ax.grid(color='#DDDDDD')
        
        self.canvas.draw()
    
    def connect_signals(self):
        """Connect all button signals"""
        self.calculate_btn.clicked.connect(self.calculate)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.plot_btn.clicked.connect(self.plot_motion)
        self.theme_btn.clicked.connect(self.toggle_theme)
    
    def toggle_theme(self):
        """Toggle only the plot theme"""
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀️ Light Plot" if self.dark_mode else "🌙 Dark Plot")
        self.update_plot_theme()
    
    def get_input_values(self):
        """Get values from input fields, return None if empty"""
        values = {}
        for var, field in self.inputs.items():
            text = field.text().strip()
            try:
                values[var] = float(text) if text else None
            except ValueError:
                values[var] = None
        return values
    
    def calculate(self):
        # Reset results to avoid stale data
        self.last_result = None
        self.result_display.setText("Calculating...")
        
        # Get inputs and solve
        values = self.get_input_values()
        try:
            result = solve_kinematics(**values)
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
            self.result_display.setText("❌ Calculation failed.")
            return
        self.last_result = result  # Store for plotting
        
        # Format results (handle lists for ± solutions)
        result_text = "📊 Results:\n"
        for var, val in result.items():
            if val is None:
                result_text += f"• {var}: (missing data)\n"
            elif isinstance(val, list):
                result_text += f"• {var}: {' or '.join(f'{x:.3f}' for x in val)}\n"
            else:
                result_text += f"• {var}: {val:.3f}\n"
        
        self.result_display.setText(result_text)
    
    def determine_used_formula(self, result, original_inputs):
        """Simple heuristic to determine which formula was likely used"""
        if result['v'] is not None and original_inputs.get('v') is None:
            if all(k in original_inputs for k in ['u', 'a', 't']):
                return "v = u + a·t"
        elif result['s'] is not None and original_inputs.get('s') is None:
            if all(k in original_inputs for k in ['u', 'v', 't']):
                return "s = ½(u + v)t"
        return "Multiple steps used"
    
    def clear_fields(self):
        """Clear all input fields and results"""
        for field in self.inputs.values():
            field.clear()
        self.result_display.setText("Results will appear here...")
        self.formula_label.setText("Used formula: -")
        self.last_result = None
        self.ax.clear()
        self.update_plot_theme()  # Reapply theme after clear
    
    def plot_motion(self):
        """Plot the motion based on available data"""
        if not self.last_result:
            QMessageBox.warning(self, "No Data", 
                               "Please calculate first before plotting.")
            return
            
        result = self.last_result
        required = ['u', 'a', 't']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", 
                               "Need u, a, and t to plot motion.")
            return
            
        u, a, t = result['u'], result['a'], result['t']
        
        # Handle case where time is zero or very small
        if t <= 0.001:
            QMessageBox.warning(self, "Invalid Time", 
                               "Time must be positive to plot motion.")
            return
        
        # Create time array
        time_points = max(10, int(t * 10))
        time = np.linspace(0, t, time_points)
        
        # Calculate position and velocity
        s = u * time + 0.5 * a * time**2
        v = u + a * time
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()  # Apply current theme
        
        # Plot with physics style
        line_s = self.ax.plot(time, s, color='#2E86AB', linewidth=2, 
                            label='Displacement (Δx)')
        line_v = self.ax.plot(time, v, color='#D62246', linewidth=2, 
                            label='Velocity (v)')
        
        # Add motion arrows
        if len(time) > 1:
            arrow_props = dict(
                arrowstyle=ArrowStyle.CurveFilledB(head_length=0.4, head_width=0.2),
                color='#2E86AB', linewidth=0
            )
            self.ax.annotate('', xy=(time[-1], s[-1]), 
                           xytext=(time[-2], s[-2]),
                           arrowprops=arrow_props)
            
            arrow_props['color'] = '#D62246'
            self.ax.annotate('', xy=(time[-1], v[-1]), 
                           xytext=(time[-2], v[-2]),
                           arrowprops=arrow_props)
        
        # Physics-style annotations
        self.ax.text(0.02, 0.95, f"a = {a:.2f} m/s²", transform=self.ax.transAxes,
                    bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                             alpha=0.8, 
                             edgecolor='none'))
        
        # Set dynamic axis limits
        x_padding = t * 0.1
        y_min = min(min(s), min(v)) - 1
        y_max = max(max(s), max(v)) + 1
        
        self.ax.set_xlim(0 - x_padding, t + x_padding)
        self.ax.set_ylim(y_min, y_max)
        
        # Add labels and legend
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Motion Graphs')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()