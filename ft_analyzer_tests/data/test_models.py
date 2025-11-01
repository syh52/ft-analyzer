import pytest
from datetime import datetime
from ft_analyzer.data.models import Trade


def test_trade_creation():
    """Test creating a Trade instance with required fields."""
    trade = Trade(
        pair="BTC/USDT:USDT",
        open_date=datetime(2024, 1, 1, 10, 0),
        close_date=datetime(2024, 1, 1, 12, 0),
        open_rate=45000.0,
        close_rate=46000.0,
        profit_abs=100.0,
        profit_ratio=0.02,
        enter_tag="120",
        trade_duration=120
    )

    assert trade.pair == "BTC/USDT:USDT"
    assert trade.profit_abs == 100.0
    assert trade.enter_tag == "120"


def test_trade_is_profitable():
    """Test determining if trade is profitable."""
    profitable_trade = Trade(
        pair="ETH/USDT:USDT",
        open_date=datetime(2024, 1, 1, 10, 0),
        close_date=datetime(2024, 1, 1, 11, 0),
        open_rate=3000.0,
        close_rate=3100.0,
        profit_abs=100.0,
        profit_ratio=0.033,
        enter_tag="141",
        trade_duration=60
    )

    assert profitable_trade.is_profitable is True

    losing_trade = Trade(
        pair="ETH/USDT:USDT",
        open_date=datetime(2024, 1, 1, 10, 0),
        close_date=datetime(2024, 1, 1, 11, 0),
        open_rate=3000.0,
        close_rate=2900.0,
        profit_abs=-100.0,
        profit_ratio=-0.033,
        enter_tag="141",
        trade_duration=60
    )

    assert losing_trade.is_profitable is False
