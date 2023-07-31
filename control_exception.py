def check_tolerence(tol : str):
    try:
        float(tol)
        tol = float(tol)
        if tol >= 0 and tol <= 1:
            return True
        else:
            return False
    except ValueError:
        return False

def check_sa_threshold(sa : str):
    try:
        float(sa)
        sa = float(sa)
        if sa >= 0 and sa <= 1:
            return True
        else:
            return False
    
    except ValueError:
        return False