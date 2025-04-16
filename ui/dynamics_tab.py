from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.dynamics import solve_dynamics
from PyQt6.QtGui import QFont, QColor
from matplotlib.patches import ArrowStyle
import math

class BasePhysicsTab(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.last_result = None
        self.title = title
        self.initUI()
    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Left panel for inputs
        input_panel = QGroupBox(self.title)
        input_layout = QFormLayout()
        
        # Create input fields
        self.create_input_fields(input_layout)
        
        # Buttons
        self.calculate_btn = QPushButton("🚀 Calculate")
        self.clear_btn = QPushButton("🔄 Reset")
        self.plot_btn = QPushButton("📊 Plot")
        self.theme_btn = QPushButton("🌙 Toggle Plot Theme")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.plot_btn)
        button_layout.addWidget(self.theme_btn)
        
        # Results display
        self.result_display = QLabel("Results will appear here...")
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.result_display.setWordWrap(True)
        
        input_layout.addRow(button_layout)
        input_layout.addRow(self.result_display)
        
        # Right panel for plot
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Add panels to main layout
        input_panel.setLayout(input_layout)
        main_layout.addWidget(input_panel, 1)
        main_layout.addWidget(self.canvas, 1)
        
        self.setLayout(main_layout)
        self.apply_style()
        self.connect_signals()
    
    def create_input_fields(self, layout):
        """To be implemented by subclasses"""
        pass
    
    def apply_style(self):
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
            QPushButton:disabled {
                background-color: #666666;
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
        self.update_plot_theme()
    
    def update_plot_theme(self):
        if self.dark_mode:
            self.ax.set_facecolor('#2F2F2F')
            self.figure.set_facecolor('#2F2F2F')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#EEEEEE')
            self.ax.grid(color='#444444')
        else:
            self.ax.set_facecolor('#F8F9FA')
            self.figure.set_facecolor('#F8F9FA')
            for text in [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] + self.ax.texts:
                text.set_color('#333333')
            self.ax.grid(color='#DDDDDD')
        self.canvas.draw()
    
    def connect_signals(self):
        self.calculate_btn.clicked.connect(self.calculate)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.plot_btn.clicked.connect(self.plot)
        self.theme_btn.clicked.connect(self.toggle_theme)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀️ Light Plot" if self.dark_mode else "🌙 Dark Plot")
        self.update_plot_theme()
    
    def calculate(self):
        values = self.get_input_values()
        try:
            result = solve_dynamics(**values)
            self.last_result = result
            
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def get_input_values(self):
        values = {}
        for var, field in self.inputs.items():
            text = field.text().strip()
            try:
                values[var] = float(text) if text else None
            except ValueError:
                values[var] = None
        return values
    
    def clear_fields(self):
        for field in self.inputs.values():
            field.clear()
        self.result_display.setText("Results will appear here...")
        self.last_result = None
        self.ax.clear()
        self.update_plot_theme()
        self.canvas.draw()
    
    def plot(self):
        """To be implemented by subclasses"""
        pass

class ForceMomentumTab(BasePhysicsTab):
    def __init__(self, parent=None):
        super().__init__("Force & Momentum Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'F': ["N", "kN", "lbf"],
            'm': ["kg", "g", "lb"],
            'a': ["m/s²", "ft/s²"],
            'p': ["kg·m/s", "N·s"],
            'v': ["m/s", "km/h", "ft/s"],
            't': ["s", "ms", "min"]
        }
        
        symbols = {
            'F': "F (Force)",
            'm': "m (Mass)",
            'a': "a (Acceleration)",
            'p': "p (Momentum)",
            'v': "v (Velocity)",
            't': "t (Time)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['F', 'm', 'a', 'p', 'v', 't']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['F', 'm', 'a']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need F, m, and a to plot motion.")
            return
        
        F, m, a = result['F'], result['m'], result['a']
        
        # Create time array
        t_max = 5
        if result.get('t') is not None:
            t_max = max(1, result['t'] * 1.5)
        
        time = np.linspace(0, t_max, 100)
        
        # Calculate motion
        v = a * time
        s = 0.5 * a * time**2
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot motion
        line_s = self.ax.plot(time, s, color='#2E86AB', linewidth=2, label='Displacement (m)')
        line_v = self.ax.plot(time, v, color='#D62246', linewidth=2, label='Velocity (m/s)')
        line_a = self.ax.plot(time, [a]*len(time), color='#4CB944', linewidth=2, 
                            label=f'Acceleration ({a:.2f} m/s²)')
        
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
        
        # Add annotations
        self.ax.text(0.02, 0.95, f"F = {F:.2f} N\nm = {m:.2f} kg", transform=self.ax.transAxes,
                    bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                             alpha=0.8, edgecolor='none'))
        
        # Set axis limits
        x_padding = t_max * 0.1
        y_min = min(min(s), min(v), 0) - 1
        y_max = max(max(s), max(v), a) + 1
        
        self.ax.set_xlim(0 - x_padding, t_max + x_padding)
        self.ax.set_ylim(y_min, y_max)
        
        # Add labels
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Motion Under Constant Force')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class FrictionTab(BasePhysicsTab):
    def __init__(self, parent=None):
        super().__init__("Friction Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'mu': ["unitless"],
            'FN': ["N", "kN", "lbf"],
            'Ffriction': ["N", "kN", "lbf"]
        }
        
        symbols = {
            'mu': "μ (Coeff. of Friction)",
            'FN': "Fₙ (Normal Force)",
            'Ffriction': "Ff (Friction Force)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['mu', 'FN', 'Ffriction']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['mu', 'FN']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need μ and Fₙ to plot friction.")
            return
        
        mu, FN = result['mu'], result['FN']
        
        # Create normal force range
        FN_range = np.linspace(0, FN * 1.5, 100)
        Ffriction = mu * FN_range
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot friction
        self.ax.plot(FN_range, Ffriction, color='#D62246', linewidth=2, 
                    label=f'Friction Force (μ = {mu:.2f})')
        
        # Add annotations
        self.ax.text(0.02, 0.95, f"Fₙ = {FN:.2f} N\nFf = {mu*FN:.2f} N", 
                    transform=self.ax.transAxes,
                    bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                             alpha=0.8, edgecolor='none'))
        
        # Set axis limits
        self.ax.set_xlim(0, FN * 1.5)
        self.ax.set_ylim(0, mu * FN * 1.5)
        
        # Add labels
        self.ax.set_xlabel('Normal Force (N)')
        self.ax.set_ylabel('Friction Force (N)')
        self.ax.set_title('Friction Force vs Normal Force')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class InclinedPlaneTab(BasePhysicsTab):
    def __init__(self, parent=None):
        super().__init__("Inclined Plane Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'm': ["kg", "g", "lb"],
            'theta': ["°", "rad"],
            'mu': ["unitless"],
            'Fparallel': ["N", "kN", "lbf"],
            'Fnormal': ["N", "kN", "lbf"]
        }
        
        symbols = {
            'm': "m (Mass)",
            'theta': "θ (Angle)",
            'mu': "μ (Coeff. of Friction)",
            'Fparallel': "F∥ (Parallel Force)",
            'Fnormal': "Fₙ (Normal Force)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['m', 'theta', 'mu', 'Fparallel', 'Fnormal']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['m', 'theta']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need m and θ to plot the inclined plane.")
            return
        
        m, theta = result['m'], result['theta']
        
        # Calculate components
        Fnormal = m * 9.81 * math.cos(math.radians(theta))
        Fparallel = m * 9.81 * math.sin(math.radians(theta))
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot components
        self.ax.plot([0, 90], [Fnormal, Fnormal], color='#2E86AB', linewidth=2, label='Normal Force')
        self.ax.plot([0, 90], [Fparallel, Fparallel], color='#D62246', linewidth=2, label='Parallel Force')
        
        # Add annotations
        self.ax.text(0.02, 0.95, f"Fₙ = {Fnormal:.2f} N\nF∥ = {Fparallel:.2f} N", 
                    transform=self.ax.transAxes,
                    bbox=dict(facecolor='white' if not self.dark_mode else '#444444',
                             alpha=0.8, edgecolor='none'))
        
        # Set axis limits
        self.ax.set_xlim(0, 90)
        self.ax.set_ylim(0, m * 9.81)
        
        # Add labels
        self.ax.set_xlabel('Angle (°)')
        self.ax.set_ylabel('Force (N)')
        self.ax.set_title('Force Components on an Inclined Plane')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class DynamicsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
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
        layout.addWidget(return_btn)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create and add sub-tabs
        self.force_momentum_tab = ForceMomentumTab()
        self.friction_tab = FrictionTab()
        self.inclined_plane_tab = InclinedPlaneTab()
        
        self.tabs.addTab(self.force_momentum_tab, "Force and Momentum")
        self.tabs.addTab(self.friction_tab, "Friction")
        self.tabs.addTab(self.inclined_plane_tab, "Inclined Plane")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu()