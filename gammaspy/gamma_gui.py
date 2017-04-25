#!/usr/bin/python3
from six import iteritems

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import os
import sys
# gammaspy imports
from gammaData import reader, spectrum


## Define main window class from template
pg.mkQApp()
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'gammaspy_gui_lite.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)


class MainWindow(TemplateBaseClass):
    def __init__(self):
        TemplateBaseClass.__init__(self)
        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.setWindowTitle('GammaSpy')
        self.show()
        # Setup buttons/widgets
        self.setup_plot()
        self.setup_menu_items()
        self.setup_buttons()
        # internal data
        self.last_clicked = []
        self.proxy = pg.SignalProxy(self.ui.plotSpectrum.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def setup_menu_items(self):
        """!
        @brief Connects menu items to actions
        """
        self.ui.actionExit_2.triggered.connect(self.exit_gui)
        self.ui.actionOpen.triggered.connect(self.import_file)
        self.ui.actionImport.triggered.connect(self.import_file)
        #self.ui.actionSave.triggered.connect(self.save_dialog)
        self.ui.actionAdd_Peak.triggered.connect(self.new_vline)

    def import_file(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Import File', filter='*.CNF *.h5 *.hdf5')
        # read file
        dreader = reader.DataReader()
        mdata, edata = dreader.read(name)
        # init the spectrum
        self.spectrum = spectrum.GammaSpectrum(edata)

    def setup_buttons(self):
        """!
        @brief Connects buttons to actions
        """
        # self.ui.pushFitPeak.clicked.connect(self.add_scatter)
        self.ui.pushClean.clicked.connect(self.clean_plot)
        self.ui.toolAddPeak.clicked.connect(self.manual_add_peak)

    def manual_add_peak(self):
        if self.current_vline_loc:
            print("adding peak at E= %f (keV)" % self.current_vline_loc)
            self.spectrum.add_peak(self.current_vline_loc)

    def setup_plot(self):
        self.current_vline_loc = None

    def clean_plot(self):
        if hasattr(self, 'spectrum'):
            self.ui.plotSpectrum.clear()
            self.ui.plotSpectrum.plot(self.spectrum.spectrum, clean=True, clickable=True)
            self.label = pg.LabelItem()
            self.ui.plotSpectrum.addItem(self.label)

    def add_scatter(self):
        scatterPlot = pg.ScatterPlotItem(x=self.spectrum.spectrum[:, 0],
                                         y=self.spectrum.spectrum[:, 1],
                                         size=5)
        scatterPlot.sigClicked.connect(self.selected_data)
        self.ui.plotSpectrum.addItem(scatterPlot)

    def moved_line(self):
        print("Hey you moved me!")

    def new_vline(self):
        if hasattr(self, 'mousePoint'):
            vert_line = pg.InfiniteLine(pos=self.mousePoint.x(), movable=True)
            vert_line.sigPositionChanged.connect(self.moved_line)
            self.ui.plotSpectrum.addItem(vert_line)
            # remove all other ver lines
            self.current_vline_loc = self.mousePoint.x()

    def manual_roi(self):
        roi = pg.LinearRegionItem(values=[990, 1100], movable=True)
        self.ui.plotSpectrum.addItem(roi)

    def selected_data(self, plot, points):
        for p in self.last_clicked:
            p.resetPen()
        print("clicked points", points)
        for p in points:
            p.setPen('b', width=30)
        self.last_clicked = points


    # ======== Mouse Tracking ================================================ #
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.ui.plotSpectrum.sceneBoundingRect().contains(pos) and hasattr(self, 'spectrum') and hasattr(self, 'label'):
            mousePoint = self.ui.plotSpectrum.plotItem.vb.mapSceneToView(pos)
            self.mousePoint = mousePoint
            index = int(mousePoint.x())
            if index > 0 and index < len(self.spectrum.spectrum[:, 0]):
                self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), self.spectrum.spectrum[index, 1], 0.0))
            #vLine.setPos(mousePoint.x())
            #hLine.setPos(mousePoint.y())

    def exit_gui(self):
        sys.exit(0)

def main():
    win = MainWindow()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    main()
