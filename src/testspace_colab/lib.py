""" API Library

    All the API we are going to come up with=

"""
import os
import pkg_resources
import pathlib
import configparser
import urllib.parse
import testspace.testspace as testspace


class API:
    """Programming Interface for this package."""

    def __init__(self, token=None, url=None, project=None, space=None):
        # Try to attempt to load the configuration information
        self._token = None
        self._url = None
        self._project = None
        self._space = None

        config_path = (
            pathlib.Path(os.path.expanduser("~")) / ".config" / "testspace" / "config"
        )
        if config_path.is_file():
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
            self._token = token
        if url:
            self._url = url
        if project:
            self._project = project
        if space:
            self._space = space

        self.client = testspace.Testspace(
            token=self._token, url=self._url, project=self._project, space=space
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
        return self.client.__getattribute__(item)

    @staticmethod
    def get_version():
        """Return the distribution version"""
        return pkg_resources.get_distribution("testspace-colab").version
