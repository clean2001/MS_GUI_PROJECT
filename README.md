# 2023 MS Analysis GUI Tool


2023.07.24 작성

### Language & Library

- Language: Python
- Library:
    - pyqt5
    - spectrum_utils
    - pandas
    

### Implementation

앞으로의 구현 목적

![Untitled](GUI%20%E1%84%8C%E1%85%A9%E1%86%AF%E1%84%8B%E1%85%A5%E1%86%B8%20%E1%84%91%E1%85%B3%E1%84%85%E1%85%A9%E1%84%8C%E1%85%A6%E1%86%A8%E1%84%90%E1%85%B3%2018a4a195fc374088b9279cbe43aaf8df/Untitled.png)

1. gui를 통해 query file을 open
2. deephos를 실행하여 query에 대해 DB를 서치
3. 리턴된 result 파일을 파싱하여 Gui의 spectrum 목록에 띄움
4. spectrum 목록의 어떤 항목을 누르면, 그 spectrum의 ‘seq_charge’를 key로 하여, 미리 Hash에 넣어둔 DB를 서치. Hash의 value는 target-decoy DB에서의 해당 스펙트럼의 m/z, intensity 정보가 시작되는 부분의 file offset.
5. DB에서 file offset 부분으로 가면 매치된 스펙트럼의 m/z, intensity 정보가 있는데, 이를 파싱
6. mirror plot으로 query와 정답 스펙트럼을 나타냄. (top: query, bottom: DB)

현재

![Untitled](GUI%20%E1%84%8C%E1%85%A9%E1%86%AF%E1%84%8B%E1%85%A5%E1%86%B8%20%E1%84%91%E1%85%B3%E1%84%85%E1%85%A9%E1%84%8C%E1%85%A6%E1%86%A8%E1%84%90%E1%85%B3%2018a4a195fc374088b9279cbe43aaf8df/Untitled%201.png)

현재는 아직 Deephos 프로그램을 실행시키지 않고, 나박사님께서 예시로 주신 query 파일을 파싱, result 파일을 파싱하여 GUI에 띄우는 방식입니다.

아직 Deephos가 없기에, query, result 파일을 모두 가지고 있어야 실행이 가능합니다.

그 외에도

- N, C terminal을 표시
- tolerance를 user 마음대로 조정가능
- Summary(QA, QScore의 histogram, ppm Error의 boxplot)

기능을 구현했습니다.

  
   

- lib_scanner
    python lib_scanner.py ./data/Target_predicted_lib.msp ./data/target_lib.json
      
    python lib_scanner.py ./data/revDecoy_predicted_lib.msp ./data/decoy_lib.json 