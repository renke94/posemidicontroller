from typing import List, Set

import numpy as np
from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex
from PyQt6.QtWidgets import QTableView, QWidget, QHeaderView
from rtmidi import MidiMessage

from .app_state import AppState
from .pyquantum.delegates import ComboBoxDelegate
from .pyquantum.ui import Button


class MidiMapping:
    columns = ["Control", "Parameter", "Function"]
    parameters = [
        "-",
        "NoseX", "NoseY",
        "LeftHandX", "LeftHandY", "RightHandX", "RightHandY",
        "Function",
    ]

    alignments = [
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
    ]

    delegates = [None, ComboBoxDelegate(items=parameters)]
    editable = [False, True, True]

    def __init__(self, control: int):
        self.control = control
        self.name = MidiMessage.getControllerName(control) or "-"
        self.mapping = 0
        self.function = "0.0"

    def __getitem__(self, idx: int):
        return [
            self.name,
            MidiMapping.parameters[self.mapping],
            self.function
        ][idx]

    def __setitem__(self, idx: int, value):
        match idx:
            case 1:
                self.mapping = value
            case 2:
                self.function = value

    def push_button(self, parent: QWidget):
        def send_test_signal():
            AppState.midi_controller.send_cc(self.control, 0.0)

        return Button(
            parent,
            self.name,
            on_click=send_test_signal,
        )

    def send_midi(self, **kwargs):
        param = MidiMapping.parameters[self.mapping]
        if param == 'Function':
            param = eval(self.function, None, kwargs)
        else:
            param = kwargs.get(param)
            if param is None:
                return
        AppState.midi_controller.send_cc(self.control, np.clip(param, 0, 1))

    def __str__(self):
        return f"MidiMapping({self.control}, {self.name})"

    def __repr__(self):
        return str(self)


class MidiMappingTableModel(QAbstractTableModel):
    def __init__(self):
        super(MidiMappingTableModel, self).__init__()
        self.midi_mappings: List[MidiMapping] = [MidiMapping(i) for i in range(128)]
        self.registrations: Set[MidiMapping] = set()

    def send_midi(self, **kwargs):
        for mapping in self.registrations:
            mapping.send_midi(**kwargs)

    def rowCount(self, parent):
        return len(self.midi_mappings)

    def columnCount(self, parent):
        return len(MidiMapping.columns)

    def data(self, index, role):
        col = index.column()
        row = index.row()
        if role in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole}:
            return self.midi_mappings[row][col]
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return int(MidiMapping.alignments[col])

    def setData(self, index: QModelIndex, value, role: int = ...) -> bool:
        row = index.row()
        col = index.column()
        if role == Qt.ItemDataRole.EditRole:
            if not index.isValid():
                return False
            mapping = self.midi_mappings[row]
            mapping[col] = value
            if col == 1:
                if value == 0:
                    self.registrations.discard(mapping)
                else:
                    self.registrations.add(mapping)
            return True
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return MidiMapping.columns[section]
            elif orientation == Qt.Orientation.Vertical:
                return section

        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flag = super(MidiMappingTableModel, self).flags(index)
        if MidiMapping.editable[index.column()]:
            flag |= Qt.ItemFlag.ItemIsEditable
        return flag


class MidiMappingTableView(QTableView):
    def __init__(
            self,
            parent=None,
    ):
        super(MidiMappingTableView, self).__init__(parent=parent)
        self.model = MidiMappingTableModel()
        self.setModel(self.model)

        self.setColumnWidth(0, 200)
        header = self.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        for i in range(128):
            self.setIndexWidget(
                self.model.index(i, 0),
                self.model.midi_mappings[i].push_button(self)
            )

        for i, d in enumerate(MidiMapping.delegates):
            if d:
                self.setItemDelegateForColumn(i, d)

    def send_midi(self, **kwargs):
        self.model.send_midi(**kwargs)
