""" Test Result Trove

    This module helps storing test results into a trove, whether
    it is the file system or ELK (maybe?)

"""
import json
import pathlib
import testspace_colab.ts_log

DEFAULT_LOCATION = pathlib.Path("~").expanduser() / "testspace-colab"

logger = testspace_colab.ts_log.get_logger("trove")


class Trove:
    """A utility to iterate over the results found
    in the trove

    """

    def __init__(self, trove_path=DEFAULT_LOCATION):
        self.path = pathlib.Path(trove_path)
        self._org = None

    @property
    def org(self):
        """Sets or get the default organization (string)"""
        return self._org

    @org.setter
    def org(self, value):
        logger.debug(f"setting organization to {self._org}")
        self._org = value

    def organizations(self):
        """Return a generator for iterating over the organizations

        :return: directory name as a string or None if no dir is found
        """
        if not self.path.is_dir():
            logger.warning(f"trove dir {self.path} does not exist")
            return None
        for dir in self.path.iterdir():
            yield dir.name

    def load(self, org=None, project=None, space=None, result=None):
        if not self.path.is_dir():
            logger.warning(f"trove dir {self.path} does not exist")
            return None
        orgs = [org] if org else self.organizations()
        for org_name in orgs:
            load_path = self.path / org_name
            if not load_path.is_dir():
                raise OSError(f"{load_path} is not a directory")
            projects = [project] if project else load_path.iterdir()
            for project_name in projects:
                load_path = load_path / project_name
                if not load_path.is_dir():
                    raise OSError(f"{load_path} is not a directory")
                spaces = [space] if space else load_path.iterdir()
                for space_name in spaces:
                    load_path = load_path / space_name
                    if not load_path.is_dir():
                        raise OSError(f"{load_path} is not a directory")
                    for result in load_path.iterdir():
                        if not result.is_file():
                            logger.warning(f"{result} result is not a file")
                        else:
                            try:
                                with open(result, "r") as file_hanfle:
                                    yield json.load(file_hanfle)
                            except json.JSONDecodeError as json_error:
                                logger.warning(
                                    f"Failed to load {result} - error {json_error}"
                                )
