import os
import re
import datetime

from warnings import warn
from typing import TypeVar, Any
from .foam_parser import FOAMParser, FOAMBuilder

T = TypeVar('T')

def _parse_env(path: str) -> str:
    return re.sub(
        r"\$\{(.+?)\}",
        lambda m: os.environ.get(m.group(1), ''),
        path
    )

class SingletonMeta(type):
    _instances = {}

    def __call__(cls: type[T], path: str) -> T:
        path = os.path.abspath(_parse_env(path))
        key = (cls, path)
        if key not in SingletonMeta._instances:
            instance = super().__call__(path)
            SingletonMeta._instances[key] = instance
        return SingletonMeta._instances[key]

class Folder(metaclass=SingletonMeta):
    """
    Represents a folder in the OpenFOAM simulation environment.
    """
    
    def __init__(self, path: str) -> None:
        self._path = path
    
    @property
    def path(self) -> str:
        return self._path

    def ensure_existence(self, show_warning: bool = False) -> None:
        if not os.path.exists(self._path):
            if show_warning:
                warn(f"Folder {self._path} does not exist. Creating it now.", UserWarning)
            os.makedirs(self._path)

class File(metaclass=SingletonMeta):
    """
    Represents a file in the OpenFOAM simulation environment.
    Maybe add snapshots or other features in the future.
    """
    _path: str
    _autosave: bool
    _dict: dict[str, Any] | None = None
    _snapshots: list["File"] = []

    def __init__(
        self,
        path: str,
        autosave: bool = True
    ) -> None:
        self._path = path
        self._autosave = autosave
        self._snapshots = []
        if not self.is_snapshot:
            for file in os.listdir(self.path.path):
                if file.startswith(self.name + '-snapshot-'):
                    self._snapshots.append(File(os.path.join(self.path.path, file)))
            self._snapshots.sort(key=lambda f: f.name)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return NotImplemented
        return self._path == other._path
    
    def __hash__(self) -> int:
        return hash(self._path)

    def rollback(self, snapshot: "File") -> None:
        """
        Rollback to a snapshot of the file.
        """
        if snapshot not in self._snapshots:
            raise ValueError("Snapshot not found in the file's snapshots.")
        self.content = snapshot.content
        snapshot.delete()
    
    def delete(self) -> None:
        """
        Delete the file.
        """
        if self.exists:
            os.remove(self._path)
            self.delete_snapshots()
    
    def delete_snapshots(self) -> None:
        """
        Delete all snapshots of the file.
        """
        for snapshot in self._snapshots:
            if snapshot.exists:
                snapshot.delete()
        self._snapshots.clear()

    @property
    def is_snapshot(self) -> bool:
        """
        Check if the file is a snapshot.
        """
        return "-snapshot-" in self.name

    @property
    def snapshots(self) -> tuple["File", ...]:
        """
        Returns a tuple of snapshots of the file.
        """
        return tuple(self._snapshots)

    @property
    def content(self) -> str:
        with open(self._path, 'r') as file:
            return file.read()

    @content.setter
    def content(self, value: str):
        if self._autosave:
            # Create a snapshot before changing the content
            snapshot_path = self._path + '-snapshot-' + \
                datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            with open(snapshot_path, 'w') as snapshot_file:
                snapshot_file.write(self.content)
            self._snapshots.append(File(snapshot_path))
        with open(self._path, 'w') as file:
            file.write(value)

    @property
    def name(self) -> str:
        return os.path.basename(self._path)

    @property
    def path(self) -> Folder:
        return Folder(os.path.dirname(self._path))
    
    @property
    def exists(self) -> bool:
        return os.path.exists(self._path)
    
    def ensure_existence(self, show_warning: bool = False) -> None:
        if not self.exists:
            if show_warning:
                warn(f"File {self._path} does not exist. Creating it now.", UserWarning)
            self.path.ensure_existence(show_warning)
            with open(self._path, 'w') as file:
                file.write('')

    @property
    def dict(self) -> dict[str, Any]:
        """
        Parse the file content as a dictionary and allow field modification.
        """
        if self._dict is None:
            if not self.exists:
                raise FileNotFoundError(f"File {self._path} does not exist.")
            self._dict = FOAMParser(self.content).value
        return self._dict
    
    def save(self) -> None:
        """
        Save the current state of the file.
        """
        if self._dict is not None:
            self.content = FOAMBuilder(self._dict).content
        else:
            raise ValueError("No setter defined for this file.")
    
    def __str__(self) -> str:
        return f"File(path={self._path}, name={self.name}, exists={self.exists})"
    
    def __repr__(self) -> str:
        return self.__str__()
