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
        self.ui.listWidget.currentItemChanged.connect(self.list_item_clicked)

    def setup_menu_items(self):
        """!
        @brief Connects menu items to actions
        """
        #self.ui.actionSave.triggered.connect(self.save_dialog)
        self.ui.actionExit_2.triggered.connect(self.exit_gui)
        self.ui.actionOpen.triggered.connect(self.import_file)
        self.ui.actionImport.triggered.connect(self.import_file)
        self.ui.actionAdd_Peak.triggered.connect(self.new_vline)
        self.ui.actionAuto_Peaks.triggered.connect(self.auto_add_peaks)
        self.ui.actionDelete_Peak.triggered.connect(self.delete_list_item)

    def import_file(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Import File', filter='*.CNF *.h5 *.hdf5')
        # read file
        dreader = reader.DataReader()
        mdata, edata = dreader.read(name)
        # init the spectrum
        self.spectrum = spectrum.GammaSpectrum(edata)
        self.clean_plot()

    def setup_buttons(self):
        """!
        @brief Connects buttons to actions
        """
        self.ui.pushFitPeak.clicked.connect(self.fit_selected_peak)
        self.ui.pushClean.clicked.connect(self.clean_plot)
        self.ui.pushShowPeaks.clicked.connect(self.show_peak_locs)
        self.ui.toolAddPeak.clicked.connect(self.manual_add_peak)

    def manual_add_peak(self):
        if self.current_vline_loc:
            print("adding peak at E= %f (keV)" % self.current_vline_loc)
            self.spectrum.add_peak(self.current_vline_loc)
            self.add_single_list_item()

    def auto_add_peaks(self):
        """!
        @brief Runs automated peak finding routine.  Adds
        all found peaks to the peak_bank
        """
        self.spectrum.auto_peaks()
        # show the peaks
        self.show_peak_locs()
        self.update_list_item_db()

    def setup_plot(self):
        self.current_vline_loc = None

    def clean_plot(self):
        if hasattr(self, 'spectrum'):
            # self.ui.plotSpectrum.clear()
            self.ui.plotSpectrum.plot(self.spectrum.spectrum, clean=True, clickable=True)
            for item in self.ui.plotSpectrum.allChildItems():
                if type(item) == pg.graphicsItems.InfiniteLine.InfiniteLine:
                    print("cleaned: %s" % type(item))
                    self.ui.plotSpectrum.removeItem(item)
            self.label = pg.LabelItem()
            self.ui.plotSpectrum.addItem(self.label)

    def moved_line(self):
        # print("Hey, you moved me")
        self.current_vline_loc = self.mousePoint.x()

    def show_peak_locs(self):
        for peak_loc in self.spectrum.peak_bank.keys():
            # draw vert lines on screen at peak locs
            peak_line = pg.InfiniteLine(pos=peak_loc, movable=False, pen='y')
            self.ui.plotSpectrum.addItem(peak_line)

    def new_vline(self):
        if hasattr(self, 'mousePoint'):
            if hasattr(self, 'vert_line'):
                # remove current vert line
                self.ui.plotSpectrum.removeItem(self.vert_line)
                del self.vert_line
            self.vert_line = pg.InfiniteLine(pos=self.mousePoint.x(), movable=True, pen='g')
            self.vert_line.sigPositionChanged.connect(self.moved_line)
            self.ui.plotSpectrum.addItem(self.vert_line)
            self.current_vline_loc = self.mousePoint.x()

    # ======== Scatter Plot ================================================= #
    def add_scatter(self):
        scatterPlot = pg.ScatterPlotItem(x=self.spectrum.spectrum[:, 0],
                                         y=self.spectrum.spectrum[:, 1],
                                         size=5)
        scatterPlot.sigClicked.connect(self.selected_data)
        self.ui.plotSpectrum.addItem(scatterPlot)


    def selected_data(self, plot, points):
        for p in self.last_clicked:
            p.resetPen()
        print("clicked points", points)
        for p in points:
            p.setPen('b', width=30)
        self.last_clicked = points
    # ======== End Scatter Plot ============================================== #

    # ======== Mouse Tracking ================================================ #
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.ui.plotSpectrum.sceneBoundingRect().contains(pos) and hasattr(self, 'spectrum') and hasattr(self, 'label'):
            mousePoint = self.ui.plotSpectrum.plotItem.vb.mapSceneToView(pos)
            self.mousePoint = mousePoint
            index = int(mousePoint.x())
            if index > 0 and index < len(self.spectrum.spectrum[:, 0]):
                self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), self.spectrum.spectrum[index, 1], 0.0))
    # ======= End Mouse Tracking ============================================= #

    #======== List Widget ==================================================== #
    def add_single_list_item(self):
        """!
        @brief On event create peak, update the peaks in the list to
        reflect current state of self.spectrum.peak_bank
        """
        self.update_list_item_db()

    def update_list_item_db(self):
        self.ui.listWidget.clear()
        for peak_loc in self.spectrum.peak_bank.keys():
            # new_item = QtGui.QListWidgetItem("Peak E(KeV)=" + str(peak_loc))
            new_item = QtGui.QListWidgetItem(str(peak_loc))
            new_item.setText("Peak E(KeV)=" + str(peak_loc))
            # args: (role, value)
            new_item.setData(0, peak_loc)
            self.ui.listWidget.addItem(new_item)

    def delete_list_item(self):
        del_flagged_item = self.ui.listWidget.currentItem()
        del_peak_loc = del_flagged_item.data(0)
        self.spectrum.pop_peak(del_peak_loc)
        row = self.ui.listWidget.currentRow()
        self.ui.listWidget.takeItem(row)
        #
        self.update_list_item_db()
        self.del_selected_peak_line()
        self.del_selected_roi()

    def del_selected_peak_line(self):
        if hasattr(self, 'selected_peak_line'):
            # remove current vert line
            self.ui.plotSpectrum.removeItem(self.selected_peak_line)
            del self.selected_peak_line

    def del_selected_roi(self):
        if hasattr(self, 'selected_roi'):
            # remove current vert line
            self.ui.plotSpectrum.removeItem(self.selected_roi)
            del self.selected_roi

    def list_item_clicked(self, arg=None):
        # role=0 is energy loc
        if arg:
            # Display selected peak info
            print("Selected Peak: %f" % arg.data(0))
            # Display peak centroid
            self.del_selected_peak_line()
            self.selected_peak_line = pg.InfiniteLine(pos=arg.data(0), movable=False, pen='r')
            self.ui.plotSpectrum.addItem(self.selected_peak_line)
            # Display peak ROI
            self.del_selected_roi()
            self.selected_peak = self.spectrum.peak_bank[arg.data(0)]
            values = [self.spectrum.peak_bank[arg.data(0)].lbound,
                      self.spectrum.peak_bank[arg.data(0)].ubound]
            self.manual_roi(values)

    def update_selected_roi(self):
        updated_roi_bounds = self.selected_roi.getRegion()
        self.selected_peak.lbound = updated_roi_bounds[0]
        self.selected_peak.ubound = updated_roi_bounds[-1]

    def manual_roi(self, values=[990, 1100]):
        self.selected_roi = pg.LinearRegionItem(values=values, movable=True)
        self.selected_roi.sigRegionChanged.connect(self.update_selected_roi)
        self.ui.plotSpectrum.addItem(self.selected_roi)
    #========= End List Widget ================================================ #

    def fit_selected_peak(self):
        if hasattr(self, 'selected_peak'):
            self.selected_peak.fit()
            y = self.selected_peak.y_hat
            x = self.selected_peak.roi_data[:, 0]
            fit_plot = pg.PlotCurveItem(x=x, y=y, pen='r')
            self.ui.plotSpectrum.addItem(fit_plot)

    def exit_gui(self):
        sys.exit(0)

def main():
    win = MainWindow()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    main()
