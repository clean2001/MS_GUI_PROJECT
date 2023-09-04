# 이게 진짜임
import sys, os

import numpy as np
import pandas as pd
import math
import webbrowser

from PyQt6.QtWidgets import *
import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor
import PyQt6.QtGui as QtGui
from PyQt6.QtCore import Qt, QFile, QTextStream

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import matplotlib.pyplot as plt
# import spectrum_utils.plot as sups
import draw_functions.spectrum_plot as sup # spectrum_util을 내 로컬로 가져온 것
import spectrum_utils.spectrum as sus

# custom modules
import help_functions.process_data as process_data
import help_functions.terminal as terminal
import help_functions.lib_parser as lib_parser
import help_functions.process_sequence as process_sequence
import help_functions.filtering_list as filtering_list
import control_exception
import draw_functions.mass_error as mass_error
from draw_functions import draw_terminal_line
from dlgs import (input_dialog, filtering_dialog, run_config_dialog)

from custom_class.filter import FilterInfo

import help_functions.lib_scanner as lib_scanner


sys.path.append(os.getcwd())
cur_path = os.path.dirname(os.path.realpath(__file__))


class GraphWrapperWidget(QWidget):
    def __init__(self):
        super().__init__()

# _mirror plot custom widget_ start
class MirrorFigureCanvas(FigureCanvas):
    lock = None
    def __init__(self, figure=None, app=None):
        self.myapp = app
        figure.canvas.mpl_connect("button_press_event", self.click)
        figure.canvas.mpl_connect("button_release_event", self.release)
        figure.canvas.mpl_connect("motion_notify_event", self.moved)
        self.start, self.end = 0, 0
        super().__init__(figure = figure)

    def mouseDoubleClickEvent(self, event):
        plt.xlim([0, self.myapp.max_peptide_mz])
        self.myapp.graph_x_start, self.myapp.graph_x_end = -1, -1
        self.myapp.canvas.draw()
        return super().mouseDoubleClickEvent(event)

    def click(self, event):
        self.start = event.xdata

    def release(self, event):
        self.end = event.xdata
        if self.end < self.start:
            tmp = self.start
            self.start = self.end
            self.end = tmp
        
        if self.end - self.start <= 5:
            return
        
        plt.xlim([self.start, self.end])
        self.myapp.graph_x_start, self.myapp.graph_x_end = self.start, self.end
        self.myapp.canvas.draw()
    
    def moved(self, event):
        x, y = event.xdata, event.ydata
        if not (x and y):
            self.myapp.loc_label.setText("")
            return

        self.myapp.loc_label.setText("m/z = "+str(round(x, 2))+",   intensity = "+str(abs(round(y, 2))))

# _mirror plot custom widget_ end



