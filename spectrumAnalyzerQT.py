"""Audio stream spectrum analyzer with pyqtgraph

Reference: http://www.pyqtgraph.org/documentation/qtcrashcourse.html
"""

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import struct
import pyaudio
from scipy.fftpack import fft

import sys

class AudioStream:
    def __init__(self):
        # pyqtgraph
        pg.setConfigOptions(antialias=True)

        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1910, 1070)

        # weveform

        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(0, '0'), (127, '127'), (255, '255')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        # spectrum
        sp_xlabels = [(np.log10(10), '10'), (np.log10(100), '100'),
                      (np.log10(1000), '1000'), (np.log10(22050), '22050')]

        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        self.waveform = self.win.addPlot(
            title='Waveform', row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )

        self.spectrum = self.win.addPlot(
            title='Spectrum', row=2, col=1, axisItems={'bottom': sp_xaxis},
        )

        # pyaudio config

        self.FORMAT   = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE     = 44100
        self.CHUNK    = 1024 * 2

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format           =self.FORMAT,
            channels         =self.CHANNELS,
            rate             =self.RATE,
            input            =True,
            output           =True,
            frames_per_buffer=self.CHUNK,
        )

        # waveform and spectrum x points

        self.x   = np.arange(0, 2 * self.CHUNK, 2)              # samples
        self.x_f = np.linspace(0, self.RATE / 2, self.CHUNK / 2)  # frequencies

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()  # starts the QT event loop

    def set_plotData(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        elif name == 'waveform':
            self.traces[name] = self.waveform.plot(pen='c', width=3)
            self.waveform.setYRange(0, 255, padding=0)
            self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
        elif name == 'spectrum':
            self.traces[name] = self.spectrum.plot(pen='m', width=3)
            self.spectrum.setLogMode(x=True, y=True)
            self.spectrum.setYRange(-4, 0, padding=0.005)
            self.spectrum.setXRange(np.log10(20), np.log10(self.RATE / 2), padding=0.005)

    def update(self):
        """Reads audio info from stream and updates the plot"""
        # for waveform
        wf_data = self.stream.read(self.CHUNK) # read audio data
        wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data) # unpack it
        wf_data = np.array(wf_data, dtype='b')[::2] + 128 # turn the unpacked string into a number array
        self.set_plotData(name='waveform', data_x=self.x, data_y=wf_data, )

        # spectrum transform
        sp_data = fft(np.array(wf_data, dtype='int8') - 128) # fft of waveform stream chunk
        # get absolute value and normlize so that all the peaks are less than 1
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)]) * 2 / (128 / self.CHUNK)
        self.set_plotData(name='spectrum', data_x=self.x_f, data_y=sp_data, )

    def animate(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()

if __name__ == '__main__':
    audio_app = AudioStream()
    audio_app.animate()
