import pytest
from datetime import datetime
from ft_analyzer.data.models import Trade, BacktestData, BacktestMetadata
from ft_analyzer.data.stats import StatsCalculator


@pytest.fixture
def sample_trades():
    """Sample trades for testing."""
    return [
        Trade(
            pair="BTC/USDT:USDT",
            open_date=datetime(2024, 1, 1, 10, 0),
            close_date=datetime(2024, 1, 1, 12, 0),
            open_rate=45000.0,
            close_rate=46000.0,
            profit_abs=100.0,
            profit_ratio=0.02,
            enter_tag="120",
            trade_duration=120
        ),
        Trade(
            pair="ETH/USDT:USDT",
            open_date=datetime(2024, 1, 2, 10, 0),
            close_date=datetime(2024, 1, 2, 11, 0),
            open_rate=3000.0,
            close_rate=2950.0,
            profit_abs=-50.0,
            profit_ratio=-0.0167,
            enter_tag="141",
            trade_duration=60
        ),
        Trade(
            pair="BTC/USDT:USDT",
            open_date=datetime(2024, 1, 3, 10, 0),
            close_date=datetime(2024, 1, 3, 15, 0),
            open_rate=46000.0,
            close_rate=47000.0,
            profit_abs=200.0,
            profit_ratio=0.0217,
            enter_tag="120",
            trade_duration=300
        ),
    ]


def test_stats_calculator_basic(sample_trades):
    """Test basic statistics calculation."""
    calculator = StatsCalculator()
    stats = calculator.calculate(sample_trades)

    assert stats['total_trades'] == 3
    assert stats['profitable_trades'] == 2
    assert stats['losing_trades'] == 1
    assert stats['win_rate'] == pytest.approx(66.67, rel=0.01)
    assert stats['total_profit'] == 250.0


def test_stats_by_pair(sample_trades):
    """Test statistics grouped by pair."""
    calculator = StatsCalculator()
    stats_by_pair = calculator.stats_by_pair(sample_trades)

    assert 'BTC/USDT:USDT' in stats_by_pair
    assert 'ETH/USDT:USDT' in stats_by_pair

    btc_stats = stats_by_pair['BTC/USDT:USDT']
    assert btc_stats['total_trades'] == 2
    assert btc_stats['total_profit'] == 300.0


def test_stats_by_enter_tag(sample_trades):
    """Test statistics grouped by enter tag."""
    calculator = StatsCalculator()
    stats_by_tag = calculator.stats_by_enter_tag(sample_trades)

    assert '120' in stats_by_tag
    assert '141' in stats_by_tag

    mode_120 = stats_by_tag['120']
    assert mode_120['total_trades'] == 2
    assert mode_120['win_rate'] == 100.0
