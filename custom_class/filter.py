# 현재 필터링 상황을 나타내는 싱글톤 인스턴스
class FilterInfo:
    def __init__(self, myapp):
        super().__init__()
        self.myapp = myapp
        self.filename, self.index, self.scanno, self.title, self.pmz, self.charge, self.peptide, self.calcmass, self.sa, self.qscore, self.ions, self.sig, self.ppmerror, self.c13, self.expratio,self.protsites = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

    def reset_all_values(self):
        self.filename, self.index, self.scanno, self.title, self.pmz, self.charge, self.peptide, self.calcmass, self.sa, self.qscore, self.ions, self.sig, self.ppmerror, self.c13, self.expratio,self.protsites = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

    # 범위 값의 유효성 체크
    def check_range_values(_value : list[2]):
        # 실수인지 확인
        try:
            _value[0] = float(_value[0])
            _value[1] = float(_value[1])
        except:
            return False
        
        if _value[0] > _value[1]:
            return False
        
        return True
    
    def check_float_values(_value):
        # 실수인지 확인
        try:
            _value = float(_value)
        except Exception as e:
            print(e)
            return False
        
        return True
    
    def check_int_values(self, _value):
        # 정수인지 확인
        try:
            _value = int(_value)
        except Exception as e:
            print(e)
            return False
    
    def check_not_null(self, _value):
        if not _value:
            return False
        return True
    
    
    def setFilterInfo(self, _filename, _index, _scanno, _title,
                      _pmz, _charge, _peptide, _calcmass, _sa, _qscore,
                      _ions, _sig, _ppmerror, _c13, _expratio, _prosites):
        
        info = [_filename, _index, _scanno, _title,
                      _pmz, _charge, _peptide, _calcmass, _sa, _qscore,
                      _ions, _sig, _ppmerror, _c13, _expratio, _prosites]
        
        # null check는 하지 않아도 된다. -> Null인 항목은 필터링에 들어가지 않음
        
        # 모든 테스트 통과. 적용
        info = [_filename, _index, _scanno, _title,
                      _pmz, _charge, _peptide, _calcmass, _sa, _qscore,
                      _ions, _sig, _ppmerror, _c13, _expratio, _prosites]
        
        [self.filename, self.index, self.scanno, self.title,
        self.pmz, self.charge, self.peptide, self.calcmass,
        self.sa, self.qscore, self.ions, self.sig,
        self.ppmerror, self.c13, self.expratio, self.protsites] = info

        return True