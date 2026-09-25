def chunks(xs, n):
    """Split xs into consecutive lists of length n (the last may be shorter)."""
    return [xs[i:i + n] for i in range(0, len(xs) - n, n)]
