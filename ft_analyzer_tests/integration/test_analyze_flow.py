import pytest
from pathlib import Path
from click.testing import CliRunner
from ft_analyzer.cli import cli


@pytest.fixture
def sample_backtest_file():
    """Path to sample backtest JSON."""
    return Path(__file__).parent.parent / "data" / "fixtures" / "sample_backtest.json"


def test_analyze_command_with_file(sample_backtest_file):
    """Test analyze command with actual file."""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', str(sample_backtest_file)])

    # Should succeed (even if just generating simple report without AI)
    assert result.exit_code == 0
    assert '分析完成' in result.output or 'TestStrategy' in result.output


def test_analyze_command_with_nonexistent_file():
    """Test analyze command with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'nonexistent.json'])

    assert result.exit_code != 0
    assert 'not found' in result.output.lower() or '找不到' in result.output or '不存在' in result.output
