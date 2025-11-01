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
