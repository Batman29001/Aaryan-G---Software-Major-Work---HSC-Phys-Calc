import math
from typing import Dict

class PhysicsSolver:
    def __init__(self):
        self.g = 9.81
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

    def solve(self, **kwargs) -> Dict[str, float]:
        self.solutions = {
            'm': None, 't': None,
            'a': None, 'v0': None, 'vf': None, 's': None,
            'F': None, 'p': None, 'impulse': None,
            'W': None, 'KE': None, 'PE': None, 'theta': None,
            'mu': None, 'FN': None, 'Ffriction': None,
            'Fnormal': None, 'Fparallel': None,
            'v': None, 'P': None
        }

        for k, v in kwargs.items():
            if k in self.solutions:
                self.solutions[k] = v

        changed = True
        while changed:
            changed = False
            for equation in self.equations:
                changed |= equation()

        return {k: v for k, v in self.solutions.items() if v is not None}

    def _solve_kinematics(self) -> bool:
        c = self.solutions
        changed = False

        if c['t'] is not None:
            if c['a'] is not None:
                if c['v0'] is not None and c['vf'] is None:
                    c['vf'] = c['v0'] + c['a'] * c['t']
                    changed = True
                if c['vf'] is not None and c['v0'] is None:
                    c['v0'] = c['vf'] - c['a'] * c['t']
                    changed = True
                if c['v'] is None:
                    c['v'] = c['a'] * c['t']
                    changed = True

        if c['vf'] is not None and c['v0'] is not None and c['a'] is None and c['t'] is not None and c['t'] != 0:
            c['a'] = (c['vf'] - c['v0']) / c['t']
            changed = True

        if c['v0'] is not None and c['a'] is not None and c['vf'] is None and c['t'] is not None:
            c['vf'] = c['v0'] + c['a'] * c['t']
            changed = True

        if c['v0'] is not None and c['vf'] is not None and c['a'] is not None and c['t'] is None and c['a'] != 0:
            c['t'] = (c['vf'] - c['v0']) / c['a']
            changed = True

        if c['s'] is None:
            if c['v0'] is not None and c['a'] is not None and c['t'] is not None:
                c['s'] = c['v0'] * c['t'] + 0.5 * c['a'] * c['t']**2
                changed = True
            elif c['v0'] is not None and c['vf'] is not None and c['t'] is not None:
                c['s'] = 0.5 * (c['v0'] + c['vf']) * c['t']
                changed = True

        if c['vf'] is None and c['v0'] is not None and c['a'] is not None and c['s'] is not None:
            disc = c['v0']**2 + 2 * c['a'] * c['s']
            if disc >= 0:
                c['vf'] = math.sqrt(disc)
                changed = True

        if c['v0'] is None and c['vf'] is not None and c['a'] is not None and c['s'] is not None:
            disc = c['vf']**2 - 2 * c['a'] * c['s']
            if disc >= 0:
                c['v0'] = math.sqrt(disc)
                changed = True

        if c['a'] is None and c['vf'] is not None and c['v0'] is not None and c['s'] is not None and c['s'] != 0:
            c['a'] = (c['vf']**2 - c['v0']**2) / (2 * c['s'])
            changed = True

        if c['t'] is None and c['a'] is not None and c['v0'] is not None and c['s'] is not None:
            disc = c['v0']**2 + 2 * c['a'] * c['s']
            if disc >= 0:
                t1 = (-c['v0'] + math.sqrt(disc)) / c['a']
                t2 = (-c['v0'] - math.sqrt(disc)) / c['a']
                c['t'] = max(t for t in [t1, t2] if t >= 0)
                changed = True

        if c['t'] is None and c['v0'] is not None and c['vf'] is not None and c['s'] is not None:
            denom = c['v0'] + c['vf']
            if denom != 0:
                c['t'] = (2 * c['s']) / denom
                changed = True

        return changed

    def _solve_fma(self) -> bool:
        c = self.solutions
        changed = False

        if c['F'] is None and c['m'] is not None and c['a'] is not None:
            c['F'] = c['m'] * c['a']
            changed = True
        if c['a'] is None and c['F'] is not None and c['m'] is not None:
            c['a'] = c['F'] / c['m']
            changed = True
        if c['m'] is None and c['F'] is not None and c['a'] is not None and c['a'] != 0:
            c['m'] = c['F'] / c['a']
            changed = True

        return changed

    def _solve_pmv(self) -> bool:
        c = self.solutions
        changed = False

        if c['p'] is None and c['m'] is not None and c['vf'] is not None:
            c['p'] = c['m'] * c['vf']
            changed = True
        if c['m'] is None and c['p'] is not None and c['vf'] is not None and c['vf'] != 0:
            c['m'] = c['p'] / c['vf']
            changed = True
        if c['vf'] is None and c['p'] is not None and c['m'] is not None and c['m'] != 0:
            c['vf'] = c['p'] / c['m']
            changed = True

        return changed

    def _solve_impulse(self) -> bool:
        c = self.solutions
        changed = False

        if c['impulse'] is None:
            if c['F'] is not None and c['t'] is not None:
                c['impulse'] = c['F'] * c['t']
                changed = True
            elif c['m'] is not None and c['vf'] is not None and c['v0'] is not None:
                c['impulse'] = c['m'] * (c['vf'] - c['v0'])
                changed = True

        if c['F'] is None and c['impulse'] is not None and c['t'] is not None and c['t'] != 0:
            c['F'] = c['impulse'] / c['t']
            changed = True

        if c['t'] is None and c['impulse'] is not None and c['F'] is not None and c['F'] != 0:
            c['t'] = c['impulse'] / c['F']
            changed = True

        return changed

    def _solve_work_energy(self) -> bool:
        c = self.solutions
        changed = False

        if c['W'] is None and c['F'] is not None and c['s'] is not None:
            theta_rad = math.radians(c['theta']) if c['theta'] is not None else 0
            c['W'] = c['F'] * c['s'] * math.cos(theta_rad)
            changed = True

        if c['KE'] is None and c['m'] is not None and c['vf'] is not None:
            c['KE'] = 0.5 * c['m'] * c['vf']**2
            changed = True

        if c['vf'] is None and c['m'] is not None and c['KE'] is not None and c['m'] != 0:
            c['vf'] = math.sqrt(2 * c['KE'] / c['m'])
            changed = True

        if c['PE'] is None and c['m'] is not None and c['s'] is not None and c['theta'] is not None:
            c['PE'] = c['m'] * self.g * c['s'] * math.sin(math.radians(c['theta']))
            changed = True

        if c['m'] is None and c['KE'] is not None and c['vf'] is not None and c['vf'] != 0:
            c['m'] = (2 * c['KE']) / c['vf']**2
            changed = True

        if c['s'] is None and c['W'] is not None and c['F'] is not None and c['F'] != 0:
            theta_rad = math.radians(c['theta']) if c['theta'] is not None else 0
            denom = c['F'] * math.cos(theta_rad)
            if denom != 0:
                c['s'] = c['W'] / denom
                changed = True

        return changed

    def _solve_friction(self) -> bool:
        c = self.solutions
        changed = False

        if c['Ffriction'] is None and c['mu'] is not None and c['FN'] is not None:
            c['Ffriction'] = c['mu'] * c['FN']
            changed = True

        if c['FN'] is None and c['m'] is not None and c['theta'] is None:
            c['FN'] = c['m'] * self.g
            changed = True

        return changed

    def _solve_inclined_plane(self) -> bool:
        c = self.solutions
        changed = False

        if c['m'] is not None and c['theta'] is not None:
            theta_rad = math.radians(c['theta'])
            if c['Fnormal'] is None:
                c['Fnormal'] = c['m'] * self.g * math.cos(theta_rad)
                changed = True
            if c['Fparallel'] is None:
                c['Fparallel'] = c['m'] * self.g * math.sin(theta_rad)
                changed = True

        return changed

    def _solve_power(self) -> bool:
        c = self.solutions
        changed = False

        if c['P'] is None and c['W'] is not None and c['t'] is not None and c['t'] != 0:
            c['P'] = c['W'] / c['t']
            changed = True

        if c['W'] is None and c['P'] is not None and c['t'] is not None:
            c['W'] = c['P'] * c['t']
            changed = True

        if c['t'] is None and c['W'] is not None and c['P'] is not None and c['P'] != 0:
            c['t'] = c['W'] / c['P']
            changed = True

        return changed

def solve_dynamics(**kwargs) -> Dict[str, float]:
    solver = PhysicsSolver()
    return solver.solve(**kwargs)
