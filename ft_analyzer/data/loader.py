"""Data loader for backtest results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from ft_analyzer.data.models import Trade, BacktestMetadata, BacktestData


class BacktestLoader:
    """Load backtest data from JSON files."""

    def load_from_json(self, file_path: Path) -> BacktestData:
        """Load backtest data from JSON file.

        Args:
            file_path: Path to backtest JSON file

        Returns:
            BacktestData instance

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Backtest file not found: {file_path}")

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Parse metadata
        metadata = self._parse_metadata(data)

        # Parse trades
        trades = [self._parse_trade(t) for t in data.get('trades', [])]

        return BacktestData(trades=trades, metadata=metadata)

    def _parse_metadata(self, data: Dict[str, Any]) -> BacktestMetadata:
        """Parse backtest metadata from JSON."""
        strategy = data.get('strategy', {})

        return BacktestMetadata(
            strategy_name=strategy.get('strategy_name', 'Unknown'),
            timerange_start=self._parse_datetime(data.get('backtest_start')),
            timerange_end=self._parse_datetime(data.get('backtest_end')),
            pairs=self._extract_pairs(data.get('trades', [])),
            timeframe=strategy.get('timeframe'),
            max_open_trades=strategy.get('max_open_trades'),
            stake_amount=strategy.get('stake_amount')
        )

    def _parse_trade(self, trade_data: Dict[str, Any]) -> Trade:
        """Parse a single trade from JSON."""
        return Trade(
            pair=trade_data['pair'],
            open_date=self._parse_datetime(trade_data['open_date']),
            close_date=self._parse_datetime(trade_data['close_date']),
            open_rate=float(trade_data['open_rate']),
            close_rate=float(trade_data['close_rate']),
            profit_abs=float(trade_data['profit_abs']),
            profit_ratio=float(trade_data['profit_ratio']),
            enter_tag=trade_data.get('enter_tag', ''),
            trade_duration=int(trade_data.get('trade_duration', 0)),
            exit_reason=trade_data.get('exit_reason'),
            stake_amount=trade_data.get('stake_amount'),
            leverage=trade_data.get('leverage'),
            is_short=trade_data.get('is_short', False)
        )

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string."""
        if not date_str:
            return datetime.now()

        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse datetime: {date_str}")

    def _extract_pairs(self, trades: list[Dict]) -> list[str]:
        """Extract unique pairs from trades."""
        return list(set(t['pair'] for t in trades if 'pair' in t))
