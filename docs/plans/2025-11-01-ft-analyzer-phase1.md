# ft-analyzer Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a functional CLI tool that can analyze Freqtrade backtest results and generate Markdown reports with AI-powered insights.

**Architecture:** Independent CLI tool using Click framework, Claude Agent SDK for analysis, and modular analyzer components. Follows data flow: Load JSON → Prepare contexts → Call Claude → Generate report.

**Tech Stack:** Python 3.10+, Click (CLI), Claude Agent SDK, Pandas, PyArrow (feather files), PyYAML (config)

---

## Task 1: Project Structure Setup

**Files:**
- Create: `ft_analyzer/__init__.py`
- Create: `ft_analyzer/core/__init__.py`
- Create: `ft_analyzer/analyzers/__init__.py`
- Create: `ft_analyzer/data/__init__.py`
- Create: `ft_analyzer/reporters/__init__.py`
- Create: `ft_analyzer/utils/__init__.py`
- Create: `setup.py`
- Create: `requirements.txt`

**Step 1: Create directory structure**

```bash
mkdir -p ft_analyzer/{core,analyzers,data,reporters,utils}
touch ft_analyzer/__init__.py
touch ft_analyzer/{core,analyzers,data,reporters,utils}/__init__.py
```

**Step 2: Create setup.py**

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="ft-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pandas>=2.1.0",
        "pyarrow>=14.0.0",
        "pyyaml>=6.0",
        "anthropic>=0.18.0",
    ],
    entry_points={
        "console_scripts": [
            "ft-analyzer=ft_analyzer.cli:cli",
        ],
    },
    python_requires=">=3.10",
)
```

**Step 3: Create requirements.txt**

Create `requirements.txt`:

```
click>=8.1.0
pandas>=2.1.0
pyarrow>=14.0.0
pyyaml>=6.0
anthropic>=0.18.0
```

**Step 4: Create package version**

Edit `ft_analyzer/__init__.py`:

```python
"""ft-analyzer: Intelligent Freqtrade backtest analyzer using Claude Agent SDK."""

__version__ = "0.1.0"
```

**Step 5: Verify structure**

Run: `tree ft_analyzer -I __pycache__`

Expected: Clean directory structure with all folders

**Step 6: Commit**

```bash
git add ft_analyzer/ setup.py requirements.txt
git commit -m "feat: initialize ft-analyzer project structure

Create basic package structure with:
- Core modules (core, analyzers, data, reporters, utils)
- Setup configuration for pip install
- Requirements file with dependencies"
```

---

## Task 2: Data Models

**Files:**
- Create: `ft_analyzer/data/models.py`
- Create: `tests/data/test_models.py`

**Step 1: Write failing test for Trade model**

Create `tests/data/test_models.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_models.py -v`

Expected: FAIL with "cannot import name 'Trade'"

**Step 3: Create Trade dataclass**

Create `ft_analyzer/data/models.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/data/test_models.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add ft_analyzer/data/models.py tests/data/test_models.py
git commit -m "feat: add data models for trades and backtest results

Add dataclass models:
- Trade: individual trade with profit/liquidation checks
- BacktestMetadata: backtest configuration info
- BacktestData: complete dataset with statistics"
```

---

## Task 3: Data Loader - JSON Parsing

**Files:**
- Create: `ft_analyzer/data/loader.py`
- Create: `tests/data/test_loader.py`
- Create: `tests/fixtures/sample_backtest.json`

**Step 1: Create sample test data**

Create `tests/fixtures/sample_backtest.json`:

```json
{
  "strategy": {
    "strategy_name": "TestStrategy",
    "timeframe": "5m"
  },
  "backtest_start": "2024-01-01 00:00:00",
  "backtest_end": "2024-01-31 23:59:59",
  "trades": [
    {
      "pair": "BTC/USDT:USDT",
      "open_date": "2024-01-05 10:00:00",
      "close_date": "2024-01-05 12:30:00",
      "open_rate": 45000.0,
      "close_rate": 46000.0,
      "profit_abs": 100.0,
      "profit_ratio": 0.02,
      "enter_tag": "120",
      "trade_duration": 150,
      "exit_reason": "roi"
    },
    {
      "pair": "ETH/USDT:USDT",
      "open_date": "2024-01-10 14:00:00",
      "close_date": "2024-01-10 16:00:00",
      "open_rate": 3000.0,
      "close_rate": 2950.0,
      "profit_abs": -50.0,
      "profit_ratio": -0.0167,
      "enter_tag": "141",
      "trade_duration": 120,
      "exit_reason": "stop_loss"
    }
  ]
}
```

**Step 2: Write failing test for JSON loader**

Create `tests/data/test_loader.py`:

```python
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
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/data/test_loader.py -v`

Expected: FAIL with "cannot import name 'BacktestLoader'"

**Step 4: Implement BacktestLoader**

Create `ft_analyzer/data/loader.py`:

```python
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
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/data/test_loader.py -v`

Expected: PASS (2 tests)

**Step 6: Commit**

```bash
git add ft_analyzer/data/loader.py tests/data/test_loader.py tests/fixtures/
git commit -m "feat: implement backtest JSON loader

