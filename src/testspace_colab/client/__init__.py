""" Test Space Client representation

"""

import platform
import pathlib
import subprocess
import re


class Binary:
    """Testspace Client

    This class provides access to the testspace native client. The path
    is automatically resolved based on the operating system.

    """

    def __init__(self):
        """Testspace binary accessor

        Instances of this class provide a way to access and invoke the Testspace
        client binary provided in the distribution.

        :raises: FileNotFoundError if the binary associated to the plaform is not found.
        """
        self._version = None
        self._path = (
            pathlib.Path(__file__).parent / f"testspace-{platform.system().lower()}"
        )
        if platform.system().lower() == "windows":
            self._path = pathlib.Path(str(self._path) + ".exe")
        if not self._path.is_file():
            raise FileNotFoundError(f"Could not find testspace binary {self.path}")

    @property
    def path(self):
        """Returns the path to the appropriate binary as pathlib.Path"""
        return self._path

    @property
    def version(self):
        if not self._version:
            output = subprocess.run(
                f"{self._path} --version", stdout=subprocess.PIPE, shell=True
            ).stdout
            self._version = re.sub(
                r".*version\s+", "", output.decode("utf-8").split("\n")[0]
            )
        return self._version

    def exec(self, args, return_code=0):
        """Executes the client with the specified arguments

        :param args: A list of arguments or a string.
        :param return_code: The expected return code
        :return: the process return code.
        :raise: ChildProcessError if the command did not return the
                expected return code.
        """
        if isinstance(args, list) or isinstance(args, tuple):
            command = f"{self._path} {' '.join(args)}"
        else:
            command = f"{self._path} {args}"
        completed = subprocess.run(command, shell=True)
        if return_code is not None and completed.returncode != return_code:
            raise ChildProcessError(f"Failed to run {command}")
        return completed.returncode
