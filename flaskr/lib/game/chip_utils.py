def get_value(chip: str):
    """
    Returns value of chip in cents
    """
    if chip == "black":
        return 10000
    if chip == "green":
        return 2500
    if chip == "blue":
        return 1000
    if chip == "red":
        return 500
    if chip == "pink":
        return 200
    if chip == "white":
        return 100
