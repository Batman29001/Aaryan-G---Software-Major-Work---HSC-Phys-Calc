# electromagnetism.py
import math
from typing import Dict, Optional, Tuple
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

class ElectromagnetismSolver:
    def __init__(self, unit_system: UnitSystem = UnitSystem.SI):
        self.mu_0 = 4 * math.pi * 1e-7  # Permeability of free space (N/A²)
        self.epsilon_0 = 8.8541878128e-12  # Permittivity of free space (F/m)
        self.e_charge = 1.602176634e-19  # Elementary charge (C)
        self.unit_system = unit_system

    def _validate_inputs(self, inputs: Dict[str, float], required: Optional[Tuple[str]] = None) -> None:
        """Validate input values for physical feasibility"""
        for key, value in inputs.items():
            if value is None:
                continue
                
            if not isinstance(value, (int, float)):
                raise InputValidationError(f"Value for {key} must be a number, got {type(value)}")
                
            # Check for negative values where not allowed
            if key in ['F', 'q', 'E', 'v', 'B', 'I', 'L', 'torque', 'n', 'A', 
                      'F_per_length', 'I1', 'I2', 'r', 'emf', 'N', 'delta_phi', 
                      'delta_t', 'phi', 'V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s'] and value < 0:
                raise InputValidationError(f"{key} cannot be negative, got {value}")
                
            # Special angle validation
            if key == 'theta' and (value > 360 or value < -360):
                raise InputValidationError(f"Angle theta must be between -360 and 360 degrees, got {value}")
                
            # Special validation for charge
            if key == 'q' and value == 0:
                raise InputValidationError("Charge cannot be zero")
                
            # Special validation for current
            if key in ['I', 'I1', 'I2', 'I_p', 'I_s'] and value == 0:
                raise InputValidationError("Current cannot be zero")
                
            # Special validation for length/distance
            if key in ['L', 'r'] and value <= 0:
                raise InputValidationError(f"{key} must be positive, got {value}")
                
            # Special validation for time
            if key == 'delta_t' and value <= 0:
                raise InputValidationError("Time change must be positive")
                
            # Special validation for turns
            if key in ['N', 'N_p', 'N_s', 'n'] and value <= 0:
                raise InputValidationError(f"{key} must be positive, got {value}")

        if required:
            missing = [k for k in required if inputs.get(k) is None]
            if missing:
                raise InsufficientDataError(f"Missing required parameters: {', '.join(missing)}")

    def solve_lorentz_force(self, **kwargs) -> Dict[str, float]:
        """
        Solves Lorentz force problems (F = qE + qvBsinθ)
        Possible variables: F, q, E, v, B, theta
        """
        solutions = {k: kwargs.get(k, None) for k in ['F', 'q', 'E', 'v', 'B', 'theta']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            # Convert theta to radians if provided
            theta_rad = math.radians(solutions['theta']) if solutions['theta'] is not None else None
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Electric component (F = qE)
                if solutions['F'] is None and solutions['q'] is not None and solutions['E'] is not None:
                    solutions['F'] = solutions['q'] * solutions['E']
                    changed = True
                    
                # Magnetic component (F = qvBsinθ)
                if solutions['F'] is None and all(solutions.get(k) is not None for k in ['q', 'v', 'B', 'theta']):
                    if math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate force when sinθ is zero")
                    solutions['F'] = solutions['q'] * solutions['v'] * solutions['B'] * math.sin(theta_rad)
                    changed = True
                    
                # Solve for other variables
                if solutions['q'] is None and solutions['F'] is not None and solutions['E'] is not None:
                    if solutions['E'] == 0:
                        raise PhysicsError("Cannot calculate charge when E is zero")
                    solutions['q'] = solutions['F'] / solutions['E']
                    changed = True
                    
                if solutions['E'] is None and solutions['F'] is not None and solutions['q'] is not None:
                    if solutions['q'] == 0:
                        raise PhysicsError("Cannot calculate E when charge is zero")
                    solutions['E'] = solutions['F'] / solutions['q']
                    changed = True
                    
                if solutions['v'] is None and all(solutions.get(k) is not None for k in ['F', 'q', 'B', 'theta']):
                    if solutions['q'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate velocity when q, B or sinθ is zero")
                    solutions['v'] = solutions['F'] / (solutions['q'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['B'] is None and all(solutions.get(k) is not None for k in ['F', 'q', 'v', 'theta']):
                    if solutions['q'] == 0 or solutions['v'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate B when q, v or sinθ is zero")
                    solutions['B'] = solutions['F'] / (solutions['q'] * solutions['v'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['theta'] is None and all(solutions.get(k) is not None for k in ['F', 'q', 'v', 'B']):
                    try:
                        sin_theta = solutions['F'] / (solutions['q'] * solutions['v'] * solutions['B'])
                        if abs(sin_theta) > 1:
                            raise PhysicsError("Invalid combination of values - |sinθ| cannot exceed 1")
                        theta_rad = math.asin(sin_theta)
                        solutions['theta'] = math.degrees(theta_rad)
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate angle when q, v or B is zero")

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            # Validate results
            if solutions.get('theta') is not None and not (0 <= solutions['theta'] <= 180):
                raise InputValidationError("Angle must be between 0° and 180°")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in Lorentz force calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving Lorentz force: {str(e)}") from e

    def solve_force_on_wire(self, **kwargs) -> Dict[str, float]:
        """
        Solves force on current-carrying wire problems (F = BILsinθ)
        Possible variables: F, I, L, B, theta
        """
        solutions = {k: kwargs.get(k, None) for k in ['F', 'I', 'L', 'B', 'theta']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            # Convert theta to radians if provided
            theta_rad = math.radians(solutions['theta']) if solutions['theta'] is not None else None
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Main equation (F = ILBsinθ)
                if solutions['F'] is None and all(solutions.get(k) is not None for k in ['I', 'L', 'B', 'theta']):
                    if math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate force when sinθ is zero")
                    solutions['F'] = solutions['I'] * solutions['L'] * solutions['B'] * math.sin(theta_rad)
                    changed = True
                    
                # Solve for other variables
                if solutions['I'] is None and all(solutions.get(k) is not None for k in ['F', 'L', 'B', 'theta']):
                    if solutions['L'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate current when L, B or sinθ is zero")
                    solutions['I'] = solutions['F'] / (solutions['L'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['L'] is None and all(solutions.get(k) is not None for k in ['F', 'I', 'B', 'theta']):
                    if solutions['I'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate length when I, B or sinθ is zero")
                    solutions['L'] = solutions['F'] / (solutions['I'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['B'] is None and all(solutions.get(k) is not None for k in ['F', 'I', 'L', 'theta']):
                    if solutions['I'] == 0 or solutions['L'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate B when I, L or sinθ is zero")
                    solutions['B'] = solutions['F'] / (solutions['I'] * solutions['L'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['theta'] is None and all(solutions.get(k) is not None for k in ['F', 'I', 'L', 'B']):
                    try:
                        sin_theta = solutions['F'] / (solutions['I'] * solutions['L'] * solutions['B'])
                        if abs(sin_theta) > 1:
                            raise PhysicsError("Invalid combination of values - |sinθ| cannot exceed 1")
                        theta_rad = math.asin(sin_theta)
                        solutions['theta'] = math.degrees(theta_rad)
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate angle when I, L or B is zero")

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            # Validate results
            if solutions.get('theta') is not None and not (0 <= solutions['theta'] <= 180):
                raise InputValidationError("Angle must be between 0° and 180°")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in force on wire calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving force on wire: {str(e)}") from e

    def solve_parallel_wires(self, **kwargs) -> Dict[str, float]:
        """
        Solves force between parallel wires problems (F/l = μ₀I₁I₂/2πr)
        Possible variables: F_per_length, I1, I2, r
        """
        solutions = {k: kwargs.get(k, None) for k in ['F_per_length', 'I1', 'I2', 'r']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Main equation (F/l = μ₀I₁I₂/2πr)
                if solutions['F_per_length'] is None and all(solutions.get(k) is not None for k in ['I1', 'I2', 'r']):
                    if solutions['r'] <= 0:
                        raise PhysicsError("Separation distance must be positive")
                    solutions['F_per_length'] = (self.mu_0 * solutions['I1'] * solutions['I2']) / (2 * math.pi * solutions['r'])
                    changed = True
                    
                # Solve for other variables
                if solutions['I1'] is None and all(solutions.get(k) is not None for k in ['F_per_length', 'I2', 'r']):
                    if solutions['I2'] == 0 or solutions['r'] <= 0:
                        raise PhysicsError("Current 2 and separation must be non-zero")
                    solutions['I1'] = (2 * math.pi * solutions['r'] * solutions['F_per_length']) / (self.mu_0 * solutions['I2'])
                    changed = True
                        
                if solutions['I2'] is None and all(solutions.get(k) is not None for k in ['F_per_length', 'I1', 'r']):
                    if solutions['I1'] == 0 or solutions['r'] <= 0:
                        raise PhysicsError("Current 1 and separation must be non-zero")
                    solutions['I2'] = (2 * math.pi * solutions['r'] * solutions['F_per_length']) / (self.mu_0 * solutions['I1'])
                    changed = True
                        
                if solutions['r'] is None and all(solutions.get(k) is not None for k in ['F_per_length', 'I1', 'I2']):
                    if solutions['I1'] == 0 or solutions['I2'] == 0:
                        raise PhysicsError("Currents must be non-zero")
                    if solutions['F_per_length'] == 0:
                        raise PhysicsError("Force per length cannot be zero when calculating distance")
                    solutions['r'] = (self.mu_0 * solutions['I1'] * solutions['I2']) / (2 * math.pi * solutions['F_per_length'])
                    changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in parallel wires calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving parallel wires: {str(e)}") from e

    def solve_emf_induction(self, **kwargs) -> Dict[str, float]:
        """
        Solves EMF induction problems (ε = -NΔΦ/Δt, Φ = BAcosθ)
        Possible variables: emf, N, delta_phi, delta_t, B, A, theta, phi
        """
        solutions = {k: kwargs.get(k, None) for k in ['emf', 'N', 'delta_phi', 'delta_t', 'B', 'A', 'theta', 'phi']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            # Convert theta to radians if provided
            theta_rad = math.radians(solutions['theta']) if solutions['theta'] is not None else None
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Flux equation (Φ = BAcosθ)
                if solutions['phi'] is None and solutions['B'] is not None and solutions['A'] is not None:
                    theta = theta_rad if solutions['theta'] is not None else 0
                    solutions['phi'] = solutions['B'] * solutions['A'] * math.cos(theta)
                    changed = True
                    
                # EMF equation (ε = -NΔΦ/Δt)
                if solutions['emf'] is None and all(solutions.get(k) is not None for k in ['N', 'delta_phi', 'delta_t']):
                    if solutions['delta_t'] <= 0:
                        raise PhysicsError("Time change must be positive")
                    solutions['emf'] = -solutions['N'] * solutions['delta_phi'] / solutions['delta_t']
                    changed = True
                    
                # Solve for other variables
                if solutions['N'] is None and all(solutions.get(k) is not None for k in ['emf', 'delta_phi', 'delta_t']):
                    if solutions['delta_phi'] == 0 or solutions['delta_t'] <= 0:
                        raise PhysicsError("Flux change and time must be non-zero")
                    solutions['N'] = -solutions['emf'] * solutions['delta_t'] / solutions['delta_phi']
                    changed = True
                        
                if solutions['delta_phi'] is None and all(solutions.get(k) is not None for k in ['emf', 'N', 'delta_t']):
                    if solutions['delta_t'] <= 0:
                        raise PhysicsError("Time change must be positive")
                    solutions['delta_phi'] = -solutions['emf'] * solutions['delta_t'] / solutions['N']
                    changed = True
                        
                if solutions['delta_t'] is None and all(solutions.get(k) is not None for k in ['emf', 'N', 'delta_phi']):
                    if solutions['delta_phi'] == 0:
                        raise PhysicsError("Flux change cannot be zero when calculating time")
                    solutions['delta_t'] = -solutions['N'] * solutions['delta_phi'] / solutions['emf']
                    changed = True
                        
                if solutions['B'] is None and solutions['phi'] is not None and solutions['A'] is not None:
                    if solutions['A'] <= 0:
                        raise PhysicsError("Area must be positive")
                    theta = theta_rad if solutions['theta'] is not None else 0
                    try:
                        solutions['B'] = solutions['phi'] / (solutions['A'] * math.cos(theta))
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate B when area is zero or cosθ is zero")
                            
                if solutions['A'] is None and solutions['phi'] is not None and solutions['B'] is not None:
                    if solutions['B'] == 0:
                        raise PhysicsError("Magnetic field must be non-zero")
                    theta = theta_rad if solutions['theta'] is not None else 0
                    try:
                        solutions['A'] = solutions['phi'] / (solutions['B'] * math.cos(theta))
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate area when B is zero or cosθ is zero")
                            
                if solutions['theta'] is None and all(solutions.get(k) is not None for k in ['phi', 'B', 'A']):
                    try:
                        cos_theta = solutions['phi'] / (solutions['B'] * solutions['A'])
                        if abs(cos_theta) > 1:
                            raise PhysicsError("Invalid combination of values - |cosθ| cannot exceed 1")
                        theta_rad = math.acos(cos_theta)
                        solutions['theta'] = math.degrees(theta_rad)
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate angle when B or A is zero")

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            # Validate results
            if solutions.get('theta') is not None and not (0 <= solutions['theta'] <= 180):
                raise InputValidationError("Angle must be between 0° and 180°")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in EMF induction calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving EMF induction: {str(e)}") from e

    def solve_transformer(self, **kwargs) -> Dict[str, float]:
        """
        Solves ideal transformer problems (Vp/Vs = Np/Ns, Ip/Is = Ns/Np)
        Possible variables: V_p, V_s, N_p, N_s, I_p, I_s
        """
        solutions = {k: kwargs.get(k, None) for k in ['V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Voltage ratio (Vp/Vs = Np/Ns)
                if solutions['V_s'] is None and all(solutions.get(k) is not None for k in ['V_p', 'N_p', 'N_s']):
                    if solutions['N_s'] <= 0:
                        raise PhysicsError("Secondary turns must be positive")
                    solutions['V_s'] = solutions['V_p'] * solutions['N_s'] / solutions['N_p']
                    changed = True
                        
                if solutions['V_p'] is None and all(solutions.get(k) is not None for k in ['V_s', 'N_p', 'N_s']):
                    if solutions['N_p'] <= 0:
                        raise PhysicsError("Primary turns must be positive")
                    solutions['V_p'] = solutions['V_s'] * solutions['N_p'] / solutions['N_s']
                    changed = True
                        
                if solutions['N_s'] is None and all(solutions.get(k) is not None for k in ['V_p', 'V_s', 'N_p']):
                    if solutions['V_s'] == 0:
                        raise PhysicsError("Secondary voltage cannot be zero")
                    if solutions['N_p'] <= 0:
                        raise PhysicsError("Primary turns must be positive")
                    solutions['N_s'] = solutions['N_p'] * solutions['V_s'] / solutions['V_p']
                    changed = True
                        
                if solutions['N_p'] is None and all(solutions.get(k) is not None for k in ['V_p', 'V_s', 'N_s']):
                    if solutions['V_p'] == 0:
                        raise PhysicsError("Primary voltage cannot be zero")
                    if solutions['N_s'] <= 0:
                        raise PhysicsError("Secondary turns must be positive")
                    solutions['N_p'] = solutions['N_s'] * solutions['V_p'] / solutions['V_s']
                    changed = True
                        
                # Current ratio (Ip/Is = Ns/Np)
                if solutions['I_s'] is None and all(solutions.get(k) is not None for k in ['I_p', 'N_p', 'N_s']):
                    if solutions['N_p'] <= 0:
                        raise PhysicsError("Primary turns must be positive")
                    solutions['I_s'] = solutions['I_p'] * solutions['N_p'] / solutions['N_s']
                    changed = True
                        
                if solutions['I_p'] is None and all(solutions.get(k) is not None for k in ['I_s', 'N_p', 'N_s']):
                    if solutions['N_s'] <= 0:
                        raise PhysicsError("Secondary turns must be positive")
                    solutions['I_p'] = solutions['I_s'] * solutions['N_s'] / solutions['N_p']
                    changed = True

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in transformer calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving transformer problem: {str(e)}") from e

    def solve_motor_torque(self, **kwargs) -> Dict[str, float]:
        """
        Solves motor torque problems (τ = nIABsinθ)
        Possible variables: torque, n, I, A, B, theta
        """
        solutions = {k: kwargs.get(k, None) for k in ['torque', 'n', 'I', 'A', 'B', 'theta']}
        
        try:
            self._validate_inputs({k: v for k, v in solutions.items() if v is not None})
            
            # Convert theta to radians if provided
            theta_rad = math.radians(solutions['theta']) if solutions['theta'] is not None else None
            
            changed = True
            iteration = 0
            max_iterations = 10
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # Main equation (τ = nIABsinθ)
                if solutions['torque'] is None and all(solutions.get(k) is not None for k in ['n', 'I', 'A', 'B', 'theta']):
                    if math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate torque when sinθ is zero")
                    solutions['torque'] = solutions['n'] * solutions['I'] * solutions['A'] * solutions['B'] * math.sin(theta_rad)
                    changed = True
                    
                # Solve for other variables
                if solutions['n'] is None and all(solutions.get(k) is not None for k in ['torque', 'I', 'A', 'B', 'theta']):
                    if solutions['I'] == 0 or solutions['A'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate turns when I, A, B or sinθ is zero")
                    solutions['n'] = solutions['torque'] / (solutions['I'] * solutions['A'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['I'] is None and all(solutions.get(k) is not None for k in ['torque', 'n', 'A', 'B', 'theta']):
                    if solutions['n'] == 0 or solutions['A'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate current when n, A, B or sinθ is zero")
                    solutions['I'] = solutions['torque'] / (solutions['n'] * solutions['A'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['A'] is None and all(solutions.get(k) is not None for k in ['torque', 'n', 'I', 'B', 'theta']):
                    if solutions['n'] == 0 or solutions['I'] == 0 or solutions['B'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate area when n, I, B or sinθ is zero")
                    solutions['A'] = solutions['torque'] / (solutions['n'] * solutions['I'] * solutions['B'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['B'] is None and all(solutions.get(k) is not None for k in ['torque', 'n', 'I', 'A', 'theta']):
                    if solutions['n'] == 0 or solutions['I'] == 0 or solutions['A'] == 0 or math.sin(theta_rad) == 0:
                        raise PhysicsError("Cannot calculate B when n, I, A or sinθ is zero")
                    solutions['B'] = solutions['torque'] / (solutions['n'] * solutions['I'] * solutions['A'] * math.sin(theta_rad))
                    changed = True
                        
                if solutions['theta'] is None and all(solutions.get(k) is not None for k in ['torque', 'n', 'I', 'A', 'B']):
                    try:
                        sin_theta = solutions['torque'] / (solutions['n'] * solutions['I'] * solutions['A'] * solutions['B'])
                        if abs(sin_theta) > 1:
                            raise PhysicsError("Invalid combination of values - |sinθ| cannot exceed 1")
                        theta_rad = math.asin(sin_theta)
                        solutions['theta'] = math.degrees(theta_rad)
                        changed = True
                    except ZeroDivisionError:
                        raise PhysicsError("Cannot calculate angle when n, I, A or B is zero")

            if iteration >= max_iterations:
                raise PhysicsError("Maximum iterations reached without convergence")
                
            # Validate results
            if solutions.get('theta') is not None and not (0 <= solutions['theta'] <= 180):
                raise InputValidationError("Angle must be between 0° and 180°")
                
            return {k: v for k, v in solutions.items() if v is not None}
            
        except ZeroDivisionError as e:
            raise PhysicsError("Division by zero occurred in motor torque calculations") from e
        except ValueError as e:
            raise PhysicsError(f"Invalid value encountered: {str(e)}") from e
        except Exception as e:
            raise PhysicsError(f"Error solving motor torque: {str(e)}") from e


# Convenience functions
def solve_lorentz_force(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_lorentz_force(**kwargs)

def solve_force_on_wire(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_force_on_wire(**kwargs)

def solve_parallel_wires(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_parallel_wires(**kwargs)

def solve_emf_induction(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_emf_induction(**kwargs)

def solve_transformer(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_transformer(**kwargs)

def solve_motor_torque(**kwargs) -> Dict[str, float]:
    solver = ElectromagnetismSolver()
    return solver.solve_motor_torque(**kwargs)