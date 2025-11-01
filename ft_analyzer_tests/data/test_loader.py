import pytest
from pathlib import Path
from ft_analyzer.data.loader import BacktestLoader


@pytest.fixture
def sample_backtest_file():
    """Path to sample backtest JSON."""
    return Path(__file__).parent / "fixtures" / "sample_backtest.json"


def test_load_backtest_json(sample_backtest_file):
    """Test loading backtest from JSON file."""
    loader = BacktestLoader()
    data = loader.load_from_json(sample_backtest_file)

    assert data.metadata.strategy_name == "TestStrategy"
    assert data.total_trades == 2
    assert len(data.trades) == 2

    # Check first trade
    trade1 = data.trades[0]
    assert trade1.pair == "BTC/USDT:USDT"
    assert trade1.profit_abs == 100.0
    assert trade1.enter_tag == "120"

    # Check second trade
    trade2 = data.trades[1]
    assert trade2.pair == "ETH/USDT:USDT"
    assert trade2.profit_abs == -50.0
    assert trade2.is_profitable is False


def test_load_nonexistent_file():
    """Test loading non-existent file raises error."""
    loader = BacktestLoader()

    with pytest.raises(FileNotFoundError):
        loader.load_from_json(Path("nonexistent.json"))
