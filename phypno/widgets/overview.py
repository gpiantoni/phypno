"""Wide widget giving an overview of the markers, events, and sleep scores.

"""
from logging import getLogger
lg = getLogger(__name__)

from datetime import datetime, timedelta

from numpy import floor
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QBrush,
                         QPen,
                         QGraphicsLineItem,
                         QGraphicsRectItem,
                         QGraphicsScene,
                         QGraphicsView,
                         QGraphicsItem,
                         QFormLayout,
                         QGroupBox,
                         QVBoxLayout,
                         )

from .settings import Config, FormInt

# marker
# event
# stage
# available
current_line_height = 10

NoPen = QPen()
NoPen.setStyle(Qt.NoPen)

NoBrush = QBrush()
NoBrush.setStyle(Qt.NoBrush)

STAGES = {'Wake': {'pos0': 5, 'pos1': 25, 'color': Qt.black},
          'Movement': {'pos0': 5, 'pos1': 25, 'color': Qt.gray},
          'REM': {'pos0': 10, 'pos1': 20, 'color': Qt.magenta},
          'NREM1': {'pos0': 15, 'pos1': 15, 'color': Qt.cyan},
          'NREM2': {'pos0': 20, 'pos1': 10, 'color': Qt.blue},
          'NREM3': {'pos0': 25, 'pos1': 5, 'color': Qt.darkBlue},
          'Unknown': {'pos0': 30, 'pos1': 0, 'color': NoBrush},
          }

BARS = {'marker': {'pos0': 15, 'pos1': 10, 'tip': 'Markers'},
        'event': {'pos0': 30, 'pos1': 10, 'tip': 'Events'},
        'stage': {'pos0': 45, 'pos1': 30, 'tip': 'Sleep Stage'},
        'available': {'pos0': 80, 'pos1': 10, 'tip': 'Available Recordings'},
        }
TIME_HEIGHT = 92
TOTAL_HEIGHT = 100


