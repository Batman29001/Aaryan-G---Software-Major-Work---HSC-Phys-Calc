# ui/advanced_mechanics_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QGroupBox, QFormLayout,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from core.advanced_mechanics import (solve_projectile_motion, solve_circular_motion,
                                    solve_banked_tracks, solve_gravitation,
                                    InputValidationError, InsufficientDataError)
from PyQt6.QtGui import QFont, QColor
from matplotlib.patches import Circle, Arrow, FancyArrowPatch
import math

class BaseAdvancedMechanicsTab(QWidget):
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
        else:
            return f"Calculation error: {str(e)}"

class ProjectileMotionTab(BaseAdvancedMechanicsTab):
    def __init__(self, parent=None):
        super().__init__("Projectile Motion Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'u': ["m/s", "km/h"],
            'θ': ["°"],
            'ux': ["m/s"],
            'uy': ["m/s"],
            't_flight': ["s"],
            'max_height': ["m"],
            'range': ["m"]
        }
        
        symbols = {
            'u': "Initial velocity (u)",
            'θ': "Launch angle (θ)",
            'ux': "Horizontal velocity (uₓ)",
            'uy': "Vertical velocity (uᵧ)",
            't_flight': "Time of flight (t)",
            'max_height': "Max height (h)",
            'range': "Range (R)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['u', 'θ', 'ux', 'uy', 't_flight', 'max_height', 'range']:
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
        if values.get('u') is not None and self.unit_combos['u'].currentText() == "km/h":
            values['u'] = values['u'] * 1000 / 3600  # km/h to m/s
            
        try:
            result = solve_projectile_motion(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['u', 'θ']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need initial velocity and angle to plot trajectory.")
            return
        
        u = result['u']
        θ = math.radians(result['θ'])
        ux = u * math.cos(θ)
        uy = u * math.sin(θ)
        t_flight = result.get('t_flight', 2 * uy / 9.81)
        max_height = result.get('max_height', (uy ** 2) / (2 * 9.81))
        range_val = result.get('range', ux * t_flight)
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Calculate trajectory
        t = np.linspace(0, t_flight, 100)
        x = ux * t
        y = uy * t - 0.5 * 9.81 * t ** 2
        
        # Plot trajectory
        self.ax.plot(x, y, 'b-', label='Trajectory')
        
        # Mark important points
        self.ax.plot(0, 0, 'ro', label='Launch')
        self.ax.plot(range_val, 0, 'go', label='Landing')
        self.ax.plot(ux * t_flight/2, max_height, 'yo', label='Max height')
        
        # Add labels and title
        self.ax.set_xlim(0, range_val * 1.1)
        self.ax.set_ylim(0, max_height * 1.2)
        self.ax.set_xlabel('Horizontal distance (m)')
        self.ax.set_ylabel('Vertical distance (m)')
        self.ax.set_title('Projectile Motion')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class CircularMotionTab(BaseAdvancedMechanicsTab):
    def __init__(self, parent=None):
        super().__init__("Circular Motion Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'v': ["m/s", "km/h"],
            'r': ["m", "km"],
            'T': ["s", "min"],
            'f': ["Hz"],
            'ω': ["rad/s"],
            'a_c': ["m/s²"],
            'F_c': ["N"],
            'm': ["kg"]
        }
        
        symbols = {
            'v': "Linear velocity (v)",
            'r': "Radius (r)",
            'T': "Period (T)",
            'f': "Frequency (f)",
            'ω': "Angular velocity (ω)",
            'a_c': "Centripetal accel (a_c)",
            'F_c': "Centripetal force (F_c)",
            'm': "Mass (m)"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['v', 'r', 'T', 'f', 'ω', 'a_c', 'F_c', 'm']:
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
        if values.get('v') is not None and self.unit_combos['v'].currentText() == "km/h":
            values['v'] = values['v'] * 1000 / 3600  # km/h to m/s
        if values.get('r') is not None and self.unit_combos['r'].currentText() == "km":
            values['r'] = values['r'] * 1000  # km to m
        if values.get('T') is not None and self.unit_combos['T'].currentText() == "min":
            values['T'] = values['T'] * 60  # min to s
            
        try:
            result = solve_circular_motion(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['v', 'r']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need velocity and radius to plot circular motion.")
            return
        
        v = result['v']
        r = result['r']
        ω = result.get('ω', v / r)
        T = result.get('T', 2 * math.pi / ω if ω is not None else None)
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Draw circle
        circle = plt.Circle((0, 0), r, fill=False, color='b')
        self.ax.add_artist(circle)
        
        # Draw velocity vector
        self.ax.arrow(0, r, v, 0, head_width=0.1*r, head_length=0.1*r, fc='r', ec='r', label=f'Velocity: {v:.1f} m/s')
        
        # Draw centripetal force vector
        if result.get('F_c') is not None:
            self.ax.arrow(0, r, 0, -0.5, head_width=0.1*r, head_length=0.1*r, fc='g', ec='g', label=f'Centripetal force: {result["F_c"]:.1f} N')
        
        # Add labels
        self.ax.set_xlim(-1.2*r, 1.2*r)
        self.ax.set_ylim(-1.2*r, 1.2*r)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Uniform Circular Motion')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class BankedTracksTab(BaseAdvancedMechanicsTab):
    def __init__(self, parent=None):
        super().__init__("Banked Tracks Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'θ': ["°"],
            'v': ["m/s", "km/h"],
            'r': ["m"],
            'μ': [""],
            'v_min': ["m/s"],
            'v_max': ["m/s"]
        }
        
        symbols = {
            'θ': "Bank angle (θ)",
            'v': "Velocity (v)",
            'r': "Radius (r)",
            'μ': "Friction coeff (μ)",
            'v_min': "Min safe speed",
            'v_max': "Max safe speed"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['θ', 'v', 'r', 'μ', 'v_min', 'v_max']:
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
        if values.get('v') is not None and self.unit_combos['v'].currentText() == "km/h":
            values['v'] = values['v'] * 1000 / 3600  # km/h to m/s
            
        try:
            result = solve_banked_tracks(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    result_text += f"• {var}: {val:.3f} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)

    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['θ', 'r']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need bank angle and radius to plot banked track.")
            return
        
        θ = math.radians(result['θ'])
        r = result['r']
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Draw banked track
        x = np.linspace(-r, r, 100)
        y = np.tan(θ) * x
        
        self.ax.plot(x, y, 'b-', linewidth=3, label='Banked track')
        
        # Draw car
        car_x = 0
        car_y = 0
        car_width = 0.2 * r
        car_height = 0.1 * r
        
        # Draw forces if velocity is provided
        if result.get('v') is not None:
            v = result['v']
            # Normal force
            self.ax.arrow(car_x, car_y, 0, 0.5, head_width=0.1*r, head_length=0.1*r, fc='g', ec='g', label='Normal force')
            # Friction force
            self.ax.arrow(car_x, car_y, 0.3, 0, head_width=0.1*r, head_length=0.1*r, fc='r', ec='r', label='Friction force')
        
        # Add labels
        self.ax.set_xlim(-1.2*r, 1.2*r)
        self.ax.set_ylim(-0.5*r, 1.5*r)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title(f'Banked Track (θ={math.degrees(θ):.1f}°)')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class GravitationTab(BaseAdvancedMechanicsTab):
    def __init__(self, parent=None):
        super().__init__("Gravitation Calculator", parent)
    
    def create_input_fields(self, layout):
        units = {
            'M': ["kg", "M⊕"],
            'm': ["kg"],
            'r': ["m", "km"],
            'F_g': ["N"],
            'g': ["m/s²"],
            'v_orbital': ["m/s", "km/s"],
            'T': ["s", "h", "d"],
            'altitude': ["m", "km"]
        }
        
        symbols = {
            'M': "Primary mass (M)",
            'm': "Secondary mass (m)",
            'r': "Distance (r)",
            'F_g': "Grav force (F_g)",
            'g': "Grav field (g)",
            'v_orbital': "Orbital velocity",
            'T': "Orbital period",
            'altitude': "Altitude"
        }
        
        self.inputs = {}
        self.unit_combos = {}
        
        for var in ['M', 'm', 'r', 'F_g', 'g', 'v_orbital', 'T', 'altitude']:
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
        if values.get('M') is not None and self.unit_combos['M'].currentText() == "M⊕":
            values['M'] = values['M'] * 5.972e24  # Earth masses to kg
        if values.get('r') is not None and self.unit_combos['r'].currentText() == "km":
            values['r'] = values['r'] * 1000  # km to m
        if values.get('v_orbital') is not None and self.unit_combos['v_orbital'].currentText() == "km/s":
            values['v_orbital'] = values['v_orbital'] * 1000  # km/s to m/s
        if values.get('T') is not None:
            if self.unit_combos['T'].currentText() == "h":
                values['T'] = values['T'] * 3600  # hours to seconds
            elif self.unit_combos['T'].currentText() == "d":
                values['T'] = values['T'] * 86400  # days to seconds
        if values.get('altitude') is not None and self.unit_combos['altitude'].currentText() == "km":
            values['altitude'] = values['altitude'] * 1000  # km to m
            
        try:
            result = solve_gravitation(**values)
            self.last_result = result
            
            # Display results
            result_text = "📊 Results:\n"
            for var, val in result.items():
                if val is not None:
                    # Use scientific notation for very large/small numbers in gravitation
                    if abs(val) > 1e4 or abs(val) < 1e-4:
                        result_text += f"• {var}: {val:.3e} {self.unit_combos[var].currentText()}\n"
                    else:
                        result_text += f"• {var}: {val:.3f} {self.unit_combos[var].currentText()}\n"
            
            self.result_display.setText(result_text)
            
        except Exception as e:
            error_msg = self.handle_calculation_error(e)
            QMessageBox.critical(self, "Calculation Error", error_msg)
    
    def plot(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Data", "Please calculate first before plotting.")
            return
        
        result = self.last_result
        required = ['M', 'r']
        if any(result.get(k) is None for k in required):
            QMessageBox.warning(self, "Missing Data", "Need mass and distance to plot gravitational field.")
            return
        
        M = result['M']
        r = result['r']
        v_orbital = result.get('v_orbital', math.sqrt(6.67430e-11 * M / r))
        
        # Clear and style plot
        self.ax.clear()
        self.update_plot_theme()
        
        # Draw central mass
        central_size = min(0.1 * r, 0.5)  # Limit size for visibility
        self.ax.add_artist(plt.Circle((0, 0), central_size, color='r', label=f'Mass: {M:.1e} kg'))
        
        # Draw orbit
        orbit = plt.Circle((0, 0), r, fill=False, color='b', label=f'Orbit: {r:.1e} m')
        self.ax.add_artist(orbit)
        
        # Draw orbital velocity if available
        if v_orbital is not None:
            self.ax.arrow(0, r, v_orbital/1000, 0, head_width=0.05*r, head_length=0.05*r, 
                         fc='g', ec='g', label=f'Orbital velocity: {v_orbital:.1f} m/s')
        
        # Add labels
        self.ax.set_xlim(-1.2*r, 1.2*r)
        self.ax.set_ylim(-1.2*r, 1.2*r)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('Position (m)')
        self.ax.set_ylabel('Position (m)')
        self.ax.set_title('Gravitational Field and Orbit')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()

class AdvancedMechanicsTab(QWidget):
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
        self.projectile_tab = ProjectileMotionTab()
        self.circular_tab = CircularMotionTab()
        self.banked_tab = BankedTracksTab()
        self.gravitation_tab = GravitationTab()
        
        self.tabs.addTab(self.projectile_tab, "Projectile Motion")
        self.tabs.addTab(self.circular_tab, "Circular Motion")
        self.tabs.addTab(self.banked_tab, "Banked Tracks")
        self.tabs.addTab(self.gravitation_tab, "Gravitation")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Connect return button
        return_btn.clicked.connect(self.return_to_menu)
    
    def return_to_menu(self):
        self.parent().parent().return_to_menu()