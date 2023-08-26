class FilterInfo:
    filename, index, scanno, title, pmz, charge, peptide, calcmass, sa, qscore, ions, sig, ppmerror, c13, expratio, prosites = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

    def __init__(self, myapp):
        super.__init__()
        self.myapp = myapp
    
    def setFilterInfo(_filename, _index, _scanno, _title,
                      _pmz, _charge, _peptide, _calcmass, _sa, _qscore,
                      _ions, _sig, _ppmerror, _c13, _expratio, _prosites):
        return
    