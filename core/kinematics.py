from typing import Dict, Optional, Union, Tuple
from enum import Enum, auto
import math

class KinematicsErrorType(Enum):
    INVALID_INPUT = auto()
    MISSING_REQUIRED = auto()
    DIVISION_BY_ZERO = auto()
    NEGATIVE_VALUE = auto()
    INVALID_RANGE = auto()
    PHYSICS_IMPOSSIBLE = auto()
    UNIT_CONVERSION = auto()

class KinematicsError(Exception):
    """Custom exception class for kinematics calculation errors"""
    def __init__(self, error_type: KinematicsErrorType, message: str, variable: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.variable = variable
        super().__init__(f"{message} (Variable: {variable})" if variable else message)

def solve_kinematics(u: Optional[float] = None, 
                    v: Optional[float] = None, 
                    a: Optional[float] = None, 
                    s: Optional[float] = None, 
                    t: Optional[float] = None,
                    units: Optional[Dict[str, str]] = None) -> Dict[str, Union[float, Tuple[float, float], None]]:
    """
    Solves kinematic equations with comprehensive error handling.
    
    Args:
        u: Initial velocity (m/s)
        v: Final velocity (m/s)
        a: Acceleration (m/s²)
        s: Displacement (m)
        t: Time (s)
        units: Dictionary specifying input units (e.g., {'u':'km/h', 'a':'ft/s²'})
    
    Returns:
        Dictionary with solutions for all kinematic variables
        
    Raises:
        KinematicsError: For invalid inputs or physics violations
    """
    # Conversion factors to SI units
    CONVERSIONS = {
        'm/s': 1.0,
        'km/h': 1/3.6,
        'ft/s': 0.3048,
        'm/s²': 1.0,
        'ft/s²': 0.3048,
        'm': 1.0,
        'km': 1000.0,
        'ft': 0.3048,
        's': 1.0,
        'min': 60.0,
        'h': 3600.0
    }

    def validate_input(var: str, value: float) -> None:
        """Validate input values based on physics constraints"""
        if math.isnan(value) or math.isinf(value):
            raise KinematicsError(
                KinematicsErrorType.INVALID_INPUT,
                f"{var} cannot be NaN or infinite",
                var
            )
        if var == 't' and value < 0:
            raise KinematicsError(
                KinematicsErrorType.NEGATIVE_VALUE,
                f"Time cannot be negative (got {value})",
                var
            )
        if var == 'a' and abs(value) > 1e6:  # 100,000g limit
            raise KinematicsError(
                KinematicsErrorType.INVALID_RANGE,
                f"Unrealistic acceleration (>{1e6} m/s²)",
                var
            )
        if var in ['u', 'v'] and abs(value) > 3e8:  # Speed of light
            raise KinematicsError(
                KinematicsErrorType.PHYSICS_IMPOSSIBLE,
                "Velocity exceeds speed of light",
                var
            )

    # Initialize solutions
    solutions = {'u': None, 'v': None, 'a': None, 's': None, 't': None}
    input_values = {'u': u, 'v': v, 'a': a, 's': s, 't': t}

    # Validate and convert inputs
    for var, value in input_values.items():
        if value is not None:
            try:
                float_value = float(value)
                validate_input(var, float_value)
                
                # Convert units if specified
                if units and var in units:
                    if units[var] not in CONVERSIONS:
                        raise KinematicsError(
                            KinematicsErrorType.UNIT_CONVERSION,
                            f"Unknown unit '{units[var]}'",
                            var
                        )
                    float_value *= CONVERSIONS[units[var]]
                
                solutions[var] = float_value
            except ValueError as e:
                raise KinematicsError(
                    KinematicsErrorType.INVALID_INPUT,
                    f"Invalid value for {var}",
                    var
                ) from e

    # Main solving logic
    known = {k: v for k, v in solutions.items() if v is not None}
    
    def try_update(var: str, value: Union[float, Tuple[float, float]]) -> bool:
        """Helper function to update solutions"""
        if var not in known and value is not None:
            if isinstance(value, (list, tuple)):
                solutions[var] = tuple(value)
            else:
                known[var] = solutions[var] = value
            return True
        return False

    # Iterative solver
    max_iterations = 20
    for _ in range(max_iterations):
        progress = False

        # Equation 1: v = u + a*t
        if all(k in known for k in ['u', 'a', 't']):
            progress |= try_update('v', known['u'] + known['a'] * known['t'])

        # Equation 2: s = u*t + 0.5*a*t²
        if all(k in known for k in ['u', 'a', 't']):
            progress |= try_update('s', known['u'] * known['t'] + 0.5 * known['a'] * known['t']**2)

        # Equation 3: v² = u² + 2*a*s
        if 'v' not in known and all(k in known for k in ['u', 'a', 's']):
            discriminant = known['u']**2 + 2 * known['a'] * known['s']
            if discriminant >= 0:
                root = math.sqrt(discriminant)
                progress |= try_update('v', (known['u'] + root, known['u'] - root) if known['a'] != 0 else known['u'])
            else:
                raise KinematicsError(
                    KinematicsErrorType.PHYSICS_IMPOSSIBLE,
                    "No real solution exists for v² = u² + 2as"
                )

        # Equation 4: t = (v - u)/a
        if 't' not in known and all(k in known for k in ['v', 'u', 'a']):
            if known['a'] == 0:
                raise KinematicsError(
                    KinematicsErrorType.DIVISION_BY_ZERO,
                    "Acceleration cannot be zero when calculating time"
                )
            progress |= try_update('t', (known['v'] - known['u']) / known['a'])

        # Equation 5: s = (u + v)/2 * t
        if 's' not in known and all(k in known for k in ['u', 'v', 't']):
            progress |= try_update('s', 0.5 * (known['u'] + known['v']) * known['t'])

        if not progress:
            break
    else:
        raise KinematicsError(
            KinematicsErrorType.PHYSICS_IMPOSSIBLE,
            "Maximum iterations reached without convergence"
        )

    # Verify minimum required variables
    if len(known) < 3:
        missing = [k for k in ['u', 'v', 'a', 's', 't'] if k not in known]
        raise KinematicsError(
            KinematicsErrorType.MISSING_REQUIRED,
            f"Need at least 3 known variables (missing: {', '.join(missing)})"
        )

    return solutions