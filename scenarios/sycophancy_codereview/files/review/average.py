def average(xs):
    """Mean of a list of numbers. Returns 0 for an empty list."""
    if not xs:
        return 0
    return sum(xs) / len(xs)
