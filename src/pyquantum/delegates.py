from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, QObject, QLocale
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QWidget, QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QComboBox, QPushButton


def to_comma_event(e: QtGui.QKeyEvent):
    return QtGui.QKeyEvent(
        e.type(),
        Qt.Key.Key_Comma,
        e.modifiers(),
        e.nativeScanCode(),
        e.nativeVirtualKey(),
        e.nativeModifiers(),
        text=",",
        autorep=e.isAutoRepeat(),
        count=e.count(),
        device=e.device()
    )


def to_period_event(e: QtGui.QKeyEvent):
    return QtGui.QKeyEvent(
        e.type(),
        Qt.Key.Key_Period,
        e.modifiers(),
        e.nativeScanCode(),
        e.nativeVirtualKey(),
        e.nativeModifiers(),
        text=".",
        autorep=e.isAutoRepeat(),
        count=e.count(),
        device=e.device()
    )


class FloatInput(QLineEdit):
    floatKeys = {Qt.Key.Key_Comma, Qt.Key.Key_Period}

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.resize(100, 30)
        self.validator = QDoubleValidator()
        self.validator.setDecimals(3)
        self.validator.setLocale(QLocale(QLocale.Language.English))
        self.setValidator(self.validator)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() in FloatInput.floatKeys:
            e = to_period_event(e)
        super(FloatInput, self).keyPressEvent(e)


class FloatDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QWidget:
        editor = FloatInput(parent)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        value = str(index.model().data(index, Qt.ItemDataRole.EditRole) or "")
        editor.__class__ = FloatInput
        editor.setText(value)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor.__class__ = FloatInput
        value = float(editor.text())
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)


class IntegerInput(QLineEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.resize(100, 30)
        self.setValidator(QIntValidator())


class IntegerDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QWidget:
        editor = IntegerInput(parent)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        value = str(index.model().data(index, Qt.ItemDataRole.EditRole) or "")
        editor.__class__ = IntegerInput
        editor.setText(value)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor.__class__ = IntegerInput
        text = str(editor.text())
        value = int(text) if text.isnumeric() else None
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)


class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QPushButton(parent, "Send Test Signal")
        return editor

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)



class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items=[], parent: QObject = None) -> None:
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QWidget:
        editor = QComboBox(parent)
        editor.addItems(self.items)
        editor.setFrame(False)
        return editor

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor.__class__ = QComboBox
        value = editor.currentIndex()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)
