from .file import Folder, File
from .foam_parser import FOAMParser
from dataclasses import dataclass
from enum import Enum
from time import perf_counter
from typing import Any

import os
import subprocess
import re


class ErrorType(Enum):
    MISSING_FILE = "Missing file"
    MISSING_FIELD = "Missing field"
    UNMATCHED_FIELD = "Unmatched field"
    OTHER = "Other"
    # Errors most probably caused by the program itself
    PRIMITIVE_AS_DICT = "Primitive as dictionary" # Attempt to return dictionary entry as a primitive

@dataclass(frozen=True)
class ErrorInfo:
    type: ErrorType
    meta: dict[str, Any] | None # if missing file, this is the file name; if missing field, this is the field name
    message: str

    def __str__(self) -> str:
        if self.meta:
            return "ErrorInfo(\n" + \
                f"    Type: {self.type.value},\n" + \
                f"    Meta: {self.meta},\n" + \
                f"    Message: {self.message}\n" + \
                ")"
        lines = [
            f"Type: {self.type.value}",
            "Meta: None",
            "Message:"
        ]
        raw = self.message.splitlines()
        if len(raw) > 50:
            raw = raw[:50] + [f"... (truncated, totally {len(self.message.splitlines())} lines)"]
        for line in raw:
            lines.append(f"    {line}")
        return "ErrorInfo(\n" + "\n    ".join(lines) + "\n)"
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass(frozen=True)
class RunInfo:
    command: list[str]
    time: float
    ret_code: int
    message: str
    error: ErrorInfo | None = None

    def __str__(self) -> str:
        lines = [
            f"Command: {' '.join(self.command)}",
            f"Time: {self.time:.2f} seconds",
            f"Return Code: {self.ret_code}",
            "Message:"
        ]
        raw = self.message.splitlines()
        if len(raw) > 50:
            raw = raw[:50] + [f"... (truncated, totally {len(self.message.splitlines())} lines)"]
        for line in raw:
            lines.append(f"    {line}")
        if self.error:
            lines.append("Error:")
            for line in str(self.error).splitlines():
                lines.append(f"    {line}")
        return "RunInfo(\n" + "\n    ".join(lines) + "\n)"
        
        


