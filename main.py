import sys, os
import time
import json

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
        if self.end == None or self.start == None:
            return
        
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
        
        self.current_seq, self.top_seq='A', 'A'
        self.frag_tol, self.peptide_tol = 0.02, 10
        self.filtering_threshold = 0
        self.cur_idx, self.cur_row = -1, 0
        self.all_qscore, self.filenames, self.results = [], [], []
        self.spectrum_query, self.spectrum_answer = None, None
        self.is_list_visible = True
        self.target_lib_files, self.decoy_lib_files = None, None
        self.data,self.qidx_to_ridx = dict(), dict() # filename : 파싱된 결과(dict) 리스트
        self.loc_label = QLabel("") #그래프 내에 현재 마우스 위치 정보 label
        self.max_peptide_mz = 100 # 초기값 100
        self.filter_info = FilterInfo(self) # filtering 정보 (싱클톤 인스턴스)
        self.graph_x_start, self.graph_y_start = -1, -1 ## 그래프의 확대, (x axis 값, -1 -1 이면 기본크기)
        self.c13_isotope_tol_min, self.c13_isotope_tol_max = 0, 0
        self.target_lib, self.decoy_lib = dict(), dict()
        self.project_file_name = None
        self.top_graph_label, self.bottom_graph_label = QLabel("top: "), QLabel("Bottom: ")
        self.match_info_layout = QHBoxLayout()



        spectrum_query = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_query.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
        spectrum_answer = sus.MsmsSpectrum('', 0, 0, [], [])
        spectrum_answer.annotate_proforma('A', self.frag_tol, "Da", ion_types="by")
        self.fig,self.ax = plt.subplots(figsize=(15, 9))

        sup.mirror(spectrum_answer, spectrum_answer, ax=self.ax)
        self.sa_target, self.sa_decoy = [0 for i in range(50)], [0 for i in range(50)]


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
        self.peptide_change_btn.setCheckable(False)
        self.peptide_change_btn.setCheckable(False)


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

        newProjectAction = QAction(QIcon(cur_path), 'New Project', self)
        newProjectAction.triggered.connect(self.open_input_dlg)

        openProjectAction = QAction(QIcon(cur_path), 'Open Project', self)
        openProjectAction.triggered.connect(self.open_project_dlg)
        
        configAction = QAction(QIcon(cur_path), 'View Config', self)
        configAction.triggered.connect(self.open_config_dlg)

        docAction = QAction(QIcon(cur_path), 'Document', self)
        docAction.triggered.connect(lambda: webbrowser.open('https://github.com/clean2001/MS_GUI_PROJECT#devi-gui'))

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
        viewmenu = self.menubar.addMenu('&View')
        docmenu = self.menubar.addMenu('&Document')

        filemenu.addAction(newProjectAction)
        filemenu.addAction(openProjectAction)
        filemenu.addAction(configAction)
        filemenu.addAction(exitAction)
        viewmenu.addAction(filteringAction)
        viewmenu.addAction(listAction)
        docmenu.addAction(docAction)

        ##

        self.initUI()
        self.apply_style()


    def apply_style(self):
        self.n_btn.setObjectName('n_btn')
        self.c_btn.setObjectName('c_btn')
        try:
            with open('./qstyle/style.qss', 'r') as f:
                style = f.read()
            app.setStyleSheet(style)
        except:
            print("err")

    def Warning_event(self, warning_msg) :
        QMessageBox.warning(self,'Erorr!',warning_msg)

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

        # 색 적용 중
        # qp = QPalette()
        # qp.setColor(QPalette.ColorRole.Light, Qt.GlobalColor.white)

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
            self.toolbar = NavigationToolbar(self.canvas, self) # tool bar
            self.graph_main_layout.addWidget(self.canvas)

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
        
        lib_file_name = rdict['LibrarySource']
        if "TARGET" in rdict['ProtSites']:
            lib = self.target_lib[lib_file_name][str(seq)+'_'+str(charge)]
        else:
            lib = self.decoy_lib[lib_file_name][str(seq)+'_'+str(charge)]


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
        lib_mz, lib_intensity = lib_parser.parse_lib(lib_file_name, lib['num_peaks'], lib['offset'])
        
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
            print("line 521")
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


    def peptide_change_clicked(self):
        peptide_seq, query_filename = '', ''
        try:
            peptide_seq = self.peptide_change_text_box.text()
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()

            self.current_seq, self.top_seq = peptide_seq, peptide_seq # make_graph 내부를 고치면서 수정한 부분
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
            print("line 562")
            # 유효하지 않은 펩타이드
            self.top_seq = self.spectrum_list.item(self.cur_row, 6).text() # make_graph 내부를 고치면서 수정한 부분
            self.peptide_change_text_box.setText(self.top_seq)
            self.make_graph(query_filename, self.cur_idx)

            s, e, n, c = 0, 1, 1.0, 1.1
            if self.mass_error_btn.isChecked():
                s, e, n, c = 4, 5, -0.8, -0.9

            n_terms = terminal.make_nterm_list(self.top_seq)
            if self.n_btn.isChecked(): # n terminal 표시
                draw_terminal_line.draw_nterm_line(n_terms, self.top_seq, s, e, n)


            if self.c_btn.isChecked(): # c terminal 표시
                c_terms = terminal.make_cterm_list(self.top_seq)
                draw_terminal_line.draw_cterm_line(c_terms, self.top_seq, s, e, c)

            plt.xlim(0, n_terms[-1])
            # QMessageBox.warning(self,'Error','Invalid Peptide Sequence😵‍💫')
            return
        


    def peptide_reset_clicked(self):
        peptide_seq, query_filename = '', ''
        try:    
            peptide_seq = self.spectrum_list.item(self.cur_row, 6).text()
            query_filename = self.spectrum_list.item(self.cur_row, 0).text()

        except:
            print("line 594")
            return
        
        self.top_seq = self.spectrum_list.item(self.cur_row, 6).text() # make_graph 내부를 고치면서 수정한 부분
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
            self.Warning_event('Invalid Value!😵‍💫')
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
        self.spectrum_list.setColumnCount(17)
        self.spectrum_list.itemClicked.connect(self.chkItemChanged)
        self.spectrum_list.currentItemChanged.connect(self.chkItemChanged)
        self.column_headers = ['FileName', 'Index', 'ScanNo', 'Title', 'PMZ', 'Charge', 'Peptide', 'CalcMass', 'SA', 'QScore', '#Ions', '#Sig', 'ppmError', 'C13', 'ExpRatio', 'ProtSites', 'LibrarySource']
        self.spectrum_list.setHorizontalHeaderLabels(self.column_headers)

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

        # 매치에 대한 정보를 표시
        self.match_info_query_file_name, self.match_info_scan_no, self.match_info_pmz, self.match_info_charge, self.match_info_sa_score, self.match_info_qscore = QLabel(''), QLabel(''), QLabel(''), QLabel(''), QLabel(''), QLabel('')
        self.match_info_layout.addWidget(self.match_info_query_file_name)
        self.match_info_layout.addStretch(1)
        self.match_info_layout.addWidget(self.match_info_scan_no)
        self.match_info_layout.addStretch(1)
        self.match_info_layout.addWidget(self.match_info_pmz)
        self.match_info_layout.addStretch(1)
        self.match_info_layout.addWidget(self.match_info_charge)
        self.match_info_layout.addStretch(1)
        self.match_info_layout.addWidget(self.match_info_sa_score)
        self.match_info_layout.addStretch(1)
        self.match_info_layout.addWidget(self.match_info_qscore)
        self.match_info_layout.addStretch(1)


        bottom_sp.addLayout(self.match_info_layout)
        
        self.canvas = MirrorFigureCanvas(self.fig, self) # mirror plot
        self.canvas.setMinimumHeight(200) # 잠시 없앰
        self.graph_main_layout.addWidget(self.canvas)
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

            self.top_seq = self.spectrum_list.item(self.cur_row, 6).text()
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

            # 매치 정보를 표시
            self.set_match_info()

    def onHeaderClicked(self, logicalIndex):
        table_header_label = ['File', 'Index', 'ScanNo', 'Title', 'PMZ', 'Charge', 'Peptide', 'CalcMass', 'SA', 'QScore', '#Ions', '#Sig', 'ppmError', 'C13', 'ExpRatio', 'ProtSites', 'LibrarySource']
        self.result_data_list.sort(key=lambda x: x[table_header_label[logicalIndex]])
        self.refilter_spectrums()
        

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
        if not len(self.all_qscore):
            return
        
        for i in range(0, len(self.result_data_list)):
            cur_result = self.result_data_list[i]
            if not self.check_spectrum_item(cur_result):
                continue
                
            qidx = int(cur_result['Index'])
            seq = cur_result['Peptide']
            charge = cur_result['Charge']

            seq = process_sequence.brace_modifications(seq) # 0723
            seq = process_sequence.remove_modifications(seq)

            charge = cur_result['Charge']
            lib_file_name = cur_result['LibrarySource']
            if 'TARGET' in cur_result['ProtSites']:
                match = str(cur_result['ProtSites'].replace('\n', '')) + "_" + str(self.target_lib[lib_file_name][str(seq)+'_'+str(charge)]['index'])
            else:
                match = str(cur_result['ProtSites'].replace('\n', '')) + "_" + str(self.decoy_lib[lib_file_name][str(seq)+'_'+str(charge)]['index'])

            self.spectrum_list.setItem(idx, 0, QTableWidgetItem(cur_result['File']))
            self.spectrum_list.setItem(idx, 1, QTableWidgetItem(str(cur_result['Index'])))
            self.spectrum_list.setItem(idx, 2, QTableWidgetItem(str(cur_result['ScanNo'])))
            self.spectrum_list.setItem(idx, 3, QTableWidgetItem(cur_result['Title']))
            self.spectrum_list.setItem(idx, 4, QTableWidgetItem(str(cur_result['PMZ'])))
            self.spectrum_list.setItem(idx, 5, QTableWidgetItem(str(cur_result['Charge'])))
            self.spectrum_list.setItem(idx, 6, QTableWidgetItem(cur_result['Peptide']))
            self.spectrum_list.setItem(idx, 7, QTableWidgetItem(str(cur_result['CalcMass'])))
            self.spectrum_list.setItem(idx, 8, QTableWidgetItem(str(cur_result['SA'])))
            self.spectrum_list.setItem(idx, 9, QTableWidgetItem(str(cur_result['QScore'])))
            self.spectrum_list.setItem(idx, 10, QTableWidgetItem(str(cur_result['#Ions'])))
            self.spectrum_list.setItem(idx, 11, QTableWidgetItem(str(cur_result['#Sig'])))
            self.spectrum_list.setItem(idx, 12, QTableWidgetItem(str(cur_result['ppmError'])))
            self.spectrum_list.setItem(idx, 13, QTableWidgetItem(str(cur_result['C13'])))
            self.spectrum_list.setItem(idx, 14, QTableWidgetItem(str(cur_result['ExpRatio'])))
            self.spectrum_list.setItem(idx, 15, QTableWidgetItem(match))
            self.spectrum_list.setItem(idx, 16, QTableWidgetItem(str(cur_result['LibrarySource'])))

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
        start = time.time()
        input_dlg = input_dialog.InputDialog()
        input_dlg.exec()

        # dialog의 파라미터들을 가져오기
        try:
            # 뭔가 입력이 안된 상태 -> 에러를 띄우지 않고 리턴
            if not (input_dlg.query_file_list and input_dlg.target_lib_files and input_dlg.decoy_lib_files):
                return
            
            self.filenames = input_dlg.query_file_list # 쿼리 파일들
            self.data = process_data.process_queries(self.filenames) # data: dict[filename] = {data1[idx][content], data2[][], ...}
            self.target_lib_files = input_dlg.target_lib_files
            self.decoy_lib_files = input_dlg.decoy_lib_files
            self.frag_tol = input_dlg.frag_tol_value
            self.peptide_tol = input_dlg.pept_tol_value
            self.c13_isotope_tol_min = input_dlg.isotope_tol_value_min
            self.c13_isotope_tol_max = input_dlg.isotope_tol_value_max
            project_file_name = input_dlg.project_file_path
        except:
            return

        try:
            # library scan
            for target_lib_entry in self.target_lib_files:
                self.target_lib[target_lib_entry] = lib_scanner.lib_scanner(target_lib_entry)
            for decoy_lib_entry in self.decoy_lib_files:
                self.decoy_lib[decoy_lib_entry] = lib_scanner.lib_scanner(decoy_lib_entry)

            ## 여기다가 deephos를 실행을 시켜놓고 결과가 돌아오면
            self.results = []
            for q in self.filenames:
                self.results.append(q.split('.')[0]+'_deephos.tsv')
            self.result_data, self.result_data_list = process_data.process_results(self.results)

            self.set_items_in_table()

            self.frag_tol_input.setText(str(self.frag_tol))
            self.make_summary()

            # target, decoy, result 각각 직렬화 하여 저장
            project_file_name = project_file_name.strip('.devi')
            target_lib_json_file, decoy_lib_json_file = project_file_name+'_target.json', project_file_name+'_decoy.json'
            result_json_file, result_list_json_file = project_file_name + '_result.json', project_file_name + '_result_list.json'
            query_file = project_file_name + '_query.json'

            print('[Debug]: ', target_lib_json_file, decoy_lib_json_file)

            with open(target_lib_json_file, 'w') as f:
                json.dump(self.target_lib, f)

            with open(decoy_lib_json_file, 'w') as f:
                json.dump(self.decoy_lib, f)

            with open(result_json_file, 'w') as f:
                json.dump(self.result_data, f)

            with open(result_list_json_file, 'w') as f:
                json.dump(self.result_data_list, f)

            with open(query_file, 'w') as f:
                json.dump(self.data, f)

        except Exception as e:
            print('[Debug] error is\n', e)
            QMessageBox.warning(self,'Error','Something went wrong😵‍💫')
        
        end = time.time()
        print('New Project Execution time: ', end-start)

    def open_devi_project_file(self, devi_file_name : str):
        '''
        1. 파일을 읽어서 정보를 알아냄
        2. target, decoy 직렬화 파일을 읽어옴
        '''

        (self.project_file_name, self.target_lib_files, self.decoy_lib_files,
            make_decoy, self.peptide_tol, self.c13_isotope_tol_min,
            self.c13_isotope_tol_max, self.frag_tol, self.filenames, self.results) = process_data.parse_devi(devi_file_name)
        
        try:
            # library scan
            # for target_lib_entry in self.target_lib_files:
            #     self.target_lib[target_lib_entry] = lib_scanner.lib_scanner(target_lib_entry)
            # for decoy_lib_entry in self.decoy_lib_files:
            #     self.decoy_lib[decoy_lib_entry] = lib_scanner.lib_scanner(decoy_lib_entry)
            
            # 역직렬화
            proj_name = self.project_file_name.strip('.devi')
            target_lib_json_file, decoy_lib_json_file = proj_name+'_target.json', proj_name+'_decoy.json'
            result_json_file, result_data_list_file = proj_name+'_result.json', proj_name+'_result_list.json'
            query_file = proj_name + '_query.json'
            with open(target_lib_json_file) as f:
                self.target_lib = json.load(f) # target lib의 딕셔너리. key: seq_charge / value: offset
            with open(decoy_lib_json_file) as f:
                self.decoy_lib = json.load(f) # decoy lib의 딕셔너리. key: seq_charge / value: offset
            with open(result_json_file) as f:
                self.result_data = json.load(f) 
            with open(result_data_list_file) as f:
                self.result_data_list = json.load(f) 
            with open(result_data_list_file) as f:
                self.result_data_list = json.load(f) 
            with open(query_file) as f:
                self.data = json.load(f) 



            ## 여기다가 deephos를 실행을 시켜놓고 결과가 돌아오면
            # self.data = process_data.process_queries(self.filenames) # data: dict[filename] = {data1[idx][content], data2[][], ...}
            # self.result_data, self.result_data_list = process_data.process_results(self.results)

            self.set_items_in_table()

            self.frag_tol_input.setText(str(self.frag_tol))
            self.make_summary()

        except Exception as e:
            print('[Debug] error is\n', e)
            QMessageBox.warning(self,'Error','Something went wrong😵‍💫')
    
    def open_project_dlg(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        dlg.setNameFilter("*.devi")
        devi_file_name = None

        if dlg.exec():
            devi_file_name = dlg.selectedFiles()
            
            # 디렉토리 선택 에러 처리
            if os.path.isdir(devi_file_name[0]):
                return

            if not devi_file_name or not len(devi_file_name):
                return
        
            self.open_devi_project_file(devi_file_name[0]) # 프로젝트 파일을 통해 결과를 화면에 띄우는 함수
            

    def open_config_dlg(self):
        config_dlg = run_config_dialog.RunConfigDlg(self)
        config_dlg.exec()


    def filtering_action(self):
        filter_dlg = filtering_dialog.FilterDialog(self.filter_info)
        filter_dlg.exec()

        # 정보 바꾸기
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

                lib_file_name = data_item['LibrarySource']
                if 'TARGET' in data_item['ProtSites']:
                    match = str(data_item['ProtSites'].replace('\n', '')) + "_" + str(self.target_lib[lib_file_name][str(seq)+'_'+str(charge)]['index'])
                else:
                    match = str(data_item['ProtSites'].replace('\n', '')) + "_" + str(self.decoy_lib[lib_file_name][str(seq)+'_'+str(charge)]['index'])

                self.spectrum_list.setItem(rowcnt, 0, QTableWidgetItem(data_item['File']))
                self.spectrum_list.setItem(rowcnt, 1, QTableWidgetItem(str(data_item['Index'])))
                self.spectrum_list.setItem(rowcnt, 2, QTableWidgetItem(str(data_item['ScanNo'])))
                self.spectrum_list.setItem(rowcnt, 3, QTableWidgetItem(data_item['Title']))
                self.spectrum_list.setItem(rowcnt, 4, QTableWidgetItem(str(data_item['PMZ'])))
                self.spectrum_list.setItem(rowcnt, 5, QTableWidgetItem(str(data_item['Charge'])))
                self.spectrum_list.setItem(rowcnt, 6, QTableWidgetItem(data_item['Peptide']))
                self.spectrum_list.setItem(rowcnt, 7, QTableWidgetItem(str(data_item['CalcMass'])))
                self.spectrum_list.setItem(rowcnt, 8, QTableWidgetItem(str(data_item['SA'])))
                self.spectrum_list.setItem(rowcnt, 9, QTableWidgetItem(str(data_item['QScore'])))
                self.spectrum_list.setItem(rowcnt, 10, QTableWidgetItem(str(data_item['#Ions'])))
                self.spectrum_list.setItem(rowcnt, 11, QTableWidgetItem(str(data_item['#Sig'])))
                self.spectrum_list.setItem(rowcnt, 12, QTableWidgetItem(str(data_item['ppmError'])))
                self.spectrum_list.setItem(rowcnt, 13, QTableWidgetItem(str(data_item['C13'])))
                self.spectrum_list.setItem(rowcnt, 14, QTableWidgetItem(str(data_item['ExpRatio'])))
                self.spectrum_list.setItem(rowcnt, 15, QTableWidgetItem(match))
                self.spectrum_list.setItem(rowcnt, 16, QTableWidgetItem(lib_file_name))
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
        self.peptide_change_btn.setCheckable(True)
        self.peptide_change_btn.setCheckable(True)
        self.spectrum_list.horizontalHeader().sectionClicked.connect(self.onHeaderClicked) # 클릭으로 변경


    def make_summary(self):
        self.sa_decoy, self.sa_target = [0 for i in range(50)], [0 for i in range(50)] # binning = 50
        self.qs_decoy, self.qs_target = [0 for i in range(35)], [0 for i in range(35)] # binning = 35, max QScore = 35로 설정
        self.ppm_decoy_list, self.ppm_target_list = [], []
        self.plength_target = [0 for i in range(61)]
        self.plength_decoy = [0 for i in range(61)]
        self.charge_target_list = [0 for i in range(4)] # 1, 2, 3, 4
        self.charge_decoy_list = [0 for i in range(4)] # 1, 2, 3, 4

        for i in reversed(range(self.summary_layout.count())): 
            obj = self.summary_layout.itemAt(i).widget()
            if obj is not None:
                obj.deleteLater()
        
        # SA
        self.sa_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.sa_ax = self.sa_canvas.figure.subplots()
        self.sa_ax.hist([])

        # QScore
        self.qs_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.qs_ax = self.qs_canvas.figure.subplots()
        self.qs_ax.hist([])

        # ppm error
        self.ppm_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.ppm_ax = self.ppm_canvas.figure.subplots()
        self.ppm_ax.boxplot([])

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


        self.summary_layout.addWidget(self.sa_canvas, 0, 0)
        self.summary_layout.addWidget(self.qs_canvas, 0, 1)
        self.summary_layout.addWidget(self.ppm_canvas, 0, 2)
        self.summary_layout.addWidget(self.charge_canvas, 1, 0)
        self.summary_layout.addWidget(self.plength_canvas, 1, 1)
        
        target_cnt, decoy_cnt = 0, 0
        for r in self.results:
            cur_rslts = self.result_data[r]
            for cur_item in cur_rslts:
                if "TARGET" in cur_item['ProtSites']:
                    target_cnt += 1
                    self.sa_target[int(50*float(cur_item['SA']))] += 1
                    self.qs_target[math.trunc(float(cur_item['QScore']))] += 1
                    self.ppm_target_list.append(float(cur_item['ppmError']))

                    if int(cur_item['Charge']) >= 4:
                        self.charge_target_list[3] += 1
                    else:
                        self.charge_target_list[int(cur_item['Charge'])-1] += 1

                    if len(cur_item['Peptide']) >= 60:
                        self.plength_target[60] += 1
                    else:
                        self.plength_target[len(cur_item['Peptide'])] += 1
                else:
                    decoy_cnt += 1
                    self.sa_decoy[int(50*float(cur_item['SA']))] += 1
                    self.qs_decoy[math.trunc(float(cur_item['QScore']))] += 1
                    self.ppm_decoy_list.append(float(cur_item['ppmError']))

                    if int(cur_item['Charge']) >= 4:
                        self.charge_decoy_list[3] += 1
                    else:
                        self.charge_decoy_list[int(cur_item['Charge'])-1] += 1

                    if len(cur_item['Peptide']) >= 60:
                        self.plength_decoy[60] += 1
                    else:
                        self.plength_decoy[len(cur_item['Peptide'])] += 1


                self.all_qscore.append(float(cur_item['QScore']))

        self.all_qscore.sort()

        # summary
        labels= ['target', 'decoy']
        handles = [Rectangle((0,0),1,1,color=c) for c in ['#3669CF', '#FF9595']]

        sa_bins = np.arange(0, 1, 0.02)
        self.sa_ax.plot(sa_bins, self.sa_target, marker='.', linestyle='--', color='#3669CF')
        self.sa_ax.plot(sa_bins, self.sa_decoy, marker='.', linestyle='--', color='#FF9595')
        self.sa_ax.set_title('SA')
        self.sa_ax.legend(handles, labels)


        qs_bins = np.arange(0, 35, 1)
        self.qs_ax.plot(qs_bins, self.qs_target, marker='.', linestyle='--', color='#3669CF')
        self.qs_ax.plot(qs_bins, self.qs_decoy, marker='.', linestyle='--', color='#FF9595')
        self.qs_ax.set_title('QScore')
        self.qs_ax.legend(handles, labels)


        self.ppm_ax.boxplot([self.ppm_target_list, self.ppm_decoy_list])
        ppm_error_labels = ['target', 'decoy']
        self.ppm_ax.set_xticks(np.array([1, 2]), ppm_error_labels)
        self.ppm_ax.set_title('ppm Error')

        cx = np.arange(4)
        charge_xticks = [str(i) for i in range(1, 5)]
        charge_xticks[-1] = '4+'
        charge_bar_width = 0.25
        self.charge_ax.bar(cx, self.charge_target_list, charge_bar_width, label='target', color='blue', alpha=0.4)
        self.charge_ax.bar(cx+charge_bar_width, self.charge_decoy_list, charge_bar_width, label='decoy', color='red', alpha=0.4)
        self.charge_ax.set_xticks(cx, charge_xticks)
        self.charge_ax.set_title('charge')
        self.charge_ax.legend()

        x = np.arange(61)
        plen_xticks = ['' for i in range(61)]
        for i in range(len(plen_xticks)):
            if i % 10 == 0:
                plen_xticks[i] = str(i)
        plen_xticks[-1] = '60+'
        
        plength_bar_width = 0.25
        self.plength_ax.bar(x, self.plength_target, plength_bar_width, color='blue', alpha=0.4, label='target')
        self.plength_ax.bar(x+plength_bar_width, self.plength_decoy, plength_bar_width, color='red', alpha=0.4, label='decoy')
        self.plength_ax.set_xticks(x, plen_xticks)
        self.plength_ax.set_title('peptide length')
        self.plength_ax.legend()

        self.sa_canvas.draw()
        self.qs_canvas.draw()
        self.ppm_canvas.draw()
        self.charge_canvas.draw()
        self.plength_canvas.draw()

    # 
    def set_match_info(self):
        self.match_info_query_file_name.setText(self.spectrum_list.item(self.cur_row, 0).text().split('/')[-1])
        self.match_info_scan_no.setText('scanNo: ' + self.spectrum_list.item(self.cur_row, 2).text())
        self.match_info_pmz.setText('PMZ: ' + self.spectrum_list.item(self.cur_row, 4).text())
        self.match_info_charge.setText('charge: '+ self.spectrum_list.item(self.cur_row, 5).text())
        self.match_info_sa_score.setText('SA Score: ' + self.spectrum_list.item(self.cur_row, 8).text())
        self.match_info_qscore.setText('QScore: ' + self.spectrum_list.item(self.cur_row, 9).text())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())