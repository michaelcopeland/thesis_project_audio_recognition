"""Example class for using QT"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from numpy import arange, sin, cos, pi
import pyqtgraph as pg
import sys

class QTplot():
    def __init__(self):
        self.traces = dict()

        self.phase = 0
        self.t     = np.arange(0, 3.0, 0.01)

        pg.setConfigOptions(antialias=True)

        self.app = QtGui.QApplication(sys.argv)

        self.win = pg.GraphicsWindow(title='Plot Example')
        #self.win.reszie(1000, 600)
        self.win.setWindowTitle('pyqtgraph: plot')

        self.canvas = self.win.addPlot(title='Pytelemetry')

    def start(self):
        if(sys.flags.interactive != 10) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def trace(self, name, dataset_x, dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x, dataset_y)
        else:
            self.traces[name] = self.canvas.plot(pen='y')

    def update(self):
        s = sin(2*pi * self.t + self.phase)
        c = cos(2*pi * self.t + self.phase)

        p.trace('sin', self.t, s)
        p.trace('cos', self.t, c)

        self.phase += 0.1

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(30)

        self.start()

if __name__ == '__main__':
    p = QTplot()
    p.animation()



