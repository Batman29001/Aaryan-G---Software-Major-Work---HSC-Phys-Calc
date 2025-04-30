from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.electricity_magnetism import solve_electrostatics, solve_circuits, solve_magnetism
from PyQt6.QtGui import QFont, QColor
from matplotlib.patches import Circle, Arrow, FancyArrowPatch
import math

class BaseEMTab(QWidget):
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
    
    def plot(self):
        """To be implemented by subclasses"""
        pass

class ElectrostaticsTab(BaseEMTab):
    def __init__(self, parent=None):
        super().__init__("Electrostatics Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'q': ["C", "μC", "nC"],
            'E': ["N/C", "V/m"],
            'F': ["N"],
            'V': ["V"],
            'd': ["m", "cm"]
        }
        
        symbols = {
            'q': "q (Charge)",
            'E': "E (Electric field)",
            'F': "F (Force)",
            'V': "V (Potential difference)",
            'd': "d (Distance between plates)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['q', 'E', 'F', 'V', 'd']:
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
            # Calculate missing values
            if values['F'] is None and values['q'] is not None and values['E'] is not None:
                values['F'] = values['q'] * values['E']
            
            if values['E'] is None and values['V'] is not None and values['d'] is not None:
                values['E'] = values['V'] / values['d']
                if values['q'] is not None and values['F'] is None:
                    values['F'] = values['q'] * values['E']
            
            if values['V'] is None and values['E'] is not None and values['d'] is not None:
                values['V'] = values['E'] * values['d']
            
            self.last_result = values
            
            # Simple, clean results display
            result_text = "📊 Results:\n"
            for var in ['q', 'E', 'F', 'V', 'd']:
                if values[var] is not None:
                    result_text += f"• {var}: {values[var]:.3e}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['q', 'E']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need charge and electric field to plot.")
            return
        
        q = result['q']
        E = result['E']
        F = result.get('F', q * E)  # Use calculated F if available, else calculate
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Create coordinate system
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        X, Y = np.meshgrid(x, y)
        
        # Uniform electric field in x-direction
        Ex = np.ones_like(X) * E
        Ey = np.zeros_like(Y)
        
        # Plot the electric field
        self.ax.quiver(X, Y, Ex, Ey, color='purple', scale=20, width=0.002, label=f'Electric Field: {E:.1e} N/C')
        
        # Plot the charge at origin
        color = 'red' if q > 0 else 'blue'
        marker = '+' if q > 0 else '_'
        self.ax.plot(0, 0, marker=marker, color=color, markersize=15, 
                     markeredgewidth=2, label=f'Charge: {q:.1e} C')
        
        # Draw force vector
        if F != 0:
            force_scale = 0.5  # Scale factor for better visualization
            self.ax.arrow(0, 0, F*force_scale, 0, head_width=0.3, head_length=0.5, 
                         fc='green', ec='green', label=f'Force: {F:.1e} N')
        
        # Add labels and title
        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-6, 6)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Force on Charge in Electric Field')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class CircuitsTab(BaseEMTab):
    def __init__(self, parent=None):
        super().__init__("Electric Circuits Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'I': ["A", "mA"],
            'V_circuit': ["V"],
            'R': ["Ω", "kΩ"],
            'P': ["W", "mW"],
            'E_energy': ["J", "kWh"],
            't': ["s", "h"],
            'R_series': ["Ω", "kΩ"],
            'R_parallel': ["Ω", "kΩ"],
            'R1': ["Ω", "kΩ"],
            'R2': ["Ω", "kΩ"]
        }
        
        symbols = {
            'I': "I (Current)",
            'V_circuit': "V (Voltage)",
            'R': "R (Resistance)",
            'P': "P (Power)",
            'E_energy': "E (Energy)",
            't': "t (Time)",
            'R_series': "R_series (Series resistance)",
            'R_parallel': "R_parallel (Parallel resistance)",
            'R1': "R₁ (Resistor 1)",
            'R2': "R₂ (Resistor 2)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['I', 'V_circuit', 'R', 'P', 'E_energy', 't', 'R_series', 'R_parallel', 'R1', 'R2']:
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
            result = solve_circuits(**values)
            self.last_result = result
            
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred:\n{str(e)}")
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['V_circuit', 'R']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need voltage and resistance to plot circuit.")
            return
        
        V, R = result['V_circuit'], result['R']
        I = V / R if R != 0 else 0
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Draw circuit elements
        resistor_x = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        resistor_y = np.array([0, 0.05, -0.05, 0.05, -0.05, 0.05, 0])
        
        # Wires
        self.ax.plot([0, 0.2], [0, 0], 'k-', linewidth=2)  # Left wire
        self.ax.plot([0.8, 1], [0, 0], 'k-', linewidth=2)  # Right wire
        
        # Battery
        self.ax.plot([0, 0], [-0.1, 0.1], 'k-', linewidth=2)  # Vertical line
        self.ax.plot([0, -0.05], [0.1, 0.1], 'k-', linewidth=2)  # Top terminal
        self.ax.plot([0, -0.05], [-0.1, -0.1], 'k-', linewidth=2)  # Bottom terminal
        
        # Resistor
        self.ax.plot(resistor_x, resistor_y, 'r-', linewidth=2)
        self.ax.text(0.5, -0.15, f"{R:.1f} Ω", ha='center')
        
        # Current arrow
        self.ax.arrow(0.5, 0.2, 0.2, 0, head_width=0.05, head_length=0.05, fc='b', ec='b')
        self.ax.text(0.6, 0.25, f"I = {I:.2f} A", ha='center', color='b')
        
        # Voltage label
        self.ax.text(-0.1, 0, f"{V:.1f} V", va='center', ha='right')
        
        # Add labels
        self.ax.set_xlim(-0.2, 1.1)
        self.ax.set_ylim(-0.3, 0.3)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title('Circuit Visualization')
        
        self.canvas.draw()

class MagnetismTab(BaseEMTab):
    def __init__(self, parent=None):
        super().__init__("Magnetism Calculator", parent)
        self.permeability = 4 * math.pi * 1e-7  # μ₀ in N/A²
        self.setup_connections()
    
    def setup_connections(self):
        """Safe connection of signals"""
        try:
            self.calculate_btn.clicked.connect(self.safe_calculate)
            self.plot_btn.clicked.connect(self.safe_plot)
            self.inputs['r_wire'].textChanged.connect(self.enforce_straight_wire_rules)
            self.inputs['N'].textChanged.connect(self.enforce_solenoid_rules)
        except Exception as e:
            print(f"Connection error: {e}")

    def enforce_straight_wire_rules(self):
        """When r_wire is entered, disable N"""
        has_r = bool(self.inputs['r_wire'].text().strip())
        self.inputs['N'].setDisabled(has_r)
        if has_r:
            self.inputs['N'].clear()

    def enforce_solenoid_rules(self):
        """When N is entered, disable r_wire but keep L enabled"""
        has_N = bool(self.inputs['N'].text().strip())
        self.inputs['r_wire'].setDisabled(has_N)
        if has_N:
            self.inputs['r_wire'].clear()
        self.inputs['L'].setEnabled(True)  # Always enable L

    def create_input_fields(self, layout):
        units = {
            'I_wire': ["A", "mA"],
            'r_wire': ["m", "cm"],  # Only for straight wire
            'N': ["turns"],         # Only for solenoid
            'L': ["m", "cm"],       # For both cases
            'B': ["T", "mT"]
        }
        
        symbols = {
            'I_wire': "I (Current)",
            'r_wire': "r (Distance from wire) - straight wire only",
            'N': "N (Number of turns) - solenoid only",
            'L': "L (Length) - required for both",
            'B': "B (Magnetic field)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['I_wire', 'r_wire', 'N', 'L', 'B']:
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
        
        # Input validation
        if not values['I_wire']:
            raise ValueError("Current (I) is required")
            
        # Straight wire case
        if values['r_wire']:
            if not values['r_wire'] > 0:
                raise ValueError("Distance from wire must be positive")
            result = self.calculate_straight_wire(values)
        
        # Solenoid case
        elif values['N']:
            if not values['L']:
                raise ValueError("Length (L) is required for solenoids")
            if not (values['N'] > 0 and values['L'] > 0):
                raise ValueError("Turns and length must be positive")
            result = self.calculate_solenoid(values)
        
        else:
            raise ValueError("Either r_wire or N must be specified")
        
        self.last_result = result
        self.display_results(result)

    def calculate_straight_wire(self, values):
        """Straight wire calculation with safety checks"""
        try:
            B = (self.permeability * values['I_wire']) / \
                (2 * math.pi * values['r_wire'])
            return {
                'B': B,
                'I_wire': values['I_wire'],
                'r_wire': values['r_wire'],
                'L': values.get('L')  # Include L if provided
            }
        except ZeroDivisionError:
            raise ValueError("Distance from wire cannot be zero")

    def calculate_solenoid(self, values):
        """Solenoid calculation with safety checks"""
        try:
            B = (self.permeability * values['N'] * values['I_wire']) / values['L']
            return {
                'B': B,
                'I_wire': values['I_wire'],
                'N': values['N'],
                'L': values['L']
            }
        except ZeroDivisionError:
            raise ValueError("Solenoid length cannot be zero")

    def plot(self):
        if not self.last_result:
            self.show_error("No results to plot. Calculate first.")
            return
        
        try:
            self.ax.clear()
            
            if 'r_wire' in self.last_result:
                self.plot_straight_wire()
            elif 'N' in self.last_result:
                self.plot_solenoid()
            
            self.canvas.draw()
        except Exception as e:
            self.show_error(f"Plotting error: {str(e)}")
            self.ax.clear()
            self.canvas.draw()

    def plot_straight_wire(self):
        """Plot straight wire with field lines"""
        I = self.last_result['I_wire']
        r = self.last_result['r_wire']
        L = self.last_result.get('L', 1.0)  # Default length
        
        # Draw wire
        self.ax.plot([0, 0], [-L/2, L/2], 'k-', linewidth=3, label='Wire')
        
        # Draw field lines
        for y in np.linspace(-L/2, L/2, 5):
            circle = plt.Circle((0, y), r, color='b', fill=False, alpha=0.3)
            self.ax.add_artist(circle)
        
        # Add current direction indicator
        self.ax.arrow(0, -L/2-0.5, 0, 0.3, head_width=0.2, fc='r', ec='r')
        self.ax.text(0.2, -L/2-0.4, f"I = {I:.1f} A", color='r')
        
        # Format plot
        self.ax.set_xlim(-2*r, 2*r)
        self.ax.set_ylim(-L-1, L+1)
        self.ax.set_aspect('equal')
        self.ax.set_title(f"Straight Wire (L={L:.2f}m)")
        self.ax.legend()
        self.ax.grid(True)

    def plot_solenoid(self):
        """Plot solenoid with uniform field"""
        I = self.last_result['I_wire']
        N = self.last_result['N']
        L = self.last_result['L']
        
        # Draw coils
        for i, y in enumerate(np.linspace(-L/2, L/2, min(N, 20))):  # Limit to 20 coils for visibility
            self.ax.add_artist(plt.Circle((0, y), 0.3, fill=False, color='r'))
        
        # Draw uniform field
        self.ax.arrow(0, -L/2, 0, L, head_width=0.3, fc='b', ec='b', 
                     label=f'B = {self.last_result["B"]:.1e} T')
        
        # Format plot
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-L-1, L+1)
        self.ax.set_aspect('equal')
        self.ax.set_title(f"Solenoid (N={N}, L={L:.2f}m)")
        self.ax.legend()
        self.ax.grid(True)

class ElectricityMagnetismTab(QWidget):
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
        self.electrostatics_tab = ElectrostaticsTab()
        self.circuits_tab = CircuitsTab()
        self.magnetism_tab = MagnetismTab()
        
        self.tabs.addTab(self.electrostatics_tab, "Electrostatics")
        self.tabs.addTab(self.circuits_tab, "Electric Circuits")
        self.tabs.addTab(self.magnetism_tab, "Magnetism")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu()