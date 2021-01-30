#!/usr/bin/env python

"""Tests for `testspace_utils` package."""

import pytest

from click.testing import CliRunner
import testspace_utils.client as client
from testspace_utils import lib
from testspace_utils import cli


def test_click_help():
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


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
