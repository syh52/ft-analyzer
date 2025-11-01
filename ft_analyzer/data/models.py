"""Data models for backtest analysis."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Represents a single trade from backtest results."""

    pair: str
    open_date: datetime
    close_date: datetime
    open_rate: float
    close_rate: float
    profit_abs: float
    profit_ratio: float
    enter_tag: str
    trade_duration: int  # minutes

    # Optional fields
    exit_reason: Optional[str] = None
    stake_amount: Optional[float] = None
    leverage: Optional[float] = None
    is_short: bool = False

    @property
    def is_profitable(self) -> bool:
        """Check if trade was profitable."""
        return self.profit_abs > 0

    @property
    def is_liquidation(self) -> bool:
        """Check if trade resulted in liquidation."""
        return self.profit_ratio < -0.90


@dataclass
class BacktestMetadata:
    """Metadata from backtest results."""

    strategy_name: str
    timerange_start: datetime
    timerange_end: datetime
    pairs: list[str]

    # Optional
    timeframe: Optional[str] = None
    max_open_trades: Optional[int] = None
    stake_amount: Optional[str] = None


@dataclass
class BacktestData:
    """Complete backtest data including trades and metadata."""

    trades: list[Trade]
    metadata: BacktestMetadata

    @property
    def total_trades(self) -> int:
        """Total number of trades."""
        return len(self.trades)

    @property
    def profitable_trades(self) -> int:
        """Number of profitable trades."""
        return sum(1 for t in self.trades if t.is_profitable)

    @property
    def win_rate(self) -> float:
        """Win rate percentage."""
        if self.total_trades == 0:
            return 0.0
        return (self.profitable_trades / self.total_trades) * 100
