import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import random

def onclick(event):
    global clicks
    clicks.append(event.xdata)

def process_csv_data(file_name):
    df = pd.read_csv(file_name)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, file_name):
        super(ApplicationWindow, self).__init__()
        self.title = 'Venlilator waveform real-time'
        self.setWindowTitle(self.title)

        self.file_name = file_name

        self.main = QtWidgets.QWidget()
        self.setCentralWidget(self.main)

        # the "time series plot" setting
        '''
        dynamic_canvas = FigureCanvas(Figure(figsize=(10, 10)))
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        dynamic_canvas.figure.canvas.mpl_connect('button_press_event', onclick)
        self._dynamic_ax.grid()
        self._timer = dynamic_canvas.new_timer(100, [(self.update_window, (), {})])
        self._timer.start()
        '''

        # the "time series plot" setting
        dynamic_canvas = FigureCanvas(self.figure)
        self.plot1()


        # the "buttons and labels" setting
        button_stop = QtWidgets.QPushButton('Stop', self)
        button_stop.clicked.connect(self._timer.stop)
        button_start = QtWidgets.QPushButton('Start', self)
        button_start.clicked.connect(self._timer.start)

        # the "table" setting
        self.table_clicks = QtWidgets.QTableWidget(0, 2)
        self.table_clicks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # the "other widget" setting, make this part blank for now
        other_widget = QtWidgets.QLabel("Other widgets", font=QtGui.QFont("Times", 60, QtGui.QFont.Bold), alignment=QtCore.Qt.AlignCenter)


        # *************** layouts design ******************#
        # the layouts of the picture box, table, and "other widgets"
        layout = QtWidgets.QGridLayout(self.main)
        layout.addWidget(self.table_clicks, 0, 0)
        layout.addWidget(dynamic_canvas, 0, 1)
        layout.addWidget(other_widget, 1, 1)

        # set up for the area of "button and labels"
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addWidget(button_stop)
        button_layout.addWidget(button_start)        

        # the layout for the area of "button and labels"
        layout.addLayout(button_layout, 1, 0)

        # the ratio of the width of the columns (the grid has two columns)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)

        process_csv_data(file_name)

    def plot1(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]
        # instead of ax.hold(False)
        self.figure.clear()
        # create an axis
        ax = self.figure.add_subplot(111)
        # discards the old graph
        # ax.hold(False) # deprecated, see above
        # plot data
        ax.plot(data, '*-')
        # refresh canvas
        self.canvas.draw()

    def update_window(self):
        self._dynamic_ax.clear()
        global x, y1, y2, y3, N, count_iter, last_number_clicks
        x.append(x[count_iter] + 0.01)
        y1.append(np.random.random())
        idx_inf = max([count_iter-N, 0])
        if last_number_clicks < len(clicks):
            for new_click in clicks[last_number_clicks:(len(clicks))]:
                rowPosition = self.table_clicks.rowCount()
                self.table_clicks.insertRow(rowPosition)
                self.table_clicks.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(new_click)))
                self.table_clicks.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem("Descripcion"))
            last_number_clicks = len(clicks)
        self._dynamic_ax.plot(x[idx_inf:count_iter], y1[idx_inf:count_iter], '-o', color='b')
        count_iter += 1
        self._dynamic_ax.figure.canvas.draw()

if __name__ == "__main__":
    pressed_key = {}
    clicks = []
    last_number_clicks = len(clicks)
    N = 25
    y1 = [np.random.random()]
    x = [0]
    count_iter = 0

    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow('data.csv')
    app.show()
    sys.exit(qapp.exec_())