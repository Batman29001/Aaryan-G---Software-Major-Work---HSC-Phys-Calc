import math
from typing import Dict, Optional

class WaveSolver:
    def __init__(self):
        self.speed_of_sound = 343  # m/s at 20°C
        self.speed_of_light = 3e8  # m/s
        self.solutions = {}
        
        # Ordered by dependency
        self.equations = [
            self._solve_wave_properties,
            self._solve_sound_waves,
            self._solve_light_properties
        ]
    
    def solve(self, category: str, **kwargs) -> Dict[str, float]:
        """Main solver that handles all wave calculations"""
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
        
        # Set provided values
        for k, v in kwargs.items():
            if k in self.solutions:
                self.solutions[k] = v
        
        # Keep solving until no more progress can be made
        changed = True
        while changed:
            changed = False
            for equation in self.equations:
                if equation.__name__ == f"_solve_{category}":
                    changed |= equation()
        
        # Return only calculated values (remove None values)
        return {k: v for k, v in self.solutions.items() if v is not None}
    
    def _solve_wave_properties(self) -> bool:
        """Solve wave property equations"""
        changed = False
        
        # v = λf
        if self.solutions['v'] is None:
            if self.solutions['λ'] is not None and self.solutions['f'] is not None:
                self.solutions['v'] = self.solutions['λ'] * self.solutions['f']
                changed = True
        
        if self.solutions['λ'] is None:
            if self.solutions['v'] is not None and self.solutions['f'] is not None:
                self.solutions['λ'] = self.solutions['v'] / self.solutions['f']
                changed = True
        
        if self.solutions['f'] is None:
            if self.solutions['v'] is not None and self.solutions['λ'] is not None:
                self.solutions['f'] = self.solutions['v'] / self.solutions['λ']
                changed = True
        
        # T = 1/f
        if self.solutions['T'] is None and self.solutions['f'] is not None:
            self.solutions['T'] = 1 / self.solutions['f']
            changed = True
        
        if self.solutions['f'] is None and self.solutions['T'] is not None:
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
            self.solutions['k'] = 2 * math.pi / self.solutions['λ']
            changed = True
        
        if self.solutions['λ'] is None and self.solutions['k'] is not None:
            self.solutions['λ'] = 2 * math.pi / self.solutions['k']
            changed = True
        
        return changed
    
    def _solve_sound_waves(self) -> bool:
        """Solve sound wave equations including Doppler effect"""
        changed = False
        
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
        
        # 1. Calculate f_observed if possible (existing logic)
        if f_observed is None:
            if f_source is not None and v_medium is not None:
                # Source moving directly toward observer
                if v_source is not None and (θ_source is None or math.isclose(θ_source, 0, abs_tol=1e-6)):
                    self.solutions['f_observed'] = (v_medium / (v_medium - v_source)) * f_source
                    changed = True
                
                # Observer moving directly toward source
                elif v_observer is not None and (θ_observer is None or math.isclose(θ_observer, 0, abs_tol=1e-6)):
                    self.solutions['f_observed'] = ((v_medium + v_observer) / v_medium) * f_source
                    changed = True
                
                # General case with angles
                elif v_source is not None and θ_source is not None:
                    self.solutions['f_observed'] = (
                        (v_medium / (v_medium - v_source * math.cos(math.radians(θ_source)))) * f_source
                    )
                    changed = True
        
        # 2. Calculate v_source if possible (reverse Doppler)
        if v_source is None:
            # Only handle head-on approach θ_source = 0 or None for simplicity
            if (f_observed is not None and f_source is not None and v_medium is not None and
                (θ_source is None or math.isclose(θ_source, 0, abs_tol=1e-6))):
                candidate_v_source = v_medium * (1 - f_source / f_observed)
                if abs(candidate_v_source) < 1.5 * v_medium:  # sanity check
                    self.solutions['v_source'] = candidate_v_source
                    changed = True
        
        # 3. Calculate v_observer if possible (reverse Doppler)
        if v_observer is None:
            # Only handle head-on approach θ_observer = 0 or None
            if (f_observed is not None and f_source is not None and v_medium is not None and
                (θ_observer is None or math.isclose(θ_observer, 0, abs_tol=1e-6))):
                candidate_v_observer = v_medium * (f_observed / f_source - 1)
                if abs(candidate_v_observer) < 1.5 * v_medium:  # sanity check
                    self.solutions['v_observer'] = candidate_v_observer
                    changed = True
        
        return changed
    
    def _solve_light_properties(self) -> bool:
        """Solve light wave equations including Snell's law and intensity"""
        changed = False
        
        # Snell's law: n1 sinθ1 = n2 sinθ2
        if self.solutions['θ2'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                 for k in ['n1', 'n2', 'θ1']):
                
                n1, n2, θ1 = self.solutions['n1'], self.solutions['n2'], self.solutions['θ1']
                sinθ2 = (n1 * math.sin(math.radians(θ1))) / n2
                
                if abs(sinθ2) <= 1:  # Check for total internal reflection
                    self.solutions['θ2'] = math.degrees(math.asin(sinθ2))
                    changed = True
        
        if self.solutions['θ1'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                 for k in ['n1', 'n2', 'θ2']):
                
                n1, n2, θ2 = self.solutions['n1'], self.solutions['n2'], self.solutions['θ2']
                sinθ1 = (n2 * math.sin(math.radians(θ2))) / n1
                
                if abs(sinθ1) <= 1:
                    self.solutions['θ1'] = math.degrees(math.asin(sinθ1))
                    changed = True
        
        # Intensity ratio: I1/I2 = (n1/n2) for transmitted light
        if self.solutions['I2'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                 for k in ['I1', 'n1', 'n2']):
                
                self.solutions['I2'] = self.solutions['I1'] * (self.solutions['n2'] / self.solutions['n1'])
                changed = True
        
        if self.solutions['I1'] is None:
            if all(k in self.solutions and self.solutions[k] is not None 
                 for k in ['I2', 'n1', 'n2']):
                
                self.solutions['I1'] = self.solutions['I2'] * (self.solutions['n1'] / self.solutions['n2'])
                changed = True
        
        return changed

def solve_wave_properties(**kwargs) -> Dict[str, float]:
    """Convenience function for wave properties"""
    solver = WaveSolver()
    return solver.solve('wave_properties', **kwargs)

def solve_sound_waves(**kwargs) -> Dict[str, float]:
    """Convenience function for sound waves"""
    solver = WaveSolver()
    return solver.solve('sound_waves', **kwargs)

def solve_light_properties(**kwargs) -> Dict[str, float]:
    """Convenience function for light properties"""
    solver = WaveSolver()
    return solver.solve('light_properties', **kwargs)
