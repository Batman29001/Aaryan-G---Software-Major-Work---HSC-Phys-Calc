from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.electromagnetism import (solve_lorentz_force, solve_force_on_wire,
                                  solve_parallel_wires, solve_emf_induction,
                                  solve_transformer, solve_motor_torque,
                                  PhysicsError, InputValidationError, InsufficientDataError)
from PyQt6.QtGui import QFont
from matplotlib.patches import Circle, Arrow, FancyArrowPatch
import math

class BaseElectromagnetismTab(QWidget):
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
        """To be implemented by subclasses"""
        pass
    
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

    def handle_calculation_error(self, e: Exception) -> str:
        """Convert core physics exceptions to user-friendly messages"""
        if isinstance(e, InputValidationError):
            return f"Invalid input: {str(e)}"
        elif isinstance(e, InsufficientDataError):
            return f"Missing required data: {str(e)}"
        elif "Division by zero" in str(e):
            return "Calculation error: Division by zero occurred (check your inputs)"
        elif "Maximum iterations reached" in str(e):
            return "Calculation didn't converge - check if inputs are physically possible"
        elif "invalid value" in str(e).lower():
            return "Invalid value encountered in calculations"
        elif "cannot be negative" in str(e).lower():
            return "Negative value provided where not allowed"
        elif "cannot be zero" in str(e).lower():
            return "Zero value provided where not allowed"
        else:
            return f"Calculation error: {str(e)}"
    
    def plot(self):
        """To be implemented by subclasses"""
        pass

class LorentzForceTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Lorentz Force", parent)
    
    def create_input_fields(self, layout):
        units = {
            'F': ["N"],
            'q': ["C", "e"],
            'E': ["N/C", "V/m"],
            'v': ["m/s"],
            'B': ["T"],
            'theta': ["°"]
        }
        
        symbols = {
            'F': "Force (F)",
            'q': "Charge (q)",
            'E': "Electric field (E)",
            'v': "Velocity (v)",
            'B': "Magnetic field (B)",
            'theta': "Angle (θ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['F', 'q', 'E', 'v', 'B', 'theta']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        # Convert units
        if values.get('q') is not None and self.unit_combos['q'].currentText() == "e":
            values['q'] = values['q'] * 1.602e-19  # Elementary charge
            
        try:
            result = solve_lorentz_force(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot electric field if available
        if result.get('E') is not None:
            x = np.linspace(-3, 3, 10)
            y = np.zeros_like(x)
            u = np.zeros_like(x)
            v = np.ones_like(x) * result['E']
            self.ax.quiver(x, y, u, v, scale=10, color='r', label='Electric Field')
        
        # Plot magnetic field if available
        if result.get('B') is not None:
            circle = plt.Circle((0, 0), 1, fill=False, color='b', label='Magnetic Field')
            self.ax.add_artist(circle)
        
        # Plot particle velocity if available
        if result.get('v') is not None:
            theta = math.radians(result.get('theta', 0))
            vx = result['v'] * math.cos(theta)
            vy = result['v'] * math.sin(theta)
            self.ax.arrow(0, 0, vx, vy, head_width=0.2, head_length=0.2, 
                         fc='g', ec='g', label='Velocity')
        
        # Plot force if available
        if result.get('F') is not None:
            self.ax.arrow(0, 0, 0, 1, head_width=0.2, head_length=0.2, 
                         fc='m', ec='m', label='Force')
        
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-4, 4)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Lorentz Force Visualization')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class ForceOnWireTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Force on Current-Carrying Wire", parent)
    
    def create_input_fields(self, layout):
        units = {
            'F': ["N"],
            'I': ["A"],
            'L': ["m"],
            'B': ["T"],
            'theta': ["°"]
        }
        
        symbols = {
            'F': "Force (F)",
            'I': "Current (I)",
            'L': "Length (L)",
            'B': "Magnetic field (B)",
            'theta': "Angle (θ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['F', 'I', 'L', 'B', 'theta']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        try:
            result = solve_force_on_wire(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Wire representation
        self.ax.plot([-3, 3], [0, 0], 'k-', linewidth=3, label='Wire')
        
        # Magnetic field
        if result.get('B') is not None:
            x, y = np.meshgrid(np.linspace(-3, 3, 5), np.linspace(-1, 1, 3))
            self.ax.quiver(x, y, np.zeros_like(x), np.ones_like(y)*0.5, 
                          scale=10, color='b', label='Magnetic Field')
        
        # Force direction
        if result.get('F') is not None:
            direction = 1 if result['F'] > 0 else -1
            self.ax.arrow(0, 0, 0, direction, head_width=0.2, head_length=0.2, 
                         fc='r', ec='r', label='Force')
        
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Force on Current-Carrying Wire')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class ParallelWiresTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Force Between Parallel Wires", parent)
    
    def create_input_fields(self, layout):
        units = {
            'F_per_length': ["N/m"],
            'I1': ["A"],
            'I2': ["A"],
            'r': ["m"]
        }
        
        symbols = {
            'F_per_length': "Force per length (F/l)",
            'I1': "Current 1 (I₁)",
            'I2': "Current 2 (I₂)",
            'r': "Separation (r)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['F_per_length', 'I1', 'I2', 'r']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        try:
            result = solve_parallel_wires(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Wire positions
        r = result.get('r', 1)
        self.ax.plot([-3, 3], [-r/2, -r/2], 'b-', linewidth=2, label='Wire 1')
        self.ax.plot([-3, 3], [r/2, r/2], 'r-', linewidth=2, label='Wire 2')
        
        # Current directions (assume same direction if force is attractive)
        if result.get('F_per_length') is not None:
            direction = 1 if result['F_per_length'] > 0 else -1
            self.ax.arrow(-2, -r/2, 0, -0.1*direction, head_width=0.1, head_length=0.1, fc='b', ec='b')
            self.ax.arrow(-2, r/2, 0, 0.1*direction, head_width=0.1, head_length=0.1, fc='r', ec='r')
        
        # Force direction
        if result.get('F_per_length') is not None:
            direction = 1 if result['F_per_length'] > 0 else -1
            self.ax.arrow(0, -r/2, 0, direction*0.3, head_width=0.2, head_length=0.1, 
                         fc='g', ec='g', label='Force')
            self.ax.arrow(0, r/2, 0, -direction*0.3, head_width=0.2, head_length=0.1, 
                         fc='g', ec='g')
        
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-max(2, r+0.5), max(2, r+0.5))
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Force Between Parallel Wires')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class EMFInductionTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("EMF Induction", parent)
    
    def create_input_fields(self, layout):
        units = {
            'emf': ["V"],
            'N': [""],
            'delta_phi': ["Wb"],
            'delta_t': ["s"],
            'B': ["T"],
            'A': ["m²"],
            'theta': ["°"],
            'phi': ["Wb"]
        }
        
        symbols = {
            'emf': "Induced EMF (ε)",
            'N': "Number of turns (N)",
            'delta_phi': "Change in flux (ΔΦ)",
            'delta_t': "Time change (Δt)",
            'B': "Magnetic field (B)",
            'A': "Area (A)",
            'theta': "Angle (θ)",
            'phi': "Magnetic flux (Φ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['emf', 'N', 'delta_phi', 'delta_t', 'B', 'A', 'theta', 'phi']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        try:
            result = solve_emf_induction(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Coil representation
        coil_x = np.linspace(-2, 2, 100)
        coil_y = 0.5 * np.sin(coil_x * np.pi)
        self.ax.plot(coil_x, coil_y, 'b-', linewidth=2, label='Coil')
        
        # Magnetic field if available
        if result.get('B') is not None:
            x, y = np.meshgrid(np.linspace(-2, 2, 5), np.linspace(-1, 1, 3))
            self.ax.quiver(x, y, np.zeros_like(x), np.ones_like(y)*0.5, 
                          scale=10, color='r', label='Magnetic Field')
        
        # Induced current direction if EMF available
        if result.get('emf') is not None:
            direction = -1 if result['emf'] > 0 else 1
            self.ax.arrow(0, 0.7, direction*0.5, 0, head_width=0.1, head_length=0.2, 
                         fc='g', ec='g', label='Induced Current')
        
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Electromagnetic Induction')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class TransformerTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Transformer Calculations", parent)
    
    def create_input_fields(self, layout):
        units = {
            'V_p': ["V"],
            'V_s': ["V"],
            'N_p': [""],
            'N_s': [""],
            'I_p': ["A"],
            'I_s': ["A"]
        }
        
        symbols = {
            'V_p': "Primary voltage (Vₚ)",
            'V_s': "Secondary voltage (Vₛ)",
            'N_p': "Primary turns (Nₚ)",
            'N_s': "Secondary turns (Nₛ)",
            'I_p': "Primary current (Iₚ)",
            'I_s': "Secondary current (Iₛ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        try:
            result = solve_transformer(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Primary coil
        self.ax.plot([-1, -1], [-1, 1], 'b-', linewidth=3, label='Primary')
        
        # Secondary coil
        self.ax.plot([1, 1], [-1, 1], 'r-', linewidth=3, label='Secondary')
        
        # Core
        self.ax.plot([-1, 1], [0, 0], 'k-', linewidth=1)
        
        # Labels
        if result.get('V_p') is not None:
            self.ax.text(-1.2, 1.2, f"{result['V_p']:.1f}V", color='b')
        if result.get('V_s') is not None:
            self.ax.text(0.8, 1.2, f"{result['V_s']:.1f}V", color='r')
        
        # Current directions if available
        if result.get('I_p') is not None and result.get('I_s') is not None:
            ip_dir = 1 if result['I_p'] > 0 else -1
            is_dir = 1 if result['I_s'] > 0 else -1
            self.ax.arrow(-1.2, 0.8, 0, -0.2*ip_dir, head_width=0.1, head_length=0.1, fc='b', ec='b')
            self.ax.arrow(1.2, 0.8, 0, -0.2*is_dir, head_width=0.1, head_length=0.1, fc='r', ec='r')
        
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position')
        self.ax.set_ylabel('Position')
        self.ax.set_title('Transformer Operation')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class MotorTorqueTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Motor Torque", parent)
    
    def create_input_fields(self, layout):
        units = {
            'torque': ["N·m"],
            'n': [""],
            'I': ["A"],
            'A': ["m²"],
            'B': ["T"],
            'theta': ["°"]
        }
        
        symbols = {
            'torque': "Torque (τ)",
            'n': "Number of loops (n)",
            'I': "Current (I)",
            'A': "Area (A)",
            'B': "Magnetic field (B)",
            'theta': "Angle (θ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['torque', 'n', 'I', 'A', 'B', 'theta']:
            self.inputs[var] = QLineEdit()
            unit_combo = QComboBox()
            unit_combo.addItems(units.get(var, [""]))
            hbox = QHBoxLayout()
            hbox.addWidget(self.inputs[var])
            hbox.addWidget(unit_combo)
            layout.addRow(symbols[var], hbox)
            self.unit_combos[var] = unit_combo
    
    def calculate(self):
        values = self.get_input_values()
        
        try:
            result = solve_motor_torque(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Stator magnets
        self.ax.add_artist(plt.Circle((0, 0), 2, fill=False, color='b', linestyle='--', label='Stator'))
        
        # Rotor coil
        angle = result.get('theta', 0)
        angle_rad = math.radians(angle)
        x1, y1 = 1.5 * math.cos(angle_rad), 1.5 * math.sin(angle_rad)
        x2, y2 = -1.5 * math.cos(angle_rad), -1.5 * math.sin(angle_rad)
        self.ax.plot([x1, x2], [y1, y2], 'r-', linewidth=3, label='Rotor')
        
        # Current direction
        self.ax.arrow(x1*0.8, y1*0.8, (x2-x1)*0.2, (y2-y1)*0.2, 
                     head_width=0.2, head_length=0.2, fc='k', ec='k', label='Current')
        
        # Torque direction if available
        if result.get('torque') is not None:
            torque_dir = 1 if result['torque'] > 0 else -1
            self.ax.arrow(0, 0, -y1*0.5*torque_dir, x1*0.5*torque_dir, 
                         head_width=0.2, head_length=0.2, fc='g', ec='g', label='Torque')
        
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('DC Motor Operation')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class ElectromagnetismTab(QWidget):
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
        self.lorentz_force_tab = LorentzForceTab()
        self.force_on_wire_tab = ForceOnWireTab()
        self.parallel_wires_tab = ParallelWiresTab()
        self.emf_induction_tab = EMFInductionTab()
        self.transformer_tab = TransformerTab()
        self.motor_torque_tab = MotorTorqueTab()
        
        self.tabs.addTab(self.lorentz_force_tab, "Lorentz Force")
        self.tabs.addTab(self.force_on_wire_tab, "Force on Wire")
        self.tabs.addTab(self.parallel_wires_tab, "Parallel Wires")
        self.tabs.addTab(self.emf_induction_tab, "EMF Induction")
        self.tabs.addTab(self.transformer_tab, "Transformer")
        self.tabs.addTab(self.motor_torque_tab, "Motor Torque")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu()