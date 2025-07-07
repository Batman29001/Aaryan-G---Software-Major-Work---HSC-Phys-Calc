def solve_kinematics(u=None, v=None, a=None, s=None, t=None):
    """
    units: Dict specifying input units (e.g., {'u':'km/h', 'a':'ft/s²'})
    """
    # Conversion factors to SI
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

    # Convert inputs to SI units first
    if units:
        for var in ['u', 'v', 'a', 's', 't']:
            if locals()[var] is not None and units.get(var):
                try:
                    locals()[var] *= CONVERSIONS[units[var]]
                except KeyError:
                    pass
    
    """
    Solves for ALL possible kinematic variables given any valid input combination.
    Returns: Dict with keys 'u', 'v', 'a', 's', 't' (floats, lists for ± solutions, or None).
    Guaranteed to find every possible solution.
    """
    # Initialize with input values (ignore None)
    known = {k: v for k, v in locals().items() if v is not None and k != 'known'}
    solutions = {'u': None, 'v': None, 'a': None, 's': None, 't': None}

    def try_update(var, value):
        """Update known/solutions if new value is valid and not already known."""
        if var not in known and value is not None:
            if isinstance(value, (list, tuple)):
                solutions[var] = value
            else:
                known[var] = solutions[var] = value
            return True
        return False

    # Loop until no more variables can be found
    while True:
        progress = False

        # --- Equation 1: v = u + a*t ---
        if all(k in known for k in ['u', 'a', 't']):
            progress |= try_update('v', known['u'] + known['a'] * known['t'])

        # --- Equation 2: u = v - a*t ---
        if all(k in known for k in ['v', 'a', 't']):
            progress |= try_update('u', known['v'] - known['a'] * known['t'])

        # --- Equation 3: a = (v - u)/t ---
        if all(k in known for k in ['v', 'u', 't']) and known['t'] != 0:
            progress |= try_update('a', (known['v'] - known['u']) / known['t'])

        # --- Equation 4: t = (v - u)/a ---
        if all(k in known for k in ['v', 'u', 'a']) and known['a'] != 0:
            progress |= try_update('t', (known['v'] - known['u']) / known['a'])

        # --- Equation 5: s = (u + v)/2 * t ---
        if all(k in known for k in ['u', 'v', 't']):
            progress |= try_update('s', 0.5 * (known['u'] + known['v']) * known['t'])

        # --- Equation 6: s = u*t + 0.5*a*t² ---
        if all(k in known for k in ['u', 'a', 't']):
            progress |= try_update('s', known['u'] * known['t'] + 0.5 * known['a'] * known['t']**2)

        # --- Equation 7: v² = u² + 2*a*s (solve for v or u) ---
        if 'v' not in known and all(k in known for k in ['u', 'a', 's']):
            discriminant = known['u']**2 + 2 * known['a'] * known['s']
            if discriminant >= 0:
                root = discriminant**0.5
                progress |= try_update('v', [known['u'] + root, known['u'] - root] if known['a'] != 0 else known['u'])

        if 'u' not in known and all(k in known for k in ['v', 'a', 's']):
            discriminant = known['v']**2 - 2 * known['a'] * known['s']
            if discriminant >= 0:
                root = discriminant**0.5
                progress |= try_update('u', [known['v'] - root, known['v'] + root] if known['a'] != 0 else known['v'])

        # --- Equation 8: a = (v² - u²)/(2*s) ---
        if 'a' not in known and all(k in known for k in ['v', 'u', 's']) and known['s'] != 0:
            progress |= try_update('a', (known['v']**2 - known['u']**2) / (2 * known['s']))

        # --- Equation 9: Quadratic solution for t (s = u*t + 0.5*a*t²) ---
        if 't' not in known and all(k in known for k in ['u', 'a', 's']):
            a, u, s = known['a'], known['u'], known['s']
            if a != 0:
                discriminant = u**2 + 2 * a * s
                if discriminant >= 0:
                    t1 = (-u + discriminant**0.5) / a
                    t2 = (-u - discriminant**0.5) / a
                    valid_times = [t for t in [t1, t2] if t >= 0]
                    if valid_times:
                        progress |= try_update('t', valid_times[0] if len(valid_times) == 1 else valid_times)
            else:  # a=0 (constant velocity)
                if u != 0:
                    progress |= try_update('t', s / u)

        # --- Equation 10: t = 2*s / (u + v) ---
        if 't' not in known and all(k in known for k in ['u', 'v', 's']):
            denominator = known['u'] + known['v']
            if denominator != 0:
                progress |= try_update('t', (2 * known['s']) / denominator)

        # --- Early exit if no progress ---
        if not progress:
            break

    return solutions