class Case:
    """
    Represents a case in the OpenFOAM simulation environment.
    
    This class is a placeholder for future implementations and currently does not contain any methods or attributes.
    """
    _directory: Folder
    _files: list[File]
    _run_info: list[RunInfo]

    def __init__(self, directory: str | Folder) -> None:
        self._directory = directory if isinstance(directory, Folder) else Folder(directory)
        self.load()
    
    @property
    def directory(self) -> Folder:
        return self._directory
    
    def load(self) -> None:
        """
        Load files in the case.
        """
        self._files = []
        for root, _, files in os.walk(self._directory.path):
            for file in files:
                if "snapshot" in file:
                    continue
                file_path = os.path.join(root, file)
                self._files.append(File(file_path))
    
    def __contains__(self, path: File) -> bool:
        """
        Check if the file is in the case directory.
        """
        if not isinstance(path, File):
            raise TypeError("Expected a File instance.")
        return path.path.path.startswith(self._directory.path)

    def __getitem__(self, path: str) -> File:
        """
        Get a file by its absolute path or relative path or name (if unique) from the case directory.
        """
        old_cwd = os.getcwd()
        os.chdir(self._directory.path)
        try:
            abs_path = os.path.abspath(path)
            if not os.path.exists(abs_path):
                cnt = 0
                for file in self._files:
                    if file.name == path:
                        cnt += 1
                        if cnt > 1:
                            raise ValueError(f"Multiple files with name '{path}' found in the case directory.")
                        return file
                raise FileNotFoundError(f"File {abs_path} does not exist.")
            return File(abs_path)
        finally:
            os.chdir(old_cwd)
    
    def __setitem__(self, path: str | File, content: str) -> None:
        """
        Change the content of a file in the case or create a new file with the given content.
        """
        if isinstance(path, File):
            file = path
        else:
            old_cwd = os.getcwd()
            os.chdir(self._directory.path)
            try:
                file = File(path)
                if file not in self:
                    raise FileNotFoundError(f"File {file.path} escapes the case directory.")
            finally:
                os.chdir(old_cwd)
        file.content = content
    
    def __str__(self) -> str:
        return f"Case({self._directory.path}, {len(self._files)} files)"

    def _run(self, command: list[str]) -> RunInfo:
        """
        Run a command in the case directory.
        
        Returns a RunInfo object containing the result of the command execution.
        """
        start = perf_counter()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=self._directory.path
        )
        stdout, stderr = process.communicate()
        time = perf_counter() - start
        ret_code=process.returncode
        message = stdout.decode('utf-8')
        
        if ret_code != 0:
            error_type = ErrorType.OTHER
            meta = None
            error_message = stderr.decode('utf-8').strip()

            # MISSING_FILE
            match = re.search(
                r"cannot find file \"([\w/\\-]+)\"",
                error_message
            )
            if match:
                error_type = ErrorType.MISSING_FILE
                file = os.path.abspath(match.group(1))
                if file.startswith(self._directory.path):
                    file = file[len(self._directory.path) + 1:]
                meta = {"File": file}
                error_message = f"Cannot find file \"{file}\""

            # MISSING_FIELD
            match = re.search(
                r"Entry '(\w+)' not found in dictionary \"([\w/\\-]+)\"",
                error_message
            )
            if match:
                error_type = ErrorType.MISSING_FIELD
                meta = {
                    "Missing Field": match.group(1),
                    "File": match.group(2)
                }
                error_message = f"Entry '{match.group(1)}' not found in dictionary \"{match.group(2)}\""

            # UNMATCHED_FIELD
            match = re.search(
                r"Cannot find (\w+) entry for (\w+).*file: ([\w/\\.]+) at line ([\w ]+).",
                error_message,
                re.DOTALL
            )
            if match:
                error_type = ErrorType.MISSING_FIELD
                meta = {
                    "Unmatched Field": match.group(2),
                    "File": match.group(3),
                    "Line": match.group(4)
                }
                error_message = f"Cannot find {match.group(1)} entry for {match.group(2)} " \
                    f"in file: {match.group(3)} at line {match.group(4)}."
            
            # PRIMITIVE_AS_DICT
            match = re.search(
                r"Attempt to return dictionary entry as a primitive.*file: ([\w/\\.]+) at line ([\w ]+).",
                error_message,
                re.DOTALL
            )
            if match:
                error_type = ErrorType.PRIMITIVE_AS_DICT
                meta = {
                    "Info": "This is likely a bug in the python program.",
                    "File": match.group(1),
                    "Line": match.group(2)
                }
                error_message = "Attempt to return dictionary entry as a primitive."

            error = ErrorInfo(
                type=error_type,
                meta=meta,
                message=error_message
            )
        else:
            error = None

        return RunInfo(
            time=time,
            command=command,
            ret_code=ret_code,
            message=message,
            error=error
        )

    def run(self) -> None:
        self._run_info = []
        # blockMesh
        command = ["blockMesh"]
        run_info = self._run(command)
        self._run_info.append(run_info)
        if run_info.ret_code != 0:
            return
        # solve
        control_dict_file = File(
            os.path.join(self._directory.path, "system", "controlDict")
        )
        if not control_dict_file.exists:
            raise FileNotFoundError(f"Control dictionary file {control_dict_file.path} does not exist.")
        control_dict = FOAMParser(control_dict_file.content).value
        if "application" not in control_dict:
            raise ValueError(f"Control dictionary {control_dict_file.path} does not contain 'application' field.")
        command = [
            control_dict["application"],
            "-case",
            self._directory.path
        ]
        run_info = self._run(command)
        self._run_info.append(run_info)
        if run_info.ret_code != 0:
            return


    @property
    def is_successful(self) -> bool:
        if not hasattr(self, '_run_info'):
            raise RuntimeError("Run information is not available. Please run the case first.")
        return all(info.ret_code == 0 for info in self._run_info)
    
    @property
    def run_info(self) -> list[RunInfo]:
        if not hasattr(self, '_run_info'):
            raise RuntimeError("Run information is not available. Please run the case first.")
        return self._run_info
    
    @property
    def error(self) -> ErrorInfo | None:
        if not hasattr(self, '_run_info'):
            raise RuntimeError("Run information is not available. Please run the case first.")
        if self.is_successful:
            return None
        return next((info.error for info in self._run_info if info.error), None)
    
