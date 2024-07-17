from pathlib import Path
from typing import Union, List, Optional, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QPushButton, QLineEdit, QPlainTextEdit, QHBoxLayout, QLayout, QVBoxLayout, \
    QGridLayout, QSplitter, QFrame, QFileDialog, QComboBox, QTabWidget

from src.pyquantum.value import Value, Observer


class TabView(QTabWidget):
    def __init__(
            self,
            parent: QWidget,
            tabs: dict[str, QWidget],
    ):
        super(TabView, self).__init__(parent=parent)
        for name, widget in tabs.items():
            self.addTab(widget, name)

class ComboBox(QComboBox):
    def __init__(
            self,
            parent: QWidget,
            items: List[str],
            enabled: Union[Value, bool] = True,
            index_changed: Callable[[int], None] = None,
            min_width: int = None,
            max_width: int = None,
            stretch: int = 0
    ):
        super(ComboBox, self).__init__(parent=parent)
        self.addItems(items)
        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if index_changed is not None:
            self.currentIndexChanged[int].connect(index_changed)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)

        self._stretch = stretch

class Label(QLabel):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Value, str],
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None,
            stretch: int = 0
    ):
        super(Label, self).__init__(parent=parent)
        if isinstance(value, Value):
            self.setText(value.data)
            self._value_observer = Observer([value])
            self._value_observer.on_update(self.setText)
        else:
            self.setText(value)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)

        self._stretch = stretch


class Button(QPushButton):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Value, str],
            on_click=None,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None,
            stretch: int = 0,
    ):
        super(Button, self).__init__(parent=parent)

        if isinstance(value, Value):
            self.setText(value.data)
            self._text_observer = Observer([value])
            self._text_observer.on_update(self.setText)
        else:
            self.setText(value)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if on_click is not None:
            self.clicked.connect(on_click)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)

        self._stretch = stretch


class Input(QLineEdit):
    def __init__(
            self,
            parent: QWidget,
            binding: Value,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None,
            stretch: int = 0,
    ):
        super(Input, self).__init__(parent=parent)
        self.setText(binding.data)
        self.textEdited.connect(binding.set_data)
        self._binding_observer = Observer([binding])
        self._binding_observer.on_update(self.setText)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)

        self._stretch = stretch


class MultiLineInput(QPlainTextEdit):
    def __init__(
            self,
            parent: QWidget,
            binding: Value,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None,
            stretch: int = 0,
    ):
        super(MultiLineInput, self).__init__(parent=parent)
        self.setPlainText(binding.data)
        def set_data():
            binding.set_data(self.toPlainText())

        self.textChanged.connect(set_data)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)

        self._stretch = stretch


class Row(QHBoxLayout):
    def __init__(self, children: List = [], stretch: int = 0):
        super(QHBoxLayout, self).__init__()
        for child in children:
            if isinstance(child, (tuple, list)):
                child, _stretch = child
            else:
                child, _stretch = child, 1

            _stretch = child._stretch if hasattr(child, '_stretch') else _stretch

            if isinstance(child, QWidget):
                self.addWidget(child, _stretch)
            elif isinstance(child, QLayout):
                self.addLayout(child, _stretch)
            elif isinstance(child, Spacer):
                self.addStretch(_stretch)

        self._stretch = stretch


class Column(QVBoxLayout):
    def __init__(self, children: List = [], stretch: int = 0):
        super(QVBoxLayout, self).__init__()
        for child in children:
            if isinstance(child, (tuple, list)):
                child, _stretch = child
            else:
                child, _stretch = child, 1

            _stretch = child._stretch if hasattr(child, '_stretch') else _stretch

            if isinstance(child, QWidget):
                self.addWidget(child, _stretch)
            elif isinstance(child, QLayout):
                self.addLayout(child, _stretch)
            elif isinstance(child, Spacer):
                self.addStretch(child._stretch)

        self._stretch = stretch


class GridLayout(QGridLayout):
    def __init__(self, children: List = [], stretch: int = 0):
        super(GridLayout, self).__init__()
        for child, row, column in children:
            self.addWidget(child, row, column)

        self._stretch = stretch


class Spacer:
    def __init__(self, stretch: int):
        self._stretch = stretch


class Splitter(QSplitter):
    def __init__(
            self,
            parent: Optional[QWidget] = None,
            orientation: str = 'horizontal',
            children: List = [],
            stretch: int = 0,
    ):
        if orientation == 'horizontal':
            orientation = Qt.Orientation.Horizontal
        elif orientation == 'vertical':
            orientation = Qt.Orientation.Vertical
        else:
            raise ValueError("Orientation must be either 'horizontal' or 'vertical'")

        super(Splitter, self).__init__(orientation=orientation, parent=parent)

        for i, child in enumerate(children):
            if isinstance(child, (tuple, list)):
                child, stretch = child
            else:
                child, stretch = child, 1

            if isinstance(child, QLayout):
                frame = QFrame()
                frame.setLayout(child)
                child = frame

            self.addWidget(child)
            self.setStretchFactor(i, stretch)

        self._stretch = stretch


class ViewModel:
    def __setattr__(self, key, value):
        if key in self.__dict__:
            if isinstance(value, Value):
                value = value.data
            self.__dict__[key].set_data(value)
        else:
            self.__dict__[key] = Value(value)


class View(QWidget):
    def __init__(self):
        super(View, self).__init__()
        self.model = ViewModel()


class FileDialog(QFileDialog):
    base_path = Path.home()

    @staticmethod
    def _process_kwargs(parent: QWidget, title: str, directory: Optional[Path] = None, filters: List[str] = []):
        return dict(
            parent=parent,
            caption=title,
            directory=str(directory or FileDialog.base_path),
            filter=";; ".join(filters),
            initialFilter=filters[0] if len(filters) > 0 else 'All Files (*)',
        )

    @staticmethod
    def open_file(parent: QWidget, title: str, directory: Optional[Path] = None, filters: List[str] = []):
        path, _ = QFileDialog.getOpenFileName(**FileDialog._process_kwargs(parent, title, directory, filters))

        if path is None or path == '':
            return None

        path = Path(path)
        FileDialog.base_path = path.parent
        return path


    @staticmethod
    def open_files(parent: QWidget, title: str, directory: Optional[Path] = None, filters: List[str] = []):
        paths, _ = QFileDialog.getOpenFileNames(**FileDialog._process_kwargs(parent, title, directory, filters))

        if len(paths) == 0:
            return None

        paths = list(map(Path, paths))
        FileDialog.base_path = paths[0].parent
        return paths

    @staticmethod
    def open_directory(parent: QWidget, title: str, directory: Optional[Path] = None):
        path = QFileDialog.getExistingDirectory(
            parent=parent,
            caption=title,
            directory=str(directory or FileDialog.base_path),
        )

        if path == '':
            return None

        path = Path(path)
        FileDialog.base_path = path
        return path

    @staticmethod
    def save_file(parent: QWidget, title: str, directory: Optional[Path] = None, filters: List[str] = []):
        path, _ = QFileDialog.getSaveFileName(**FileDialog._process_kwargs(parent, title, directory, filters))

        if path is None or path == '':
            return None

        path = Path(path)
        FileDialog.base_path = path.parent
        return path
