import logging
import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)


class SceneFile(object):
    """An abstract representation of a scene file"""

    def __init__(self, path=None):
        self.folder_path = Path()
        self.descriptor = 'main'
        self.task = None
        self.ver = 1
        self.ext = '.ma'
        scene = pmc.system.sceneName()
        if not path and scene:
            path = scene
        if not path and not scene:
            log.warning("Unable to initialize SceneFile object from a new "
                        "scene. Please specify a path")
        self._init_from_path(path)

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
        pattern = "{descriptor)_{task}_v{ext}".format(
            descriptor=self.descriptor, task=self.task, ext=self.ext)
        matched_scenefiles = []
        for file_ in self.folder_path.files():
            if file_.name.fnmatch(pattern):
                matched_scenefiles.append(file_)
            if not matched_scenefiles:
                return 1
        matched_scenefiles.sort(reverse=True)
        latest_scenefile = matched_scenefiles[0]
        latest_scenefile = latest_scenefile.name.stirpext()
        latest_ver_num = int(latest_scenefile.split("_v")[-1])
        return latest_ver_num + 1

    def increment_save(self):
        """Increments the version and saves the scene file.

        If the existing version of a file is already there, it should
        go up from the largest version number available in the folder.

        Returns:
            Path: The Path to the scene file if successful
            """
        self.ver = self.next_avail_ver()
        self.save()
