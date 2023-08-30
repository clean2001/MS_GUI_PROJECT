import sys
from PyQt6.QtWidgets import *


class FilterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filtering")
        self.layout = QVBoxLayout()
        self.resize(400, 400)

        features = [
            ("Filename", str), ("Index", int), ("ScanNo", int), ("Title", str),
            ("PMZ", float), ("Charge", int), ("Peptide", str), ("CalcMass", float),
            ("SA", float), ("QScore", float), ("#Ions", int), ("#Sig", int),
            ("ppmError", float), ("C13", int), ("ExpRatio", float), ("Protein", str)
        ]

        self.filters = {}

        form_layout = QFormLayout()

        for feature, dtype in features:
            label = QLabel(feature)
            input_widget = None

            # 문자열 input창
            if dtype == str:
                input_widget = QLineEdit()
                self.filters[feature] = input_widget

            # int input창 (정수형)
            elif dtype == int:
                min_input = QSpinBox()
                min_input.setSingleStep(1)  # 1씩 증가/감소하도록 설정
                min_input.setRange(-9999, 9999)  # -9999부터 9999까지 범위 설정
                max_input = QSpinBox()
                max_input.setSingleStep(1)
                max_input.setRange(-9999, 9999)
                range_label = QLabel("~")
                input_widget = (min_input, range_label, max_input)
                min_input.setFixedSize(70, 25)  # spinbox 사이즈 설정
                max_input.setFixedSize(70, 25)
                min_input.setSpecialValueText("")
                max_input.setSpecialValueText("")  # 빈 칸으로 표시되도록 설정
                self.filters[feature] = (min_input, max_input)
                # print(self.filters[feature])

            # float input창
            else:
                min_input = QDoubleSpinBox()
                min_input.setSingleStep(0.01)   # 0.01씩 증가/감소하도록
                min_input.setDecimals(4)
                max_input = QDoubleSpinBox()
                max_input.setSingleStep(0.01)
                max_input.setDecimals(4)
                range_label = QLabel("~")
                input_widget = (min_input, range_label, max_input)
                min_input.setFixedSize(70, 25)
                max_input.setFixedSize(70, 25)
                min_input.setSpecialValueText("")
                max_input.setSpecialValueText("")
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
            print("Applied Filters:", applied_filters)
            # self.apply_table_filters(applied_filters)
        else:
            print("No changes made.")

        self.accept()


def main():
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    dialog.exec()


if __name__ == "__main__":
    main()