Add BacktestLoader class to parse Freqtrade JSON results:
- Parse metadata (strategy, timerange, pairs)
- Parse individual trades
- Handle datetime conversion
- Include test fixtures"
```

---

## Task 4: Basic Statistics Calculator

**Files:**
- Create: `ft_analyzer/data/stats.py`
- Create: `tests/data/test_stats.py`

**Step 1: Write failing test for statistics**

Create `tests/data/test_stats.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_stats.py -v`

Expected: FAIL with "cannot import name 'StatsCalculator'"

**Step 3: Implement StatsCalculator**

Create `ft_analyzer/data/stats.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/data/test_stats.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add ft_analyzer/data/stats.py tests/data/test_stats.py
git commit -m "feat: add statistics calculator

Implement StatsCalculator for computing:
- Basic metrics (win rate, profit, etc)
- Stats grouped by trading pair
- Stats grouped by entry mode"
```

---

## Task 5: Risk Pattern Analyzer

**Files:**
- Create: `ft_analyzer/analyzers/risk_pattern.py`
- Create: `tests/analyzers/test_risk_pattern.py`

**Step 1: Write failing test for risk detection**

Create `tests/analyzers/test_risk_pattern.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/analyzers/test_risk_pattern.py -v`

Expected: FAIL with "cannot import name 'RiskPatternAnalyzer'"

**Step 3: Implement RiskPatternAnalyzer**

Create `ft_analyzer/analyzers/risk_pattern.py`:

```python
"""Risk pattern analyzer for identifying dangerous trading patterns."""

from typing import Dict, List, Any
from collections import defaultdict

from ft_analyzer.data.models import Trade


class RiskPatternAnalyzer:
    """Analyze trades for risk patterns."""

    def prepare_context(self, trades: List[Trade]) -> Dict[str, Any]:
        """Prepare risk analysis context.

        Args:
            trades: List of trades to analyze

        Returns:
            Dictionary containing:
            - risk_events: List of individual risk events
            - patterns: List of identified patterns
        """
        context = {
            'risk_events': [],
            'patterns': []
        }

        # Detect liquidations
        for trade in trades:
            if trade.is_liquidation:
                context['risk_events'].append({
                    'type': 'liquidation',
                    'pair': trade.pair,
                    'enter_mode': trade.enter_tag,
                    'loss_amount': trade.profit_abs,
                    'date': trade.close_date.strftime('%Y-%m-%d')
                })

        # Detect large drawdowns
        for trade in trades:
            if trade.profit_ratio < -0.05 and not trade.is_liquidation:
                context['risk_events'].append({
                    'type': 'large_drawdown',
                    'pair': trade.pair,
                    'enter_mode': trade.enter_tag,
                    'drawdown_pct': trade.profit_ratio * 100,
                    'date': trade.close_date.strftime('%Y-%m-%d')
                })

        # Detect consecutive losses
        sorted_trades = sorted(trades, key=lambda t: t.close_date)
        consecutive_count = 0
        consecutive_trades = []

        for trade in sorted_trades:
            if not trade.is_profitable:
                consecutive_count += 1
                consecutive_trades.append(trade)
            else:
                if consecutive_count >= 3:
                    total_loss = sum(t.profit_abs for t in consecutive_trades)
                    context['patterns'].append({
                        'type': 'consecutive_losses',
                        'count': consecutive_count,
                        'total_loss': total_loss,
                        'trades': [t.pair for t in consecutive_trades]
                    })
                consecutive_count = 0
                consecutive_trades = []

        # Check final consecutive losses
        if consecutive_count >= 3:
            total_loss = sum(t.profit_abs for t in consecutive_trades)
            context['patterns'].append({
                'type': 'consecutive_losses',
                'count': consecutive_count,
                'total_loss': total_loss,
                'trades': [t.pair for t in consecutive_trades]
            })

        # Detect high-risk modes
        mode_stats = defaultdict(lambda: {'total': 0, 'liquidations': 0})
        for trade in trades:
            mode = trade.enter_tag or 'unknown'
            mode_stats[mode]['total'] += 1
            if trade.is_liquidation:
                mode_stats[mode]['liquidations'] += 1

        for mode, stats in mode_stats.items():
            if stats['liquidations'] > 0:
                liquidation_rate = stats['liquidations'] / stats['total']
                context['patterns'].append({
                    'type': 'high_risk_mode',
                    'mode': mode,
                    'liquidation_rate': liquidation_rate,
                    'total_trades': stats['total'],
                    'liquidations': stats['liquidations']
                })

        return context
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/analyzers/test_risk_pattern.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add ft_analyzer/analyzers/risk_pattern.py tests/analyzers/test_risk_pattern.py
git commit -m "feat: implement risk pattern analyzer

Add RiskPatternAnalyzer to detect:
- Liquidations (profit_ratio < -0.90)
- Large drawdowns (> 5%)
- Consecutive loss streaks
- High-risk entry modes"
```

---

## Task 6: CLI基础框架

**Files:**
- Create: `ft_analyzer/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing test for CLI**

Create `tests/test_cli.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`

Expected: FAIL with "cannot import name 'cli'"

**Step 3: Implement basic CLI**

Create `ft_analyzer/cli.py`:

```python
"""CLI interface for ft-analyzer."""

import click
from pathlib import Path

from ft_analyzer import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Freqtrade 回测分析工具

    使用 Claude Agent SDK 自动分析回测结果，提供多维度洞察。
    """
    pass


@cli.command()
@click.argument('result', default='latest')
def analyze(result: str):
    """分析回测结果

    RESULT: 回测结果文件路径或 'latest' (分析最新结果)

    示例:
        ft-analyzer analyze latest
        ft-analyzer analyze /path/to/backtest-result.json
    """
    click.echo(f"分析功能开发中...")
    click.echo(f"目标文件: {result}")


@cli.command()
@click.option('--daemon', is_flag=True, help='以守护进程模式运行')
def watch(daemon: bool):
    """监听回测结果目录，自动分析新结果

    示例:
        ft-analyzer watch              # 前台监听
        ft-analyzer watch --daemon     # 后台守护进程
    """
    if daemon:
        click.echo("守护进程模式开发中...")
    else:
        click.echo("监听模式开发中...")


@cli.command()
def status():
    """查看运行状态"""
    click.echo("状态查询功能开发中...")


if __name__ == '__main__':
    cli()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`

Expected: PASS (3 tests)

**Step 5: Test CLI manually**

Run: `python -m ft_analyzer.cli --version`

Expected: Output showing version 0.1.0

Run: `python -m ft_analyzer.cli --help`

Expected: Help text with commands listed

**Step 6: Commit**

```bash
git add ft_analyzer/cli.py tests/test_cli.py
git commit -m "feat: add CLI framework with Click

Implement basic CLI structure:
- Main group with version support
- analyze command (stub)
- watch command (stub)
- status command (stub)"
```

---

## Task 7: Markdown Report Generator

**Files:**
- Create: `ft_analyzer/reporters/markdown.py`
- Create: `tests/reporters/test_markdown.py`

**Step 1: Write failing test for report generation**

Create `tests/reporters/test_markdown.py`:

```python
import pytest
from datetime import datetime
from ft_analyzer.reporters.markdown import MarkdownReporter


@pytest.fixture
def sample_stats():
    """Sample statistics for report."""
    return {
        'strategy_name': 'TestStrategy',
        'timerange': ('2024-01-01', '2024-01-31'),
        'pairs': ['BTC/USDT:USDT', 'ETH/USDT:USDT'],
        'total_trades': 10,
        'total_profit': 500.0,
        'win_rate': 80.0,
        'avg_duration': '4h 30m',
        'max_drawdown': 5.2,
        'liquidations': 0
    }


@pytest.fixture
def sample_insights():
    """Sample AI insights."""
    return {
        'risk_pattern': {
            'summary': '本次回测未发现严重风险事件。',
            'recommendations': ['保持当前风控策略']
        },
        'overall_conclusion': '策略表现稳定，风险可控。'
    }


def test_generate_report_header(sample_stats, sample_insights):
    """Test report header generation."""
    reporter = MarkdownReporter()
    report = reporter.generate(sample_stats, sample_insights)

    assert '# 📊 Freqtrade 回测分析报告' in report
    assert 'TestStrategy' in report
    assert '2024-01-01' in report
    assert '2024-01-31' in report


def test_generate_report_stats_table(sample_stats, sample_insights):
    """Test statistics table generation."""
    reporter = MarkdownReporter()
    report = reporter.generate(sample_stats, sample_insights)

    assert '## 📈 总体表现' in report
    assert '总利润' in report
    assert '500.00 USDT' in report
    assert '交易次数' in report
    assert '10' in report
    assert '胜率' in report
    assert '80.0%' in report


def test_generate_report_conclusion(sample_stats, sample_insights):
    """Test conclusion section."""
    reporter = MarkdownReporter()
    report = reporter.generate(sample_stats, sample_insights)

    assert '## 🎯 综合结论' in report
    assert '策略表现稳定' in report
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/reporters/test_markdown.py -v`

Expected: FAIL with "cannot import name 'MarkdownReporter'"

**Step 3: Implement MarkdownReporter**

Create `ft_analyzer/reporters/markdown.py`:

```python
"""Markdown report generator."""

from datetime import datetime
from typing import Dict, Any


class MarkdownReporter:
    """Generate Markdown analysis reports."""

    def generate(self, stats: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate complete analysis report.

        Args:
            stats: Basic statistics
            insights: AI-generated insights

        Returns:
            Markdown-formatted report
        """
        sections = [
            self._generate_header(stats),
            self._generate_stats_section(stats),
            self._generate_risk_section(insights.get('risk_pattern', {})),
            self._generate_conclusion(insights.get('overall_conclusion', ''))
        ]

        return '\n\n'.join(sections)

    def _generate_header(self, stats: Dict[str, Any]) -> str:
        """Generate report header."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return f"""# 📊 Freqtrade 回测分析报告

**生成时间**: {now}
**策略**: {stats.get('strategy_name', 'Unknown')}
**回测周期**: {stats.get('timerange', ['N/A', 'N/A'])[0]} 至 {stats.get('timerange', ['N/A', 'N/A'])[1]}
**交易对**: {', '.join(stats.get('pairs', []))}

---"""

    def _generate_stats_section(self, stats: Dict[str, Any]) -> str:
        """Generate statistics table."""
        return f"""## 📈 总体表现

| 指标 | 数值 | 评级 |
|------|------|------|
| 总利润 | {stats.get('total_profit', 0):.2f} USDT | {self._grade_profit(stats.get('total_profit', 0))} |
| 交易次数 | {stats.get('total_trades', 0)} | - |
| 胜率 | {stats.get('win_rate', 0):.1f}% | {self._grade_winrate(stats.get('win_rate', 0))} |
| 平均持仓时长 | {stats.get('avg_duration', 'N/A')} | - |
| 最大回撤 | {stats.get('max_drawdown', 0):.2f}% | {self._grade_drawdown(stats.get('max_drawdown', 0))} |
| 爆仓次数 | {stats.get('liquidations', 0)} | {self._grade_liquidations(stats.get('liquidations', 0))} |

{self._render_risk_badge(stats)}

---"""

    def _generate_risk_section(self, risk_data: Dict[str, Any]) -> str:
        """Generate risk analysis section."""
        summary = risk_data.get('summary', '暂无风险分析数据')
        recommendations = risk_data.get('recommendations', [])

        rec_list = '\n'.join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))

        return f"""## ⚠️ 风险模式识别

{summary}

### 📝 风险控制建议

{rec_list if rec_list else '暂无建议'}

---"""

    def _generate_conclusion(self, conclusion: str) -> str:
        """Generate conclusion section."""
        return f"""## 🎯 综合结论

{conclusion if conclusion else '暂无结论'}

---

*报告由 ft-analyzer v0.1.0 自动生成*
*AI 分析引擎: Claude Agent SDK*"""

    def _grade_profit(self, profit: float) -> str:
        """Grade profit level."""
        if profit > 1000:
            return '✅ 优秀'
        elif profit > 0:
            return '🟢 良好'
        elif profit > -500:
            return '🟡 一般'
        else:
            return '🔴 较差'

    def _grade_winrate(self, winrate: float) -> str:
        """Grade win rate."""
        if winrate >= 90:
            return '✅ 优秀'
        elif winrate >= 70:
            return '🟢 良好'
        elif winrate >= 50:
            return '🟡 一般'
        else:
            return '🔴 较差'

    def _grade_drawdown(self, drawdown: float) -> str:
        """Grade max drawdown."""
        if drawdown < 5:
            return '✅ 优秀'
        elif drawdown < 10:
            return '🟢 良好'
        elif drawdown < 20:
            return '🟡 一般'
        else:
            return '🔴 较差'

    def _grade_liquidations(self, liquidations: int) -> str:
        """Grade liquidation count."""
        if liquidations == 0:
            return '✅ 优秀'
        elif liquidations <= 2:
            return '🟡 警告'
        else:
            return '🔴 危险'

    def _render_risk_badge(self, stats: Dict[str, Any]) -> str:
        """Render overall risk badge."""
        liquidations = stats.get('liquidations', 0)
        drawdown = stats.get('max_drawdown', 0)

        if liquidations == 0 and drawdown < 10:
            badge = '🟢 **风险评级: 低**'
        elif liquidations <= 2 and drawdown < 20:
            badge = '🟡 **风险评级: 中**'
        else:
            badge = '🔴 **风险评级: 高**'

        return badge
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/reporters/test_markdown.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add ft_analyzer/reporters/markdown.py tests/reporters/test_markdown.py
git commit -m "feat: implement Markdown report generator

Add MarkdownReporter class:
- Report header with metadata
- Statistics table with grading
- Risk analysis section
- Conclusion section
- Automatic grading system"
```

---

## Task 8: Integration - Analyze Command

**Files:**
- Modify: `ft_analyzer/cli.py`
- Create: `tests/integration/test_analyze_flow.py`

**Step 1: Write integration test**

Create `tests/integration/test_analyze_flow.py`:

```python
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
    assert 'not found' in result.output.lower() or '找不到' in result.output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_analyze_flow.py -v`

Expected: FAIL (analyze command not yet implemented)

**Step 3: Implement analyze command**

Edit `ft_analyzer/cli.py`:

