import math
from typing import Dict

class AdvancedMechanicsSolver:
    def __init__(self):
        self.g = 9.81  # m/s² (standard gravity)
        self.G = 6.67430e-11  # universal gravitational constant (m³ kg⁻¹ s⁻²)

    def solve_projectile_motion(self, **kwargs) -> Dict[str, float]:
        """Solve projectile motion problems, maximizing variable derivation"""
        solutions = {
            'u': None, 'θ': None, 'ux': None, 'uy': None,
            't_flight': None, 'max_height': None, 'range': None
        }

        # Set provided values
        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v

        # Convert angle to radians if provided (and not already converted)
        if solutions['θ'] is not None and solutions['θ'] > 2 * math.pi:
            solutions['θ'] = math.radians(solutions['θ'])

        changed = True
        while changed:
            changed = False

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
                    solutions['u'] = math.sqrt(solutions['ux']**2 + solutions['uy']**2)
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

        # Convert angle back to degrees if it was input as degrees
        if solutions['θ'] is not None:
            solutions['θ'] = math.degrees(solutions['θ'])

        return {k: v for k, v in solutions.items() if v is not None}

    def solve_circular_motion(self, **kwargs) -> Dict[str, float]:
        """Solve uniform circular motion problems with max variable derivation"""
        solutions = {
            'v': None, 'r': None, 'T': None, 'f': None,
            'ω': None, 'a_c': None, 'F_c': None, 'm': None
        }

        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v

        changed = True
        while changed:
            changed = False

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

        return {k: v for k, v in solutions.items() if v is not None}

    def solve_banked_tracks(self, **kwargs) -> Dict[str, float]:
        """Solve banked track problems with max variable derivation"""
        solutions = {
            'θ': None, 'v': None, 'r': None, 'μ': None,
            'v_min': None, 'v_max': None
        }

        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v

        # Convert angle to radians if provided (and not already)
        if solutions['θ'] is not None and solutions['θ'] > 2 * math.pi:
            solutions['θ'] = math.radians(solutions['θ'])

        changed = True
        while changed:
            changed = False

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

        # Convert angle back to degrees if it was input as degrees
        if solutions['θ'] is not None:
            solutions['θ'] = math.degrees(solutions['θ'])

        return {k: v for k, v in solutions.items() if v is not None}

    def solve_gravitation(self, **kwargs) -> Dict[str, float]:
        """Solve gravitation problems with max variable derivation"""
        solutions = {
            'M': None, 'm': None, 'r': None, 'F_g': None,
            'g': None, 'v_orbital': None, 'T': None, 'altitude': None
        }

        for k, v in kwargs.items():
            if k in solutions:
                solutions[k] = v

        earth_radius = 6.371e6  # meters

        changed = True
        while changed:
            changed = False

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
                solutions['altitude'] = solutions['r'] - earth_radius
                changed = True
            if solutions['r'] is None and solutions['altitude'] is not None:
                solutions['r'] = solutions['altitude'] + earth_radius
                changed = True

        return {k: v for k, v in solutions.items() if v is not None}


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
