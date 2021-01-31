#!/usr/bin/env python

"""Tests for `testspace_colab` package."""

import pkg_resources
from click.testing import CliRunner
from testspace_colab import cli


def test_click_version():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--version"])
    assert help_result.exit_code == 0
    assert (
        pkg_resources.get_distribution("testspace-colab").version in help_result.output
    )


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