```python
"""CLI interface for ft-analyzer."""

import click
from pathlib import Path

from ft_analyzer import __version__
from ft_analyzer.data.loader import BacktestLoader
from ft_analyzer.data.stats import StatsCalculator
from ft_analyzer.analyzers.risk_pattern import RiskPatternAnalyzer
from ft_analyzer.reporters.markdown import MarkdownReporter


@click.group()
@click.version_option(version=__version__)
def cli():
    """Freqtrade 回测分析工具

    使用 Claude Agent SDK 自动分析回测结果，提供多维度洞察。
    """
    pass


@cli.command()
@click.argument('result', default='latest')
def analyze(result: str):
    """分析回测结果

    RESULT: 回测结果文件路径或 'latest' (分析最新结果)

    示例:
        ft-analyzer analyze latest
        ft-analyzer analyze /path/to/backtest-result.json
    """
    try:
        # Parse result path
        result_path = Path(result)
        if not result_path.exists():
            click.secho(f"❌ 文件不存在: {result_path}", fg='red', err=True)
            raise click.Abort()

        click.echo(f"正在分析: {result_path.name}")

        # Load data
        loader = BacktestLoader()
        data = loader.load_from_json(result_path)

        click.echo(f"✓ 加载 {data.total_trades} 笔交易")

        # Calculate statistics
        calculator = StatsCalculator()
        basic_stats = calculator.calculate(data.trades)

        # Prepare analysis contexts
        risk_analyzer = RiskPatternAnalyzer()
        risk_context = risk_analyzer.prepare_context(data.trades)

        # For now, create simple insights without AI
        insights = {
            'risk_pattern': {
                'summary': f"检测到 {len(risk_context['risk_events'])} 个风险事件",
                'recommendations': ['基于本地分析的建议（AI分析待实现）']
            },
            'overall_conclusion': f"回测包含 {data.total_trades} 笔交易，胜率 {data.win_rate:.1f}%"
        }

        # Generate report
        reporter = MarkdownReporter()
        stats_for_report = {
            'strategy_name': data.metadata.strategy_name,
            'timerange': (
                data.metadata.timerange_start.strftime('%Y-%m-%d'),
                data.metadata.timerange_end.strftime('%Y-%m-%d')
            ),
            'pairs': data.metadata.pairs,
            **basic_stats
        }

        report = reporter.generate(stats_for_report, insights)

        # Save report
        output_dir = Path('user_data/analysis_reports')
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = data.metadata.timerange_end.strftime('%Y%m%d-%H%M%S')
        report_path = output_dir / f"analysis-{data.metadata.strategy_name}-{timestamp}.md"

        report_path.write_text(report, encoding='utf-8')

        click.secho(f"\n✅ 分析完成!", fg='green', bold=True)
        click.echo(f"报告已保存: {report_path}")

    except FileNotFoundError as e:
        click.secho(f"❌ 文件未找到: {e}", fg='red', err=True)
        raise click.Abort()
    except Exception as e:
        click.secho(f"❌ 分析失败: {e}", fg='red', err=True)
        raise click.Abort()


@cli.command()
@click.option('--daemon', is_flag=True, help='以守护进程模式运行')
def watch(daemon: bool):
    """监听回测结果目录，自动分析新结果

    示例:
        ft-analyzer watch              # 前台监听
        ft-analyzer watch --daemon     # 后台守护进程
    """
    if daemon:
        click.echo("守护进程模式开发中...")
    else:
        click.echo("监听模式开发中...")


@cli.command()
def status():
    """查看运行状态"""
    click.echo("状态查询功能开发中...")


if __name__ == '__main__':
    cli()
```

**Step 4: Run integration test**

Run: `pytest tests/integration/test_analyze_flow.py -v`

Expected: PASS (2 tests)

**Step 5: Manual test**

Run: `python -m ft_analyzer.cli analyze tests/data/fixtures/sample_backtest.json`

Expected:
- Output showing analysis progress
- Report file created in user_data/analysis_reports/

**Step 6: Commit**

```bash
git add ft_analyzer/cli.py tests/integration/test_analyze_flow.py
git commit -m "feat: implement analyze command

Integrate components for end-to-end analysis:
- Load backtest JSON
- Calculate statistics
- Run risk analysis
- Generate Markdown report
- Save to user_data/analysis_reports/"
```

---

## Summary

**Phase 1 Complete!**

You now have a functional CLI tool that can:
- ✅ Load Freqtrade backtest results
- ✅ Calculate basic statistics
- ✅ Detect risk patterns
- ✅ Generate professional Markdown reports

**What's missing (Phase 2):**
- Claude Agent SDK integration for AI insights
- File watching mode
- Configuration management

**What's ready:**
- All data models and loaders
- Statistics calculation
- Risk pattern detection
- Report generation
- CLI interface

**Next steps:**
1. Install the package: `pip install -e .`
2. Test with real backtest data
3. Review generated reports
4. Proceed to Phase 2 for AI integration

---

**Total estimated time:** 2-3 days for a skilled developer following this plan step-by-step.
