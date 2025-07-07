from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.electromagnetism import (solve_charged_particles, solve_motor_effect,
                                  solve_induction, solve_motor_applications)
from PyQt6.QtGui import QFont, QColor
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
        self.calculate_btn = QPushButton("⚡ Calculate")
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
    
    def plot(self):
        """To be implemented by subclasses"""
        pass

class ChargedParticlesTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Charged Particles & Fields", parent)
    
    def create_input_fields(self, layout):
        units = {
            'E': ["N/C", "V/m"],
            'V': ["V"],
            'd': ["m"],
            'q': ["C", "e"],
            'F': ["N"],
            'B': ["T"],
            'v': ["m/s"],
            'theta': ["°"],
            'r': ["m"],
            'm': ["kg"],
            'work': ["J"],
            'K': ["J"],
            'U': ["J"]
        }
        
        symbols = {
            'E': "Electric field (E)",
            'V': "Potential difference (V)",
            'd': "Distance (d)",
            'q': "Charge (q)",
            'F': "Force (F)",
            'B': "Magnetic field (B)",
            'v': "Velocity (v)",
            'theta': "Angle (θ)",
            'r': "Radius (r)",
            'm': "Mass (m)",
            'work': "Work (W)",
            'K': "Kinetic energy (K)",
            'U': "Potential energy (U)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['E', 'V', 'd', 'q', 'F', 'B', 'v', 'theta', 'r', 'm', 'work', 'K', 'U']:
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
            values['q'] = values['q'] * self.e_charge
            
        try:
            result = solve_charged_particles(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot electric field if available
        if result.get('E') is not None:
            x = np.linspace(-5, 5, 10)
            y = np.zeros_like(x)
            u = np.zeros_like(x)
            v = np.ones_like(x) * result['E']
            self.ax.quiver(x, y, u, v, scale=10, color='r', label='Electric Field')
        
        # Plot magnetic field if available
        if result.get('B') is not None:
            circle = plt.Circle((0, 0), 0.5, fill=False, color='b', label='Magnetic Field')
            self.ax.add_artist(circle)
        
        # Plot particle trajectory if available
        if result.get('r') is not None and result.get('v') is not None:
            theta = np.linspace(0, 2*np.pi, 100)
            x = result['r'] * np.cos(theta)
            y = result['r'] * np.sin(theta)
            self.ax.plot(x, y, 'g-', label='Particle Path')
        
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Charged Particle in Fields')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class MotorEffectTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Motor Effect", parent)
    
    def create_input_fields(self, layout):
        units = {
            'F': ["N"],
            'I': ["A"],
            'l': ["m"],
            'B': ["T"],
            'theta': ["°"],
            'F_per_length': ["N/m"],
            'I1': ["A"],
            'I2': ["A"],
            'r': ["m"]
        }
        
        symbols = {
            'F': "Force (F)",
            'I': "Current (I)",
            'l': "Length (l)",
            'B': "Magnetic field (B)",
            'theta': "Angle (θ)",
            'F_per_length': "Force per length",
            'I1': "Current 1 (I₁)",
            'I2': "Current 2 (I₂)",
            'r': "Separation (r)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['F', 'I', 'l', 'B', 'theta', 'F_per_length', 'I1', 'I2', 'r']:
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
            result = solve_motor_effect(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot current-carrying wire in magnetic field
        if result.get('I') is not None and result.get('B') is not None:
            # Wire
            self.ax.plot([-3, 3], [0, 0], 'k-', linewidth=3, label='Conductor')
            
            # Magnetic field
            x, y = np.meshgrid(np.linspace(-3, 3, 5), np.linspace(-1, 1, 3))
            self.ax.quiver(x, y, np.zeros_like(x), np.ones_like(y)*0.5, 
                          scale=10, color='b', label='Magnetic Field')
            
            # Force direction
            if result.get('F') is not None:
                self.ax.arrow(0, 0, 0, 1, head_width=0.2, head_length=0.2, 
                             fc='r', ec='r', label='Force')
        
        # Plot parallel wires if data available
        if result.get('I1') is not None and result.get('I2') is not None:
            self.ax.plot([-3, 3], [-0.5, -0.5], 'k-', linewidth=2, label='Wire 1')
            self.ax.plot([-3, 3], [0.5, 0.5], 'k-', linewidth=2, label='Wire 2')
            
            if result.get('F_per_length') is not None:
                # Show attractive/repulsive force
                direction = 1 if (result['I1'] * result['I2']) > 0 else -1
                self.ax.arrow(0, -0.5, 0, direction*0.3, head_width=0.2, head_length=0.1, 
                             fc='r', ec='r', label='Force')
                self.ax.arrow(0, 0.5, 0, -direction*0.3, head_width=0.2, head_length=0.1, 
                             fc='r', ec='r')
        
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position')
        self.ax.set_ylabel('Position')
        self.ax.set_title('Motor Effect Visualization')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class InductionTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Electromagnetic Induction", parent)
    
    def create_input_fields(self, layout):
        units = {
            'emf': ["V"],
            'N': [""],
            'delta_phi': ["Wb"],
            'delta_t': ["s"],
            'B': ["T"],
            'A': ["m²"],
            'theta': ["°"],
            'phi': ["Wb"],
            'V_p': ["V"],
            'V_s': ["V"],
            'N_p': [""],
            'N_s': [""],
            'I_p': ["A"],
            'I_s': ["A"]
        }
        
        symbols = {
            'emf': "Induced EMF (ε)",
            'N': "Number of turns (N)",
            'delta_phi': "Change in flux (ΔΦ)",
            'delta_t': "Time change (Δt)",
            'B': "Magnetic field (B)",
            'A': "Area (A)",
            'theta': "Angle (θ)",
            'phi': "Magnetic flux (Φ)",
            'V_p': "Primary voltage (Vₚ)",
            'V_s': "Secondary voltage (Vₛ)",
            'N_p': "Primary turns (Nₚ)",
            'N_s': "Secondary turns (Nₛ)",
            'I_p': "Primary current (Iₚ)",
            'I_s': "Secondary current (Iₛ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['emf', 'N', 'delta_phi', 'delta_t', 'B', 'A', 'theta', 'phi', 
                   'V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s']:
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
            result = solve_induction(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot changing magnetic flux if available
        if result.get('B') is not None and result.get('A') is not None:
            # Coil
            coil_x = np.linspace(-2, 2, 100)
            coil_y = 0.5 * np.sin(coil_x * np.pi)
            self.ax.plot(coil_x, coil_y, 'b-', linewidth=2, label='Coil')
            
            # Magnetic field lines
            x, y = np.meshgrid(np.linspace(-2, 2, 5), np.linspace(-1, 1, 3))
            self.ax.quiver(x, y, np.zeros_like(x), np.ones_like(y)*0.5, 
                          scale=10, color='r', label='Magnetic Field')
            
            # Induced current direction if EMF available
            if result.get('emf') is not None:
                direction = -1 if result['emf'] > 0 else 1
                self.ax.arrow(0, 0.7, direction*0.5, 0, head_width=0.1, head_length=0.2, 
                             fc='g', ec='g', label='Induced Current')
        
        # Plot transformer if data available
        if result.get('V_p') is not None and result.get('V_s') is not None:
            # Primary coil
            self.ax.plot([-1, -1], [-1, 1], 'b-', linewidth=3, label='Primary')
            
            # Secondary coil
            self.ax.plot([1, 1], [-1, 1], 'r-', linewidth=3, label='Secondary')
            
            # Core
            self.ax.plot([-1, 1], [0, 0], 'k-', linewidth=1)
            
            # Labels
            self.ax.text(-1.2, 1.2, f"{result['V_p']:.1f}V", color='b')
            self.ax.text(0.8, 1.2, f"{result['V_s']:.1f}V", color='r')
        
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position')
        self.ax.set_ylabel('Position')
        self.ax.set_title('Electromagnetic Induction')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class MotorApplicationsTab(BaseElectromagnetismTab):
    def __init__(self, parent=None):
        super().__init__("Motor Applications", parent)
    
    def create_input_fields(self, layout):
        units = {
            'torque': ["N·m"],
            'n': [""],
            'I': ["A"],
            'A': ["m²"],
            'B': ["T"],
            'theta': ["°"],
            'back_emf': ["V"],
            'omega': ["rad/s"],
            'N': [""],
            'phi': ["Wb"]
        }
        
        symbols = {
            'torque': "Torque (τ)",
            'n': "Number of loops (n)",
            'I': "Current (I)",
            'A': "Area (A)",
            'B': "Magnetic field (B)",
            'theta': "Angle (θ)",
            'back_emf': "Back EMF (ε)",
            'omega': "Angular velocity (ω)",
            'N': "Number of turns (N)",
            'phi': "Magnetic flux (Φ)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['torque', 'n', 'I', 'A', 'B', 'theta', 'back_emf', 'omega', 'N', 'phi']:
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
            result = solve_motor_applications(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        self.ax.clear()
        self.update_plot_theme()
        
        # Plot DC motor if torque available
        if result.get('torque') is not None:
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
            
            # Torque direction
            if result['torque'] > 0:
                self.ax.arrow(0, 0, -y1*0.5, x1*0.5, 
                             head_width=0.2, head_length=0.2, fc='g', ec='g', label='Torque')
        
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position')
        self.ax.set_ylabel('Position')
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
        self.charged_particles_tab = ChargedParticlesTab()
        self.motor_effect_tab = MotorEffectTab()
        self.induction_tab = InductionTab()
        self.motor_applications_tab = MotorApplicationsTab()
        
        self.tabs.addTab(self.charged_particles_tab, "Charged Particles")
        self.tabs.addTab(self.motor_effect_tab, "Motor Effect")
        self.tabs.addTab(self.induction_tab, "Electromagnetic Induction")
        self.tabs.addTab(self.motor_applications_tab, "Motor Applications")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu() 