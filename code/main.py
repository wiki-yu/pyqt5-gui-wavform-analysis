import sys
import matplotlib
import numpy as np
import pandas as pd
# matplotlib.use("Qt5Agg")
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QLabel, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import num2date, date2num
import datetime
from PandasModel import PandasModel

# class GraphCanvas(FigureCanvas):
#     def __init__(self, parent=None, width=1, height=1, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi,facecolor='#041105') #figure options
#         #first subplot
#         self.axes = fig.add_subplot(211,facecolor='#041105')
#         self.axes.tick_params(axis='both',color='#ffffff',labelcolor ='#ffffff') #tick options
#         self.axes.grid(color='lightgray', linewidth=.5, linestyle=':')
#         self.axes.yaxis.tick_right()  # show yaxis tick text in right side
#         self.axes.xaxis_date()
#         #second subplot
#         self.axes2 = fig.add_subplot(212,facecolor='#041105')
#         self.axes2.tick_params(axis='both', color='#ffffff', labelcolor='#ffffff')  # tick options
#         self.axes2.grid(color='lightgray', linewidth=.5, linestyle=':')
#         self.axes2.yaxis.tick_right()  # show yaxis tick text in right side
#         self.axes2.xaxis_date()
#
#         # ploting all trace
#         self.plot_traces()
#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)
#         FigureCanvas.setSizePolicy(self,
#                 QSizePolicy.Expanding,
#                 QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#
# class GraphTraces(GraphCanvas):
#     """Simple canvas with a sine plot."""
#     def plot_traces(self):
#         dates = ['2017/01/01', '2017/01/02', '2017/01/03', '2017/01/04', '2017/01/05','2017/01/06','2017/01/07']
#         x = date2num([datetime.datetime.strptime(d, '%Y/%m/%d').date() for d in dates])
#         #scatter line chart
#         y1 = [2,5,4,7,6,5,4]
#         self.axes.plot(x, y1,color='orange')
#         #bar chart
#         y2 = [2,5,4,7,6,5,4]
#         self.axes2.bar(x, y2,width=.8,color='g')
#
# def onclick(event):
#     global clicks
#     clicks.append(event.xdata)

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
        self.setWindowTitle('Venlilator Waveform Analysis')

        self.main = QWidget()
        self.setCentralWidget(self.main)
        layout = QtWidgets.QGridLayout(self.main)

        #**************** the "time series plots" setting***************#

        # plot 1
        simple_canvas = FigureCanvas(Figure(figsize=(10, 5)))
        self._static_ax = simple_canvas.figure.subplots()
        self.plot_basic(arr_resp_data, peaks_list, troughs_list)

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
        button_reject = QtWidgets.QPushButton('Reject')
        button_reject.clicked.connect(self.reset_plot)

        #********************** the "table" setting ********************#
        model = PandasModel(df_table)
        self.table_clicks = QtWidgets.QTableView(self)
        self.table_clicks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table_clicks.setModel(model)

        # ********************** the "stats widgets" setting ********************#
        button_1 = QtWidgets.QPushButton('STAT1', self)
        button_2 = QtWidgets.QPushButton('STAT2', self)
        button_3 = QtWidgets.QPushButton('STAT3', self)
        button_4 = QtWidgets.QPushButton('STAT4', self)
        button_5 = QtWidgets.QPushButton('STAT5', self)
        button_6 = QtWidgets.QPushButton('STAT6', self)
        button_7 = QtWidgets.QPushButton('STAT7', self)
        button_8 = QtWidgets.QPushButton('STAT8', self)

        # *************** layouts design ******************#
        # the layouts of the table
        layout.addWidget(self.table_clicks, 0, 0)
        # the layouts of the picture boxes
        pictures_layout = QtWidgets.QGridLayout();
        pictures_layout.addWidget(dynamic_canvas, 0, 0)
        pictures_layout.addWidget(simple_canvas, 1, 0)
        layout.addLayout(pictures_layout, 0, 1)
        # the layout of "button and labels"
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(button_previous)
        button_layout.addWidget(button_next)
        button_layout.addWidget(button_undo)
        button_layout.addWidget(button_reject)
        layout.addLayout(button_layout, 1, 0)
        # the layout of stats widgets
        stats_widgets = QtWidgets.QGridLayout();
        stats_widgets = QtWidgets.QGridLayout();
        stats_widgets.addWidget(button_1, 0, 0)
        stats_widgets.addWidget(button_2, 0, 1)
        stats_widgets.addWidget(button_3, 1, 0)
        stats_widgets.addWidget(button_4, 1, 1)
        stats_widgets.addWidget(button_5, 2, 0)
        stats_widgets.addWidget(button_6, 2, 1)
        stats_widgets.addWidget(button_7, 3, 0)
        stats_widgets.addWidget(button_8, 3, 1)
        layout.addLayout(stats_widgets, 1, 1)

        # the ratio of the width of the columns (the  grid has two columns)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)

    def plot_basic(self, arr_resp_data, peaks_list, troughs_list):
        ''' plot some random stuff '''
        self._static_ax.plot(arr_resp_data, '-', color='b')
        self._static_ax.plot(peaks_list, arr_resp_data[peaks_list], "ro", markersize=3)
        self._static_ax.plot(troughs_list, arr_resp_data[troughs_list], "go", markersize=3)
        self._static_ax.figure.canvas.draw()

    def plot_table_triggerd(self, arr_resp_data, peaks_list, troughs_list):
        self._static_ax.clear()
        x = np.arange(peaks_list[1] - peaks_list[0])
        self._static_ax.plot(x, arr_resp_data[peaks_list[0]:peaks_list[1]], '-o', color='b')
        self._static_ax.figure.canvas.draw()

    def plot_dynamic(self):
        self._dynamic_ax.clear()
        global counter
        len_shown = 400
        if counter < len_shown:
            self._dynamic_ax.plot(arr_resp_data[:counter], '-', color='b')
            # button_1.setText("test")
        else:
            if len(arr_resp_data) - counter > len_shown:
                self._dynamic_ax.plot(arr_resp_data[counter-len_shown : counter], '-', color='b')
            # else:
            #     self._staic_ax.plot(arr_resp_data[counter - len_shown: counter], '-', color='b')
        counter += 3
        self._dynamic_ax.figure.canvas.draw()


if __name__ == "__main__":

    # the respiratory data from CSV file
    df = pd.read_csv("sample1.csv")
    arr_resp_data, peaks_list, troughs_list = process_dataframe(df)
    df_table = obtain_onsets_offsets(arr_resp_data, peaks_list, troughs_list)
    counter = 100

    # the interface part
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("Ventilator test V1.0")
    aw.show()
    sys.exit(app.exec_())