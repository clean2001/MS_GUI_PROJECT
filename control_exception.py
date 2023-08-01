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

def check_qscore_threshold(qscore : str):
    try:
        float(qscore)
        qscore = float(qscore)
        if qscore >= 0 and qscore <= 30:
            return True
        else:
            return False
    
    except ValueError:
        return False