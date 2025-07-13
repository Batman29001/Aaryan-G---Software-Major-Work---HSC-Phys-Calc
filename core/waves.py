import math
from typing import Dict, Optional, Union, Tuple
from enum import Enum, auto

class WaveError(Exception):
    """Base class for wave-related errors"""
    pass

class InputValidationError(WaveError):
    """Exception raised for invalid input values"""
    pass

class InsufficientDataError(WaveError):
    """Exception raised when not enough data is provided to solve the problem"""
    pass

class PhysicsConfigurationError(WaveError):
    """Exception raised for physically impossible configurations"""
    pass

class UnitSystem(Enum):
    SI = auto()
    CGS = auto()
    IMPERIAL = auto()

class WaveSolver:
    def __init__(self, unit_system: UnitSystem = UnitSystem.SI):
        self.speed_of_sound = 343  # m/s at 20°C
        self.speed_of_light = 3e8  # m/s
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
            if key in ['v', 'f', 'λ', 'T', 'ω', 'k', 
                      'f_observed', 'f_source', 'v_source', 'v_observer', 'v_medium',
                      'n1', 'n2', 'I1', 'I2']:
                if value < 0:
                    raise InputValidationError(f"{key} cannot be negative, got {value}")
                
            # Special validation for angles
            if key in ['θ_source', 'θ_observer', 'θ1', 'θ2']:
                if not (-360 <= value <= 360):
                    raise InputValidationError(f"Angle {key} must be between -360 and 360 degrees, got {value}")
                
            # Special validation for frequencies
            if key in ['f', 'f_observed', 'f_source'] and value == 0:
                raise InputValidationError(f"Frequency {key} cannot be zero")
                
            # Special validation for refractive indices
            if key in ['n1', 'n2'] and value < 1:
                raise InputValidationError(f"Refractive index {key} should typically be ≥1, got {value}")
                
            # Special validation for velocities
            if key in ['v_source', 'v_observer'] and abs(value) > 3 * self.speed_of_sound:
                raise PhysicsConfigurationError(f"Velocity {key} exceeds 3x speed of sound: {value} m/s")

        # Category-specific validations
        if category == 'wave_properties':
            if inputs.get('λ') is not None and inputs.get('f') is not None:
                if inputs['λ'] * inputs['f'] > 1.1 * self.speed_of_light:
                    raise PhysicsConfigurationError("Wave velocity exceeds speed of light")
                    
        elif category == 'sound_waves':
            if inputs.get('v_source') is not None and inputs.get('v_observer') is not None:
                if abs(inputs['v_source'] - inputs['v_observer']) > 2 * self.speed_of_sound:
                    raise PhysicsConfigurationError("Relative velocity exceeds 2x speed of sound")
                    
        elif category == 'light_properties':
            if inputs.get('n1') is not None and inputs.get('n2') is not None and inputs.get('θ1') is not None:
                critical_angle = math.degrees(math.asin(inputs['n2']/inputs['n1'])) if inputs['n1'] > inputs['n2'] else 90
                if inputs['θ1'] > critical_angle:
                    raise PhysicsConfigurationError(f"Angle θ1={inputs['θ1']}° exceeds critical angle {critical_angle:.1f}°")

    def _check_sufficient_data(self, category: str) -> None:
        """Check if enough data is provided to solve the problem"""
        if category == 'wave_properties':
            if not any(k in self.solutions and self.solutions[k] is not None 
                      for k in ['v', 'f', 'λ']):
                raise InsufficientDataError("Need at least two of: v/f/λ")
                
        elif category == 'sound_waves':
            if not (('f_source' in self.solutions and self.solutions['f_source'] is not None) and
                   (('v_source' in self.solutions and self.solutions['v_source'] is not None) or
                    ('v_observer' in self.solutions and self.solutions['v_observer'] is not None))):
                raise InsufficientDataError(
                    "Need source frequency and either source or observer velocity"
                )
                
        elif category == 'light_properties':
            if not (('n1' in self.solutions and self.solutions['n1'] is not None) and
                   ('n2' in self.solutions and self.solutions['n2'] is not None) and
                   (('θ1' in self.solutions and self.solutions['θ1'] is not None) or
                    ('θ2' in self.solutions and self.solutions['θ2'] is not None))):
                raise InsufficientDataError(
                    "Need both refractive indices and at least one angle"
                )

    def solve(self, category: str, **kwargs) -> Dict[str, float]:
        """Main solver with comprehensive error handling"""
        try:
            # Initialize all possible variables with None
            self.solutions = {
                # Wave properties
                'v': None, 'f': None, 'λ': None, 'T': None, 'k': None, 'ω': None,
                # Sound waves
                'f_observed': None, 'f_source': None, 'v_source': None, 'v_observer': None,
                'v_medium': None, 'θ_source': None, 'θ_observer': None,
                # Light properties
                'n1': None, 'n2': None, 'θ1': None, 'θ2': None, 'I1': None, 'I2': None
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

                if category == 'wave_properties':
                    changed = self._solve_wave_properties()
                elif category == 'sound_waves':
                    changed = self._solve_sound_waves()
                elif category == 'light_properties':
                    changed = self._solve_light_properties()

            if iteration >= self.max_iterations:
                raise WaveError("Maximum iterations reached without convergence")

            # Final validation of results
            self._validate_inputs(
                {k: v for k, v in self.solutions.items() if v is not None},
                category
            )

            return {k: v for k, v in self.solutions.items() if v is not None}

        except ZeroDivisionError as e:
            raise WaveError("Division by zero occurred in calculations") from e
        except ValueError as e:
            raise WaveError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise WaveError(f"Error solving {category} problem: {str(e)}") from e

    def _solve_wave_properties(self) -> bool:
        """Solve wave property equations with robust error handling"""
        changed = False

        try:
            # v = λf
            if self.solutions['v'] is None:
                if self.solutions['λ'] is not None and self.solutions['f'] is not None:
                    self.solutions['v'] = self.solutions['λ'] * self.solutions['f']
                    changed = True
        
            if self.solutions['λ'] is None:
                if self.solutions['v'] is not None and self.solutions['f'] is not None:
                    if self.solutions['f'] == 0:
                        raise PhysicsConfigurationError("Frequency cannot be zero when calculating wavelength")
                    self.solutions['λ'] = self.solutions['v'] / self.solutions['f']
                    changed = True
        
            if self.solutions['f'] is None:
                if self.solutions['v'] is not None and self.solutions['λ'] is not None:
                    if self.solutions['λ'] == 0:
                        raise PhysicsConfigurationError("Wavelength cannot be zero when calculating frequency")
                    self.solutions['f'] = self.solutions['v'] / self.solutions['λ']
                    changed = True
        
            # T = 1/f
            if self.solutions['T'] is None and self.solutions['f'] is not None:
                if self.solutions['f'] == 0:
                    raise PhysicsConfigurationError("Frequency cannot be zero when calculating period")
                self.solutions['T'] = 1 / self.solutions['f']
                changed = True
        
            if self.solutions['f'] is None and self.solutions['T'] is not None:
                if self.solutions['T'] == 0:
                    raise PhysicsConfigurationError("Period cannot be zero when calculating frequency")
                self.solutions['f'] = 1 / self.solutions['T']
                changed = True
        
            # ω = 2πf
            if self.solutions['ω'] is None and self.solutions['f'] is not None:
                self.solutions['ω'] = 2 * math.pi * self.solutions['f']
                changed = True
        
            if self.solutions['f'] is None and self.solutions['ω'] is not None:
                self.solutions['f'] = self.solutions['ω'] / (2 * math.pi)
                changed = True
        
            # k = 2π/λ
            if self.solutions['k'] is None and self.solutions['λ'] is not None:
                if self.solutions['λ'] == 0:
                    raise PhysicsConfigurationError("Wavelength cannot be zero when calculating wave number")
                self.solutions['k'] = 2 * math.pi / self.solutions['λ']
                changed = True
        
            if self.solutions['λ'] is None and self.solutions['k'] is not None:
                if self.solutions['k'] == 0:
                    raise PhysicsConfigurationError("Wave number cannot be zero when calculating wavelength")
                self.solutions['λ'] = 2 * math.pi / self.solutions['k']
                changed = True

        except Exception as e:
            raise WaveError(f"Wave properties calculation error: {str(e)}") from e

        return changed

    def _solve_sound_waves(self) -> bool:
        """Solve sound wave equations including Doppler effect with robust validation"""
        changed = False

        try:
            # Set default speed of sound if not provided
            if self.solutions['v_medium'] is None:
                self.solutions['v_medium'] = self.speed_of_sound
                changed = True
        
            v_medium = self.solutions['v_medium']
            f_source = self.solutions['f_source']
            f_observed = self.solutions['f_observed']
            v_source = self.solutions['v_source']
            v_observer = self.solutions['v_observer']
            θ_source = self.solutions['θ_source']
            θ_observer = self.solutions['θ_observer']
            
            # 1. Calculate f_observed if possible
            if f_observed is None and f_source is not None and v_medium is not None:
                # Source moving directly toward observer
                if v_source is not None and (θ_source is None or math.isclose(θ_source, 0, abs_tol=1e-6)):
                    if math.isclose(v_source, v_medium, abs_tol=1e-6):
                        raise PhysicsConfigurationError("Source velocity equals speed of sound (sonic boom)")
                    self.solutions['f_observed'] = (v_medium / (v_medium - v_source)) * f_source
                    changed = True
                
                # Observer moving directly toward source
                elif v_observer is not None and (θ_observer is None or math.isclose(θ_observer, 0, abs_tol=1e-6)):
                    self.solutions['f_observed'] = ((v_medium + v_observer) / v_medium) * f_source
                    changed = True
                
                # General case with angles
                elif v_source is not None and θ_source is not None:
                    denominator = v_medium - v_source * math.cos(math.radians(θ_source))
                    if abs(denominator) < 1e-6:
                        raise PhysicsConfigurationError("Denominator approaches zero in Doppler calculation")
                    self.solutions['f_observed'] = (v_medium / denominator) * f_source
                    changed = True
            
            # 2. Calculate v_source if possible (reverse Doppler)
            if v_source is None and f_observed is not None and f_source is not None and v_medium is not None:
                if (θ_source is None or math.isclose(θ_source, 0, abs_tol=1e-6)):
                    if f_observed == 0:
                        raise PhysicsConfigurationError("Observed frequency cannot be zero")
                    candidate_v_source = v_medium * (1 - f_source / f_observed)
                    if abs(candidate_v_source) < 1.5 * v_medium:  # sanity check
                        self.solutions['v_source'] = candidate_v_source
                        changed = True
            
            # 3. Calculate v_observer if possible (reverse Doppler)
            if v_observer is None and f_observed is not None and f_source is not None and v_medium is not None:
                if (θ_observer is None or math.isclose(θ_observer, 0, abs_tol=1e-6)):
                    if f_source == 0:
                        raise PhysicsConfigurationError("Source frequency cannot be zero")
                    candidate_v_observer = v_medium * (f_observed / f_source - 1)
                    if abs(candidate_v_observer) < 1.5 * v_medium:  # sanity check
                        self.solutions['v_observer'] = candidate_v_observer
                        changed = True

        except Exception as e:
            raise WaveError(f"Sound wave calculation error: {str(e)}") from e

        return changed

    def _solve_light_properties(self) -> bool:
        """Solve light wave equations including Snell's law and intensity with robust checks"""
        changed = False

        try:
            # Snell's law: n1 sinθ1 = n2 sinθ2
            if self.solutions['θ2'] is None:
                if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['n1', 'n2', 'θ1']):
                    
                    n1, n2, θ1 = self.solutions['n1'], self.solutions['n2'], self.solutions['θ1']
                    sinθ2 = (n1 * math.sin(math.radians(θ1))) / n2
                    
                    if abs(sinθ2) > 1:
                        raise PhysicsConfigurationError("Total internal reflection occurs (sinθ2 > 1)")
                    self.solutions['θ2'] = math.degrees(math.asin(sinθ2))
                    changed = True
            
            if self.solutions['θ1'] is None:
                if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['n1', 'n2', 'θ2']):
                    
                    n1, n2, θ2 = self.solutions['n1'], self.solutions['n2'], self.solutions['θ2']
                    sinθ1 = (n2 * math.sin(math.radians(θ2))) / n1
                    
                    if abs(sinθ1) > 1:
                        raise PhysicsConfigurationError("Invalid configuration (sinθ1 > 1)")
                    self.solutions['θ1'] = math.degrees(math.asin(sinθ1))
                    changed = True
            
            # Intensity ratio: I1/I2 = (n1/n2) for transmitted light
            if self.solutions['I2'] is None:
                if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['I1', 'n1', 'n2']):
                    
                    if self.solutions['n2'] == 0:
                        raise PhysicsConfigurationError("Refractive index n2 cannot be zero")
                    self.solutions['I2'] = self.solutions['I1'] * (self.solutions['n2'] / self.solutions['n1'])
                    changed = True
            
            if self.solutions['I1'] is None:
                if all(k in self.solutions and self.solutions[k] is not None 
                     for k in ['I2', 'n1', 'n2']):
                    
                    if self.solutions['n1'] == 0:
                        raise PhysicsConfigurationError("Refractive index n1 cannot be zero")
                    self.solutions['I1'] = self.solutions['I2'] * (self.solutions['n1'] / self.solutions['n2'])
                    changed = True

        except Exception as e:
            raise WaveError(f"Light properties calculation error: {str(e)}") from e

        return changed


def solve_wave_properties(**kwargs) -> Dict[str, float]:
    """Convenience function for wave properties with error handling"""
    solver = WaveSolver()
    return solver.solve('wave_properties', **kwargs)


def solve_sound_waves(**kwargs) -> Dict[str, float]:
    """Convenience function for sound waves with error handling"""
    solver = WaveSolver()
    return solver.solve('sound_waves', **kwargs)


def solve_light_properties(**kwargs) -> Dict[str, float]:
    """Convenience function for light properties with error handling"""
    solver = WaveSolver()
    return solver.solve('light_properties', **kwargs)
