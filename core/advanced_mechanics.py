import math
from typing import Dict, Optional, Union, Tuple
from enum import Enum, auto

class PhysicsError(Exception):
    """Base class for physics-related errors"""
    pass

class InputValidationError(PhysicsError):
    """Exception raised for invalid input values"""
    pass

class InsufficientDataError(PhysicsError):
    """Exception raised when not enough data is provided to solve the problem"""
    pass

class UnitSystem(Enum):
    SI = auto()
    CGS = auto()
    IMPERIAL = auto()

class AdvancedMechanicsSolver:
    def __init__(self, unit_system: UnitSystem = UnitSystem.SI):
        self.g = 9.81  # m/s² (standard gravity)
        self.G = 6.67430e-11  # universal gravitational constant (m³ kg⁻¹ s⁻²)
        self.unit_system = unit_system
        self.earth_radius = 6.371e6  # meters

    def _validate_inputs(self, inputs: Dict[str, float], required: Optional[Tuple[str]] = None) -> None:
        """Validate input values for physical feasibility"""
        for key, value in inputs.items():
            if value is None:
                continue
                
            if not isinstance(value, (int, float)):
                raise InputValidationError(f"Value for {key} must be a number, got {type(value)}")
                
            # Check for negative values where not allowed
            if key in ['u', 'θ', 'ux', 'uy', 't_flight', 'max_height', 'range', 
                      'v', 'r', 'T', 'f', 'ω', 'a_c', 'F_c', 'm', 
                      'M', 'F_g', 'g', 'v_orbital', 'altitude'] and value < 0:
                raise InputValidationError(f"{key} cannot be negative, got {value}")
                
            # Special angle validation
            if key == 'θ' and (value > 360 or value < -360):
                raise InputValidationError(f"Angle θ must be between -360 and 360 degrees, got {value}")
                
            # Special validation for friction coefficient
            if key == 'μ' and (value < 0 or value > 1.5):
                raise InputValidationError(f"Friction coefficient μ must be between 0 and 1.5, got {value}")
                
            # Special validation for mass
            if key in ['m', 'M'] and value <= 0:
                raise InputValidationError(f"Mass {key} must be positive, got {value}")
                
            # Special validation for radius
            if key == 'r' and value <= 0:
                raise InputValidationError(f"Radius must be positive, got {value}")
                
            # Special validation for time period
            if key == 'T' and value <= 0:
                raise InputValidationError(f"Time period must be positive, got {value}")
                
        if required:
            missing = [k for k in required if inputs.get(k) is None]
            if missing:
                raise InsufficientDataError(f"Missing required parameters: {', '.join(missing)}")

    def _convert_units(self, values: Dict[str, float], conversions: Dict[str, Tuple[float, str]]) -> Dict[str, float]:
        """Convert units based on the provided conversion factors"""
        converted = values.copy()
        for key, (factor, unit_type) in conversions.items():
            if key in converted and converted[key] is not None:
                if unit_type == 'length':
                    converted[key] *= factor
                elif unit_type == 'time':
                    converted[key] *= factor
                elif unit_type == 'velocity':
                    converted[key] *= factor
                elif unit_type == 'mass':
                    converted[key] *= factor
        return converted

    def solve_projectile_motion(self, **kwargs) -> Dict[str, float]:
        """Solve projectile motion problems with comprehensive error handling"""
        solutions = {
            'u': None, 'θ': None, 'ux': None, 'uy': None,
            't_flight': None, 'max_height': None, 'range': None
        }

        try:
            # Validate inputs
            self._validate_inputs(kwargs)
            
            # Set provided values
            for k, v in kwargs.items():
                if k in solutions:
                    solutions[k] = v

            # Convert angle to radians if provided (and not already converted)
            if solutions['θ'] is not None and solutions['θ'] > 2 * math.pi:
                solutions['θ'] = math.radians(solutions['θ'])

            changed = True
            iteration = 0
            max_iterations = 10  # Prevent infinite loops
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1

                # u, θ -> ux, uy
                if solutions['u'] is not None and solutions['θ'] is not None:
                    if solutions['ux'] is None:
                        solutions['ux'] = solutions['u'] * math.cos(solutions['θ'])
                        changed = True
                    if solutions['uy'] is None:
                        solutions['uy'] = solutions['u'] * math.sin(solutions['θ'])
                        changed = True

                # ux, uy -> u, θ
                if solutions['ux'] is not None and solutions['uy'] is not None:
                    if solutions['u'] is None:
                        solutions['u'] = math.hypot(solutions['ux'], solutions['uy'])
                        changed = True
                    if solutions['θ'] is None:
                        solutions['θ'] = math.atan2(solutions['uy'], solutions['ux'])
                        changed = True

                # Time of flight: t_flight = 2 * uy / g
                if solutions['t_flight'] is None and solutions['uy'] is not None:
                    solutions['t_flight'] = 2 * solutions['uy'] / self.g
                    changed = True
                if solutions['uy'] is None and solutions['t_flight'] is not None:
                    solutions['uy'] = (solutions['t_flight'] * self.g) / 2
                    changed = True

                # Max height: h = uy² / (2g)
                if solutions['max_height'] is None and solutions['uy'] is not None:
                    solutions['max_height'] = (solutions['uy'] ** 2) / (2 * self.g)
                    changed = True
                if solutions['uy'] is None and solutions['max_height'] is not None:
                    solutions['uy'] = math.sqrt(2 * self.g * solutions['max_height'])
                    changed = True

                # Range: R = ux * t_flight
                if solutions['range'] is None and solutions['ux'] is not None and solutions['t_flight'] is not None:
                    solutions['range'] = solutions['ux'] * solutions['t_flight']
                    changed = True
                if solutions['ux'] is None and solutions['range'] is not None and solutions['t_flight'] is not None and solutions['t_flight'] != 0:
                    solutions['ux'] = solutions['range'] / solutions['t_flight']
                    changed = True
                if solutions['t_flight'] is None and solutions['range'] is not None and solutions['ux'] is not None and solutions['ux'] != 0:
                    solutions['t_flight'] = solutions['range'] / solutions['ux']
                    changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")

            # Convert angle back to degrees if it was input as degrees
            if solutions['θ'] is not None:
                solutions['θ'] = math.degrees(solutions['θ'])

            # Final validation of results
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})

            return {k: v for k, v in solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving projectile motion: {str(e)}") from e

    def solve_circular_motion(self, **kwargs) -> Dict[str, float]:
        """Solve uniform circular motion problems with robust error handling"""
        solutions = {
            'v': None, 'r': None, 'T': None, 'f': None,
            'ω': None, 'a_c': None, 'F_c': None, 'm': None
        }

        try:
            # Validate inputs
            self._validate_inputs(kwargs)
            
            for k, v in kwargs.items():
                if k in solutions:
                    solutions[k] = v

            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1

                # Angular velocity ω from T or f
                if solutions['ω'] is None:
                    if solutions['T'] is not None and solutions['T'] != 0:
                        solutions['ω'] = 2 * math.pi / solutions['T']
                        changed = True
                    elif solutions['f'] is not None:
                        solutions['ω'] = 2 * math.pi * solutions['f']
                        changed = True

                # Period T or frequency f from ω
                if solutions['T'] is None and solutions['ω'] is not None and solutions['ω'] != 0:
                    solutions['T'] = 2 * math.pi / solutions['ω']
                    changed = True
                if solutions['f'] is None and solutions['T'] is not None and solutions['T'] != 0:
                    solutions['f'] = 1 / solutions['T']
                    changed = True

                # Velocity from ω and r
                if solutions['v'] is None and solutions['ω'] is not None and solutions['r'] is not None:
                    solutions['v'] = solutions['ω'] * solutions['r']
                    changed = True
                if solutions['ω'] is None and solutions['v'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['ω'] = solutions['v'] / solutions['r']
                    changed = True
                if solutions['r'] is None and solutions['v'] is not None and solutions['ω'] is not None and solutions['ω'] != 0:
                    solutions['r'] = solutions['v'] / solutions['ω']
                    changed = True

                # Centripetal acceleration a_c = v²/r
                if solutions['a_c'] is None and solutions['v'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['a_c'] = (solutions['v'] ** 2) / solutions['r']
                    changed = True
                if solutions['v'] is None and solutions['a_c'] is not None and solutions['r'] is not None:
                    solutions['v'] = math.sqrt(solutions['a_c'] * solutions['r'])
                    changed = True
                if solutions['r'] is None and solutions['v'] is not None and solutions['a_c'] is not None and solutions['a_c'] != 0:
                    solutions['r'] = (solutions['v'] ** 2) / solutions['a_c']
                    changed = True

                # Centripetal force F_c = m * a_c
                if solutions['F_c'] is None and solutions['m'] is not None and solutions['a_c'] is not None:
                    solutions['F_c'] = solutions['m'] * solutions['a_c']
                    changed = True
                if solutions['m'] is None and solutions['F_c'] is not None and solutions['a_c'] is not None and solutions['a_c'] != 0:
                    solutions['m'] = solutions['F_c'] / solutions['a_c']
                    changed = True
                if solutions['a_c'] is None and solutions['F_c'] is not None and solutions['m'] is not None and solutions['m'] != 0:
                    solutions['a_c'] = solutions['F_c'] / solutions['m']
                    changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")

            # Final validation of results
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})

            return {k: v for k, v in solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in circular motion calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered in circular motion: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving circular motion: {str(e)}") from e

    def solve_banked_tracks(self, **kwargs) -> Dict[str, float]:
        """Solve banked track problems with comprehensive error handling"""
        solutions = {
            'θ': None, 'v': None, 'r': None, 'μ': None,
            'v_min': None, 'v_max': None
        }

        try:
            # Validate inputs
            self._validate_inputs(kwargs)
            
            for k, v in kwargs.items():
                if k in solutions:
                    solutions[k] = v

            # Convert angle to radians if provided (and not already)
            if solutions['θ'] is not None and solutions['θ'] > 2 * math.pi:
                solutions['θ'] = math.radians(solutions['θ'])

            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1

                tan_θ = math.tan(solutions['θ']) if solutions['θ'] is not None else None

                # Ideal banked curve (no friction): θ = atan(v²/(g r))
                if solutions['θ'] is None and solutions['v'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['θ'] = math.atan((solutions['v'] ** 2) / (self.g * solutions['r']))
                    changed = True
                    tan_θ = math.tan(solutions['θ'])

                # v from θ and r (ideal banking)
                if solutions['v'] is None and solutions['θ'] is not None and solutions['r'] is not None:
                    solutions['v'] = math.sqrt(self.g * solutions['r'] * tan_θ)
                    changed = True

                # v_min and v_max with friction
                if solutions['μ'] is not None and tan_θ is not None and solutions['r'] is not None and solutions['r'] != 0:
                    # v_min = sqrt(g r (tanθ - μ)/(1 + μ tanθ))
                    if solutions['v_min'] is None:
                        denom = 1 + solutions['μ'] * tan_θ
                        numer = tan_θ - solutions['μ']
                        if denom != 0 and numer > 0:
                            solutions['v_min'] = math.sqrt(self.g * solutions['r'] * numer / denom)
                            changed = True

                    # v_max = sqrt(g r (tanθ + μ)/(1 - μ tanθ))
                    if solutions['v_max'] is None:
                        denom = 1 - solutions['μ'] * tan_θ
                        numer = tan_θ + solutions['μ']
                        if denom != 0 and numer > 0:
                            solutions['v_max'] = math.sqrt(self.g * solutions['r'] * numer / denom)
                            changed = True

                # If v_min or v_max provided, try to reverse calculate μ
                if solutions['μ'] is None and tan_θ is not None and solutions['r'] is not None and solutions['r'] != 0:
                    # Using v_min formula:
                    if solutions['v_min'] is not None:
                        lhs = (solutions['v_min'] ** 2) / (self.g * solutions['r'])
                        # Solve μ from: lhs = (tanθ - μ)/(1 + μ tanθ) -> μ = (tanθ - lhs)/(lhs tanθ + 1)
                        denom = lhs * tan_θ + 1
                        if denom != 0:
                            mu_calc = (tan_θ - lhs) / denom
                            if mu_calc >= 0:  # friction coefficient must be non-negative
                                solutions['μ'] = mu_calc
                                changed = True
                    # Using v_max formula:
                    if solutions['v_max'] is not None and solutions['μ'] is None:
                        lhs = (solutions['v_max'] ** 2) / (self.g * solutions['r'])
                        # Solve μ from: lhs = (tanθ + μ)/(1 - μ tanθ) -> μ = (lhs - tanθ)/(lhs tanθ + 1)
                        denom = lhs * tan_θ + 1
                        if denom != 0:
                            mu_calc = (lhs - tan_θ) / denom
                            if mu_calc >= 0:
                                solutions['μ'] = mu_calc
                                changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")

            # Convert angle back to degrees if it was input as degrees
            if solutions['θ'] is not None:
                solutions['θ'] = math.degrees(solutions['θ'])

            # Final validation of results
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})

            return {k: v for k, v in solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in banked track calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered in banked track: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving banked track: {str(e)}") from e

    def solve_gravitation(self, **kwargs) -> Dict[str, float]:
        """Solve gravitation problems with robust error handling"""
        solutions = {
            'M': None, 'm': None, 'r': None, 'F_g': None,
            'g': None, 'v_orbital': None, 'T': None, 'altitude': None
        }

        try:
            # Validate inputs
            self._validate_inputs(kwargs)
            
            for k, v in kwargs.items():
                if k in solutions:
                    solutions[k] = v

            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1

                # Gravitational force: F = G M m / r²
                if solutions['F_g'] is None and solutions['M'] is not None and solutions['m'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['F_g'] = self.G * solutions['M'] * solutions['m'] / (solutions['r'] ** 2)
                    changed = True
                if solutions['M'] is None and solutions['F_g'] is not None and solutions['m'] is not None and solutions['r'] is not None and solutions['r'] != 0 and solutions['m'] != 0:
                    solutions['M'] = solutions['F_g'] * (solutions['r'] ** 2) / (self.G * solutions['m'])
                    changed = True
                if solutions['m'] is None and solutions['F_g'] is not None and solutions['M'] is not None and solutions['r'] is not None and solutions['r'] != 0 and solutions['M'] != 0:
                    solutions['m'] = solutions['F_g'] * (solutions['r'] ** 2) / (self.G * solutions['M'])
                    changed = True
                if solutions['r'] is None and solutions['F_g'] is not None and solutions['M'] is not None and solutions['m'] is not None and solutions['F_g'] != 0:
                    solutions['r'] = math.sqrt(self.G * solutions['M'] * solutions['m'] / solutions['F_g'])
                    changed = True

                # Gravitational field strength: g = G M / r²
                if solutions['g'] is None and solutions['M'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['g'] = self.G * solutions['M'] / (solutions['r'] ** 2)
                    changed = True
                if solutions['M'] is None and solutions['g'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['M'] = solutions['g'] * (solutions['r'] ** 2) / self.G
                    changed = True
                if solutions['r'] is None and solutions['g'] is not None and solutions['M'] is not None and solutions['g'] != 0:
                    solutions['r'] = math.sqrt(self.G * solutions['M'] / solutions['g'])
                    changed = True

                # Orbital velocity: v = sqrt(G M / r)
                if solutions['v_orbital'] is None and solutions['M'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['v_orbital'] = math.sqrt(self.G * solutions['M'] / solutions['r'])
                    changed = True
                if solutions['M'] is None and solutions['v_orbital'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['M'] = (solutions['v_orbital'] ** 2) * solutions['r'] / self.G
                    changed = True
                if solutions['r'] is None and solutions['v_orbital'] is not None and solutions['M'] is not None and solutions['v_orbital'] != 0:
                    solutions['r'] = self.G * solutions['M'] / (solutions['v_orbital'] ** 2)
                    changed = True

                # Orbital period: T = 2πr / v_orbital
                if solutions['T'] is None and solutions['v_orbital'] is not None and solutions['r'] is not None:
                    solutions['T'] = 2 * math.pi * solutions['r'] / solutions['v_orbital']
                    changed = True
                if solutions['v_orbital'] is None and solutions['T'] is not None and solutions['r'] is not None and solutions['r'] != 0:
                    solutions['v_orbital'] = 2 * math.pi * solutions['r'] / solutions['T']
                    changed = True
                if solutions['r'] is None and solutions['T'] is not None and solutions['v_orbital'] is not None and solutions['v_orbital'] != 0:
                    solutions['r'] = (solutions['T'] * solutions['v_orbital']) / (2 * math.pi)
                    changed = True

                # Altitude from radius
                if solutions['altitude'] is None and solutions['r'] is not None:
                    solutions['altitude'] = solutions['r'] - self.earth_radius
                    changed = True
                if solutions['r'] is None and solutions['altitude'] is not None:
                    solutions['r'] = solutions['altitude'] + self.earth_radius
                    changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")

            # Final validation of results
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})

            return {k: v for k, v in solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in gravitation calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered in gravitation: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving gravitation problem: {str(e)}") from e


def solve_projectile_motion(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_projectile_motion(**kwargs)

def solve_circular_motion(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_circular_motion(**kwargs)

def solve_banked_tracks(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_banked_tracks(**kwargs)

def solve_gravitation(**kwargs) -> Dict[str, float]:
    solver = AdvancedMechanicsSolver()
    return solver.solve_gravitation(**kwargs)