class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # load하는 코드를 삭제
        # with open('./data/target_lib.json') as f:
        #     self.target_lib = json.load(f) # target lib의 딕셔너리. key: seq_charge / value: offset
        # with open('./data/decoy_lib.json') as f:
        #     self.decoy_lib = json.load(f) # decoy lib의 딕셔너리. key: seq_charge / value: offset

        self.current_seq='A'
        self.top_seq = 'A'
        self.frag_tol = 0.02
        self.peptide_tol = 10
        self.filtering_threshold = 0
        self.cur_idx = -1
        self.all_qscore = []
        self.qidx_to_ridx = dict()
        self.spectrum_query = None
        self.spectrum_answer = None
        self.is_list_visible = True
        self.cur_row = 0
        self.target_lib_file = None
        self.decoy_lib_file = None
        self.data = dict() # filename : 파싱된 결과(dict) 리스트
        self.filenames = []
        self.loc_label = QLabel("") #그래프 내에 현재 마우스 위치 정보 label
        self.max_peptide_mz = 100 # 초기값 100
        self.filter_info = FilterInfo(self) # filtering 정보 (싱클톤 인스턴스)
        self.results = []
        self.graph_x_start, self.graph_y_start = -1, -1 ## 그래프의 확대, (x axis 값, -1 -1 이면 기본크기)
        self.c13_isotope_tol_min, self.c13_isotope_tol_max = 0, 0


        spectrum_query = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_query.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
        spectrum_answer = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_answer.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
        self.fig,self.ax = plt.subplots(figsize=(15, 9))

        sup.mirror(spectrum_answer, spectrum_answer, ax=self.ax)
        self.sa_target, self.sa_decoy = [], []


        self.main_widget = QWidget() # Make main window
        self.setCentralWidget(self.main_widget) # Main Window set center
        self.resize(1200, 800) # Main Window Size

        self.n_btn = QPushButton('N', self)
        self.c_btn = QPushButton('C', self)
        self.mass_error_btn = QCheckBox('mass error', self)
        self.n_btn.setCheckable(False)
        self.c_btn.setCheckable(False)
        self.mass_error_btn.setCheckable(False)

        self.peptide_change_text_box = QLineEdit()
        self.peptide_change_text_box.setMinimumWidth(280)
        self.peptide_change_btn = QPushButton('apply', self)
        self.peptide_reset_btn = QPushButton('reset', self)
        self.peptide_change_btn.clicked.connect(self.peptide_change_clicked)
        self.peptide_reset_btn.clicked.connect(self.peptide_reset_clicked)

        self.switch_btn = QCheckBox('switch mirror', self)
        self.switch_btn.setCheckable(False)
        self.switch_status = QLabel('top: query / bottom: library')

        self.n_btn.toggled.connect(self.n_button)
        self.c_btn.toggled.connect(self.c_button)
        self.mass_error_btn.toggled.connect(self.mass_error_btn_clicked)
        self.switch_btn.toggled.connect(self.switch_clicked)

        # filtering reset btn
        self.filter_reset_button = QPushButton('filter reset', self)
        self.filter_reset_button.clicked.connect(self.filter_reset)

        # tolerance
        self.frag_tol_input = QLineEdit()
        self.frag_tol_input.setText('0.02')
        self.frag_tol_input.setFixedWidth(50)
        self.frag_tol_btn = QPushButton('submit', self)
        self.frag_tol_btn.clicked.connect(self.change_tol)
        self.frag_tol_label = QLabel('tolerance(Da): ')


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
        runAction.triggered.connect(self.open_input_dlg)
        
        configAction = QAction(QIcon(cur_path), 'View Config', self)
        configAction.triggered.connect(self.open_config_dlg)

        docAction = QAction(QIcon(cur_path), 'Document', self)
        docAction.triggered.connect(lambda: webbrowser.open('https://github.com/clean2001/MS_GUI_PROJECT#spectrum-library-search-program'))

        # 리스트 단축키
        listAction = QAction(QIcon(cur_path +'ui\\image\\exit.png'), 'Hide/Show List', self)
        listAction.setShortcut('Ctrl+J')
        listAction.triggered.connect(self.toggle_spectrum_list)
        ##

        # _list filtering_
        filteringAction = QAction(QIcon(cur_path +'ui\\image\\exit.png'), 'Filter', self)
        filteringAction.triggered.connect(self.filtering_action)
        # _list filtering_ end

        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        filemenu = self.menubar.addMenu('&File')
        runmenu = self.menubar.addMenu('&Run')
        viewmenu = self.menubar.addMenu('&View')
        docmenu = self.menubar.addMenu('&Document')

        filemenu.addAction(openFileAction)
        filemenu.addAction(exitAction)
        filemenu.addAction(listAction)
        runmenu.addAction(runAction)
        runmenu.addAction(configAction)
        docmenu.addAction(docAction)
        viewmenu.addAction(filteringAction)
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
            plt.close()
            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))

            if self.switch_btn.isChecked():
                self.fig = mass_error.mass_error_plot(self.spectrum_answer, self.spectrum_query)
            else:
                self.fig = mass_error.mass_error_plot(self.spectrum_query, self.spectrum_answer)
            
            self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
            # self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            self.graph_main_layout.addWidget(self.canvas)
            # self.graph_main_layout.addWidget(self.toolbar)

            self.canvas.draw()
        else:
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()
            self.make_graph(query_filename, self.cur_idx)

        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n, c = 4, 5, -0.8, -0.9
        if self.n_btn.isChecked(): # 방금 체크 됨
            self.n_btn.setStyleSheet("background-color: #191970")
            n_terms = terminal.make_nterm_list(self.current_seq)
            draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


        if self.c_btn.isChecked():
            c_terms = terminal.make_cterm_list(self.current_seq)
            draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

        self.canvas.draw()
        

    def switch_clicked(self):
        query_filename = self.spectrum_list.item(self.cur_row, 0).text()

        if self.switch_btn.isChecked(): # 라이브러리가 위로
            self.switch_status.setText('top: library / bottom: query')
        else:
            self.switch_status.setText('top: query / bottom: library')

        self.make_graph(query_filename, self.cur_idx)
        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n, c = 4, 5, -0.8, -0.9

        if self.n_btn.isChecked(): # 방금 체크 됨
            self.n_btn.setStyleSheet("background-color: #191970")
            n_terms = terminal.make_nterm_list(self.current_seq)
            draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


        if self.c_btn.isChecked():
            c_terms = terminal.make_cterm_list(self.current_seq)
            draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

            
        self.canvas.draw() # refresh plot
    
    def n_button(self):
        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n , c = 4, 5, -0.8, -0.9

        if self.n_btn.isChecked(): # 방금 체크 됨
            self.n_btn.setStyleSheet("background-color: #191970")
            n_terms = terminal.make_nterm_list(self.current_seq)
            draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)
            
            self.canvas.draw() # refresh plot
        else:
            self.n_btn.setStyleSheet("background-color: #1E90FF")
            plt.close()
            
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()
            self.make_graph(query_filename, self.cur_idx)

            if self.c_btn.isChecked():
                c_terms = terminal.make_cterm_list(self.current_seq)
                draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

            if self.graph_x_start != -1 and self.graph_x_end != -1:
                plt.xlim(self.graph_x_start, self.graph_x_end)

   
    def c_button(self):
        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n , c = 4, 5, -0.8, -0.9

        if self.c_btn.isChecked():
            self.c_btn.setStyleSheet("background-color: #800000")#CD5C5C
            c_terms = terminal.make_cterm_list(self.current_seq)
            draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

        
            self.canvas.draw() # refresh plot
        else:
            self.c_btn.setStyleSheet("background-color: #CD5C5C")

            query_filename = self.spectrum_list.item(self.cur_row, 0).text()
            self.make_graph(query_filename, self.cur_idx)

            if self.n_btn.isChecked():
                n_terms = terminal.make_nterm_list(self.current_seq)
                draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)

            if self.graph_x_start != -1 and self.graph_x_end != -1:
                plt.xlim([self.graph_x_start, self.graph_x_end])
            self.canvas.draw() # refresh plot

    def make_graph(self, filename:str, qidx:int):
        ridx = int(self.qidx_to_ridx[filename + '_' + str(qidx)])
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
        self.spectrum_query = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, query_mz))),
            np.array(list(map(float, query_intensity)))
        )
        self.spectrum_query.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")

        # 이부분에서 offset으로 라이브러리를 열어서 mz, intensity를 파싱해서 리턴
        lib_mz, lib_intensity = lib_parser.parse_lib(lib_file, lib['num_peaks'], lib['offset'])
        
        self.spectrum_answer = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, lib_mz))),
            np.array(list(map(float, lib_intensity)))
        )
        self.spectrum_answer.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")
        plt.close()

        ## mass error를 그리는 부분
        if self.mass_error_btn.isChecked():
            plt.close()
            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))

            if self.switch_btn.isChecked():
                self.fig = mass_error.mass_error_plot(self.spectrum_answer, self.spectrum_query)
            else:
                self.fig = mass_error.mass_error_plot(self.spectrum_query, self.spectrum_answer)

            self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
            self.graph_main_layout.addWidget(self.canvas)

            
            self.canvas.draw()
            return
        
        ##

        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        if self.switch_btn.isChecked():
            sup.mirror(self.spectrum_answer, self.spectrum_query, ax=self.ax)
        else:
            sup.mirror(self.spectrum_query, self.spectrum_answer, ax=self.ax)

        for i in reversed(range(self.graph_main_layout.count())): 
            obj = self.graph_main_layout.itemAt(i).widget()
            if obj is not None:
                obj.deleteLater()

        self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
        # self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addWidget(self.canvas)
        # self.graph_main_layout.addWidget(self.toolbar)
        if self.graph_x_start != -1 and self.graph_x_end != -1:
            plt.xlim([self.graph_x_start, self.graph_x_end])
        
        self.canvas.draw()

        
    def make_graph_with_top_seq(self, filename:str, qidx:int):
        ridx = int(self.qidx_to_ridx[filename + '_' + str(qidx)])
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

        seq = self.top_seq
        seq = process_sequence.brace_modifications(self.top_seq)
        
        self.current_seq = seq #terminal btn을 눌렀을 때 다시 그리기 위해 저장해놓는 것
        query_filename = self.spectrum_list.item(self.cur_row, 0).text()
        query_mz, query_intensity = lib_parser.parse_spectrum(query_filename, int(dict['offset']))
        self.spectrum_query = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, query_mz))),
            np.array(list(map(float, query_intensity)))
        )
        self.spectrum_query.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")

        # 이부분에서 offset으로 라이브러리를 열어서 mz, intensity를 파싱해서 리턴
        lib_mz, lib_intensity = lib_parser.parse_lib(lib_file, lib['num_peaks'], lib['offset'])
        
        self.spectrum_answer = sus.MsmsSpectrum(
            dict['title'],
            float(dict['pepmass']),
            int(dict['charge']),
            np.array(list(map(float, lib_mz))),
            np.array(list(map(float, lib_intensity)))
        )
        self.spectrum_answer.annotate_proforma(seq, self.frag_tol, "Da", ion_types="by")
        plt.close()

        ## mass error를 그리는 부분
        if self.mass_error_btn.isChecked():
            plt.close()
            for i in reversed(range(self.graph_main_layout.count())): 
                obj = self.graph_main_layout.itemAt(i).widget()
                if obj is not None:
                    obj.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(15, 9))

            if self.switch_btn.isChecked():
                self.fig = mass_error.mass_error_plot(self.spectrum_answer, self.spectrum_query)
            else:
                self.fig = mass_error.mass_error_plot(self.spectrum_query, self.spectrum_answer)

            self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
            self.graph_main_layout.addWidget(self.canvas)

            
            self.canvas.draw()
            return
        
        ##

        self.fig, self.ax = plt.subplots(figsize=(15, 9))
        if self.switch_btn.isChecked():
            sup.mirror(self.spectrum_answer, self.spectrum_query, ax=self.ax)
        else:
            sup.mirror(self.spectrum_query, self.spectrum_answer, ax=self.ax)

        for i in reversed(range(self.graph_main_layout.count())): 
            obj = self.graph_main_layout.itemAt(i).widget()
            if obj is not None:
                obj.deleteLater()

        self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
        # self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addWidget(self.canvas)
        # self.graph_main_layout.addWidget(self.toolbar)
        if self.graph_x_start != -1 and self.graph_x_end != -1:
            plt.xlim([self.graph_x_start, self.graph_x_end])
        
        self.canvas.draw()

    def peptide_change_clicked(self):
        peptide_seq, query_filename = '', ''
        try:
            peptide_seq = self.peptide_change_text_box.text()
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()

            self.make_graph(query_filename, self.cur_idx)

            s, e, n, c = 0, 1, 1.0, 1.1
            if self.mass_error_btn.isChecked():
                s, e, n, c = 4, 5, -0.8, -0.9

            n_terms = terminal.make_nterm_list(peptide_seq)
            if self.n_btn.isChecked(): # n terminal 표시
                draw_terminal_line.draw_nterm_line(n_terms, peptide_seq, s, e, n)


            if self.c_btn.isChecked(): # c terminal 표시
                c_terms = terminal.make_cterm_list(peptide_seq)
                draw_terminal_line.draw_cterm_line(c_terms, peptide_seq, s, e, c)
        except:
            self.peptide_change_text_box.setText(self.top_seq)

            s, e, n, c = 0, 1, 1.0, 1.1
            if self.mass_error_btn.isChecked():
                s, e, n, c = 4, 5, -0.8, -0.9

            n_terms = terminal.make_nterm_list(self.top_seq)
            if self.n_btn.isChecked(): # n terminal 표시
                draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


            if self.c_btn.isChecked(): # c terminal 표시
                c_terms = terminal.make_cterm_list(self.top_seq)
                draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

            return
        
        self.current_seq, self.top_seq = peptide_seq, peptide_seq


    def peptide_reset_clicked(self):
        peptide_seq, query_filename = '', ''
        try:    
            peptide_seq = self.spectrum_list.item(self.cur_row, 6).text()
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()

        except:
            return
        
        self.make_graph(query_filename, self.cur_idx)

        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n, c = 4, 5, -0.8, -0.9

        n_terms = terminal.make_nterm_list(peptide_seq)
        if self.n_btn.isChecked(): # n terminal 표시
            draw_terminal_line.draw_nterm_line(n_terms, peptide_seq, s, e, n)


        if self.c_btn.isChecked(): # c terminal 표시
            c_terms = terminal.make_cterm_list(peptide_seq)
            draw_terminal_line.draw_cterm_line(c_terms, peptide_seq, s, e, c)
        
        self.top_seq, self.current_seq = peptide_seq, peptide_seq
        self.peptide_change_text_box.setText(self.top_seq)



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

        s, e, n, c = 0, 1, 1.0, 1.1
        if self.mass_error_btn.isChecked():
            s, e, n, c = 4, 5, -0.8, -0.9

        n_terms = terminal.make_nterm_list(self.current_seq)
        if self.n_btn.isChecked(): # n terminal 표시
            draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


        if self.c_btn.isChecked(): # c terminal 표시
            c_terms = terminal.make_cterm_list(self.current_seq)
            draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

        


    def ui1(self):
        self.graph_outer_layout = QVBoxLayout()
        self.graph_main_layout = QVBoxLayout() # 캔버스와 툴바가 들어가는 부분, 바뀌는 부분
        self.spectrum_list_layout = QVBoxLayout() # 파일을 열었을 때 바뀌는 부분
        self.terminal_btn_layout = QHBoxLayout()
        filter_hbox = QHBoxLayout()

        top_sp = QVBoxLayout()
        bottom_sp = QVBoxLayout()


        self.splitter = QSplitter()

        self.top_label = QLabel('0 spectra')

        filter_hbox.addWidget(self.top_label)
        filter_hbox.addStretch(40)
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
        self.terminal_btn_layout.addStretch(5)
        self.terminal_btn_layout.addWidget(self.peptide_change_text_box)
        self.terminal_btn_layout.addWidget(self.peptide_change_btn)
        self.terminal_btn_layout.addWidget(self.peptide_reset_btn)
        self.terminal_btn_layout.addStretch(5)
        self.terminal_btn_layout.addWidget(self.switch_btn)
        self.terminal_btn_layout.addWidget(self.switch_status)
        self.terminal_btn_layout.addStretch(4)
        self.terminal_btn_layout.addWidget(self.mass_error_btn)
        self.terminal_btn_layout.addStretch(1)
        self.terminal_btn_layout.addWidget(self.frag_tol_label)
        self.terminal_btn_layout.addWidget(self.frag_tol_input)
        self.terminal_btn_layout.addWidget(self.frag_tol_btn)
        bottom_sp.addLayout(self.terminal_btn_layout)
        
        self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
        self.canvas.setMinimumHeight(200) # 잠시 없앰
        # self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
        self.graph_main_layout.addWidget(self.canvas)
        # self.graph_main_layout.addWidget(self.toolbar)
        bottom_sp.addLayout(self.graph_main_layout)

        main = QWidget()

        ## self.splitter를 위한 wrapper
        wrapper_widget1 = QWidget()
        self.wrapper_widget2 = GraphWrapperWidget()
        wrapper_widget1.setLayout(top_sp)
        self.wrapper_widget2.setLayout(bottom_sp)

        self.inner_sp = QSplitter()
        self.inner_sp.addWidget(self.wrapper_widget2)
        self.splitter.addWidget(wrapper_widget1)
        self.splitter.addWidget(self.inner_sp)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.graph_outer_layout.addWidget(self.splitter)
        self.splitter.setSizes([218, 445])
        # sp.setFrameShape(QFrame.Shape.Panel)
        self.graph_outer_layout.addWidget(self.loc_label)

        # 더블클릭하면 home으로 돌아감

        main.setLayout(self.graph_outer_layout)


        return main
    
    def graph_event(self) :
        QDialog.exec(self)
    
    
        
    def chkItemChanged(self): # index를 반환 받아서 그걸로 그래프 새로 그리기
        self.graph_x_start, self.graph_x_end = -1, -1

        # 해제된 항목의 색을 돌려놓기      
        if self.spectrum_list.item(self.cur_row, 0):
            for i in range(0, 16):
                item = self.spectrum_list.item(self.cur_row, i)
                item.setBackground(QColor(0, 0, 0, 0)) # alpha = 0

        self.cur_row = self.spectrum_list.currentRow()

        if self.spectrum_list.item(self.cur_row, 1):
            qidx = int(self.spectrum_list.item(self.cur_row, 1).text())

        if self.cur_row >= 0:
            cur_query_file = self.spectrum_list.item(self.cur_row, 0).text()
            self.n_btn.setCheckable(True)
            self.c_btn.setCheckable(True)
            self.mass_error_btn.setCheckable(True)
            self.switch_btn.setCheckable(True)

        else:
            return
        query_filename = self.spectrum_list.item(self.cur_row, 0).text()
        result_filename = query_filename.split('.')[0] + '_deephos.tsv'
        self.currenst_seq = process_sequence.brace_modifications(self.result_data[result_filename][int(self.qidx_to_ridx[query_filename + '_' + str(qidx)])]['Peptide'])
        self.current_seq = process_sequence.remove_modifications(self.current_seq)
        self.cur_idx = qidx
        if self.spectrum_list.item(self.spectrum_list.currentRow(), 0):
            # row의 색깔을 바꾸기
            for i in range(0, 16):
                item = self.spectrum_list.item(int(self.spectrum_list.currentRow()), i)
                item.setBackground(QColor(72, 123, 225, 70))
        
            self.make_graph(cur_query_file, self.cur_idx)
            s, e, n, c = 0, 1, 1.0, 1.1
            if self.mass_error_btn.isChecked():
                s, e, n, c = 4, 5, -0.8, -0.9

            n_terms = terminal.make_nterm_list(self.current_seq)
            if self.n_btn.isChecked(): # n terminal 표시
                draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


            if self.c_btn.isChecked(): # c terminal 표시
                c_terms = terminal.make_cterm_list(self.current_seq)
                draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)
            
            self.ax.set_xlim(0, n_terms[-1])
            self.max_peptide_mz = n_terms[-1]

            self.peptide_change_text_box.setText(self.top_seq)

    
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
        # self.sa_ax.set_xlabel('SA')
        # self.sa_ax.set_ylabel('# of PSMs')

        # QScore
        self.qs_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.qs_ax = self.qs_canvas.figure.subplots()
        self.qs_ax.hist([])
        # self.qs_ax.set_xlabel('QScore')
        # self.qs_ax.set_ylabel('# of PSMs')

        # ppm error
        self.ppm_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.ppm_ax = self.ppm_canvas.figure.subplots()
        self.ppm_ax.boxplot([])
        # self.ppm_ax.set_xlabel('target')
        # self.ppm_ax.set_ylabel('Mass Deviation(ppm)')

        # number of charge
        self.charge_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.charge_ax = self.charge_canvas.figure.subplots()
        self.charge_ax.hist([])
        self.charge_ax.set_ylabel('# of charge')


        # peptide length
        self.plength_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.plength_ax = self.plength_canvas.figure.subplots()
        self.plength_ax.hist([])
        self.plength_ax.set_ylabel('# of spectra')
        # self.plength_ax.set_xlabel('peptide length')


        self.summary_layout.addWidget(self.sa_canvas, 0, 0)
        self.summary_layout.addWidget(self.qs_canvas, 0, 1)
        self.summary_layout.addWidget(self.ppm_canvas, 0, 2)
        self.summary_layout.addWidget(self.charge_canvas, 1, 0)
        self.summary_layout.addWidget(self.plength_canvas, 1, 1)



        main.setLayout(self.summary_layout)
        return main
    
    def check_spectrum_item(self, cur):
        fi = self.filter_info

        # 1. 파일 이름을 필터링 -> str
        if fi.filename:
            if not fi.filename in cur['File']:
                return False
        # 2. 인덱스 필터링 -> int 
        if fi.index:
            if int(fi.index[0]) > 0 and int(cur['Index']) < int(fi.index[0]):
                return False
            if int(fi.index[1]) > 0 and int(cur['Index']) > int(fi.index[1]):
                return False
        # 3. ScanNo 필터링 -> int
        if fi.scanno:
            if int(fi.scanno[0]) > 0 and int(cur['ScanNo']) < int(fi.scanno[0]):
                return False
            if int(fi.scanno[1]) > 0 and int(cur['ScanNo']) > int(fi.scanno[1]):
                return False
            
        # 4. Title 필터링 -> str
        if fi.title:
            if not fi.title in cur['Title']:
                return False
        
        # 5. PMZ 필터링 -> float
        if fi.pmz:
            if float(fi.pmz[0]) > 0 and float(cur['PMZ']) < float(fi.pmz[0]):
                return False
            if float(fi.pmz[1]) > 0 and float(cur['PMZ']) > float(fi.pmz[1]):
                return False
            
        # 6. Charge 필터링 -> int
        if fi.charge:
            if int(fi.charge[0]) > 0 and int(cur['Charge']) < int(fi.charge[0]):
                return False
            if int(fi.charge[1]) > 0 and int(cur['Charge']) > int(fi.charge[1]):
                return False

        # 7. Peptide 필터링 -> str 
        if fi.peptide:
            if not fi.peptide in cur['Peptide']:
                return False
            
        # 8. CalcMass 필터링 -> float
        if fi.calcmass:
            if float(fi.calcmass[0]) > 0 and float(cur['CalcMass']) < float(fi.calcmass[0]):
                return False
            if float(fi.calcmass[1]) > 0 and float(cur['CalcMass']) > float(fi.calcmass[1]):
                return False
            
        # 9. SA 필터링 -> float
        if fi.sa:
            if float(fi.sa[0]) > 0 and float(cur['SA']) < float(fi.sa[0]):
                return False
            if float(fi.sa[1]) > 0 and float(cur['SA']) > float(fi.sa[1]):
                return False
        
        # 10. QScore 필터링 -> float
        if fi.qscore:
            if float(fi.qscore[0]) > 0 and float(cur['QScore']) < float(fi.qscore[0]):
                return False
            if float(fi.qscore[1]) > 0 and float(cur['QScore']) > float(fi.qscore[1]):
                return False
            
        # 11. #Ions 필터링 -> int
        if fi.ions:
            if int(fi.ions[0]) > 0 and int(cur['#Ions']) < int(fi.ions[0]):
                return False
            if int(fi.ions[1]) > 0 and int(cur['#Ions']) > int(fi.ions[1]):
                return False
        
        # 12. #Sig 필터링 -> int
        if fi.sig:
            if int(fi.sig[0]) > 0 and int(cur['#Sig']) < int(fi.sig[0]):
                return False
            if int(fi.sig[1]) > 0 and int(cur['#Sig']) > int(fi.sig[1]):
                return False
        
        # 13. ppmError -> float
        if fi.ppmerror:
            if float(fi.ppmerror[0]) > 0 and float(cur['ppmError']) < float(fi.ppmerror[0]):
                return False
            if float(fi.ppmerror[1]) and float(cur['ppmError']) > float(fi.ppmerror[1]):
                return False
            
        # 14. C13 -> float
        if fi.c13:
            if float(fi.c13[0]) > 0 and float(cur['C13']) < float(fi.c13[0]):
                return False
            if float(fi.c13[1]) > 0 and float(cur['C13']) > float(fi.c13[1]):
                return False

        # 15. expRatio -> float
        if fi.expratio:
            if float(fi.expratio[0]) > 0 and float(cur['ExpRatio']) < float(fi.expratio[0]):
                return False
            if float(fi.expratio[1]) > 0 and float(cur['ExpRatio']) > float(fi.expratio[1]):
                return False
        
        # 16. ProSites -> str
        if fi.protsites:
            if not fi.protsites in cur['ProtSites']:
                return False

        
        return True
    

    def refilter_spectrums(self):
        idx = 0
        self.spectrum_list.setRowCount(len(self.all_qscore))
        for i in range(0, len(self.results)):
            cur_result = self.result_data[self.results[i]]
            for j in range(0, len(cur_result)):
                if not self.check_spectrum_item(cur_result[j]):
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
                self.spectrum_list.setRowHeight(idx, 20)

                for k in range(0, 16):
                    self.spectrum_list.item(idx, k).setFlags(Qt.ItemFlag.ItemIsEnabled)

                idx += 1
        
        self.spectrum_list.setRowCount(idx)
        self.top_label.setText(str(idx) +' / ' + str(len(self.all_qscore))+ ' spectra')


    
    def filter_reset(self):
        self.filter_info.reset_all_values()
        self.set_items_in_table()
        return

    def open_input_dlg(self):
        input_dlg = input_dialog.InputDialog()
        input_dlg.exec()

        # dialog의 파라미터들을 가져오기
        try:
            # 뭔가 입력이 안된 상태 -> 에러를 띄우지 않고 리턴
            if not (input_dlg.query_file_list and input_dlg.target_lib_file and input_dlg.decoy_lib_file):
                return
            
            self.filenames = input_dlg.query_file_list # 쿼리 파일들
            self.data = process_data.process_queries(self.filenames) # data: dict[filename] = {data1[idx][content], data2[][], ...}
            self.target_lib_file = input_dlg.target_lib_file
            self.decoy_lib_file = input_dlg.decoy_lib_file
            self.frag_tol = input_dlg.frag_tol_value
            self.peptide_tol = input_dlg.pept_tol_value
            self.c13_isotope_tol_min = input_dlg.isotope_tol_value_min
            self.c13_isotope_tol_max = input_dlg.isotope_tol_value_max
        
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

        except Exception as e:
            print('[Debug] error is\n', e)
            QMessageBox.warning(self,'Error','Something went wrong😵‍💫')
    

    def open_config_dlg(self):
        config_dlg = run_config_dialog.RunConfigDlg(self)
        config_dlg.exec()


    def filtering_action(self):
        filter_dlg = filtering_dialog.FilterDialog(self.filter_info)
        filter_dlg.exec()

        # 정보 바꾸기
        print('main, line 870. filname:', self.filter_info.filename)
        self.refilter_spectrums()


        return
        
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
        
        rowcnt = 0
        for i, r in enumerate(self.results):
            cur_file_list = self.result_data[r] # 리스트
            for j in range(len(cur_file_list)):
                data_item = cur_file_list[j]

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

                self.spectrum_list.setItem(rowcnt, 0, QTableWidgetItem(data_item['File']))
                self.spectrum_list.setItem(rowcnt, 1, QTableWidgetItem(data_item['Index']))
                self.spectrum_list.setItem(rowcnt, 2, QTableWidgetItem(data_item['ScanNo']))
                self.spectrum_list.setItem(rowcnt, 3, QTableWidgetItem(data_item['Title']))
                self.spectrum_list.setItem(rowcnt, 4, QTableWidgetItem(data_item['PMZ']))
                self.spectrum_list.setItem(rowcnt, 5, QTableWidgetItem(data_item['Charge']))
                self.spectrum_list.setItem(rowcnt, 6, QTableWidgetItem(data_item['Peptide']))
                self.spectrum_list.setItem(rowcnt, 7, QTableWidgetItem(data_item['CalcMass']))
                self.spectrum_list.setItem(rowcnt, 8, QTableWidgetItem(data_item['SA']))
                self.spectrum_list.setItem(rowcnt, 9, QTableWidgetItem(data_item['QScore']))
                self.spectrum_list.setItem(rowcnt, 10, QTableWidgetItem(data_item['#Ions']))
                self.spectrum_list.setItem(rowcnt, 11, QTableWidgetItem(data_item['#Sig']))
                self.spectrum_list.setItem(rowcnt, 12, QTableWidgetItem(data_item['ppmError']))
                self.spectrum_list.setItem(rowcnt, 13, QTableWidgetItem(data_item['C13']))
                self.spectrum_list.setItem(rowcnt, 14, QTableWidgetItem(data_item['ExpRatio']))
                self.spectrum_list.setItem(rowcnt, 15, QTableWidgetItem(match))
                self.spectrum_list.setRowHeight(rowcnt, 20)

                for k in range(0, 16):
                    self.spectrum_list.item(rowcnt, k).setFlags(Qt.ItemFlag.ItemIsEnabled)

                # QScore 필터링 후, make_graph 호출을 위해 필요
                qidx = str(data_item['File'])+ '_' + str(data_item['Index'])
                self.qidx_to_ridx[qidx] = str(j)

                rowcnt += 1

        # colum들의 크기를 조정
        self.spectrum_list.setColumnWidth(1, 60) # index
        self.spectrum_list.setColumnWidth(2, 60) # scanno
        self.spectrum_list.setColumnWidth(4, 80) # pmz
        self.spectrum_list.setColumnWidth(5, 60) # charge
        self.spectrum_list.setColumnWidth(6, 280) # peptide
        self.spectrum_list.setColumnWidth(7, 80) # calcmass
        self.spectrum_list.setColumnWidth(8, 70) # sa
        self.spectrum_list.setColumnWidth(9, 70) # QScore
        self.spectrum_list.setColumnWidth(10, 60) # ions
        self.spectrum_list.setColumnWidth(11, 60) # sig
        self.spectrum_list.setColumnWidth(12, 70) # ppmerror
        self.spectrum_list.setColumnWidth(13, 60) # C13
        self.spectrum_list.setColumnWidth(14, 60) # expratio
        self.spectrum_list.setColumnWidth(15, 120) # protsites


        self.top_label.setText(str(rowcnt) +' / ' + str(rowcnt)+ ' spectra')


    def make_summary(self):
        self.sa_decoy, self.sa_target = [], []
        self.qs_decoy, self.qs_target = [], []
        self.ppm_list = []
        self.plength = [0 for i in range(61)]
        self.charge_list = [0 for i in range(4)] # 1, 2, 3, 4
        
        for r in self.results:
            cur_rslts = self.result_data[r]
            for cur_item in cur_rslts:
                if "TARGET" in cur_item['ProtSites']:
                    self.sa_target.append(float(cur_item['SA']))
                    self.qs_target.append(float(cur_item['QScore']))
                else:
                    self.sa_decoy.append(float(cur_item['SA']))
                    self.qs_decoy.append(float(cur_item['QScore']))

                self.ppm_list.append(float(cur_item['ppmError']))
                self.all_qscore.append(float(cur_item['QScore']))
                if len(cur_item['Peptide']) >= 60:
                    self.plength[60] += 1
                else:
                    self.plength[len(cur_item['Peptide'])] += 1

                
                if int(cur_item['Charge']) >= 4:
                    self.charge_list[3] += 1
                else:
                    self.charge_list[int(cur_item['Charge'])-1] += 1
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

        cx = np.arange(4)
        charge_xticks = [str(i) for i in range(1, 5)]
        charge_xticks[-1] = '4+'
        self.charge_ax.bar(cx, self.charge_list)
        self.charge_ax.set_xticks(cx, charge_xticks)
        self.charge_ax.set_title('charge')

        x = np.arange(61)
        plen_xticks = ['' for i in range(61)]
        for i in range(len(plen_xticks)):
            if i % 10 == 0:
                plen_xticks[i] = str(i)
        plen_xticks[-1] = '60+'
        
        self.plength_ax.bar(x, self.plength)
        self.plength_ax.set_xticks(x, plen_xticks)
        self.plength_ax.set_title('peptide length')


        labels= ['target', 'decoy']
        handles = [Rectangle((0,0),1,1,color=c) for c in ['#3669CF', '#FF9595']]
        self.sa_ax.legend(handles, labels)
        self.sa_canvas.draw()
        self.qs_canvas.draw()
        self.ppm_canvas.draw()
        self.charge_canvas.draw()
        self.plength_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())