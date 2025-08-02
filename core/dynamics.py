import math
from typing import Dict, Optional, Union, List
from enum import Enum, auto

class PhysicsErrorType(Enum):
    INVALID_INPUT = auto()
    MISSING_REQUIRED = auto()
    DIVISION_BY_ZERO = auto()
    NEGATIVE_VALUE = auto()
    INVALID_RANGE = auto()
    PHYSICS_IMPOSSIBLE = auto()
    UNIT_CONVERSION = auto()

class PhysicsError(Exception):
    """Custom exception class for physics calculation errors"""
    def __init__(self, error_type: PhysicsErrorType, message: str, variable: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.variable = variable
        super().__init__(f"{message} (Variable: {variable})" if variable else message)

class DynamicsSolver:
    def __init__(self):
        self.g = 9.81  # Standard gravity (m/s²)
        self.solutions = {}
        self.equations = [
            self._solve_kinematics,
            self._solve_fma,
            self._solve_pmv,
            self._solve_impulse,
            self._solve_work_energy,
            self._solve_friction,
            self._solve_inclined_plane,
            self._solve_power
        ]

    def _validate_input(self, var: str, value: float) -> None:
        """Validate input values based on physics constraints"""
        if math.isnan(value) or math.isinf(value):
            raise PhysicsError(
                PhysicsErrorType.INVALID_INPUT,
                f"{var} cannot be NaN or infinite",
                var
            )

        # Variable-specific validation
        if var == 'mu' and (value < 0 or value > 5):
            raise PhysicsError(
                PhysicsErrorType.INVALID_RANGE,
                f"Coefficient of friction must be between 0 and 5 (got {value})",
                var
            )
        elif var == 'theta' and (value < 0 or value > 90):
            raise PhysicsError(
                PhysicsErrorType.INVALID_RANGE,
                f"Angle must be between 0° and 90° (got {value})",
                var
            )
        elif var in ['m', 't', 's'] and value < 0:
            raise PhysicsError(
                PhysicsErrorType.NEGATIVE_VALUE,
                f"{var} cannot be negative (got {value})",
                var
            )

    def solve(self, **kwargs) -> Dict[str, float]:
        """Main solver method with enhanced validation"""
        # Initialize solution dictionary
        self.solutions = {
            'm': None, 't': None, 'a': None, 'v0': None, 'vf': None, 's': None,
            'F': None, 'p': None, 'impulse': None, 'W': None, 'KE': None,
            'PE': None, 'theta': None, 'mu': None, 'FN': None, 'Ffriction': None,
            'Fnormal': None, 'Fparallel': None, 'P': None
        }

        # Validate and set input values
        for var, value in kwargs.items():
            if var not in self.solutions:
                raise PhysicsError(
                    PhysicsErrorType.INVALID_INPUT,
                    f"Unknown variable '{var}' provided",
                    var
                )
            if value is None:
                continue  # skip unset inputs
            try:
                float_value = float(value)
                self._validate_input(var, float_value)
                self.solutions[var] = float_value
            except ValueError as e:
                raise PhysicsError(
                    PhysicsErrorType.INVALID_INPUT,
                    f"Invalid value for {var}: must be a number",
                    var
                ) from e

        # Iteratively solve equations
        changed = True
        iterations = 0
        max_iterations = 20
        
        while changed and iterations < max_iterations:
            changed = False
            for equation in self.equations:
                try:
                    changed |= equation()
                except ZeroDivisionError as e:
                    raise PhysicsError(
                        PhysicsErrorType.DIVISION_BY_ZERO,
                        f"Division by zero in {equation.__name__}",
                        None
                    ) from e
            iterations += 1

        if iterations >= max_iterations:
            raise PhysicsError(
                PhysicsErrorType.PHYSICS_IMPOSSIBLE,
                "Maximum iterations reached without convergence"
            )

        return {k: v for k, v in self.solutions.items() if v is not None}

    def _solve_kinematics(self) -> bool:
        c = self.solutions
        changed = False

        # v = v0 + a*t
        if c['v0'] is not None and c['a'] is not None and c['t'] is not None and c['vf'] is None:
            c['vf'] = c['v0'] + c['a'] * c['t']
            changed = True
        
        # s = v0*t + 0.5*a*t²
        if c['v0'] is not None and c['a'] is not None and c['t'] is not None and c['s'] is None:
            c['s'] = c['v0'] * c['t'] + 0.5 * c['a'] * c['t']**2
            changed = True
            
        # vf² = v0² + 2*a*s
        if c['v0'] is not None and c['a'] is not None and c['s'] is not None and c['vf'] is None:
            try:
                c['vf'] = math.sqrt(c['v0']**2 + 2 * c['a'] * c['s'])
                changed = True
            except ValueError:
                raise PhysicsError(
                    PhysicsErrorType.PHYSICS_IMPOSSIBLE,
                    "Impossible kinematics combination (negative square root)"
                )

        return changed

    def _solve_fma(self) -> bool:
        c = self.solutions
        changed = False
        
        # F = m*a
        if c['m'] is not None and c['a'] is not None and c['F'] is None:
            c['F'] = c['m'] * c['a']
            changed = True
            
        # a = F/m
        if c['F'] is not None and c['m'] is not None and c['m'] != 0 and c['a'] is None:
            c['a'] = c['F'] / c['m']
            changed = True
            
        # m = F/a
        if c['F'] is not None and c['a'] is not None and c['a'] != 0 and c['m'] is None:
            c['m'] = c['F'] / c['a']
            changed = True
            
        return changed

    def _solve_pmv(self) -> bool:
        c = self.solutions
        changed = False
        
        # p = m*v
        if c['m'] is not None and c['vf'] is not None and c['p'] is None:
            c['p'] = c['m'] * c['vf']
            changed = True
            
        # m = p/v
        if c['p'] is not None and c['vf'] is not None and c['vf'] != 0 and c['m'] is None:
            c['m'] = c['p'] / c['vf']
            changed = True
            
        # v = p/m
        if c['p'] is not None and c['m'] is not None and c['m'] != 0 and c['vf'] is None:
            c['vf'] = c['p'] / c['m']
            changed = True
            
        return changed

    def _solve_impulse(self) -> bool:
        c = self.solutions
        changed = False
        
        # impulse = F*t
        if c['F'] is not None and c['t'] is not None and c['impulse'] is None:
            c['impulse'] = c['F'] * c['t']
            changed = True
            
        # impulse = m*Δv
        if c['m'] is not None and c['v0'] is not None and c['vf'] is not None and c['impulse'] is None:
            c['impulse'] = c['m'] * (c['vf'] - c['v0'])
            changed = True
            
        return changed

    def _solve_work_energy(self) -> bool:
        c = self.solutions
        changed = False
        
        # W = F*s*cosθ
        if c['F'] is not None and c['s'] is not None and c['W'] is None:
            theta_rad = math.radians(c['theta']) if c['theta'] is not None else 0
            c['W'] = c['F'] * c['s'] * math.cos(theta_rad)
            changed = True
            
        # KE = 0.5*m*v²
        if c['m'] is not None and c['vf'] is not None and c['KE'] is None:
            c['KE'] = 0.5 * c['m'] * c['vf']**2
            changed = True
            
        return changed

    def _solve_friction(self) -> bool:
        c = self.solutions
        changed = False
        
        # Ffriction = μ*FN
        if c['mu'] is not None and c['FN'] is not None and c['Ffriction'] is None:
            c['Ffriction'] = c['mu'] * c['FN']
            changed = True
            
        # FN = m*g (if on flat surface)
        if c['m'] is not None and c['FN'] is None and c['theta'] is None:
            c['FN'] = c['m'] * self.g
            changed = True
            
        return changed

    def _solve_inclined_plane(self) -> bool:
        c = self.solutions
        changed = False
        
        if c['m'] is not None and c['theta'] is not None:
            theta_rad = math.radians(c['theta'])
            
            # Fnormal = m*g*cosθ
            if c['Fnormal'] is None:
                c['Fnormal'] = c['m'] * self.g * math.cos(theta_rad)
                changed = True
                
            # Fparallel = m*g*sinθ
            if c['Fparallel'] is None:
                c['Fparallel'] = c['m'] * self.g * math.sin(theta_rad)
                changed = True
                
        return changed

    def _solve_power(self) -> bool:
        c = self.solutions
        changed = False
        
        # P = W/t
        if c['W'] is not None and c['t'] is not None and c['t'] != 0 and c['P'] is None:
            c['P'] = c['W'] / c['t']
            changed = True
            
        return changed

def solve_dynamics(**kwargs) -> Dict[str, float]:
    """Public interface for solving dynamics problems"""
    solver = DynamicsSolver()
    return solver.solve(**kwargs)