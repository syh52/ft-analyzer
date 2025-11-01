"""Statistics calculator for backtest data."""

from typing import Dict, List, Any
from collections import defaultdict

from ft_analyzer.data.models import Trade


class StatsCalculator:
    """Calculate statistics from trade data."""

    def calculate(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate basic statistics.

        Args:
            trades: List of trades

        Returns:
            Dictionary of statistics
        """
        if not trades:
            return self._empty_stats()

        total_trades = len(trades)
        profitable = [t for t in trades if t.is_profitable]
        losing = [t for t in trades if not t.is_profitable]

        return {
            'total_trades': total_trades,
            'profitable_trades': len(profitable),
            'losing_trades': len(losing),
            'win_rate': (len(profitable) / total_trades) * 100 if total_trades > 0 else 0,
            'total_profit': sum(t.profit_abs for t in trades),
            'avg_profit': sum(t.profit_abs for t in trades) / total_trades,
            'max_profit': max(t.profit_abs for t in trades),
            'max_loss': min(t.profit_abs for t in trades),
        }

    def stats_by_pair(self, trades: List[Trade]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics grouped by trading pair.

        Args:
            trades: List of trades

        Returns:
            Dictionary mapping pair -> statistics
        """
        grouped = defaultdict(list)
        for trade in trades:
            grouped[trade.pair].append(trade)

        return {
            pair: self.calculate(pair_trades)
            for pair, pair_trades in grouped.items()
        }

    def stats_by_enter_tag(self, trades: List[Trade]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics grouped by enter tag (mode).

        Args:
            trades: List of trades

        Returns:
            Dictionary mapping enter_tag -> statistics
        """
        grouped = defaultdict(list)
        for trade in trades:
            tag = trade.enter_tag or 'unknown'
            grouped[tag].append(trade)

        return {
            tag: self.calculate(tag_trades)
            for tag, tag_trades in grouped.items()
        }

    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics."""
        return {
            'total_trades': 0,
            'profitable_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'avg_profit': 0.0,
            'max_profit': 0.0,
            'max_loss': 0.0,
        }
