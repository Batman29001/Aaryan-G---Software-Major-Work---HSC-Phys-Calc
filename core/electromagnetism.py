import math
from typing import Dict, Optional


class ElectromagnetismSolver:
    def __init__(self):
        self.mu_0 = 4 * math.pi * 1e-7  # Permeability of free space (N/A²)
        self.epsilon_0 = 8.8541878128e-12  # Permittivity of free space (F/m)
        self.e_charge = 1.602176634e-19  # Elementary charge (C)

    def solve_charged_particles(self, **kwargs) -> Dict[str, float]:
        s = {k: kwargs.get(k, None) for k in [
            'E', 'V', 'd', 'q', 'F', 'B', 'v', 'theta', 'r', 'm', 'work', 'K', 'U'
        ]}
        changed = True
        while changed:
            changed = False

            if s['E'] is None and s['V'] is not None and s['d'] is not None:
                s['E'] = s['V'] / s['d']; changed = True
            if s['V'] is None and s['E'] is not None and s['d'] is not None:
                s['V'] = s['E'] * s['d']; changed = True
            if s['d'] is None and s['V'] is not None and s['E'] is not None:
                s['d'] = s['V'] / s['E']; changed = True

            if s['F'] is None and s['q'] is not None and s['E'] is not None:
                s['F'] = s['q'] * s['E']; changed = True
            if s['q'] is None and s['F'] is not None and s['E'] is not None:
                s['q'] = s['F'] / s['E']; changed = True
            if s['E'] is None and s['F'] is not None and s['q'] is not None:
                s['E'] = s['F'] / s['q']; changed = True

            if s['F'] is None and s['q'] is not None and s['v'] is not None and s['B'] is not None:
                theta = math.radians(s['theta'] or 0)
                s['F'] = s['q'] * s['v'] * s['B'] * math.sin(theta); changed = True

            if s['r'] is None and all(s.get(k) is not None for k in ['m', 'v', 'q', 'B']):
                s['r'] = s['m'] * s['v'] / (s['q'] * s['B']); changed = True

            if s['work'] is None and s['q'] is not None and s['V'] is not None:
                s['work'] = s['q'] * s['V']; changed = True
            if s['K'] is None and s['m'] is not None and s['v'] is not None:
                s['K'] = 0.5 * s['m'] * s['v'] ** 2; changed = True
            if s['v'] is None and s['K'] is not None and s['m'] is not None:
                s['v'] = math.sqrt(2 * s['K'] / s['m']); changed = True

        return {k: v for k, v in s.items() if v is not None}

    def solve_motor_effect(self, **kwargs) -> Dict[str, float]:
        s = {k: kwargs.get(k, None) for k in [
            'F', 'I', 'l', 'B', 'theta', 'F_per_length', 'I1', 'I2', 'r'
        ]}
        changed = True
        while changed:
            changed = False

            if s['F'] is None and all(s.get(k) is not None for k in ['I', 'l', 'B']):
                theta = math.radians(s['theta'] or 0)
                s['F'] = s['I'] * s['l'] * s['B'] * math.sin(theta); changed = True

            if s['F_per_length'] is None and all(s.get(k) is not None for k in ['I1', 'I2', 'r']):
                s['F_per_length'] = self.mu_0 * s['I1'] * s['I2'] / (2 * math.pi * s['r']); changed = True

        return {k: v for k, v in s.items() if v is not None}

    def solve_induction(self, **kwargs) -> Dict[str, float]:
        s = {k: kwargs.get(k, None) for k in [
            'emf', 'N', 'delta_phi', 'delta_t', 'B', 'A', 'theta', 'phi',
            'V_p', 'V_s', 'N_p', 'N_s', 'I_p', 'I_s'
        ]}
        changed = True
        while changed:
            changed = False

            if s['phi'] is None and s['B'] is not None and s['A'] is not None:
                theta = math.radians(s['theta'] or 0)
                s['phi'] = s['B'] * s['A'] * math.cos(theta); changed = True

            if s['emf'] is None and all(s.get(k) is not None for k in ['N', 'delta_phi', 'delta_t']):
                s['emf'] = -s['N'] * s['delta_phi'] / s['delta_t']; changed = True

            if s['V_s'] is None and all(s.get(k) is not None for k in ['V_p', 'N_s', 'N_p']):
                s['V_s'] = s['V_p'] * s['N_s'] / s['N_p']; changed = True
            if s['V_p'] is None and all(s.get(k) is not None for k in ['V_s', 'N_s', 'N_p']):
                s['V_p'] = s['V_s'] * s['N_p'] / s['N_s']; changed = True

            if s['I_s'] is None and all(s.get(k) is not None for k in ['I_p', 'N_p', 'N_s']):
                s['I_s'] = s['I_p'] * s['N_p'] / s['N_s']; changed = True
            if s['I_p'] is None and all(s.get(k) is not None for k in ['I_s', 'N_s', 'N_p']):
                s['I_p'] = s['I_s'] * s['N_s'] / s['N_p']; changed = True

        return {k: v for k, v in s.items() if v is not None}

    def solve_motor_applications(self, **kwargs) -> Dict[str, float]:
        s = {k: kwargs.get(k, None) for k in [
            'torque', 'n', 'I', 'A', 'B', 'theta', 'back_emf', 'omega', 'N', 'phi'
        ]}
        changed = True
        while changed:
            changed = False

            if s['torque'] is None and all(s.get(k) is not None for k in ['n', 'I', 'A', 'B']):
                theta = math.radians(s['theta'] or 0)
                s['torque'] = s['n'] * s['I'] * s['A'] * s['B'] * math.sin(theta); changed = True

            if s['back_emf'] is None and all(s.get(k) is not None for k in ['omega', 'N', 'phi']):
                s['back_emf'] = s['N'] * s['phi'] * s['omega']; changed = True

        return {k: v for k, v in s.items() if v is not None}


# Convenience functions
def solve_charged_particles(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_charged_particles(**kwargs)

def solve_motor_effect(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_motor_effect(**kwargs)

def solve_induction(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_induction(**kwargs)

def solve_motor_applications(**kwargs) -> Dict[str, float]:
    return ElectromagnetismSolver().solve_motor_applications(**kwargs)
