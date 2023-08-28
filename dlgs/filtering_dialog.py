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
            # float input창
            else:
                min_input = QDoubleSpinBox()
                min_input.setSingleStep(0.01)   # 0.01씩 증가/감소하도록
                min_input.setDecimals(4)  # 소수점 이하 두 자리까지
                max_input = QDoubleSpinBox()
                max_input.setSingleStep(0.01)  # 0.01씩 증가/감소하도록
                max_input.setDecimals(4)  # 소수점 이하 두 자리까지
                range_label = QLabel("~")
                input_widget = (min_input, range_label, max_input)
                min_input.setFixedSize(70, 25)
                max_input.setFixedSize(70, 25)
                min_input.setSpecialValueText("")
                max_input.setSpecialValueText("")

            self.filters[feature] = input_widget

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
        for feature, value in self.filters.items():
            if isinstance(value, QLineEdit):  # 문자열 input
                text = value.text().strip()
                if text:
                    applied_filters[feature] = text
            elif isinstance(value, tuple):  # 범위형 input (int, float)
                min_input, _, max_input = value
                min_value = min_input.value() if min_input.value() != min_input.minimum() else None
                max_value = max_input.value() if max_input.value() != max_input.maximum() else None
                if min_value is not None or max_value is not None:
                    applied_filters[feature] = (min_value, max_value)

        print("Applied Filters:", applied_filters)

        self.accept()


def main():
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    dialog.exec()


if __name__ == "__main__":
    main()
