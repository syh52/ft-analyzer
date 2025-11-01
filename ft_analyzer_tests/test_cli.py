import pytest
from click.testing import CliRunner
from ft_analyzer.cli import cli


def test_cli_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_cli_help():
    """Test --help flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert 'Freqtrade' in result.output
    assert 'analyze' in result.output


def test_analyze_command_exists():
    """Test that analyze command exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', '--help'])

    assert result.exit_code == 0
    assert 'analyze' in result.output.lower()
