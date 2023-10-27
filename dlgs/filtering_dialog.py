import sys
from PyQt6.QtWidgets import *

from custom_class.filter import FilterInfo


class FilterDialog(QDialog):
    def __init__(self, filter_info: FilterInfo):
        super().__init__()
        self.setWindowTitle("Filtering")
        self.layout = QVBoxLayout()
        self.resize(400, 400)
        self.filter_info = filter_info

        features = [
            ("Filename", str), ("Index", int), ("ScanNo", int), ("Title", str),
            ("PMZ", float), ("Charge", int), ("Peptide", str), ("CalcMass", float),
            ("SA", float), ("QScore", float), ("#Ions", int), ("#Sig", int),
            ("ppmError", float), ("C13", int), ("ExpRatio", float), ("Prosites", str)
        ]

        cur_info = {
            'Filename': filter_info.filename,
            'Index': filter_info.index,
            'ScanNo': filter_info.scanno,
            'Title': filter_info.title,
            'PMZ': filter_info.pmz,
            'Charge': filter_info.charge,
            'Peptide': filter_info.peptide,
            'CalcMass': filter_info.calcmass,
            'SA': filter_info.sa,
            'QScore': filter_info.qscore,
            '#Ions': filter_info.ions,
            '#Sig': filter_info.sig,
            'ppmError': filter_info.ppmerror,
            'C13': filter_info.c13,
            'ExpRatio': filter_info.expratio,
            'Prosites': filter_info.protsites
        }

        self.filters = {}

        form_layout = QFormLayout()

        for feature, dtype in features:
            label = QLabel(feature)
            input_widget = None

            # 문자열 input창
            if dtype == str:
                input_widget = QLineEdit()
                # 기존 정보 넣기
                if cur_info[feature]:
                    input_widget.setText(cur_info[feature])
                self.filters[feature] = input_widget

            # int input창 (정수형)
            elif dtype == int:
                min_input = QSpinBox()
                min_input.setSingleStep(1)  # 1씩 증가/감소하도록 설정
                min_input.setRange(0, 5000000)  # 범위 수정함
                min_input.clear()
                min_input.setLineEdit(QLineEdit())  # 입력 필드 설정
                min_input.lineEdit().setPlaceholderText("Min")  # 플레이스홀더 설정

                max_input = QSpinBox()
                max_input.setSingleStep(1)
                max_input.setRange(0, 5000000)  # 범위 수정함
                max_input.clear()
                max_input.setLineEdit(QLineEdit())  # 입력 필드 설정
                max_input.lineEdit().setPlaceholderText("Max")

                range_label = QLabel("~")
                input_widget = (min_input, range_label, max_input)
                min_input.setFixedSize(70, 25)  # spinbox 사이즈 설정
                max_input.setFixedSize(70, 25)

                self.filters[feature] = (min_input, max_input)
                # 기존 값 적용
                if cur_info[feature]:
                    if cur_info[feature][0]:
                        min_input.setValue(int(cur_info[feature][0]))
                    if cur_info[feature][1]:
                        max_input.setValue(int(cur_info[feature][1]))

            # float input창
            else:
                min_input = QDoubleSpinBox()
                min_input.setSingleStep(0.01)   # 0.01씩 증가/감소하도록
                min_input.setRange(-100, 5000000)  # 범위 수정함
                min_input.setDecimals(5)
                min_input.clear()
                min_input.setLineEdit(QLineEdit())  # 입력 필드 설정
                min_input.lineEdit().setPlaceholderText("Min")

                max_input = QDoubleSpinBox()
                max_input.setSingleStep(0.01)
                max_input.setRange(-100, 5000000)  # 범위 수정함
                max_input.setDecimals(5)
                max_input.clear()
                max_input.setLineEdit(QLineEdit())  # 입력 필드 설정
                max_input.lineEdit().setPlaceholderText("Max")

                range_label = QLabel("~")
                input_widget = (min_input, range_label, max_input)
                min_input.setFixedSize(70, 25)
                max_input.setFixedSize(70, 25)

                # 기존 값 적용
                if cur_info[feature]:
                    if cur_info[feature][0]:
                        min_input.setValue(float(cur_info[feature][0]))
                    if cur_info[feature][1]:
                        max_input.setValue(float(cur_info[feature][1]))
                self.filters[feature] = (min_input, max_input)

            if isinstance(input_widget, tuple):  # 범위형 input (int, float)
                widget_layout = QHBoxLayout()
                widget_layout.addWidget(input_widget[0])
                widget_layout.addWidget(input_widget[1])
                widget_layout.addWidget(input_widget[2])
                input_widget = widget_layout

            form_layout.addRow(label, input_widget)

        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.layout.addLayout(form_layout)

        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_filters)
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        apply_layout.addWidget(apply_button)
        self.layout.addLayout(apply_layout)

        self.setLayout(self.layout)

    def apply_filters(self):
        applied_filters = {}
        changes_made = False  # 입력이 변경되었는지 확인

        for feature, value in self.filters.items():
            if isinstance(value, QLineEdit):  # 문자열 input
                text = value.text().strip()
                applied_filters[feature] = text if text else None
                if text != self.filters[feature]:
                    changes_made = True
            elif isinstance(value, QSpinBox):  # 정수형 input
                if value.value() != 0:
                    applied_filters[feature] = value.value()
                    if value.value() != self.filters[feature][0]:
                        changes_made = True
            elif isinstance(value, QDoubleSpinBox):  # 실수형 input
                if value.value() != 0.0:
                    applied_filters[feature] = value.value()
                    if value.value() != self.filters[feature][0]:
                        changes_made = True

        # 범위형 스핀박스에 대한 값을 저장
        for feature, value in self.filters.items():
            if isinstance(value, tuple):
                min_input, max_input = value
                if isinstance(min_input, QSpinBox) or isinstance(min_input, QDoubleSpinBox):
                    min_value = min_input.value()
                    max_value = max_input.value()
                    if min_value != min_input.minimum() or max_value != max_input.maximum():
                        applied_filters[feature] = (min_value, max_value)
                        if (min_value, max_value) != self.filters[feature]:
                            changes_made = True

        if changes_made:
            # print("Applied Filters:", applied_filters)
            a = [applied_filters['Filename'],
                 list(applied_filters['Index']),
                 list(applied_filters['ScanNo']),
                 applied_filters['Title'],
                 list(applied_filters['PMZ']),
                 list(applied_filters['Charge']),
                 applied_filters['Peptide'],
                 list(applied_filters['CalcMass']),
                 list(applied_filters['SA']),
                 list(applied_filters['QScore']),
                 list(applied_filters['#Ions']),
                 list(applied_filters['#Sig']),
                 list(applied_filters['ppmError']),
                 list(applied_filters['C13']),
                 list(applied_filters['ExpRatio']),
                 applied_filters['Prosites']
                 ]

            rslt = self.filter_info.setFilterInfo(
                a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12], a[13], a[14], a[15])  # args -> 16개


        self.accept()


def main():
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    exit(dialog.exec())


if __name__ == "__main__":
    main()
