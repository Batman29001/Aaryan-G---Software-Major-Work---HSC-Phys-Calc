import math
from typing import Dict, Optional, Union, Tuple
from enum import Enum, auto

class EMError(Exception):
    """Base class for electricity & magnetism-related errors"""
    pass

class InputValidationError(EMError):
    """Exception raised for invalid input values"""
    pass

class InsufficientDataError(EMError):
    """Exception raised when not enough data is provided to solve the problem"""
    pass

class PhysicsConfigurationError(EMError):
    """Exception raised for physically impossible configurations"""
    pass

class UnitSystem(Enum):
    SI = auto()
    CGS = auto()
    IMPERIAL = auto()

class EMSolver:
    def __init__(self, unit_system: UnitSystem = UnitSystem.SI):
        self.permittivity = 8.854e-12  # ε₀ in F/m
        self.permeability = 4 * math.pi * 1e-7  # μ₀ in N/A²
        self.unit_system = unit_system
        self.max_iterations = 20  # Prevent infinite loops in solver

    def _validate_inputs(self, inputs: Dict[str, float], category: str) -> None:
        """Validate input values for physical feasibility"""
        # Common validations for all categories
        for key, value in inputs.items():
            if value is None:
                continue
                
            if not isinstance(value, (int, float)):
                raise InputValidationError(f"Value for {key} must be a number, got {type(value)}")
                
            # Check for negative values where not allowed
            if key in ['q', 'E', 'F', 'V', 'd', 'I', 'V_circuit', 'R', 'P', 'E_energy', 't', 
                      'R_series', 'R_parallel', 'R1', 'R2', 'B', 'I_wire', 'r_wire', 'N', 'L']:
                if value < 0:
                    raise InputValidationError(f"{key} cannot be negative, got {value}")
                
            # Special validation for resistance
            if key in ['R', 'R_series', 'R_parallel', 'R1', 'R2'] and value == 0:
                raise InputValidationError(f"{key} cannot be zero")
                
            # Special validation for time
            if key == 't' and value <= 0:
                raise InputValidationError(f"Time must be positive, got {value}")
                
            # Special validation for distance
            if key in ['d', 'r_wire', 'L'] and value <= 0:
                raise InputValidationError(f"{key} must be positive, got {value}")
                
            # Special validation for number of turns
            if key == 'N' and (value <= 0 or not isinstance(value, (int, float))):
                raise InputValidationError(f"Number of turns must be a positive integer, got {value}")
                
        # Category-specific validations
        if category == 'electrostatics':
            if inputs.get('d') is not None and inputs.get('V') is not None:
                if inputs['d'] == 0 and inputs['V'] != 0:
                    raise PhysicsConfigurationError("Infinite electric field (V ≠ 0 with d = 0)")
                    
        elif category == 'circuits':
            if inputs.get('I') is not None and inputs.get('R') is not None:
                power = inputs.get('I', 0)**2 * inputs['R']
                if power > 1e6:  # 1 MW threshold
                    raise PhysicsConfigurationError(f"Excessive power detected: {power} W")
                    
        elif category == 'magnetism':
            if inputs.get('I_wire') is not None and inputs.get('I_wire') > 1e6:  # 1 MA threshold
                raise PhysicsConfigurationError(f"Dangerously high current: {inputs['I_wire']} A")

    def _check_sufficient_data(self, category: str) -> None:
        """Check if enough data is provided to solve the problem"""
        if category == 'electrostatics':
            return  # Skip strict checks — allow solving from any inputs
                    
        elif category == 'circuits':
            if not any(k in self.solutions and self.solutions[k] is not None 
                      for k in ['V_circuit', 'I', 'R']):
                raise InsufficientDataError("Need at least two of: V/I/R")
                
        elif category == 'magnetism':
            if not (('I_wire' in self.solutions and self.solutions['I_wire'] is not None) and
                   (('r_wire' in self.solutions and self.solutions['r_wire'] is not None) or
                    ('N' in self.solutions and self.solutions['N'] is not None and 
                     'L' in self.solutions and self.solutions['L'] is not None))):
                raise InsufficientDataError(
                    "Need current and either distance (for wire) or N and L (for solenoid)"
                )

    def solve(self, category: str, **kwargs) -> Dict[str, float]:
        """Main solver with comprehensive error handling"""
        try:
            # Initialize all possible variables with None
            self.solutions = {
                # Electrostatics
                'F': None, 'q': None, 'E': None, 'V': None, 'd': None, 'U': None, 'W': None,
                # Circuits
                'I': None, 'V_circuit': None, 'R': None, 'P': None, 'E_energy': None, 't': None,
                'R_series': None, 'R_parallel': None, 'R1': None, 'R2': None,
                # Magnetism
                'B': None, 'I_wire': None, 'r_wire': None, 'N': None, 'L': None, 'type': None
            }

            # Validate inputs before processing
            self._validate_inputs(kwargs, category)
            
            # Set provided values
            for k, v in kwargs.items():
                if k in self.solutions:
                    self.solutions[k] = v

            # Check if we have enough data to start solving
            self._check_sufficient_data(category)

            # Keep solving until no more progress can be made
            changed = True
            iteration = 0
            
            while changed and iteration < self.max_iterations:
                changed = False
                iteration += 1

                if category == 'electrostatics':
                    changed = self._solve_electrostatics()
                elif category == 'circuits':
                    changed = self._solve_circuits()
                elif category == 'magnetism':
                    changed = self._solve_magnetism()

            if iteration >= self.max_iterations:
                raise EMError("Maximum iterations reached without convergence")

            # Final validation of results
            self._validate_inputs(
                {k: v for k, v in self.solutions.items() if v is not None},
                category
            )

            return {k: v for k, v in self.solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise EMError("Division by zero occurred in calculations") from e
        except ValueError as e:
            raise EMError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise EMError(f"Error solving {category} problem: {str(e)}") from e

    def _solve_electrostatics(self) -> bool:
        """Solve electrostatics equations with robust error handling"""
        changed = False

        # F = qE (Force on charge)
        try:
            if self.solutions['F'] is None:
                if self.solutions['q'] is not None and self.solutions['E'] is not None:
                    self.solutions['F'] = self.solutions['q'] * self.solutions['E']
                    changed = True
            if self.solutions['q'] is None:
                if self.solutions['F'] is not None and self.solutions['E'] is not None and self.solutions['E'] != 0:
                    self.solutions['q'] = self.solutions['F'] / self.solutions['E']
                    changed = True
            if self.solutions['E'] is None:
                if self.solutions['F'] is not None and self.solutions['q'] is not None and self.solutions['q'] != 0:
                    self.solutions['E'] = self.solutions['F'] / self.solutions['q']
                    changed = True

            # E = V/d (Electric field)
            if self.solutions['E'] is None:
                if self.solutions['V'] is not None and self.solutions['d'] is not None:
                    if self.solutions['d'] == 0:
                        raise PhysicsConfigurationError("Distance cannot be zero when calculating electric field")
                    self.solutions['E'] = self.solutions['V'] / self.solutions['d']
                    changed = True
            if self.solutions['V'] is None:
                if self.solutions['E'] is not None and self.solutions['d'] is not None:
                    self.solutions['V'] = self.solutions['E'] * self.solutions['d']
                    changed = True
            if self.solutions['d'] is None:
                if self.solutions['V'] is not None and self.solutions['E'] is not None:
                    if self.solutions['E'] == 0:
                        raise PhysicsConfigurationError("Electric field cannot be zero when calculating distance")
                    self.solutions['d'] = self.solutions['V'] / self.solutions['E']
                    changed = True

        except Exception as e:
            raise EMError(f"Electrostatics calculation error: {str(e)}") from e

        return changed

    def _solve_circuits(self) -> bool:
        """Solve electric circuit equations with comprehensive checks"""
        changed = False

        try:
            # Ohm's Law: V = IR
            if self.solutions['V_circuit'] is None:
                if self.solutions['I'] is not None and self.solutions['R'] is not None:
                    self.solutions['V_circuit'] = self.solutions['I'] * self.solutions['R']
                    changed = True
            if self.solutions['I'] is None:
                if self.solutions['V_circuit'] is not None and self.solutions['R'] is not None:
                    if self.solutions['R'] == 0:
                        raise PhysicsConfigurationError("Resistance cannot be zero when calculating current")
                    self.solutions['I'] = self.solutions['V_circuit'] / self.solutions['R']
                    changed = True
            if self.solutions['R'] is None:
                if self.solutions['V_circuit'] is not None and self.solutions['I'] is not None:
                    if self.solutions['I'] == 0:
                        raise PhysicsConfigurationError("Current cannot be zero when calculating resistance")
                    self.solutions['R'] = self.solutions['V_circuit'] / self.solutions['I']
                    changed = True

            # Power calculations
            if self.solutions['P'] is None:
                if self.solutions['V_circuit'] is not None and self.solutions['I'] is not None:
                    self.solutions['P'] = self.solutions['V_circuit'] * self.solutions['I']
                    changed = True
                elif self.solutions['I'] is not None and self.solutions['R'] is not None:
                    self.solutions['P'] = (self.solutions['I'] ** 2) * self.solutions['R']
                    changed = True
                elif self.solutions['V_circuit'] is not None and self.solutions['R'] is not None:
                    if self.solutions['R'] == 0:
                        raise PhysicsConfigurationError("Resistance cannot be zero when calculating power")
                    self.solutions['P'] = (self.solutions['V_circuit'] ** 2) / self.solutions['R']
                    changed = True

            # Energy calculations
            if self.solutions['E_energy'] is None:
                if self.solutions['P'] is not None and self.solutions['t'] is not None:
                    self.solutions['E_energy'] = self.solutions['P'] * self.solutions['t']
                    changed = True
                elif all(k in self.solutions and self.solutions[k] is not None for k in ['V_circuit', 'I', 't']):
                    self.solutions['E_energy'] = self.solutions['V_circuit'] * self.solutions['I'] * self.solutions['t']
                    changed = True

            # Series and parallel resistances
            if self.solutions['R_series'] is None and self.solutions['R1'] is not None and self.solutions['R2'] is not None:
                self.solutions['R_series'] = self.solutions['R1'] + self.solutions['R2']
                changed = True

            if self.solutions['R_parallel'] is None and self.solutions['R1'] is not None and self.solutions['R2'] is not None:
                if self.solutions['R1'] == 0 or self.solutions['R2'] == 0:
                    raise PhysicsConfigurationError("Parallel resistances cannot be zero")
                self.solutions['R_parallel'] = 1 / (1/self.solutions['R1'] + 1/self.solutions['R2'])
                changed = True

        except Exception as e:
            raise EMError(f"Circuit calculation error: {str(e)}") from e

        return changed

    def _solve_magnetism(self) -> bool:
        """Solve magnetism problems with robust validation"""
        changed = False

        try:
            # Straight wire case: B = μ₀I / (2πr)
            if self.solutions.get('r_wire') is not None and self.solutions.get('I_wire') is not None:
                if self.solutions.get('B') is None:
                    if self.solutions['r_wire'] == 0:
                        raise PhysicsConfigurationError("Distance from wire cannot be zero")
                    self.solutions['B'] = (self.permeability * self.solutions['I_wire']) / (2 * math.pi * self.solutions['r_wire'])
                    self.solutions['type'] = 'straight_wire'
                    changed = True

            # Solenoid case: B = μ₀NI/L
            if self.solutions.get('N') is not None and self.solutions.get('L') is not None:
                if self.solutions.get('B') is None and self.solutions.get('I_wire') is not None:
                    if self.solutions['L'] == 0:
                        raise PhysicsConfigurationError("Solenoid length cannot be zero")
                    self.solutions['B'] = (self.permeability * self.solutions['N'] * self.solutions['I_wire']) / self.solutions['L']
                    self.solutions['type'] = 'solenoid'
                    changed = True

        except Exception as e:
            raise EMError(f"Magnetism calculation error: {str(e)}") from e

        return changed


def solve_electrostatics(**kwargs) -> Dict[str, float]:
    """Convenience function for electrostatics with error handling"""
    solver = EMSolver()
    return solver.solve('electrostatics', **kwargs)


def solve_circuits(**kwargs) -> Dict[str, float]:
    """Convenience function for electric circuits with error handling"""
    solver = EMSolver()
    return solver.solve('circuits', **kwargs)


def solve_magnetism(**kwargs) -> Dict[str, float]:
    """Convenience function for magnetism with error handling"""
    solver = EMSolver()
    return solver.solve('magnetism', **kwargs)