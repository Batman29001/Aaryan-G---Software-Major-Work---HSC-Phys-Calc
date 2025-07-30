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
    def __init__(self, error_type: KinematicsErrorType, message: str, variable: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.variable = variable
        super().__init__(f"{message} (Variable: {variable})" if variable else message)

def solve_kinematics(
    u: Optional[float] = None,
    v: Optional[float] = None,
    a: Optional[float] = None,
    s: Optional[float] = None,
    t: Optional[float] = None,
    units: Optional[Dict[str, str]] = None
) -> Dict[str, Union[float, Tuple[float, float], None]]:
    CONVERSIONS = {
        'm/s': 1.0, 'km/h': 1/3.6, 'ft/s': 0.3048,
        'm/s²': 1.0, 'ft/s²': 0.3048,
        'm': 1.0, 'km': 1000.0, 'ft': 0.3048,
        's': 1.0, 'min': 60.0, 'h': 3600.0
    }

    def validate_input(var: str, value: float) -> None:
        if math.isnan(value) or math.isinf(value):
            raise KinematicsError(KinematicsErrorType.INVALID_INPUT, f"{var} cannot be NaN or infinite", var)
        if var == 't' and value < 0:
            raise KinematicsError(KinematicsErrorType.NEGATIVE_VALUE, f"Time cannot be negative", var)
        if var == 'a' and abs(value) > 1e6:
            raise KinematicsError(KinematicsErrorType.INVALID_RANGE, f"Unrealistic acceleration", var)
        if var in ['u', 'v'] and abs(value) > 3e8:
            raise KinematicsError(KinematicsErrorType.PHYSICS_IMPOSSIBLE, "Velocity exceeds speed of light", var)

    solutions = {'u': None, 'v': None, 'a': None, 's': None, 't': None}
    input_values = {'u': u, 'v': v, 'a': a, 's': s, 't': t}

    for var, value in input_values.items():
        if value is not None:
            try:
                float_value = float(value)
                validate_input(var, float_value)
                if units and var in units:
                    if units[var] not in CONVERSIONS:
                        raise KinematicsError(KinematicsErrorType.UNIT_CONVERSION, f"Unknown unit '{units[var]}'", var)
                    float_value *= CONVERSIONS[units[var]]
                solutions[var] = float_value
            except ValueError as e:
                raise KinematicsError(KinematicsErrorType.INVALID_INPUT, f"Invalid value for {var}", var) from e

    known = {k: v for k, v in solutions.items() if v is not None}

    def try_update(var: str, value: Union[float, Tuple[float, float]]) -> bool:
        if solutions[var] is None and value is not None:
            solutions[var] = value
            known[var] = value
            return True
        return False

    max_iterations = 20
    for _ in range(max_iterations):
        progress = False

        if all(k in known for k in ['u', 'a', 't']):
            progress |= try_update('v', known['u'] + known['a'] * known['t'])
            progress |= try_update('s', known['u'] * known['t'] + 0.5 * known['a'] * known['t']**2)

        if all(k in known for k in ['u', 'a', 's']) and 'v' not in known:
            discriminant = known['u']**2 + 2 * known['a'] * known['s']
            if discriminant >= 0:
                root = math.sqrt(discriminant)
                try_update('v', (known['u'] + root, known['u'] - root) if known['a'] != 0 else known['u'])
            else:
                raise KinematicsError(KinematicsErrorType.PHYSICS_IMPOSSIBLE, "No real solution exists for v² = u² + 2as")

        if all(k in known for k in ['v', 'u', 'a']) and 't' not in known:
            if known['a'] == 0:
                raise KinematicsError(KinematicsErrorType.DIVISION_BY_ZERO, "Acceleration cannot be zero when calculating time")
            progress |= try_update('t', (known['v'] - known['u']) / known['a'])

        if all(k in known for k in ['u', 'v', 't']):
            progress |= try_update('s', 0.5 * (known['u'] + known['v']) * known['t'])

        # Add: a = (v - u)/t
        if all(k in known for k in ['v', 'u', 't']) and 'a' not in known:
            if known['t'] == 0:
                raise KinematicsError(KinematicsErrorType.DIVISION_BY_ZERO, "Time cannot be zero when calculating acceleration")
            progress |= try_update('a', (known['v'] - known['u']) / known['t'])

        if not progress:
            break

    return solutions
