#!/usr/bin/env python

"""Tests for `testspace_colab` package."""
import os
import json
from unittest import mock
import pkg_resources
import logging
import pytest


from click.testing import CliRunner
from testspace_colab import cli


def test_click_version():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--version"])
    assert help_result.exit_code == 0
    assert (
        pkg_resources.get_distribution("testspace-colab").version in help_result.output
    )


@pytest.mark.xfail(reason="Need to figure out control flow")
def test_debug_level(mocker):
    """Verifies that the debug level can be controlled correctly"""
    for handler in logging.getLogger().handlers:
        if handler.name == "console":
            break
    logger = logging.getLogger("testspace_colab")
    with mock.patch.dict(os.environ, {"TS_COLAB_DEBUG": "False"}):
        runner = CliRunner()
        runner.invoke(cli.main, ["client", "--help"])
        assert logger.level == logging.NOTSET
        assert handler.level == logging.INFO

    with mock.patch.dict(os.environ, {"TS_COLAB_DEBUG": "True"}):
        runner = CliRunner()
        runner.invoke(cli.main, ["-d", "client", "--help"])
        assert logger.level == logging.NOTSET
        assert handler.level == logging.DEBUG

    # Remove the environment var
    modified_environ = {
        k: v for k, v in os.environ.items() if k not in "TS_COLAB_DEBUG"
    }
    with mock.patch.dict(os.environ, modified_environ, clear=True):
        runner = CliRunner()
        runner.invoke(cli.main, ["-d", "client", "--help"])
        assert logger.level == logging.NOTSET
        assert handler.level == logging.DEBUG


def test_click_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0


def test_click_client():
    """Test the CLI."""
    runner = CliRunner()

    result = runner.invoke(cli.client, ["push", "invalid"])
    assert result.exit_code == 2

    result = runner.invoke(cli.client, ["config"])
    assert result.exit_code == 0

    result = runner.invoke(cli.client, ["--version"])
    assert result.exit_code == 0

    result = runner.invoke(cli.client, ["--help"])
    assert result.exit_code == 0


class TestGet:
    def test_get_tabular_format(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.get, ["result", "test_data", "project=samples", "space=main"]
        )
        assert result.exit_code == 0
        assert "123753" in result.output

        runner = CliRunner()
        result = runner.invoke(
            cli.get,
            ["result", "test_data", "project=samples", "space=main", "-f", "tabular"],
        )
        assert result.exit_code == 0
        assert "123753" in result.output

    def test_get_yaml_format(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.get,
            ["result", "test_data", "project=samples", "space=main", "-f", "yaml"],
        )
        assert result.exit_code == 0
        assert "id: 123753" in result.output

    def test_get_json_format(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.get,
            ["result", "test_data", "project=samples", "space=main", "-f", "json"],
        )
        assert result.exit_code == 0
        assert "'id': 123753," in result.output

    def test_get_invalid_method(self):
        runner = CliRunner()
        result = runner.invoke(cli.get, ["foobar"])
        assert result.exit_code == 1
        assert "Error: no method 'foobar' to access resource" in str(result.output)

    def test_get_no_param(self):
        runner = CliRunner()
        result = runner.invoke(cli.get, [])
        assert result.exit_code == 1
        assert "an endpoint is required" in str(result.output)

    def test_get_file_output(self, tmpdir):
        runner = CliRunner()
        tmpfile = tmpdir.join("output.json")
        assert tmpfile.check() is False
        result = runner.invoke(cli.get, ["result", "test_data", "-o", str(tmpfile)])
        assert result.exit_code == 0
        assert tmpfile.check() is True
        with open(str(tmpfile)) as file_handle:
            json_data = json.load(file_handle)
        assert json_data["id"] == 123753

    def test_get_details(self, tmpdir):
        runner = CliRunner()
        tmpfile = tmpdir.join("output.json")
        assert tmpfile.check() is False
        result = runner.invoke(
            cli.get, ["result_details", "test_data", "-f", "json", "-o", str(tmpfile)]
        )
        assert result.exit_code == 0
        assert tmpfile.check() is True
        with open(str(tmpfile)) as file_handle:
            json_data = json.load(file_handle)
        assert "details" in json_data
        assert isinstance(json_data["details"], list)
        assert len(json_data["details"]) == 8


class TestELK:
    @pytest.mark.parametrize("elk_state", ["stopped"])
    def test_all(self, elk_api):
        runner = CliRunner()
        result = runner.invoke(cli.elk, ["start"])
        assert result.exit_code == 0
        assert "ELK Container started" in result.stdout

        result = runner.invoke(cli.elk, ["info"])
        assert result.exit_code == 0
        assert "lucene_version:" in result.stdout

        result = runner.invoke(cli.elk, ["health"])
        assert result.exit_code == 0
        assert "active_shards:" in result.stdout

        result = runner.invoke(cli.elk, ["stop"])
        assert result.exit_code == 0
        assert "ELK stopped" in result.stdout

        result = runner.invoke(cli.elk, ["info"])
        assert result.exit_code == 0
        assert "container not running" in result.stdout

        result = runner.invoke(cli.elk, ["health"])
        assert result.exit_code == 0
        assert "container not running" in result.stdout
