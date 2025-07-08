import re
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

class ProblemType(Enum):
    KINEMATICS = auto()
    DYNAMICS = auto()
    WAVES = auto()
    ELECTRICITY = auto()       # electricity_magnetism.py
    ELECTROMAGNETISM = auto()  # electromagnetism.py
    ADVANCED_MECHANICS = auto()
    UNKNOWN = auto()

class PhysicsInterpreter:
    def __init__(self):
        # Unit conversion factors (to SI)
        self.UNIT_CONVERSIONS = {
            # Length/Distance
            'm': 1.0, 'km': 1000.0, 'cm': 0.01, 'mm': 0.001, 'ft': 0.3048,
            # Time
            's': 1.0, 'ms': 1e-3, 'min': 60.0, 'h': 3600.0,
            # Mass
            'kg': 1.0, 'g': 1e-3, 'mg': 1e-6,
            # Velocity
            'm/s': 1.0, 'km/h': 0.277778, 'ft/s': 0.3048,
            # Acceleration
            'm/s²': 1.0, 'ft/s²': 0.3048,
            # Force
            'N': 1.0, 'kN': 1e3, 'lb': 4.44822,
            # Energy
            'J': 1.0, 'kJ': 1e3, 'eV': 1.60218e-19,
            # Electricity
            'V': 1.0, 'kV': 1e3, 'mV': 1e-3,
            'A': 1.0, 'mA': 1e-3, 'μA': 1e-6,
            'Ω': 1.0, 'kΩ': 1e3, 'MΩ': 1e6,
            'F': 1.0, 'μF': 1e-6, 'nF': 1e-9,
            # Electromagnetism
            'T': 1.0, 'mT': 1e-3, 'μT': 1e-6,
            'C': 1.0, 'μC': 1e-6, 'nC': 1e-9,
            'Wb': 1.0, 'H': 1.0,
        }

        # Variable patterns for each domain (regex)
        self.VARIABLE_PATTERNS = {
            ProblemType.KINEMATICS: {
                'velocity': r'(\d+\.?\d*)\s*(m/s|km/h|ft/s)',
                'acceleration': r'(\d+\.?\d*)\s*(m/s²|ft/s²)',
                'time': r'(\d+\.?\d*)\s*(s|ms|min|h)',
                'displacement': r'(\d+\.?\d*)\s*(m|km|cm|ft)',
            },
            ProblemType.DYNAMICS: {
                'mass': r'(\d+\.?\d*)\s*(kg|g|mg)',
                'force': r'(\d+\.?\d*)\s*(N|kN|lb)',
                'momentum': r'(\d+\.?\d*)\s*(kg·m/s)',
            },
            ProblemType.WAVES: {
                'frequency': r'(\d+\.?\d*)\s*(Hz|kHz|MHz)',
                'wavelength': r'(\d+\.?\d*)\s*(m|nm|μm)',
                'period': r'(\d+\.?\d*)\s*(s|ms)',
            },
            ProblemType.ELECTRICITY: {
                'voltage': r'(\d+\.?\d*)\s*(V|kV|mV)',
                'current': r'(\d+\.?\d*)\s*(A|mA|μA)',
                'resistance': r'(\d+\.?\d*)\s*(Ω|kΩ|MΩ)',
                'power': r'(\d+\.?\d*)\s*(W|kW|MW)',
            },
            ProblemType.ELECTROMAGNETISM: {
                'charge': r'(\d+\.?\d*)\s*(C|μC|nC)',
                'magnetic_field': r'(\d+\.?\d*)\s*(T|mT|μT)',
                'emf': r'(\d+\.?\d*)\s*(V|mV)',
                'flux': r'(\d+\.?\d*)\s*(Wb)',
            },
            ProblemType.ADVANCED_MECHANICS: {
                'angle': r'(\d+\.?\d*)\s*(°|deg|rad)',
                'angular_velocity': r'(\d+\.?\d*)\s*(rad/s|rpm)',
                'torque': r'(\d+\.?\d*)\s*(N·m)',
            }
        }

    def extract_variables(self, text: str) -> Dict[str, float]:
        """Extract variables/units from text with strict validation."""
        variables = {}
        errors = []

        for problem_type, patterns in self.VARIABLE_PATTERNS.items():
            for var_name, pattern in patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        unit = match.group(2)
                        si_value = value * self.UNIT_CONVERSIONS.get(unit, 1.0)
                        variables[var_name] = si_value
                    except (ValueError, KeyError) as e:
                        errors.append(f"Failed to parse {var_name}: {match.group(0)} ({str(e)})")

        if errors:
            raise ValueError(f"Variable extraction errors:\n" + "\n".join(errors))
        return variables

    def identify_problem_type(self, text: str, variables: Dict[str, float]) -> ProblemType:
        """Identify the problem type based on keywords and variables."""
        text_lower = text.lower()

        # Priority: Electromagnetism (motor effect, induction, etc.)
        em_keywords = ['magnetic field', 'lorentz force', 'motor effect', 'faraday', 'emf', 'flux']
        if any(kw in text_lower for kw in em_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.ELECTROMAGNETISM]):
            return ProblemType.ELECTROMAGNETISM

        # Priority: Electricity (circuits, resistors, etc.)
        electricity_keywords = ['circuit', 'ohm', 'resistor', 'capacitor', 'voltage', 'current', 'power']
        if any(kw in text_lower for kw in electricity_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.ELECTRICITY]):
            return ProblemType.ELECTRICITY

        # Advanced Mechanics (projectile motion, circular motion)
        advanced_keywords = ['projectile', 'trajectory', 'circular motion', 'banked track', 'gravitation']
        if any(kw in text_lower for kw in advanced_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.ADVANCED_MECHANICS]):
            return ProblemType.ADVANCED_MECHANICS

        # Dynamics (forces, momentum)
        dynamics_keywords = ['force', 'momentum', 'friction', 'impulse']
        if any(kw in text_lower for kw in dynamics_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.DYNAMICS]):
            return ProblemType.DYNAMICS

        # Kinematics (motion)
        kinematics_keywords = ['velocity', 'acceleration', 'displacement', 'kinematics']
        if any(kw in text_lower for kw in kinematics_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.KINEMATICS]):
            return ProblemType.KINEMATICS

        # Waves (sound/light)
        waves_keywords = ['wavelength', 'frequency', 'doppler', 'snell', 'refraction']
        if any(kw in text_lower for kw in waves_keywords) or any(v in variables for v in self.VARIABLE_PATTERNS[ProblemType.WAVES]):
            return ProblemType.WAVES

        return ProblemType.UNKNOWN