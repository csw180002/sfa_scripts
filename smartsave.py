import logging
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)


def maya_main_window():
    """Return Maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class SmartSaveUI(QtWidgets.QDialog):
    """Smart Class UI Class"""

    def __init__(self):
        super(SmartSaveUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Smart Save")
        self.setMinimumWidth(500)
        self.setMaximumHeight(200)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.scene_file = SceneFile()
        self.create_ui()
        self.create_connections()

    def create_ui(self):
        self.title_lbl = QtWidgets.QLabel("Smart Save")
        self.title_lbl.setStyleSheet("font: bold 20px")
        self.folder_layout = self._create_folder_ui()
        self.filename_layout = self._create_filename_ui()
        self.button_layout = self.create_btn_ui()
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.addWidget(self.title_lbl)
        self.main_lay.addLayout(self.folder_layout)
        self.main_lay.addLayout(self.filename_layout)
        self.main_lay.addStretch()
        self.main_lay.addLayout(self.button_layout)
        self.setLayout(self.main_lay)

    def create_btn_ui(self):
        self.save_inc_btn = QtWidgets.QPushButton("Save Increment")
        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.save_inc_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)
        return layout

    def _create_filename_ui(self):
        layout = self._create_filename_headers()
        self.descriptor_le = QtWidgets.QLineEdit(self.scene_file.descriptor)
        self.descriptor_le.setMinimumWidth(100)
        self.task_le = QtWidgets.QLineEdit(self.scene_file.task)
        self.task_le.setFixedWidth(50)
        self.ver_sbx = QtWidgets.QSpinBox()
        self.ver_sbx.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.ver_sbx.setFixedWidth(50)
        self.ver_sbx.setValue(self.scene_file.ver)
        self.ext_lbl = QtWidgets.QLabel(".ma")
        layout.addWidget(self.descriptor_le, 1, 0)
        layout.addWidget(self.task_le, 1, 2)
        layout.addWidget(QtWidgets.QLabel("_v"), 1, 3)
        layout.addWidget(self.ver_sbx, 1, 4)
        layout.addWidget(self.ext_lbl, 1, 5)
        return layout

    def _create_filename_headers(self):
        self.descriptor_header_lbl = QtWidgets.QLabel("Descriptor")
        self.descriptor_header_lbl.setStyleSheet("font: bold")
        self.task_header_lbl = QtWidgets.QLabel("Task")
        self.task_header_lbl.setStyleSheet("font: bold")
        self.ver_header_lbl = QtWidgets.QLabel("Version")
        self.ver_header_lbl.setStyleSheet("font: bold")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.descriptor_header_lbl, 0, 0)
        layout.addWidget(QtWidgets.QLabel("_"), 1, 1)
        layout.addWidget(self.task_header_lbl, 0, 2)
        layout.addWidget(self.ver_header_lbl, 0, 4)
        return layout

    def _create_folder_ui(self):
        default_folder = Path(cmds.workspace(rootDirectory=True, query=True))
        default_folder = default_folder / "scenes"
        self.folder_le = QtWidgets.QLineEdit(default_folder)
        self.folder_browse_btn = QtWidgets.QPushButton("Browse")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.folder_le)
        layout.addWidget(self.folder_browse_btn)
        return layout

    def create_connections(self):
        """Connects signals and slots"""
        self.cancel_btn.clicked.connect(self.cancel)
        self.folder_browse_btn.clicked.connect(self._browse_folder)
        self.save_btn.clicked.connect(self._save)
        self.save_inc_btn.clicked.connect(self._save_inc)

    @QtCore.Slot()
    def _save_inc(self):
        """Save an increment of the scene"""
        self._set_scenefile_properties_from_ui()
        self.scene_file.save_increment()
        self.ver_sbx.setValue(self.scene_file.ver)

    @QtCore.Slot()
    def _save(self):
        """Save the scene"""
        self._set_scenefile_properties_from_ui()
        self.scene_file.save()

    def _set_scenefile_properties_from_ui(self):
        self.scene_file.folder_path = self.folder_le.text()
        self.scene_file.descriptor = self.descriptor_le.text()
        self.scene_file.task = self.task_le.text()
        self.scene_file.ver = self.ver_sbx.value()
        self.scene_file.ext = self.ext_lbl.text()

    @QtCore.Slot()
    def _browse_folder(self):
        """opens a dialog box to browse the folder"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Select Folder", dir=self.folder_le.text(),
            options=QtWidgets.QFileDialog.ShowDirsOnly |
                    QtWidgets.QFileDialog.DontResolveSymlinks)
        self.folder_le.setText(folder)

    @QtCore.Slot()
    def cancel(self):
        """Closes dialog box"""
        self.close()


class SceneFile(object):
    """An abstract representation of a scene file"""

    def __init__(self, path=None):
        self._folder_path = Path(cmds.workspace(query=True,
                                                rootDirectory=True)) / "scenes"
        self.descriptor = 'main'
        self.task = 'model'
        self.ver = 1
        self.ext = '.ma'
        scene = pmc.system.sceneName()
        if not path and scene:
            path = scene
        if not path and not scene:
            log.info("Initialize with default properties")
            return
        self._init_from_path(path)

    @property
    def folder_path(self):
        return self._folder_path

    @folder_path.setter
    def folder_path(self, val):
        self._folder_path = Path(val)

    @property
    def filename(self):
        pattern = "{descriptor}_{task}_v{ver:03d}{ext}"
        return pattern.format(descriptor=self.descriptor,
                              task=self.task,
                              ver=self.ver,
                              ext=self.ext)

    @property
    def path(self):
        return self.folder_path / self.filename

    def _init_from_path(self, path):
        path = Path(path)
        self.folder_path = path.parent
        self.ext = path.ext
        self.descriptor, self.task, ver = path.name.stripext().split("_")
        self.ver = int(ver.split("v")[-1])

    def save(self):

        try:
            return pmc.system.saveAs(self.path)
        except RuntimeError as err:
            log.warning("Missing directories in path. Creating directories...")
            self.folder_path.mkdir_p()
            return pmc.system.saveAs(self.path)

    def next_avail_ver(self):
        """Return the next available version when file is saved."""
        pattern = "{descriptor}_{task}_v*{ext}".format(
            descriptor=self.descriptor, task=self.task, ext=self.ext)

        matched_scenefiles = []
        for file_ in self.folder_path.files():
            if file_.name.fnmatch(pattern):
                matched_scenefiles.append(file_)
        if not matched_scenefiles:
            return 1
        matched_scenefiles.sort(reverse=True)
        latest_scenefile = matched_scenefiles[0]
        latest_scenefile = latest_scenefile.name.stripext()
        latest_ver_num = int(latest_scenefile.split("_v")[-1])
        return latest_ver_num + 1

    def save_increment(self):
        """Increments the version and saves the scene file.

        If the existing version of a file is already there, it should
        go up from the largest version number available in the folder.

        Returns:
            Path: The path to the scene file if successful fingers crossed
            """
        self.ver = self.next_avail_ver()
        self.save()