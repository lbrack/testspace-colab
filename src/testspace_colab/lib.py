""" API Library

    All the API we are going to come up with=

"""
import pkg_resources


class API:
    """Programming Interface for this package."""

    def __init__(self, token=None, url=None, project=None, space=None):
        pass

    @staticmethod
    def get_version():
        """Return the distribution version"""
        return pkg_resources.get_distribution("testspace-colab").version
