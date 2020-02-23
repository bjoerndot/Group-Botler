def getLastNFromList(l, n):
    return l[-n:] if len(l) > n-1 else l

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
