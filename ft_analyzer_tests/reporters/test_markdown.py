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
