# 이게 진짜임
import sys, os

import numpy as np
import pandas as pd
import json
import webbrowser

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor
from PyQt6.QtCore import Qt, QFile, QTextStream

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import matplotlib.pyplot as plt
# import spectrum_utils.plot as sups
import spectrum_plot as sup # spectrum_util을 내 로컬로 가져온 것
import spectrum_utils.spectrum as sus

# custom modules
import process_data
import terminal
import lib_parser
import process_sequence
import filtering_list
import control_exception
import mass_error
import input_dialog
import lib_scanner


sys.path.append(os.getcwd())
cur_path = os.path.dirname(os.path.realpath(__file__))



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
        
        # load하는 코드를 삭제
        with open('./data/target_lib.json') as f:
            self.target_lib = json.load(f) # target lib의 딕셔너리. key: seq_charge / value: offset
        with open('./data/decoy_lib.json') as f:
            self.decoy_lib = json.load(f) # decoy lib의 딕셔너리. key: seq_charge / value: offset

        self.current_seq='A'
        self.top_seq = 'A'
        self.frag_tol = 0.02
        self.filtering_threshold = 0
        self.cur_idx = -1
        self.all_qscore = []
        self.qidx_to_ridx = dict()
        self.spectrum_top = None
        self.is_list_visible = True
        self.cur_row = 0
        self.target_lib_file = None
        self.decoy_lib_file = None
        self.data = dict() # filename : 파싱된 결과(dict) 리스트
        self.filenames = []

        spectrum_top = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_top.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
        spectrum_bottom = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_bottom.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
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
        self.frag_tol_input = QLineEdit()
        self.frag_tol_input.setText('0.02')
        self.frag_tol_input.setFixedWidth(50)
        self.frag_tol_btn = QPushButton('submit', self)
        self.frag_tol_btn.clicked.connect(self.change_tol)
        self.frag_tol_label = QLabel('tolerance: ')


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
        # openFileAction.triggered.connect(self.openFile)

        runAction = QAction(QIcon(cur_path), 'Run', self)
        runAction.triggered.connect(self.openInputDlg)
        
        configAction = QAction(QIcon(cur_path), 'View Config', self)
        configAction.triggered.connect(self.openConfigDlg)

        docAction = QAction(QIcon(cur_path), 'Document', self)
        docAction.triggered.connect(lambda: webbrowser.open('https://github.com/clean2001/MS_GUI_PROJECT#spectrum-library-search-program'))

        # 리스트 단축키
        listAction = QAction(QIcon(cur_path +'ui\\image\\exit.png'), 'Hide/Show List', self)
        listAction.setShortcut('Ctrl+J')
        listAction.triggered.connect(self.toggle_spectrum_list)
        ##

        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        filemenu = self.menubar.addMenu('&File')
        runmenu = self.menubar.addMenu('&Run')
        docmenu = self.menubar.addMenu('&Document')

        filemenu.addAction(openFileAction)
        filemenu.addAction(exitAction)
        filemenu.addAction(listAction)
        runmenu.addAction(runAction)
        runmenu.addAction(configAction)
        docmenu.addAction(docAction)
        ##

        self.initUI()
        self.apply_style()


    def apply_style(self):
        self.n_btn.setObjectName('n_btn')
        self.c_btn.setObjectName('c_btn')

        with open('./qstyle/style.qss', 'r') as f:
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

        self.n_btn.setMaximumWidth(50)
        self.c_btn.setMaximumWidth(50)



    def button1(self):
        self.right_widget.setCurrentIndex(0)

    def button2(self):
        self.right_widget.setCurrentIndex(1)

    def mass_error_btn_clicked(self):
        # mass_error 그래프 나타내는 함수
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
            # self.graph_main_layout.addWidget(QLabel(self.top_seq + "   " + str(self.result_data[self.cur_idx]['Charge'])))
            self.graph_main_layout.addWidget(self.canvas)
            self.graph_main_layout.addWidget(self.toolbar)

            self.canvas.draw()
        else:
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()
            self.make_graph(query_filename, self.cur_idx)
            self.n_btn.setCheckable(True)
            self.c_btn.setCheckable(True)
    
    def n_button(self):
        if self.n_btn.isChecked(): # 방금 체크 됨
            self.n_btn.setStyleSheet("background-color: #191970")
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
            self.n_btn.setStyleSheet("background-color: #1E90FF")
            plt.close()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()

            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            # self.graph_main_layout.addWidget(QLabel(self.top_seq + "   " + str(self.result_data[][self.cur_idx]['Charge'])))
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
            self.c_btn.setStyleSheet("background-color: #800000")#CD5C5C
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
            self.c_btn.setStyleSheet("background-color: #CD5C5C")
            plt.close()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()

            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            # self.graph_main_layout.addWidget(QLabel(self.top_seq + "   " + str(self.result_data[self.cur_idx]['Charge'])))
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

    def make_graph(self, filename:str, qidx:int):
        ridx = int(self.qidx_to_ridx[str(qidx)])
        dict = self.data[filename][qidx]
        rdict = self.result_data[self.results[0]][ridx]

        # 라이브러리
        lib, lib_file = None, None # lib is {num_peaks, offset}
        charge = dict['charge']
        seq = dict['seq']
        seq = process_sequence.brace_modifications(seq) # 0723
        seq = process_sequence.remove_modifications(seq)

        if "TARGET" in rdict['ProtSites']:
            lib = self.target_lib[str(seq)+'_'+str(charge)]
            lib_file = self.target_lib_file
        else:
            lib = self.decoy_lib[str(seq)+'_'+str(charge)]
            lib_file = self.decoy_lib_file

        self.top_seq = rdict['Peptide'] # Qlabel에 표시
        seq = self.top_seq
        seq = process_sequence.brace_modifications(self.top_seq)
        
        self.current_seq = seq #terminal btn을 눌렀을 때 다시 그리기 위해 저장해놓는 것
        query_filename = self.spectrum_list.item(self.cur_row, 0).text()
        query_mz, query_intensity = lib_parser.parse_spectrum(query_filename, int(dict['offset']))
        self.spectrum_top = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, query_mz))),
            np.array(list(map(float, query_intensity)))
        )
        self.spectrum_top.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")

        # 이부분에서 offset으로 라이브러리를 열어서 mz, intensity를 파싱해서 리턴
        lib_mz, lib_intensity = lib_parser.parse_lib(lib_file, lib['num_peaks'], lib['offset'])
        
        self.spectrum_bottom = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, lib_mz))),
            np.array(list(map(float, lib_intensity)))
        )
        self.spectrum_bottom.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")
        plt.close()

        ## mass error를 그리는 부분
        if self.mass_error_btn.isChecked():
            plt.close()
            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))
            self.fig = mass_error.mass_error_plot(self.spectrum_top, self.spectrum_bottom)
            self.canvas = FigureCanvas(self.fig) # mirror plot
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            # self.graph_main_layout.addWidget(QLabel(self.top_seq + "   " + str(self.result_data[self.cur_idx]['Charge'])))
            self.graph_main_layout.addWidget(self.canvas)
            self.graph_main_layout.addWidget(self.toolbar)

            self.canvas.draw()
            return
        
        ##

        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        sup.mirror(self.spectrum_top, self.spectrum_bottom, ax=self.ax)

        for i in reversed(range(self.graph_main_layout.count())): 
            obj = self.graph_main_layout.itemAt(i).widget()
            if obj is not None:
                obj.deleteLater()

        self.canvas = FigureCanvas(self.fig) # mirror plot
        self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        # self.graph_main_layout.addWidget(QLabel(self.top_seq + "   " + str(self.result_data[self.cur_idx]['Charge'])))
        self.graph_main_layout.addWidget(self.canvas)
        self.graph_main_layout.addWidget(self.toolbar)
        

    def change_tol(self):
        if control_exception.check_tolerence(self.frag_tol_input.text()):
            tolerance = float(self.frag_tol_input.text())
        else:
            self.frag_tol_input.setText(str(self.frag_tol))
            self.Warning_event()
            return
        if self.frag_tol == tolerance:
            return
        
        self.frag_tol = tolerance
        query_filename = self.spectrum_list.item(self.cur_row, 0).text()
        self.make_graph(query_filename, self.cur_idx)


    def ui1(self):
        self.graph_outer_layout = QVBoxLayout()
        self.graph_main_layout = QVBoxLayout() # 캔버스와 툴바가 들어가는 부분, 바뀌는 부분
        self.spectrum_list_layout = QVBoxLayout() # 파일을 열었을 때 바뀌는 부분
        self.terminal_btn_layout = QHBoxLayout()
        filter_hbox = QHBoxLayout()

        top_sp = QVBoxLayout()
        bottom_sp = QVBoxLayout()


        self.splitter = QSplitter()

        self.top_label = QLabel('0 spectrums (threshold: ' + str(self.filtering_threshold) + ')')
        # self.graph_outer_layout.addWidget(QLabel(self.top_label)) # top_label 일단은 지워놓자

        filter_hbox.addWidget(self.top_label)
        filter_hbox.addStretch(40)
        filter_hbox.addWidget(QLabel('filter threshold(QScore): '))
        filter_hbox.addWidget(self.filter_input)
        filter_hbox.addWidget(self.filter_button)
        filter_hbox.addWidget(self.filter_reset_button)
        top_sp.addLayout(filter_hbox)

        self.graph_outer_layout.addStretch(5)
        self.spectrum_list = QTableWidget() # spectrum list
        self.spectrum_list.setRowCount(0)
        self.spectrum_list.setColumnCount(16)
        self.spectrum_list.itemClicked.connect(self.chkItemChanged)
        self.spectrum_list.currentItemChanged.connect(self.chkItemChanged)
        column_headers = ['FileName', 'Index', 'ScanNo', 'Title', 'PMZ', 'Charge', 'Peptide', 'CalcMass', 'SA', 'QScore', '#Ions', '#Sig', 'ppmError', 'C13', 'ExpRatio', 'ProtSites' ]
        self.spectrum_list.setHorizontalHeaderLabels(column_headers)

        self.spectrum_list_layout.addWidget(self.spectrum_list)
        top_sp.addLayout(self.spectrum_list_layout)
        
        self.terminal_btn_layout.addWidget(self.n_btn)
        self.terminal_btn_layout.addWidget(self.c_btn)
        self.terminal_btn_layout.addWidget(self.mass_error_btn)
        self.terminal_btn_layout.addStretch(20)
        self.terminal_btn_layout.addWidget(self.frag_tol_label)
        self.terminal_btn_layout.addWidget(self.frag_tol_input)
        self.terminal_btn_layout.addWidget(self.frag_tol_btn)
        bottom_sp.addLayout(self.terminal_btn_layout)
        
        self.canvas = FigureCanvas(self.fig) # mirror plot
        self.canvas.setMinimumHeight(200) # 잠시 없앰
        self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addWidget(self.canvas)
        self.graph_main_layout.addWidget(self.toolbar)
        bottom_sp.addLayout(self.graph_main_layout)

        main = QWidget()

        ## self.splitter를 위한 wrapper
        wrapper_widget1 = QWidget()
        wrapper_widget2 = QWidget()
        wrapper_widget1.setLayout(top_sp)
        wrapper_widget2.setLayout(bottom_sp)

        self.inner_sp = QSplitter()
        self.inner_sp.addWidget(wrapper_widget2)
        self.splitter.addWidget(wrapper_widget1)
        self.splitter.addWidget(self.inner_sp)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.graph_outer_layout.addWidget(self.splitter)
        self.splitter.setSizes([218, 445])
        # sp.setFrameShape(QFrame.Shape.Panel)

        main.setLayout(self.graph_outer_layout)


        return main
    
    def graph_event(self) :
        QDialog.exec(self)
    
    
        
    def chkItemChanged(self): # index를 반환 받아서 그걸로 그래프 새로 그리기

        # 해제된 항목의 색을 돌려놓기      
        if self.spectrum_list.item(self.cur_row, 0):
            for i in range(0, 16):
                item = self.spectrum_list.item(self.cur_row, i)
                item.setBackground(QColor(0, 0, 0, 0)) # alpha = 0

        self.cur_row = self.spectrum_list.currentRow()
        if self.cur_row >= 0:
            cur_query_file = self.spectrum_list.item(self.cur_row, 0).text()
        else:
            return
        self.currenst_seq = process_sequence.brace_modifications(self.result_data[self.results[0]][self.cur_row]['Peptide'])
        self.current_seq = process_sequence.remove_modifications(self.current_seq)
        self.cur_idx = int(self.spectrum_list.item(self.cur_row, 1).text())
        if self.spectrum_list.item(self.spectrum_list.currentRow(), 0):
            # row의 색깔을 바꾸기
            for i in range(0, 16):
                item = self.spectrum_list.item(int(self.spectrum_list.currentRow()), i)
                item.setBackground(QColor(72, 123, 225, 70))
        
            self.make_graph(cur_query_file, self.cur_idx)

            n_terms = terminal.make_nterm_list(self.current_seq)
            if self.n_btn.isChecked(): # n terminal 표시
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
                
            
            self.ax.set_xlim(0, n_terms[-1])

        
    
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

        # 상단 라벨 변경
        self.top_label.setText(str(filtered_number) +' / ' + str(len(self.all_qscore))+ ' spectrums (QScore threshold: ' + str(threshold) + ')')
        idx = 0
        self.cur_idx = 0
        self.spectrum_list.setRowCount(int(filtered_number))
        # 다시 테이블에 추가
        for i in range(0, len(self.results)):
            cur_result = self.result_data[self.results[i]]
            for j in range(0, len(cur_result)):
                if float(cur_result[j]['QScore']) < threshold:
                    continue

                qidx = int(cur_result[j]['Index'])
                seq = cur_result[j]['Peptide']
                charge = cur_result[j]['Charge']

                seq = process_sequence.brace_modifications(seq) # 0723
                seq = process_sequence.remove_modifications(seq)

                charge = self.data[self.filenames[i]][qidx]['charge']
                if 'TARGET' in self.result_data[self.results[i]][j]['ProtSites']:
                    match = str(self.result_data[self.results[i]][j]['ProtSites'].replace('\n', '')) + "_" + str(self.target_lib[str(seq)+'_'+str(charge)]['index'])
                else:
                    match = str(self.result_data[self.results[i]][j]['ProtSites'].replace('\n', '')) + "_" + str(self.decoy_lib[str(seq)+'_'+str(charge)]['index'])

                # item = '%5s %5s %45s %12s %20s %15s %12s %30s ' % (str(self.result_data[i]['Index']), str(self.result_data[i]['ScanNo']), str(self.data[qidx]['title']), str(self.result_data[i]['PMZ']), str(match), 'SA: '+str(self.result_data[i]['SA']), 'charge: '+str(charge), 'seq: '+str(seq))
                self.spectrum_list.setItem(idx, 0, QTableWidgetItem(self.result_data[self.results[i]][j]['File']))
                self.spectrum_list.setItem(idx, 1, QTableWidgetItem(self.result_data[self.results[i]][j]['Index']))
                self.spectrum_list.setItem(idx, 2, QTableWidgetItem(self.result_data[self.results[i]][j]['ScanNo']))
                self.spectrum_list.setItem(idx, 3, QTableWidgetItem(self.result_data[self.results[i]][j]['Title']))
                self.spectrum_list.setItem(idx, 4, QTableWidgetItem(self.result_data[self.results[i]][j]['PMZ']))
                self.spectrum_list.setItem(idx, 5, QTableWidgetItem(self.result_data[self.results[i]][j]['Charge']))
                self.spectrum_list.setItem(idx, 6, QTableWidgetItem(self.result_data[self.results[i]][j]['Peptide']))
                self.spectrum_list.setItem(idx, 7, QTableWidgetItem(self.result_data[self.results[i]][j]['CalcMass']))
                self.spectrum_list.setItem(idx, 8, QTableWidgetItem(self.result_data[self.results[i]][j]['SA']))
                self.spectrum_list.setItem(idx, 9, QTableWidgetItem(self.result_data[self.results[i]][j]['QScore']))
                self.spectrum_list.setItem(idx, 10, QTableWidgetItem(self.result_data[self.results[i]][j]['#Ions']))
                self.spectrum_list.setItem(idx, 11, QTableWidgetItem(self.result_data[self.results[i]][j]['#Sig']))
                self.spectrum_list.setItem(idx, 12, QTableWidgetItem(self.result_data[self.results[i]][j]['ppmError']))
                self.spectrum_list.setItem(idx, 13, QTableWidgetItem(self.result_data[self.results[i]][j]['C13']))
                self.spectrum_list.setItem(idx, 14, QTableWidgetItem(self.result_data[self.results[i]][j]['ExpRatio']))
                self.spectrum_list.setItem(idx, 15, QTableWidgetItem(match))

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

        # dialog의 파라미터들을 가져오기
        try:
            # 뭔가 입력이 안된 상태 -> 에러를 띄우지 않고 리턴
            if not (inputDlg.query_file_list and inputDlg.target_lib_file and inputDlg.decoy_lib_file):
                return
            
            self.filenames = inputDlg.query_file_list # 쿼리 파일들
            self.data = process_data.process_queries(self.filenames) # data: dict[filename] = {data1[idx][content], data2[][], ...}
            self.target_lib_file = inputDlg.target_lib_file
            self.decoy_lib_file = inputDlg.decoy_lib_file
            self.frag_tol = inputDlg.frag_tol_value
        
        except:
            return

        try:
            # library scan
            self.target_lib = lib_scanner.lib_scanner(self.target_lib_file)
            self.decoy_lib = lib_scanner.lib_scanner(self.decoy_lib_file)

            ## 여기다가 deephos를 실행을 시켜놓고 결과가 돌아오면
            self.results = []
            for q in self.filenames:
                self.results.append(q.split('.')[0]+'_deephos.tsv')
            self.result_data = process_data.process_results(self.results)

            self.set_items_in_table()

            self.frag_tol_input.setText(str(self.frag_tol))
            self.make_summary()

        except:
            QMessageBox.warning(self,'Error','Something went wrong😵‍💫')
        
    def openConfigDlg(self):
        configInfo = f'''
Files: {self.filenames}
peptide tolerance:
fragment tolerance: {self.frag_tol}
C13 isotope tolerance:
'''
        QMessageBox.information(self, 'config', configInfo)



    def toggle_spectrum_list(self):
        if self.splitter.sizes()[0] == 0: # 지금은 안보니까 보이게 하기
            self.splitter.setSizes([218, 445])
        else: ## 보이니까 가리기
            self.splitter.setSizes([0, 550])


    def set_items_in_table(self):
        qnum = 0
        for r in self.results:
            qnum += len(self.result_data[r])
        self.spectrum_list.setRowCount(qnum)
        # self.spectrum_list.setColumnCount(16)

        for i, r in enumerate(self.results):
            cur_file_list = self.result_data[r] # 리스트
            for i in range(len(cur_file_list)):
                data_item = cur_file_list[i]
                # mapping
                # self.data[data_item['File']][int(data_item['Index'])]['seq'] = data_item['Peptide']
                # self.data[data_item['File']][int(data_item)['Index']]['charge'] = data_item['Charge']
                query_filename = r.split('_deephos')[0] + '.mgf'
                self.data[query_filename][int(data_item['Index'])]['seq'] = data_item['Peptide']
                self.data[query_filename][int(data_item['Index'])]['charge'] = data_item['Charge']

                # data_item 넣기
                charge = data_item['Charge']
                seq = data_item['Peptide']

                seq = process_sequence.brace_modifications(seq) # 0723
                seq = process_sequence.remove_modifications(seq)


                if 'TARGET' in data_item['ProtSites']:
                    match = str(data_item['ProtSites'].replace('\n', '')) + "_" + str(self.target_lib[str(seq)+'_'+str(charge)]['index'])
                else:
                    match = str(data_item['ProtSites'].replace('\n', '')) + "_" + str(self.decoy_lib[str(seq)+'_'+str(charge)]['index'])

                self.spectrum_list.setItem(i, 0, QTableWidgetItem(data_item['File']))
                self.spectrum_list.setItem(i, 1, QTableWidgetItem(data_item['Index']))
                self.spectrum_list.setItem(i, 2, QTableWidgetItem(data_item['ScanNo']))
                self.spectrum_list.setItem(i, 3, QTableWidgetItem(data_item['Title']))
                self.spectrum_list.setItem(i, 4, QTableWidgetItem(data_item['PMZ']))
                self.spectrum_list.setItem(i, 5, QTableWidgetItem(data_item['Charge']))
                self.spectrum_list.setItem(i, 6, QTableWidgetItem(data_item['Peptide']))
                self.spectrum_list.setItem(i, 7, QTableWidgetItem(data_item['CalcMass']))
                self.spectrum_list.setItem(i, 8, QTableWidgetItem(data_item['SA']))
                self.spectrum_list.setItem(i, 9, QTableWidgetItem(data_item['QScore']))
                self.spectrum_list.setItem(i, 10, QTableWidgetItem(data_item['#Ions']))
                self.spectrum_list.setItem(i, 11, QTableWidgetItem(data_item['#Sig']))
                self.spectrum_list.setItem(i, 12, QTableWidgetItem(data_item['ppmError']))
                self.spectrum_list.setItem(i, 13, QTableWidgetItem(data_item['C13']))
                self.spectrum_list.setItem(i, 14, QTableWidgetItem(data_item['ExpRatio']))
                self.spectrum_list.setItem(i, 15, QTableWidgetItem(match))
                self.spectrum_list.setRowHeight(i, 20)

                for j in range(0, 16):
                    self.spectrum_list.item(i, j).setFlags(Qt.ItemFlag.ItemIsEnabled)

                # QScore 필터링 후, make_graph 호출을 위해 필요
                qidx = str(data_item['Index'])
                self.qidx_to_ridx[qidx] = str(i)

            self.n_btn.setCheckable(True)
            self.c_btn.setCheckable(True)


    def make_summary(self):
        self.sa_decoy, self.sa_target = [], []
        self.qs_decoy, self.qs_target = [], []
        self.ppm_list = []
        
        for r in self.results:
            cur_rslts = self.result_data[r]
            for cur_item in cur_rslts:
                if "TARGET" in cur_item['ProtSites']:
                    self.sa_target.append(float(cur_item['SA']))
                    self.qs_target.append(float(cur_item['QScore']))
                    self.ppm_list.append(float(cur_item['ppmError']))
                else:
                    self.sa_decoy.append(float(cur_item['SA']))
                    self.qs_decoy.append(float(cur_item['QScore']))
                    self.ppm_list.append(float(cur_item['ppmError']))

                self.all_qscore.append(float(cur_item['QScore']))
        self.all_qscore.sort()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())