class ConfigOverview(Config):

    def __init__(self, update_widget):
        super().__init__('overview', update_widget)

    def create_config(self):

        box0 = QGroupBox('Current Window')
        self.index['window_start'] = FormInt()
        self.index['window_length'] = FormInt()
        self.index['window_step'] = FormInt()

        form_layout = QFormLayout()
        form_layout.addRow('Window start time',
                           self.index['window_start'])
        form_layout.addRow('Window length',
                           self.index['window_length'])
        form_layout.addRow('Step size',
                           self.index['window_step'])
        box0.setLayout(form_layout)

        box1 = QGroupBox('Overview')
        self.index['timestamp_steps'] = FormInt()
        self.index['overview_scale'] = FormInt()

        form_layout = QFormLayout()
        form_layout.addRow('Steps in overview (in s)',
                           self.index['timestamp_steps'])
        form_layout.addRow('One pixel corresponds to (s)',
                           self.index['overview_scale'])

        box1.setLayout(form_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(box0)
        main_layout.addWidget(box1)
        main_layout.addStretch(1)

        self.setLayout(main_layout)


class Overview(QGraphicsView):
    """Show an overview of data, such as hypnogram and data in memory.

    Attributes
    ----------
    parent : instance of QMainWindow
        the main window.
    window_start : int or float
        start time of the window being plotted (in s).
    window_length : int or float
        length of the window being plotted (in s).
    maximum : int or float
        maximum length of the window (in s).
    scene : instance of QGraphicsScene
        to keep track of the objects.
    idx_item : dict of RectItem, SimpleText
        all the items in the scene

    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.config = ConfigOverview(self.display_overview)  # TODO: it should update trace too

        self.minimum = None
        self.maximum = None

        self.scene = None
        self.idx_item = {}

        self.create_overview()

    def create_overview(self):
        """Define the area of QGraphicsView."""
        self.setMinimumHeight(TOTAL_HEIGHT + 30)

    def update_overview(self):
        """Read full duration and update maximum."""
        header = self.parent.info.dataset.header
        maximum = header['n_samples'] / header['s_freq']  # in s
        self.minimum = 0
        self.maximum = maximum

        self.config.value['window_start'] = 0  # the only exception, start at zero

        self.display_overview()

    def display_overview(self):
        """Updates the widgets, especially based on length of recordings."""
        lg.debug('GraphicsScene is between {}s and {}s'.format(self.minimum,
                                                               self.maximum))

        x_scale = 1 / self.config.value['overview_scale']
        lg.debug('Set scene x-scaling to {}'.format(x_scale))

        self.scale(1 / self.transform().m11(), 1)  # reset to 1
        self.scale(x_scale, 1)

        self.scene = QGraphicsScene(self.minimum, 0,
                                    self.maximum,
                                    TOTAL_HEIGHT)
        self.setScene(self.scene)

        lg.debug('WINDOW START ' + str(self.config.value['window_start']))
        self.idx_item['current'] = QGraphicsLineItem(self.config.value['window_start'], 0,
                                                     self.config.value['window_start'],
                                                     current_line_height)
        self.idx_item['current'].setPen(QPen(Qt.red))
        self.scene.addItem(self.idx_item['current'])

        for name, pos in BARS.items():
            self.idx_item[name] = QGraphicsRectItem(self.minimum, pos['pos0'],
                                                    self.maximum, pos['pos1'])
            self.idx_item[name].setToolTip(pos['tip'])
            self.scene.addItem(self.idx_item[name])

        self.add_timestamps()

    def add_timestamps(self):
        """Add timestamps at the bottom of the overview.

        TODO: to improve, don't rely on the hour

        """
        start_time_dataset = self.parent.info.dataset.header['start_time']
        start_time = start_time_dataset + timedelta(seconds=self.minimum)
        first_hour = int(datetime(start_time.year, start_time.month,
                                  start_time.day,
                                  start_time.hour + 1).timestamp())

        end_time = start_time_dataset + timedelta(seconds=self.maximum)
        last_hour = int(datetime(end_time.year, end_time.month,
                                 end_time.day,
                                 end_time.hour + 1).timestamp())

        steps = self.config.value['timestamp_steps']
        transform, _ = self.transform().inverted()

        for t in range(first_hour, last_hour, steps):
            t_as_datetime = datetime.fromtimestamp(t)
            date_as_text = t_as_datetime.strftime('%H:%M')

            text = self.scene.addSimpleText(date_as_text)
            text.setFlag(QGraphicsItem.ItemIgnoresTransformations)

            # set xpos and adjust for text width
            xpos = (t_as_datetime - start_time).total_seconds()
            text_width = text.boundingRect().width() * transform.m11()
            text.setPos(xpos - text_width / 2, TIME_HEIGHT)

    def update_position(self, new_position=None):
        """Update the cursor position and much more.

        Parameters
        ----------
        new_position : int or float
            new position in s, for plotting etc.

        Notes
        -----
        This is a central function. It updates the cursor, then updates
        the traces, the scores, and the power spectrum. In other words, this
        function is responsible for keep track of the changes every time
        the start time of the window changes.

        """
        if new_position is not None:
            lg.debug('Updating position to {}'.format(new_position))
            self.config.value['window_start'] = new_position
            self.idx_item['current'].setPos(self.config.value['window_start'],
                                            0)

            header = self.parent.info.dataset.header
            current_time = (header['start_time'] +
                            timedelta(seconds=new_position))
            msg = 'Current time: ' + current_time.strftime('%H:%M:%S')
            self.parent.statusBar().showMessage(msg)
        else:
            lg.debug('Updating position at {}'
                     ''.format(self.config.value['window_start']))

        self.parent.traces.update_traces()
        self.parent.spectrum.display_spectrum()
        if self.parent.notes.annot is not None:
            self.parent.notes.set_combobox_index()

    def mark_downloaded(self, start_value, end_value):
        """Set the value of the progress bar.

        Parameters
        ----------
        start_value : int
            beginning of the window that was read.
        end_value : int
            end of the window that was read.

        """
        avail = self.scene.addRect(start_value,
                                   BARS['available']['pos0'],
                                   end_value - start_value,
                                   BARS['available']['pos1'])
        avail.stackBefore(self.idx_item['available'])
        avail.setPen(NoPen)
        avail.setBrush(QBrush(Qt.green))

    def mousePressEvent(self, event):
        """Jump to window when user clicks on overview.

        Parameters
        ----------
        event : instance of QtCore.QEvent
            it contains the position that was clicked.

        Notes
        -----
        This function overwrites Qt function, therefore the non-standard
        name. Argument also depends on Qt.

        """
        x_in_scene = self.mapToScene(event.pos()).x()
        window_length = self.config.value['window_length']
        window_start = int(floor(x_in_scene / window_length) * window_length)
        self.update_position(window_start)
