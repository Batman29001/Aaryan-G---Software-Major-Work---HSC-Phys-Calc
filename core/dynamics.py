def get_input(var2_name):
    value = input(f"Enter {var2_name} (leave blank if unknown): ")
    try:
        return float(value) if value.strip() else None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return get_input(var2_name)


