def clamp(x, lo, hi):
    """Limit x to the range [lo, hi]."""
    return max(lo, min(x, hi))
