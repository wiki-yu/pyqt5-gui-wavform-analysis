import sys
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PandasModel import PandasModel


def find_peaks(seg_arr, coef):
    mean = np.mean(seg_arr)
    sections = []
    section = {}
    for i, val in enumerate(seg_arr):
        if val > mean * coef:
            section[i] = val
        else:
            if len(section) != 0:
                sections.append(section)
            section = {}
    peaks_list = []
    for section in sections:
        maximum = max(section, key=section.get)  # Just use 'min' instead of 'max' for minimum.
        peaks_list.append(maximum)
    return peaks_list


def find_troughs(seg_arr, coef):
    mean = np.mean(seg_arr)
    sections = []
    section = {}
    for i, val in enumerate(seg_arr):
        if val < mean * coef:
            section[i] = val
        else:
            if len(section) != 0:
                sections.append(section)
            section = {}
    troughs_list = []
    for section in sections:
        minimum = min(section, key=section.get)  # Just use 'min' instead of 'max' for minimum.
        troughs_list.append(minimum)
    return troughs_list


def most_frequent(List):
    List = list(List.flatten())
    return max(set(List), key = List.count)


def locate_onsets_offsets(arr_resp_data, peaks_list, troughs_list):
    length = min(len(peaks_list), len(troughs_list))
    count = 1
    breath_num = []
    exh_onsets = []
    inh_onsets = []
    ave_val = np.mean(arr_resp_data)
    if peaks_list[0] < troughs_list[0]:
        for i in range(length):
            breath_num.append(count)
            exh_section = arr_resp_data[peaks_list[i] : troughs_list[i]]
            exh_onset = np.argmin(np.abs(exh_section - ave_val)) + peaks_list[i]
            exh_onsets.append(exh_onset)
            inh_section = arr_resp_data[troughs_list[i] : peaks_list[i+1]]
            #inh_onset = np.argmin(np.abs(inh_section - most_frequent(inh_section))) + troughs_list[i]
            inh_onset = np.argmin(np.abs(inh_section - ave_val)) + troughs_list[i]-3
            inh_onsets.append(inh_onset)
            count += 1

    df_table = pd.DataFrame(list(zip(breath_num, exh_onsets, inh_onsets)),
                 columns=['Breath No.', 'onset', 'offset'])
    exh_onsets = [int(x) for x in exh_onsets]
    inh_onsets = [int(x) for x in inh_onsets]
    print(inh_onsets)
    return df_table, exh_onsets, inh_onsets


def obtain_onsets_offsets(arr_resp_data, peaks_list, troughs_list):
    length = min(len(peaks_list), len(troughs_list))
    count = 1
    breath = []
    breaths = []
    for i in range(length):
        breath.append(count)
        breath.append(peaks_list[i])
        breath.append(troughs_list[i])
        breaths.append(breath)
        breath = []
        count += 1
    df_table = pd.DataFrame(breaths, columns=["Breath No.", "Onset", "Offset"])
    return df_table


def process_dataframe(df):
    df_resp_data = df.iloc[:150000, 0:1]
    arr_resp_data = df_resp_data.to_numpy()
    arr_resp_data = arr_resp_data[::100]
    coef_peak = 2.5
    coef_trough = -1.2
    peaks_list = find_peaks(arr_resp_data, coef_peak)
    troughs_list = find_troughs(arr_resp_data, coef_trough)
    return arr_resp_data, peaks_list, troughs_list


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setWindowTitle("application main window")
        # self.file_menu = QMenu('&File', self)
        # self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        # self.menuBar().addMenu(self.file_menu)
        # self.help_menu = QMenu('&Help', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.help_menu)
        # self.help_menu.addAction('&About', self.about)

        self.main = QWidget()
        self.setCentralWidget(self.main)
        layout = QtWidgets.QGridLayout(self.main)

        #**************** the "time series plots" setting***************#

        # plot 1
        simple_canvas = FigureCanvas(Figure(figsize=(10, 5)))
        # simple_canvas.axes.grid(color='lightgray', linewidth=.5, linestyle=':')
        self._static_ax = simple_canvas.figure.subplots()
        self.plot_basic(arr_resp_data, peaks_list, troughs_list, exh_onsets, inh_onsets)

        # plot 2
        dynamic_canvas = FigureCanvas(Figure(figsize=(10, 5)))
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax.grid()
        self._timer = dynamic_canvas.new_timer(100, [(self.plot_dynamic, (), {})])
        self._timer.start()

        # try fancy plot......
        # self.dynamic_canvas = QWidget(self)
        # self.static_canvas = QWidget(self)
        # dynamic_canvas = GraphTraces(self.dynamic_canvas, width=10, height=8, dpi=100)
        # static_canvas = GraphTraces(self.static_canvas, width=10, height=8, dpi=100)

        # try table-triggerd plot
        # dynamic_canvas = FigureCanvas(Figure(figsize=(10, 5)))
        # self._static_ax = dynamic_canvas.figure.subplots()
        # self.plot_table_triggered(arr_resp_data, peaks_list, troughs_list)

        #**************** the "buttons and labels" setting ***************#
        button_previous = QtWidgets.QPushButton('Previous')
        button_next = QtWidgets.QPushButton('Next')
        button_undo = QtWidgets.QPushButton('Undo')
        button_check = QtWidgets.QPushButton('Check')
        button_ai = QtWidgets.QPushButton('AI Diagnosis')
        # button_reject.clicked.connect(self.plot_table_triggerd(arr_resp_data, peaks_list, troughs_list))
        button_check.clicked.connect(lambda: self.plot_basic(arr_resp_data, peaks_list, troughs_list, exh_onsets, inh_onsets))

        #********************** the "table" setting ********************#
        model = PandasModel(df_table)
        self.table_clicks = QtWidgets.QTableView(self)
        self.table_clicks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_clicks.setModel(model)
        self.table_clicks.clicked.connect(self.viewClicked)

        # ********************** the "stats widgets" setting ********************#
        self.button_1 = QtWidgets.QPushButton('Breathing rate: 14', self)
        self.button_2 = QtWidgets.QPushButton('Minute ventilation: 4500 (ml)', self)
        self.button_3 = QtWidgets.QPushButton('Average breath interval: 230', self)
        self.button_4 = QtWidgets.QPushButton('Breaths with pauses % : 65%', self)
        self.button_5 = QtWidgets.QPushButton('Average flow volume：350', self)
        self.button_6 = QtWidgets.QPushButton('Breathing rate variation：1.23', self)
        self.button_7 = QtWidgets.QPushButton('Duty cycles variation：0.24', self)
        self.button_8 = QtWidgets.QPushButton('Average tidal volume: 400', self)

        # *************** layouts design ******************#
        # the layouts of the table
        layout.addWidget(self.table_clicks, 0, 0)
        # the layouts of the picture boxes
        pictures_layout = QtWidgets.QGridLayout();
        pictures_layout.addWidget(dynamic_canvas, 0, 0)
        pictures_layout.addWidget(simple_canvas, 1, 0)
        layout.addLayout(pictures_layout, 0, 1)
        # the layout of "button and labels"
        button_layout = QtWidgets.QGridLayout()
        button_layout.addWidget(button_previous, 0, 0)
        button_layout.addWidget(button_next, 0, 1)
        button_layout.addWidget(button_undo, 0, 2)
        button_layout.addWidget(button_check, 0, 3)
        button_layout.addWidget(button_ai, 1, 0, 1, 4)
        layout.addLayout(button_layout, 1, 0)
        # the layout of stats widgets
        stats_widgets = QtWidgets.QGridLayout();
        stats_widgets.addWidget(self.button_1, 0, 0)
        stats_widgets.addWidget(self.button_2, 0, 1)
        stats_widgets.addWidget(self.button_3, 1, 0)
        stats_widgets.addWidget(self.button_4, 1, 1)
        stats_widgets.addWidget(self.button_5, 2, 0)
        stats_widgets.addWidget(self.button_6, 2, 1)
        stats_widgets.addWidget(self.button_7, 3, 0)
        stats_widgets.addWidget(self.button_8, 3, 1)
        layout.addLayout(stats_widgets, 1, 1)

        # the ratio of the width of the columns (the  grid has two columns)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)


    def plot_basic(self, arr_resp_data, peaks_list, troughs_list, exh_onsets, inh_onsets):

        self._static_ax.clear()
        self._static_ax.axes.grid(color='lightgray', linewidth=1, linestyle=':')
        self._static_ax.plot(arr_resp_data, '-', color='b')
        self._static_ax.plot(peaks_list, arr_resp_data[peaks_list], "ro", markersize=3)
        self._static_ax.plot(troughs_list, arr_resp_data[troughs_list], "go", markersize=3)
        self._static_ax.plot(exh_onsets, arr_resp_data[exh_onsets], "co", markersize=3)
        self._static_ax.plot(inh_onsets, arr_resp_data[inh_onsets], "mo", markersize=3)
        self._static_ax.figure.canvas.draw()


    def plot_table_triggerd(self, arr_resp_data, peaks_list, troughs_list, exh_onsets, inh_onsets, start, end):

        self._static_ax.clear()
        start_exp = start -50
        end_exp = end +50
        x = np.arange(start_exp, end_exp)

        peaks_plot_list = [i for i in peaks_list if i < end_exp and i > start_exp]
        troughs_plot_list = [i for i in troughs_list if i < end_exp and i > start_exp]
        exh_onsets_plot_list = [i for i in exh_onsets if i < end_exp and i > start_exp]
        inh_onsets_plot_list = [i for i in inh_onsets if i < end_exp and i > start_exp]
        self._static_ax.axes.grid(color='lightgray', linewidth=1, linestyle=':')
        self._static_ax.plot(x, arr_resp_data[start_exp: end_exp], 'o-', markersize=3)
        self._static_ax.plot(peaks_plot_list, arr_resp_data[peaks_plot_list], "ro", markersize=3)
        self._static_ax.plot(troughs_plot_list, arr_resp_data[troughs_plot_list], "go", markersize=3)
        self._static_ax.plot(exh_onsets_plot_list, arr_resp_data[exh_onsets_plot_list], "co", markersize=3)
        self._static_ax.plot(inh_onsets_plot_list, arr_resp_data[inh_onsets_plot_list], "mo", markersize=3)
        self._static_ax.figure.canvas.draw()


    def plot_dynamic(self):
        global counter
        show_len = 400

        if counter < show_len:

            self._dynamic_ax.clear()
            self._dynamic_ax.plot(arr_resp_data[:counter], '-', color='b')

            peaks_plot_list = [i for i in peaks_list if i < counter]
            troughs_plot_list = [i for i in troughs_list if i < counter]
            exh_onsets_plot_list = [i for i in exh_onsets if i < counter]
            inh_onsets_plot_list = [i for i in inh_onsets if i < counter]
            self._dynamic_ax.axes.grid(color='lightgray', linewidth=1, linestyle=':')
            self._dynamic_ax.plot(peaks_plot_list, arr_resp_data[peaks_plot_list], "ro", markersize=3)
            self._dynamic_ax.plot(troughs_plot_list, arr_resp_data[troughs_plot_list], "go", markersize=3)
            self._dynamic_ax.plot(exh_onsets_plot_list, arr_resp_data[exh_onsets_plot_list], "co", markersize=3)
            self._dynamic_ax.plot(inh_onsets_plot_list, arr_resp_data[inh_onsets_plot_list], "mo", markersize=3)

            self.button_1.setText("exhale onset: " + str(exh_onsets_plot_list[len(exh_onsets_plot_list)-1]))
            self.button_2.setText("inhale onset: " + str(inh_onsets_plot_list[len(inh_onsets_plot_list)-1]))

        elif len(arr_resp_data) - counter > show_len:

            self._dynamic_ax.clear()
            self._dynamic_ax.plot(arr_resp_data[counter-show_len : counter], '-', color='b')

            peaks_plot_list = [i for i in peaks_list if i < counter and i > counter-show_len]
            troughs_plot_list = [i for i in troughs_list if i < counter and i > counter-show_len]
            exh_onsets_plot_list = [i for i in exh_onsets if i < counter and i > counter-show_len]
            inh_onsets_plot_list = [i for i in inh_onsets if i < counter and i > counter-show_len]
            self.button_1.setText("exhale onset: " + str(exh_onsets_plot_list[len(exh_onsets_plot_list)-1]))
            self.button_2.setText("inhale onset: " + str(inh_onsets_plot_list[len(inh_onsets_plot_list)-1]))

            peaks_plot_list_new_cord = [i-(counter-show_len ) for i in peaks_plot_list]
            troughs_plot_list_new_cord = [i-(counter-show_len ) for i in troughs_plot_list]
            exh_onsets_plot_list_new_cord = [i-(counter-show_len ) for i in exh_onsets_plot_list]
            inh_onsets_plot_list_new_cord = [i-(counter-show_len ) for i in inh_onsets_plot_list]

            self._dynamic_ax.axes.grid(color='lightgray', linewidth=1, linestyle=':')
            self._dynamic_ax.plot(peaks_plot_list_new_cord, arr_resp_data[peaks_plot_list], "ro", markersize=3)
            self._dynamic_ax.plot(troughs_plot_list_new_cord, arr_resp_data[troughs_plot_list], "go", markersize=3)
            self._dynamic_ax.plot(exh_onsets_plot_list_new_cord, arr_resp_data[exh_onsets_plot_list], "co", markersize=3)
            self._dynamic_ax.plot(inh_onsets_plot_list_new_cord, arr_resp_data[inh_onsets_plot_list], "mo", markersize=3)

        else:
            self._timer.stop()

        counter += 1
        self._dynamic_ax.figure.canvas.draw()


    def viewClicked(self, clickedIndex):

        row = clickedIndex.row()
        start = df_table.iloc[row:row+1, 1:2].values.flatten()[0]
        end = df_table.iloc[row:row+1, 2:3].values.flatten()[0]
        print(start, end)
        self.plot_table_triggerd(arr_resp_data, peaks_list, troughs_list, exh_onsets, inh_onsets, start, end)


if __name__ == "__main__":
    # the respiratory data from CSV file
    df = pd.read_csv("../sample1.csv")
    arr_resp_data, peaks_list, troughs_list = process_dataframe(df)
    df_table, exh_onsets, inh_onsets = locate_onsets_offsets(arr_resp_data, peaks_list, troughs_list)
    counter = 100

    # the interface part
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("Ventilator Waveform Analysis V1.0")
    aw.show()
    sys.exit(app.exec_())