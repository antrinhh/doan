def angle_to_value(angle):
    """Converts an angle (0 to 180) to servo.value (-1 to 1)."""
    return (angle - 90) / 90