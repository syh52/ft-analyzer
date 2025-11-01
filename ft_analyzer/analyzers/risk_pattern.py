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
