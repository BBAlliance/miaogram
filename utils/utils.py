import random

def toInt(s) -> int:
    try:
        return int(s)
    except Exception:
        return 0

def rand():
    return random.randint(0, 65535)

def randStr():
    i = rand()
    return f"{i}"
