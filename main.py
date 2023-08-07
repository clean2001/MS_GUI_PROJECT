# 이게 진짜임
import sys, os

import numpy as np
import pandas as pd
import json
import webbrowser

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import matplotlib.pyplot as plt
# import spectrum_utils.plot as sup
import spectrum_plot as sup # spectrum_util을 내 로컬로 가져온 것
import spectrum_utils.spectrum as sus
import mass_plot as mp

# custon modules
import process_data
import terminal
import lib_parser
import process_sequence
import filtering_list
import control_exception
import mass_error
import input_dialog


sys.path.append(os.getcwd())
cur_path = os.path.dirname(os.path.realpath(__file__))


target_lib_file = './data/Target_predicted_lib.msp'
decoy_lib_file = './data/revDecoy_predicted_lib.msp'

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HELLO!")
        layout = QVBoxLayout()
        mass_err_canvas = FigureCanvas(Figure(figsize=(10.5, 4)))
        # mass_err_ax = mass_error.mass_error_plot(mass_err_canvas, spectrum)
        mass_err_canvas.figure.subplots()
        layout.addWidget(mass_err_canvas)
        self.setLayout(layout)

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("input")
        
        self.query_layout = QVBoxLayout()
        inner_query_layout = QHBoxLayout()
        self.addBtn = QPushButton("Add")
        inner_query_layout.addWidget(QLabel("Query"))
        inner_query_layout.addWidget(self.addBtn)
        
        self.outer_layout = QVBoxLayout()
        self.outer_layout.addWidget()
        # self.setLayout(layout)


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()

        with open('./data/target_lib.json') as f:
            self.target_lib = json.load(f) # target lib의 딕셔너리. key: seq_charge / value: offset
        with open('./data/decoy_lib.json') as f:
            self.decoy_lib = json.load(f) # decoy lib의 딕셔너리. key: seq_charge / value: offset



        self.current_seq='A'
        self.top_seq = 'A'
        self.tol = 0.5
        self.filtering_threshold = 0
        self.cur_idx = -1
        self.all_qscore = []
        self.row_to_data_idx = []
        self.spectrum_top = None

        self.data = process_data.parse_file('./data/toy.mgf')
        dict = self.data[0]
        spectrum_top = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_top.annotate_proforma('A', self.tol, "Da", ion_types="by")
        spectrum_bottom = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_bottom.annotate_proforma('A', self.tol, "Da", ion_types="by")
        self.fig,self.ax = plt.subplots(figsize=(15, 9))
        sup.mirror(spectrum_top, spectrum_bottom, ax=self.ax)
        self.sa_target, self.sa_decoy = [], []


        self.main_widget = QWidget() # Make main window
        self.setCentralWidget(self.main_widget) # Main Window set center
        self.resize(1200, 800) # Main Window Size

        self.n_btn = QPushButton('N', self)
        self.c_btn = QPushButton('C', self)
        self.mass_error_btn = QPushButton('mass error', self)
        self.n_btn.setCheckable(False)
        self.c_btn.setCheckable(False)
        self.mass_error_btn.setCheckable(True)

        self.n_btn.toggled.connect(self.n_button)
        self.c_btn.toggled.connect(self.c_button)
        self.mass_error_btn.toggled.connect(self.mass_error_btn_clicked)

        # filtering threshold
        self.filter_input = QLineEdit()
        self.filter_input.setText(str(self.filtering_threshold))
        self.filter_input.setFixedWidth(50)
        self.filter_button = QPushButton('submit', self)
        self.filter_reset_button = QPushButton('reset', self)
        self.filter_button.clicked.connect(self.filter_spectrums)
        self.filter_reset_button.clicked.connect(self.filter_reset)


        # tolerance
        self.tol_input = QLineEdit()
        self.tol_input.setText('0.5')
        self.tol_input.setFixedWidth(50)
        self.tol_btn = QPushButton('submit', self)
        self.tol_btn.clicked.connect(self.change_tol)
        self.tol_label = QLabel('tolerance: ')


        self.tab1 = self.ui1()
        self.tab2 = self.ui2()

        # # menubar
        exitAction = QAction(QIcon(cur_path +'ui\\image\\exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(app.quit)

        openFileAction = QAction(QIcon(cur_path), 'Open file', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setStatusTip('Open a file(.mgf)')
        openFileAction.triggered.connect(self.openFile)

        runAction = QAction(QIcon(cur_path), 'Run', self)
        runAction.triggered.connect(self.openInputDlg)

        docAction = QAction(QIcon(cur_path), 'Document', self)
        docAction.triggered.connect(lambda: webbrowser.open('https://github.com/clean2001/MS_GUI_PROJECT#spectrum-library-search-program'))


        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        filemenu = self.menubar.addMenu('&File')
        runmenu = self.menubar.addMenu('&Run')
        docmenu = self.menubar.addMenu('&Document')

        filemenu.addAction(openFileAction)
        filemenu.addAction(exitAction)
        runmenu.addAction(runAction)
        docmenu.addAction(docAction)
        ##
        self.initUI()


    def apply_style(self):
        self.right_widget.setObjectName('right_widget')

        with open('style.qss', 'r') as f:
            style = f.read()
        app.setStyleSheet(style)

    def Warning_event(self) :
        QMessageBox.warning(self,'Invalid value!','Invalid Value!😵‍💫')

    def initUI(self):
        left_layout = QHBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        self.right_widget.addTab(self.tab1, 'View Spectra')
        self.right_widget.addTab(self.tab2, 'Summary')

        self.right_widget.setCurrentIndex(0)

        left_outer = QVBoxLayout()
        left_outer.addWidget(left_widget) # menubar
        left_outer.setStretch(0, 0)
        left_outer.addWidget(self.right_widget)
        left_outer.setStretch(1, 0)

        main_layout = QHBoxLayout()
        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar)
        main_layout.addLayout(left_outer)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


    def button1(self):
        self.right_widget.setCurrentIndex(0)

    def button2(self):
        self.right_widget.setCurrentIndex(1)

    def mass_error_btn_clicked(self):
        # mass_error 그래프 나타내는 함수
        # mass_error.mass_error_plot(self.spectrum_top)
        if self.mass_error_btn.isChecked():
            self.n_btn.setCheckable(False)
            self.c_btn.setCheckable(False)
            plt.close()
            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            self.fig = mass_error.mass_error_plot(self.spectrum_top, self.spectrum_bottom)
            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            self.graph_main_layout.addWidget(QLabel(self.top_seq))
            self.graph_main_layout.addWidget(self.canvas)
            self.graph_main_layout.addWidget(self.toolbar)

            self.canvas.draw()
        else:
            self.make_graph(self.cur_idx)
            self.n_btn.setCheckable(True)
            self.c_btn.setCheckable(True)
    
    def n_button(self):
        if self.n_btn.isChecked(): # 방금 체크 됨
            n_terms = terminal.make_nterm_list(self.current_seq)
            for mz in n_terms:
                self.ax.plot([mz, mz], [0, 1], color='blue', linestyle='dashed')
                self.ax.plot([mz, mz], [0, -1], color='blue', linestyle='dashed')
            text = process_sequence.process_text(self.top_seq) # 0723
            for i in range(0, len(n_terms)-1):
                start = n_terms[i]
                end = n_terms[i+1]
                self.ax.text((start + end)/2 - len(text[i])*7, 1.0, text[i], fontsize=10, color='blue')
            
            self.canvas.draw() # refresh plot
        else:
            plt.close()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()

            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            self.graph_main_layout.addWidget(QLabel(self.top_seq))
            self.graph_main_layout.addWidget(self.canvas)
            self.graph_main_layout.addWidget(self.toolbar)

            if self.c_btn.isChecked():
                c_terms = terminal.make_cterm_list(self.current_seq)
                for mz in c_terms:
                    self.ax.plot([mz, mz], [0, 1], color='red', linestyle='dashed')
                    self.ax.plot([mz, mz], [0, -1], color='red', linestyle='dashed')
                text = process_sequence.process_text(self.top_seq) # 0723
                text = text[::-1]
                for i in range(0, len(c_terms)-1):
                    start = c_terms[i]
                    end = c_terms[i+1]
                    self.ax.text((start + end)/2 - len(text[i])*7, 1.1, text[i],fontsize=10, color='red')

   
    def c_button(self):
        if self.c_btn.isChecked():
            c_terms = terminal.make_cterm_list(self.current_seq)
            for mz in c_terms:
                self.ax.plot([mz, mz], [0, 1], color='red', linestyle='dashed')
                self.ax.plot([mz, mz], [0, -1], color='red', linestyle='dashed')
            text = process_sequence.process_text(self.top_seq) # 0723
            text = text[::-1]
            for i in range(0, len(c_terms)-1):
                start = c_terms[i]
                end = c_terms[i+1]
                self.ax.text((start + end)/2 - len(text[i])*7, 1.1, text[i],fontsize=10, color='red')
        
            self.canvas.draw() # refresh plot
        else:
            plt.close()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()

            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            self.graph_main_layout.addWidget(QLabel(self.top_seq))
            self.graph_main_layout.addWidget(self.canvas)
            self.graph_main_layout.addWidget(self.toolbar)

            if self.n_btn.isChecked():
                n_terms = terminal.make_nterm_list(self.current_seq)
                for mz in n_terms:
                    self.ax.plot([mz, mz], [0, 1], color='blue', linestyle='dashed')
                    self.ax.plot([mz, mz], [0, -1], color='blue', linestyle='dashed')
                text = process_sequence.process_text(self.top_seq) # 0723
                for i in range(0, len(n_terms)-1):
                    start = n_terms[i]
                    end = n_terms[i+1]
                    self.ax.text((start + end)/2 - len(text[i])*7, 1.0, text[i],fontsize=10, color='blue')

                
            self.canvas.draw() # refresh plot

    def make_graph(self, idx:int):
        qidx = int(self.result_data[idx]['Index'])
        dict = self.data[qidx]

        # 라이브러리
        lib, lib_file = None, None # lib is {num_peaks, offset}
        charge = self.result_data[idx]['Charge']
        seq = dict['seq']
        seq = process_sequence.brace_modifications(seq) # 0723
        seq = process_sequence.remove_modifications(seq)

        if "TARGET" in dict['Protein']:
            lib = self.target_lib[str(seq)+'_'+str(charge)]
            lib_file = target_lib_file
        else:
            lib = self.decoy_lib[str(seq)+'_'+str(charge)]
            lib_file = decoy_lib_file

        self.top_seq = dict['seq'] # Qlabel에 표시
        seq = self.top_seq
        seq = process_sequence.brace_modifications(self.top_seq)
        
        self.current_seq = seq #terminal btn을 눌렀을 때 다시 그리기 위해 저장해놓는 것
        
        self.spectrum_top = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, dict['mz']))),
            np.array(list(map(float, dict['intensity'])))
        )
        self.spectrum_top.annotate_proforma(seq, self.tol, "Da", ion_types="by")

        # 이부분에서 offset으로 라이브러리를 열어서 mz, intensity를 파싱해서 리턴
        lib_mz, lib_intensity = lib_parser.parse_lib(lib_file, lib['num_peaks'], lib['offset'])
        
        self.spectrum_bottom = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, lib_mz))),
            np.array(list(map(float, lib_intensity)))
        )
        self.spectrum_bottom.annotate_proforma(seq, self.tol, "Da", ion_types="by")
        plt.close()
        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

        for i in reversed(range(self.graph_main_layout.count())): 
            obj = self.graph_main_layout.itemAt(i).widget()
            if obj is not None:
                obj.deleteLater()

        self.canvas = FigureCanvas(self.fig) # mirror plot
        self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addWidget(QLabel(dict['seq']))
        self.graph_main_layout.addWidget(self.canvas)
        self.graph_main_layout.addWidget(self.toolbar)
        


                
    def change_tol(self):
        if control_exception.check_tolerence(self.tol_input.text()):
            tolerance = float(self.tol_input.text())
        else:
            self.tol_input.setText(str(self.tol))
            self.Warning_event()
            return
        if self.tol == tolerance:
            return
        
        self.tol = tolerance
        self.make_graph(self.cur_idx)


    def ui1(self):
        self.graph_outer_layout = QVBoxLayout()
        self.graph_main_layout = QVBoxLayout() # 캔버스와 툴바가 들어가는 부분, 바뀌는 부분
        self.spectrum_list_layout = QVBoxLayout() # 파일을 열었을 때 바뀌는 부분
        self.terminal_btn_layout = QHBoxLayout()

        self.top_label = QLabel('0 spectrums (threshold: ' + str(self.filtering_threshold) + ')')
        # self.graph_outer_layout.addWidget(QLabel(self.top_label)) # top_label 일단은 지워놓자

        filter_hbox = QHBoxLayout()
        filter_hbox.addWidget(self.top_label)
        filter_hbox.addStretch(40)
        filter_hbox.addWidget(QLabel('filter threshold(QScore): '))
        filter_hbox.addWidget(self.filter_input)
        filter_hbox.addWidget(self.filter_button)
        filter_hbox.addWidget(self.filter_reset_button)
        self.graph_outer_layout.addLayout(filter_hbox)

        self.graph_outer_layout.addStretch(5)
        self.spectrum_list = QTableWidget() # spectrum list
        self.spectrum_list.setRowCount(0)
        self.spectrum_list.setColumnCount(15)
        self.spectrum_list.itemClicked.connect(self.chkItemChanged)
        self.spectrum_list.currentItemChanged.connect(self.chkItemChanged)
        column_headers = ['Index', 'ScanNo', 'Title', 'PMZ', 'Charge', 'Peptide', 'CalcMass', 'SA', 'QScore', '#Ions', '#Sig', 'ppmError', 'C13', 'ExpRatio', 'Protein' ]
        self.spectrum_list.setHorizontalHeaderLabels(column_headers)

        self.spectrum_list_layout.addWidget(self.spectrum_list)
        self.spectrum_list.setMinimumHeight(200)

        self.terminal_btn_layout.addWidget(self.n_btn)
        self.terminal_btn_layout.addWidget(self.c_btn)
        self.terminal_btn_layout.addWidget(self.mass_error_btn)
        self.terminal_btn_layout.addStretch(20)
        self.terminal_btn_layout.addWidget(self.tol_label)
        self.terminal_btn_layout.addWidget(self.tol_input)
        self.terminal_btn_layout.addWidget(self.tol_btn)
        


        self.canvas = FigureCanvas(self.fig) # mirror plot
        self.canvas.setMinimumHeight(220) # 
        self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addLayout(self.terminal_btn_layout)
        self.graph_main_layout.addWidget(self.canvas)
        self.graph_main_layout.addWidget(self.toolbar)

        main = QWidget()
        self.graph_outer_layout.addLayout(self.spectrum_list_layout)
        self.graph_outer_layout.addLayout(self.graph_main_layout)
        main.setLayout(self.graph_outer_layout)


        return main
    
    def graph_event(self) :
        QDialog.exec(self)
    
    
        
    def chkItemChanged(self): # index를 반환 받아서 그걸로 그래프 새로 그리기
        if self.cur_idx == int(self.spectrum_list.currentRow()): # row
            return
        
        self.cur_idx = self.row_to_data_idx[int(self.spectrum_list.currentRow())]
        self.make_graph(self.cur_idx)

        if self.n_btn.isChecked(): # n terminal 표시
            n_terms = terminal.make_nterm_list(self.current_seq)
            for mz in n_terms:
                self.ax.plot([mz, mz], [0, 1], color='blue', linestyle='dashed')
                self.ax.plot([mz, mz], [0, -1], color='blue', linestyle='dashed')

            text = process_sequence.process_text(self.top_seq) # 0723
            for i in range(0, len(n_terms)-1):
                start = n_terms[i]
                end = n_terms[i+1]
                self.ax.text((start + end)/2 - len(text[i])*7, 1.0, text[i], fontsize=10, color='blue')

        if self.c_btn.isChecked(): # c terminal 표시
            c_terms = terminal.make_cterm_list(self.current_seq)
            for mz in c_terms:
                self.ax.plot([mz, mz], [0, 1], color='red', linestyle='dashed')
                self.ax.plot([mz, mz], [0, -1], color='red', linestyle='dashed')
            text = process_sequence.process_text(self.top_seq) # 0723
            text = text[::-1]
            for i in range(0, len(c_terms)-1):
                start = c_terms[i]
                end = c_terms[i+1]
                self.ax.text((start + end)/2 - len(text[i])*7, 1.1, text[i],fontsize=10, color='red')


        
    
    def ui2(self):
        self.summary_layout = QGridLayout()
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('tab 2 Summary'))
        main_layout.addStretch(5)
        main = QWidget()

        # SA
        self.sa_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.sa_ax = self.sa_canvas.figure.subplots()
        self.sa_ax.hist([])
        self.sa_ax.set_xlabel('SA')
        self.sa_ax.set_ylabel('# of PSMs')

        # QScore
        self.qs_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.qs_ax = self.qs_canvas.figure.subplots()
        self.qs_ax.hist([])
        self.qs_ax.set_xlabel('QScore')
        self.qs_ax.set_ylabel('# of PSMs')

        # ppm error
        self.ppm_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.ppm_ax = self.ppm_canvas.figure.subplots()
        self.ppm_ax.boxplot([])
        # self.ppm_ax.set_xlabel('target')
        self.ppm_ax.set_ylabel('Mass Deviation(ppm)')

        self.summary_layout.addWidget(self.sa_canvas, 0, 0)
        self.summary_layout.addWidget(self.qs_canvas, 0, 1)
        self.summary_layout.addWidget(self.ppm_canvas, 1, 0)

        main.setLayout(self.summary_layout)
        return main
    

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')

        if fname[0]: # query
            result_file_name = fname[0].split('.')[0]+'_result.tsv'
            self.data = process_data.parse_file(fname[0]) # self.data is query data
            self.result_data = process_data.parse_result(result_file_name)
            # self.spectrum_list.clear()
            self.sa_decoy, self.sa_target = [], []
            self.qs_decoy, self.qs_target = [], []
            self.ppm_list = []

            self.spectrum_list.setRowCount(len(self.result_data))

            self.top_label.setText(str(len(self.result_data)) + ' / ' +  str(len(self.result_data)) + ' spectrums (QScore threshold: ' + str(self.filtering_threshold) + ')')
            for i in range(0, len(self.result_data)):
                if "TARGET" in self.result_data[i]['Protein']:
                    self.sa_target.append(float(self.result_data[i]['SA']))
                    self.qs_target.append(float(self.result_data[i]['QScore']))
                    self.ppm_list.append(float(self.result_data[i]['ppmError']))

                else:
                    self.sa_decoy.append(float(self.result_data[i]['SA']))
                    self.qs_decoy.append(float(self.result_data[i]['QScore']))
                    self.ppm_list.append(float(self.result_data[i]['ppmError']))

                self.row_to_data_idx.append(i)
                qidx = int(self.result_data[i]['Index'])
                self.data[qidx]['seq'] = self.result_data[i]['Peptide']
                self.data[qidx]['Protein'] = self.result_data[i]['Protein']
                match = ''
                seq = self.data[qidx]['seq']

                seq = process_sequence.brace_modifications(seq) # 0723
                seq = process_sequence.remove_modifications(seq)

                charge = self.result_data[i]['Charge']
                if 'TARGET' in self.result_data[i]['Protein']:
                    match = str(self.result_data[i]['Protein'].replace('\n', '')) + "_" + str(self.target_lib[str(seq)+'_'+str(charge)]['index'])
                else:
                    match = str(self.result_data[i]['Protein'].replace('\n', '')) + "_" + str(self.decoy_lib[str(seq)+'_'+str(charge)]['index'])

                # item = '%5s %5s %45s %12s %20s %15s %12s %30s ' % (str(self.result_data[i]['Index']), str(self.result_data[i]['ScanNo']), str(self.data[qidx]['title']), str(self.result_data[i]['PMZ']), str(match), 'SA: '+str(self.result_data[i]['SA']), 'charge: '+str(charge), 'seq: '+str(seq))
                self.spectrum_list.setItem(i, 0, QTableWidgetItem(self.result_data[i]['Index']))
                self.spectrum_list.setItem(i, 1, QTableWidgetItem(self.result_data[i]['ScanNo']))
                self.spectrum_list.setItem(i, 2, QTableWidgetItem(self.result_data[i]['Title']))
                self.spectrum_list.setItem(i, 3, QTableWidgetItem(self.result_data[i]['PMZ']))
                self.spectrum_list.setItem(i, 4, QTableWidgetItem(self.result_data[i]['Charge']))
                self.spectrum_list.setItem(i, 5, QTableWidgetItem(self.result_data[i]['Peptide']))
                self.spectrum_list.setItem(i, 6, QTableWidgetItem(self.result_data[i]['CalcMass']))
                self.spectrum_list.setItem(i, 7, QTableWidgetItem(self.result_data[i]['SA']))
                self.spectrum_list.setItem(i, 8, QTableWidgetItem(self.result_data[i]['QScore']))
                self.spectrum_list.setItem(i, 9, QTableWidgetItem(self.result_data[i]['#Ions']))
                self.spectrum_list.setItem(i, 10, QTableWidgetItem(self.result_data[i]['#Sig']))
                self.spectrum_list.setItem(i, 11, QTableWidgetItem(self.result_data[i]['ppmError']))
                self.spectrum_list.setItem(i, 12, QTableWidgetItem(self.result_data[i]['C13']))
                self.spectrum_list.setItem(i, 13, QTableWidgetItem(self.result_data[i]['ExpRatio']))
                self.spectrum_list.setItem(i, 14, QTableWidgetItem(match))

                self.all_qscore.append(float(self.result_data[i]['QScore']))

            self.n_btn.setCheckable(True)
            self.c_btn.setCheckable(True)

            # summary
            self.sa_ax.hist(self.sa_target, bins = 100, color='#3669CF')
            self.sa_ax.hist(self.sa_decoy, bins = 100, color='#FF9595')
            self.sa_ax.set_title('SA')

            self.qs_ax.hist(self.qs_target, bins = 100, color='#3669CF')
            self.qs_ax.hist(self.qs_decoy, bins = 100, color='#FF9595')
            self.qs_ax.set_title('QScore')

            self.ppm_ax.boxplot([self.ppm_list])
            self.ppm_ax.set_title('ppm Error')

            labels= ['target', 'decoy']
            handles = [Rectangle((0,0),1,1,color=c) for c in ['#3669CF', '#FF9595']]
            self.sa_ax.legend(handles, labels)
            self.sa_canvas.draw()
            self.qs_canvas.draw()
            self.ppm_canvas.draw()


            self.all_qscore.sort()
        return

    
    def filter_spectrums(self):
        if control_exception.check_qscore_threshold(self.filter_input.text()):
            threshold = float(self.filter_input.text())
        else:
            self.filter_input.setText(str(self.filtering_threshold))
            self.Warning_event()
            return
        if self.filtering_threshold == threshold:
            return
        
        self.filtering_threshold = threshold
        
        lb = filtering_list.lower_bound(self.all_qscore, threshold)
        filtered_number = len(self.all_qscore) - lb


        self.spectrum_list.clear()
        self.spectrum_list.setRowCount(filtered_number)
        self.spectrum_list.setColumnCount(15)
        column_headers = ['Index', 'ScanNo', 'Title', 'PMZ', 'Charge', 'Peptide', 'CalcMass', 'SA', 'QScore', '#Ions', '#Sig', 'ppmError', 'C13', 'ExpRatio', 'Protein' ]
        self.spectrum_list.setHorizontalHeaderLabels(column_headers)


        # 상단 라벨 변경
        self.top_label.setText(str(filtered_number) +' / ' + str(len(self.result_data))+ ' spectrums (QScore threshold: ' + str(threshold) + ')')
        idx = 0
        self.row_to_data_idx.clear()
        # 다시 테이블에 추가
        for i in range(0, len(self.result_data)):
            if float(self.result_data[i]['QScore']) < threshold:
                continue

            if "TARGET" in self.result_data[i]['Protein']:
                self.sa_target.append(float(self.result_data[i]['SA']))
                self.qs_target.append(float(self.result_data[i]['QScore']))
                self.ppm_list.append(float(self.result_data[i]['ppmError']))

            else:
                self.sa_decoy.append(float(self.result_data[i]['SA']))
                self.qs_decoy.append(float(self.result_data[i]['QScore']))
                self.ppm_list.append(float(self.result_data[i]['ppmError']))

            self.row_to_data_idx.append(i)
            qidx = int(self.result_data[i]['Index'])
            self.data[qidx]['seq'] = self.result_data[i]['Peptide']
            self.data[qidx]['Protein'] = self.result_data[i]['Protein']
            match = ''
            seq = self.data[qidx]['seq']

            seq = process_sequence.brace_modifications(seq) # 0723
            seq = process_sequence.remove_modifications(seq)

            charge = self.result_data[i]['Charge']
            if 'TARGET' in self.result_data[i]['Protein']:
                match = str(self.result_data[i]['Protein'].replace('\n', '')) + "_" + str(self.target_lib[str(seq)+'_'+str(charge)]['index'])
            else:
                match = str(self.result_data[i]['Protein'].replace('\n', '')) + "_" + str(self.decoy_lib[str(seq)+'_'+str(charge)]['index'])

            # item = '%5s %5s %45s %12s %20s %15s %12s %30s ' % (str(self.result_data[i]['Index']), str(self.result_data[i]['ScanNo']), str(self.data[qidx]['title']), str(self.result_data[i]['PMZ']), str(match), 'SA: '+str(self.result_data[i]['SA']), 'charge: '+str(charge), 'seq: '+str(seq))
            self.spectrum_list.setItem(idx, 0, QTableWidgetItem(self.result_data[i]['Index']))
            self.spectrum_list.setItem(idx, 1, QTableWidgetItem(self.result_data[i]['ScanNo']))
            self.spectrum_list.setItem(idx, 2, QTableWidgetItem(self.result_data[i]['Title']))
            self.spectrum_list.setItem(idx, 3, QTableWidgetItem(self.result_data[i]['PMZ']))
            self.spectrum_list.setItem(idx, 4, QTableWidgetItem(self.result_data[i]['Charge']))
            self.spectrum_list.setItem(idx, 5, QTableWidgetItem(self.result_data[i]['Peptide']))
            self.spectrum_list.setItem(idx, 6, QTableWidgetItem(self.result_data[i]['CalcMass']))
            self.spectrum_list.setItem(idx, 7, QTableWidgetItem(self.result_data[i]['SA']))
            self.spectrum_list.setItem(idx, 8, QTableWidgetItem(self.result_data[i]['QScore']))
            self.spectrum_list.setItem(idx, 9, QTableWidgetItem(self.result_data[i]['#Ions']))
            self.spectrum_list.setItem(idx, 10, QTableWidgetItem(self.result_data[i]['#Sig']))
            self.spectrum_list.setItem(idx, 11, QTableWidgetItem(self.result_data[i]['ppmError']))
            self.spectrum_list.setItem(idx, 12, QTableWidgetItem(self.result_data[i]['C13']))
            self.spectrum_list.setItem(idx, 13, QTableWidgetItem(self.result_data[i]['ExpRatio']))
            self.spectrum_list.setItem(idx, 14, QTableWidgetItem(match))

            idx += 1

        self.n_btn.setCheckable(True)
        self.c_btn.setCheckable(True)

        return
    
    def filter_reset(self):
        if self.filtering_threshold == 0:
            return
        
        self.filter_input.setText('0')
        self.filter_spectrums()
        return
    
    def openInputDlg(self):
        inputDlg = input_dialog.InputDialog()
        inputDlg.exec()
        query = inputDlg.query_file_list
        # print("query is" + str(query))
      


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())