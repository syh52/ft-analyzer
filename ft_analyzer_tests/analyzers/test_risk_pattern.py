import pytest
from datetime import datetime
from ft_analyzer.data.models import Trade
from ft_analyzer.analyzers.risk_pattern import RiskPatternAnalyzer


@pytest.fixture
def trades_with_liquidation():
    """Trades including a liquidation."""
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
            close_rate=0.0,
            profit_abs=-1500.0,
            profit_ratio=-0.95,  # Liquidation
            enter_tag="141",
            trade_duration=60
        ),
    ]


def test_detect_liquidations(trades_with_liquidation):
    """Test liquidation detection."""
    analyzer = RiskPatternAnalyzer()
    context = analyzer.prepare_context(trades_with_liquidation)

    liquidations = [e for e in context['risk_events'] if e['type'] == 'liquidation']
    assert len(liquidations) == 1
    assert liquidations[0]['pair'] == 'ETH/USDT:USDT'
    assert liquidations[0]['enter_mode'] == '141'


def test_detect_consecutive_losses():
    """Test consecutive loss detection."""
    trades = [
        Trade(
            pair="BTC/USDT:USDT",
            open_date=datetime(2024, 1, 1, 10, 0),
            close_date=datetime(2024, 1, 1, 11, 0),
            open_rate=45000.0,
            close_rate=44500.0,
            profit_abs=-50.0,
            profit_ratio=-0.011,
            enter_tag="120",
            trade_duration=60
        ),
        Trade(
            pair="ETH/USDT:USDT",
            open_date=datetime(2024, 1, 1, 12, 0),
            close_date=datetime(2024, 1, 1, 13, 0),
            open_rate=3000.0,
            close_rate=2950.0,
            profit_abs=-50.0,
            profit_ratio=-0.017,
            enter_tag="141",
            trade_duration=60
        ),
        Trade(
            pair="BTC/USDT:USDT",
            open_date=datetime(2024, 1, 1, 14, 0),
            close_date=datetime(2024, 1, 1, 15, 0),
            open_rate=45000.0,
            close_rate=44800.0,
            profit_abs=-20.0,
            profit_ratio=-0.004,
            enter_tag="120",
            trade_duration=60
        ),
    ]

    analyzer = RiskPatternAnalyzer()
    context = analyzer.prepare_context(trades)

    consecutive_loss_patterns = [p for p in context['patterns'] if p['type'] == 'consecutive_losses']
    assert len(consecutive_loss_patterns) >= 1


def test_high_risk_mode_detection(trades_with_liquidation):
    """Test high-risk mode identification."""
    analyzer = RiskPatternAnalyzer()
    context = analyzer.prepare_context(trades_with_liquidation)

    high_risk_patterns = [p for p in context['patterns'] if p['type'] == 'high_risk_mode']
    assert len(high_risk_patterns) == 1
    assert high_risk_patterns[0]['mode'] == '141'
