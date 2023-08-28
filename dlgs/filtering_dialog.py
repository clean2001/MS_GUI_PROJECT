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

        max_label_width = max(len(feature)
                              for feature, dtype in features if dtype == float)

        for feature, dtype in features:
            feature_layout = QHBoxLayout()

            label = QLabel(feature)
            feature_layout.addWidget(label)

            # 문자열 input창
            if dtype == str:
                input_widget = QLineEdit()
                dummy_widget = QWidget()
                dummy_widget.setMaximumWidth(20)
                feature_layout.setSpacing(20)
                feature_layout.addWidget(input_widget)
                feature_layout.addWidget(dummy_widget)
                self.filters[feature] = input_widget
            # int input창 (정수형)
            elif dtype == int:
                int_input = QSpinBox()
                int_input.setSingleStep(1)  # 1씩 증가/감소하도록 설정
                feature_layout.addWidget(QLabel("Min:"))
                feature_layout.addWidget(int_input)
                feature_layout.addWidget(QLabel("Max:"))
                # 다른 QSpinBox로 Max input 생성
                # feature_layout.addSpacing(30)
                feature_layout.addWidget(QSpinBox())
                self.filters[feature] = (int_input, None)  # Max input은 필요 없음

            # float input창
            else:
                float_input = QDoubleSpinBox()
                float_input.setSingleStep(0.01)   # 0.01씩 증가/감소하도록
                feature_layout.addWidget(QLabel("Min:"))
                feature_layout.addWidget(float_input)
                feature_layout.addWidget(QLabel("Max:"))
                # 다른 QDoubleSpinBox으로 Max input 생성
                feature_layout.addWidget(QDoubleSpinBox())
                self.filters[feature] = (float_input, None)  # Max input은 필요 없음

                # self.filters[feature] = (min_input, max_input)

            feature_layout.setSpacing(10)
            self.layout.addLayout(feature_layout)

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
            if isinstance(value, tuple):  # 범위형 input
                min_input, max_input = value
                min_value = min_input.value()
                max_value = max_input.value()
                if min_value != min_input.minimum() or max_value != max_input.maximum():
                    applied_filters[feature] = (min_value, max_value)
            else:
                text = value.text().strip()
                if text:
                    applied_filters[feature] = text

        print("Applied Filters:", applied_filters)
        # self.apply_table_filters(applied_filters)

        self.accept()


def main():
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    dialog.exec()


if __name__ == "__main__":
    main()
