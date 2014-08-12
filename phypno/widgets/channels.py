"""Widget to define channels, montage and filters.

"""
from logging import getLogger
lg = getLogger(__name__)

from copy import deepcopy
from json import dump, load
from os.path import splitext

from PyQt4.QtGui import (QAbstractItemView,
                         QAction,
                         QColor,
                         QColorDialog,
                         QDoubleSpinBox,
                         QFileDialog,
                         QFormLayout,
                         QGridLayout,
                         QGroupBox,
                         QHBoxLayout,
                         QInputDialog,
                         QListWidget,
                         QListWidgetItem,
                         QPushButton,
                         QVBoxLayout,
                         QTabWidget,
                         QWidget
                         )


from .settings import Config, FormFloat, FormStr


class ConfigChannels(Config):
    """Widget with preferences in Settings window for Channels."""
    def __init__(self, update_widget):
        super().__init__('channels', update_widget)

    def create_config(self):
        box0 = QGroupBox('Channels')

        self.index['hp'] = FormFloat()
        self.index['lp'] = FormFloat()
        self.index['color'] = FormStr()
        self.index['scale'] = FormFloat()

        form_layout = QFormLayout()
        form_layout.addRow('Default High-Pass Filter', self.index['hp'])
        form_layout.addRow('Default Low-Pass Filter', self.index['lp'])
        form_layout.addRow('Default Color', self.index['color'])
        form_layout.addRow('Default Scale', self.index['scale'])
        box0.setLayout(form_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(box0)
        main_layout.addStretch(1)

        self.setLayout(main_layout)


class ChannelsGroup(QWidget):
    """Tab inside the Channels widget.

    Parameters
    ----------
    chan_name : list of str
        list of all the channels in the dataset
    config_value : dict
        default values for the channels
    s_freq : int
        sampling frequency (to define max of filter)

    Attributes
    ----------
    chan_name : list of str
        list of all the channels in the dataset

    idx_l0 : QListWidget
        list with the channels to plot
    idx_l1 : QListWidget
        list with the channels to use as reference
    idx_hp : QDoubleSpinBox
        spin box to indicate the high-pass filter
    idx_lp : QDoubleSpinBox
        spin box to indicate the low-pass filter
    idx_scale : QDoubleSpinBox
        spin_box to indicate the group-specific scaling
    idx_reref : QPushButton
        it triggers a selection of reference channels equal to the channels to
        plot.
    idx_color : QColor
        color of the traces beloning to this channel group (it could be a
        property of QWidget)

    Notes
    -----
    TODO: re-referencing should be more flexible, by allowing other types of
    referencing.

    Use config_value instead of config, because it's easier to pass dict
    when loading channels montage.
    """
    def __init__(self, chan_name, config_value, s_freq):
        super().__init__()

        self.chan_name = chan_name

        self.idx_l0 = QListWidget()
        self.idx_l1 = QListWidget()

        self.add_channels_to_list(self.idx_l0)
        self.add_channels_to_list(self.idx_l1)

        self.idx_hp = QDoubleSpinBox()
        self.idx_hp.setValue(config_value['hp'])
        self.idx_hp.setSuffix(' Hz')
        self.idx_hp.setDecimals(1)
        self.idx_hp.setMaximum(s_freq / 2)
        self.idx_hp.setToolTip('0 means no filter')

        self.idx_lp = QDoubleSpinBox()
        self.idx_lp.setValue(config_value['lp'])
        self.idx_lp.setSuffix(' Hz')
        self.idx_lp.setDecimals(1)
        self.idx_lp.setMaximum(s_freq / 2)
        self.idx_lp.setToolTip('0 means no filter')

        self.idx_scale = QDoubleSpinBox()
        self.idx_scale.setValue(config_value['scale'])
        self.idx_scale.setSuffix('x')

        self.idx_reref = QPushButton('Average')
        self.idx_reref.clicked.connect(self.rereference)

        self.idx_color = QColor(config_value['color'])

        l_form = QFormLayout()
        l_form.addRow('High-Pass', self.idx_hp)
        l_form.addRow('Low-Pass', self.idx_lp)

        r_form = QFormLayout()
        r_form.addRow('Scaling', self.idx_scale)
        r_form.addRow('Reference', self.idx_reref)

        l_layout = QHBoxLayout()
        l_layout.addWidget(self.idx_l0)
        l_layout.addWidget(self.idx_l1)

        lr_form = QHBoxLayout()
        lr_form.addLayout(l_form)
        lr_form.addLayout(r_form)

        layout = QVBoxLayout()
        layout.addLayout(l_layout)
        layout.addLayout(lr_form)

        self.setLayout(layout)

    def add_channels_to_list(self, l):
        """Create list of channels (one for those to plot, one for ref).

        Parameters
        ----------
        l : instance of QListWidget
            one of the two lists (chan_to_plot or ref_chan)
        """
        l.clear()

        l.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for chan in self.chan_name:
            item = QListWidgetItem(chan)
            l.addItem(item)

    def highlight_channels(self, l, selected_chan):
        """Highlight channels in the list of channels.

        Parameters
        ----------
        selected_chan : list of str
            channels to indicate as selected.
        """
        for row in range(l.count()):
            item = l.item(row)
            if item.text() in selected_chan:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def rereference(self):
        """Automatically highlight channels to use as reference, based on
        selected channels."""
        selectedItems = self.idx_l0.selectedItems()

        chan_to_plot = []
        for selected in selectedItems:
            chan_to_plot.append(selected.text())
        self.highlight_channels(self.idx_l1, chan_to_plot)

    def get_info(self):
        """Get the information about the channel groups.

        Returns
        -------
        dict
            information about this channel group

        Notes
        -----
        The items in selectedItems() are ordered based on the user's selection
        (which appears pretty random). It's more consistent to use the same
        order of the main channel list. That's why the additional for-loop
        is necessary. We don't care about the order of the reference channels.
        """
        selectedItems = self.idx_l0.selectedItems()
        selected_chan = [x.text() for x in selectedItems]
        chan_to_plot = []
        for chan in self.chan_name:
            if chan in selected_chan:
                chan_to_plot.append(chan)

        selectedItems = self.idx_l1.selectedItems()
        ref_chan = []
        for selected in selectedItems:
            ref_chan.append(selected.text())

        hp = self.idx_hp.value()
        if hp == 0:
            low_cut = None
        else:
            low_cut = hp

        lp = self.idx_lp.value()
        if lp == 0:
            high_cut = None
        else:
            high_cut = lp

        scale = self.idx_scale.value()

        group_info = {'name': '',  # not present in widget
                      'chan_to_plot': chan_to_plot,
                      'ref_chan': ref_chan,
                      'hp': low_cut,
                      'lp': high_cut,
                      'scale': float(scale),
                      'color': self.idx_color
                      }

        return group_info


class Channels(QWidget):
    """Widget with information about channel groups.

    Attributes
    ----------
    parent : QMainWindow
        the main window
    config : ConfigChannels
        preferences for this widget

    filename : path to file
        file with the channel groups
    groups : list of dict
        each dict contains information about one channel group
    chan_name : list of str
        list of all the channels in the dataset

    tabs : QTabWidget
        Widget that contains the tabs with channel groups
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.config = ConfigChannels(lambda: None)

        self.filename = None
        self.groups = []
        self.chan_name = []  # those in the dataset

        self.tabs = None

        self.create()
        self.create_action()

    def create(self):
        """Create Channels Widget"""
        add_button = QPushButton('New')
        add_button.clicked.connect(self.new_group)
        color_button = QPushButton('Color')
        color_button.clicked.connect(self.color_group)
        del_button = QPushButton('Delete')
        del_button.clicked.connect(self.del_group)
        apply_button = QPushButton('Apply')
        apply_button.clicked.connect(self.apply)

        buttons = QGridLayout()
        buttons.addWidget(add_button, 0, 0)
        buttons.addWidget(color_button, 1, 0)
        buttons.addWidget(del_button, 0, 1)
        buttons.addWidget(apply_button, 1, 1)

        self.tabs = QTabWidget()

        layout = QVBoxLayout()
        layout.addLayout(buttons)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def create_action(self):
        """Create actions related to channel selection."""
        actions = {}

        act = QAction('Load Channels Montage...', self)
        act.triggered.connect(self.load_channels)
        actions['load_channels'] = act

        act = QAction('Save Channels Montage...', self)
        act.triggered.connect(self.save_channels)
        actions['save_channels'] = act

        self.action = actions

    def update(self, chan_name):
        """Read the channels and updates the widget.

        Parameters
        ----------
        chan_name : list of str
            list of channels, to choose from.

        """
        self.chan_name = chan_name

    def new_group(self):
        """Create a new channel group.

        Notes
        -----
        It's not necessary to call self.apply()

        """
        if self.chan_name is None:
            self.parent.statusBar().showMessage('No dataset loaded')

        else:
            new_name = QInputDialog.getText(self, 'New Channel Group',
                                            'Enter Name')
            if new_name[1]:
                s_freq = self.parent.info.dataset.header['s_freq']
                group = ChannelsGroup(self.chan_name, self.config.value,
                                      s_freq)
                self.tabs.addTab(group, new_name[0])
                self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)

    def color_group(self):
        """Change the color of the group."""
        group = self.tabs.currentWidget()
        newcolor = QColorDialog.getColor(group.idx_color)
        group.idx_color = newcolor

        self.apply()

    def del_group(self):
        """Delete current group."""
        idx = self.tabs.currentIndex()
        self.tabs.removeTab(idx)

        self.apply()

    def apply(self):
        """Apply changes to the plots."""
        self.read_group_info()
        self.parent.overview.update_position()
        self.parent.spectrum.update()

    def read_group_info(self):
        self.groups = []
        for i in range(self.tabs.count()):
            one_group = self.tabs.widget(i).get_info()
            one_group['name'] = self.tabs.tabText(i)
            self.groups.append(one_group)

    def load_channels(self, debug_filename=None):
        """Load channel groups from file. """
        if not debug_filename:
            if self.filename is not None:
                filename = self.filename
            elif self.parent.info.filename is not None:
                filename = (splitext(self.parent.info.filename)[0] +
                            '_channels.json')
            else:
                filename = None

            filename = QFileDialog.getOpenFileName(self, 'Open Channels Montage',
                                                   filename,
                                                   'Channels File (*.json)')
            if filename == '':
                return
        else:
            filename = debug_filename

        self.filename = filename
        with open(filename, 'r') as outfile:
            groups = load(outfile)

        for one_grp in groups:
            group = ChannelsGroup(self.chan_name, one_grp)
            group.highlight_channels(group.idx_l0, one_grp['chan_to_plot'])
            group.highlight_channels(group.idx_l1, one_grp['ref_chan'])
            self.tabs.addTab(group, one_grp['name'])

        self.apply()

    def save_channels(self):
        """Save channel groups to file."""
        self.read_group_info()

        if self.filename is not None:
            filename = self.filename
        elif self.parent.info.filename is not None:
            filename = (splitext(self.parent.info.filename)[0] +
                        '_channels.json')
        else:
            filename = None

        filename = QFileDialog.getSaveFileName(self, 'Save Channels Montage',
                                               filename,
                                               'Channels File (*.json)')
        if filename == '':
            return

        self.filename = filename

        groups = deepcopy(self.groups)
        for one_grp in groups:
            one_grp['color'] = one_grp['color'].rgba()

        with open(filename, 'w') as outfile:
            dump(groups, outfile, indent=' ')

    def reset(self):
        """Reset all the information of this widget."""
        self.filename = None
        self.chan_name = []
        self.groups = []

        self.tabs.clear()
