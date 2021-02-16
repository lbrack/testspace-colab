""" API Library

    All the API we are going to come up with=

"""
import os
import json
import pkg_resources
import pathlib
import configparser
import urllib.parse
import xml.etree.ElementTree as ElementTree
import click
import rich.progress
import testspace.testspace as testspace
import testspace_colab.utils as utils_module
import testspace_colab.ts_log

logger = testspace_colab.ts_log.get_logger("api")


class API:
    """Programming Interface for this package."""

    def __init__(self, token=None, url=None, project=None, space=None):
        # Try to attempt to load the configuration information
        self._token = None
        self._url = None
        self._project = None
        self._space = None

        config_dir = pathlib.Path(os.path.expanduser("~")) / ".config" / "testspace"
        if "TS_COLAB_CONFIG_DIR" in os.environ:
            config_dir = pathlib.Path(os.environ["TS_COLAB_CONFIG_DIR"])
            assert config_dir.is_dir(), f"{config_dir} dir not found"
            click.secho(f"using TS_COLAB_CONFIG_DIR={config_dir}")

        config_path = config_dir / "config"

        logger.debug(f"testspace config file {config_path}")
        if config_path.is_file():
            logger.debug(f"loading testspace config file {config_path} ")
            with open(config_path) as file_handle:
                # Config parser expects a section so we trick it by injecting
                # one and ignoring it
                file_content = "[dummy_section]\n" + file_handle.read()
            config = configparser.RawConfigParser()
            config.read_string(file_content)
            domain = config["dummy_section"].get("remote.domain")
            if domain:
                parts = urllib.parse.urlparse(domain)
                if ":@" in parts.netloc:
                    self._token, self._url = parts.netloc.split(":@")
                else:
                    self._url = parts.netloc
                self._url = parts.scheme + "://" + self._url

            self._project = config["dummy_section"].get("remote.project")
            self._space = config["dummy_section"].get("remote.space")

        if token:
            logger.debug("overrideing token with argument")
            self._token = token
        if url:
            logger.debug(f"overrideing url {self._url} with arg {url}")
            self._url = url
        if project:
            logger.debug(f"overrideing project {self._project} with arg {project}")
            self._project = project
        if space:
            logger.debug(f"overrideing space {self._space} with arg {space}")
            self._space = space

        logger.debug(
            f"token={self._token} url={self._url}, project={self._project}, space={self._space}"
        )

        self.client = testspace.Testspace(
            token=self._token, url=self._url, project=self._project, space=self._space
        )

    @property
    def token(self):
        return self._token

    @property
    def url(self):
        return self._url

    @property
    def project(self):
        return self._project

    @property
    def space(self):
        return self._space

    def __getattr__(self, item):
        # First check if this class has the method
        # (This is used by the cli::get command
        try:
            return self.__getattribute__(item)
        except AttributeError:
            pass
        # Otherwise we query the client api
        return self.client.__getattribute__(item)

    def get_result_details(self, result, project=None, space=None):
        """This method recursively walk the results structure and extracts information
        from the "xml snipped" associated to suites (containing testcases).

        It basically calls the testspace::get_result() method and then recurlively
        loads the information.

        :param result: the result ID or name
        :param project: The project ID or name (optional - to override ctor argument)
        :param space: The project ID or name (optional - to override ctor argument)
        :return: a JSON structure (from testspace)
        """
        logger.debug(
            f"get_result_details result={result} project={project} space={space}"
        )
        response = self.client.get_result(result=result, project=project, space=space)

        with rich.progress.Progress(transient=True) as progress:

            tasks = {
                "suites": {
                    "increment": 1000 / sum(response["session_suite_counts"]),
                    "task": progress.add_task("[red] Suites", total=1000, start=False),
                },
                "cases": {
                    "increment": 1000 / sum(response["session_case_counts"]),
                    "task": progress.add_task("[green] Cases", total=1000, start=False),
                },
                "annotations": {
                    "increment": 1000 / sum(response["annotation_counts"]),
                    "task": progress.add_task(
                        "[blue] Annotations", total=1000, start=False
                    ),
                },
            }

            def download_progress(object_type, object_count):
                progress.update(
                    tasks[object_type]["task"],
                    advance=tasks[object_type]["increment"] * object_count,
                )

            response["details"] = self._load_results(
                result_id=response["id"],
                project=project,
                space=space,
                progress_callback=download_progress,
            )
        return response

    def _load_results(
        self, result_id, project, space, path=None, progress_callback=None
    ):
        logger.debug(f"getting result content {path}")
        try:
            response = self.client.get_result_contents(
                result_id, project=project, space=space, contents_path=path
            )
        except Exception as load_error:
            msg = f"failed to load {path}"
            logger.exception(msg)
            return [dict(load_error=str(load_error))]

        if isinstance(response, dict):  # If we do not receive a list
            response = [response]

        for container in response:
            if container["type"].startswith("suite"):
                # We have a suite. This maybe container test cases
                # or simply annotation
                container["suites"] = []
                container["cases"] = []
                case_count = sum(container["case_counts"])
                if case_count and "download_url" in container:
                    xml_snippet = self.client.get_request(container["download_url"])
                    if xml_snippet.status_code == 200:
                        # print(response.content.decode('utf-8'))
                        content = xml_snippet.content.decode("utf-8")
                        try:
                            xml_tree = ElementTree.fromstring(content)
                            json_data = utils_module.xml_to_json(
                                xml_tree, progress_callback=progress_callback
                            )
                        except ElementTree.ParseError:
                            # For manual testing the content is in JSON format
                            json_data = json.loads(content)
                        if "suite" in json_data:
                            container["suites"].append(json_data["suite"])
                        if "case" in json_data:
                            container["cases"].append(json_data["case"])
                else:
                    if progress_callback:
                        progress_callback(object_type="suites", object_count=1)
            elif container["type"].startswith("folder"):
                # FIXME: this is wrong - we should handle the return value
                container["folders"] = self._load_results(
                    result_id=result_id,
                    path=container["path"],
                    project=project,
                    space=space,
                    progress_callback=progress_callback,
                )
            else:
                logger.debug(f"unknown container type {container['type']}")
        return response

    @staticmethod
    def get_version():
        """Return the distribution version"""
        return pkg_resources.get_distribution("testspace-colab").version
