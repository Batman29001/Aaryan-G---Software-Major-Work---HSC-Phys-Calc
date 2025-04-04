def solve_kinematics(u=None, v=None, a=None, s=None, t=None):
    """
    Solves kinematics equations for missing variables.
    Returns: Dictionary with keys 'u', 'v', 'a', 's', 't' containing:
             - Single float value when uniquely determined
             - None when cannot be determined
    """
    known_vars = {k: v for k, v in locals().items() if v is not None and k != 'known_vars'}
    solutions = {'u': None, 'v': None, 'a': None, 's': None, 't': None}
    
    while True:
        missing = [k for k in ['u', 'v', 'a', 's', 't'] if k not in known_vars]
        if not missing:
            break

        initial_count = len(known_vars)
        
        # Equation 1: v = u + a*t
        if 'v' not in known_vars and all(k in known_vars for k in ['u', 'a', 't']):
            known_vars['v'] = known_vars['u'] + known_vars['a'] * known_vars['t']
            
        # Equation 2: u = v - a*t
        elif 'u' not in known_vars and all(k in known_vars for k in ['v', 'a', 't']):
            known_vars['u'] = known_vars['v'] - known_vars['a'] * known_vars['t']
            
        # Equation 3: a = (v - u)/t
        elif 'a' not in known_vars and all(k in known_vars for k in ['v', 'u', 't']):
            known_vars['a'] = (known_vars['v'] - known_vars['u']) / known_vars['t']
            
        # Equation 4: t = (v - u)/a
        elif 't' not in known_vars and all(k in known_vars for k in ['v', 'u', 'a']):
            known_vars['t'] = (known_vars['v'] - known_vars['u']) / known_vars['a']
            
        # Equation 5: s = ((u + v)/2) * t
        elif 's' not in known_vars and all(k in known_vars for k in ['u', 'v', 't']):
            known_vars['s'] = ((known_vars['u'] + known_vars['v']) / 2) * known_vars['t']
            
        # Equation 6: s = u*t + 0.5*a*t²
        elif 's' not in known_vars and all(k in known_vars for k in ['u', 'a', 't']):
            known_vars['s'] = known_vars['u'] * known_vars['t'] + 0.5 * known_vars['a'] * (known_vars['t'] ** 2)
            
        # Equation 7: v² = u² + 2*a*s
        elif 'v' not in known_vars and all(k in known_vars for k in ['u', 'a', 's']):
            known_vars['v'] = (known_vars['u'] ** 2 + 2 * known_vars['a'] * known_vars['s']) ** 0.5
            
        elif 'u' not in known_vars and all(k in known_vars for k in ['v', 'a', 's']):
            known_vars['u'] = (known_vars['v'] ** 2 - 2 * known_vars['a'] * known_vars['s']) ** 0.5
            
        # Equation 8: a = (v² - u²) / (2*s)
        elif 'a' not in known_vars and all(k in known_vars for k in ['v', 'u', 's']):
            known_vars['a'] = (known_vars['v'] ** 2 - known_vars['u'] ** 2) / (2 * known_vars['s'])
            
        # Equation 9: Quadratic solution for t when s, u, a known
        elif 't' not in known_vars and all(k in known_vars for k in ['u', 'a', 's']):
            a = known_vars['a']
            u = known_vars['u']
            s = known_vars['s']
            discriminant = u**2 + 2 * a * s
            
            if discriminant >= 0:
                t1 = (-u + discriminant ** 0.5) / a
                t2 = (-u - discriminant ** 0.5) / a
                # Select only positive time solutions
                valid_times = [t for t in [t1, t2] if t >= 0]
                if valid_times:
                    known_vars['t'] = valid_times[0]  # Take first valid solution
        
        # Equation 10: t = 2s / (u + v)
        elif 't' not in known_vars and all(k in known_vars for k in ['u', 'v', 's']):
            known_vars['t'] = (2 * known_vars['s']) / (known_vars['u'] + known_vars['v'])
        
        if len(known_vars) == initial_count:
            break

    # Prepare final result
    for var in ['u', 'v', 'a', 's', 't']:
        solutions[var] = known_vars.get(var)
    
    return solutions