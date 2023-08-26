import sys
from PyQt6.QtWidgets import *


class FilterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filtering")
        self.layout = QVBoxLayout()
        self.resize(500, 500)

        features = [
            ("Filename", str), ("Index", float), ("ScanNo", float), ("Title", str),
            ("PMZ", float), ("Charge", float), ("Peptide", str), ("CalcMass", float),
            ("SA", float), ("QScore", float), ("#Ions", float), ("#Sig", float),
            ("ppmError", float), ("C13", float), ("ExpRatio", float), ("Protein", str)
        ]

        self.filters = {}

        for feature, dtype in features:
            feature_layout = QHBoxLayout()

            label = QLabel(feature)
            feature_layout.addWidget(label)

            # 문자열 input창
            if dtype == str:
                input_widget = QLineEdit()
                dummy_widget = QWidget()
                dummy_widget.setMaximumWidth(10)
                feature_layout.addWidget(input_widget)
                feature_layout.addWidget(dummy_widget)
                self.filters[feature] = input_widget
            # 숫자형 input창
            else:
                min_input = QDoubleSpinBox()
                max_input = QDoubleSpinBox()

                min_input.setSingleStep(0.01)   # 0.01씩 증가/감소하도록
                max_input.setSingleStep(0.01)

                feature_layout.addWidget(QLabel("Min:"))
                feature_layout.addWidget(min_input)
                feature_layout.addWidget(QLabel("Max:"))
                feature_layout.addWidget(max_input)

                self.filters[feature] = (min_input, max_input)

            self.layout.addLayout(feature_layout)

        # Applyt button
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
        
    # filetering 했을 때 table에 적용하기
    # def apply_table_filters(self, filters):
    #     for row in range(self.spectrum_list.rowCount()):
    #         row_visible = all(self.apply_row_filter(row, col, filters) for col in range(self.spectrum_list.columnCount()))
    #         self.spectrum_list.setRowHidden(row, not row_visible)

    # def apply_row_filter(self, row, col, filters):
    #     if col not in filters:  # No filter for this column
    #         return True

    #     filter_value = filters[col]
    #     item = self.spectrum_list.item(row, col)

    #     if item is None:  # No item in this cell
    #         return False

    #     item_text = item.text()

    #     if isinstance(filter_value, tuple):  # Range filter
    #         min_value, max_value = filter_value
    #         try:
    #             cell_value = float(item_text)
    #             return min_value <= cell_value <= max_value
    #         except ValueError:
    #             return False
    #     else:  # String filter
    #         return filter_value.lower() in item_text.lower()


def main():
    app = QApplication(sys.argv)
    dialog = FilterDialog()
    dialog.exec()


if __name__ == "__main__":
    main()
