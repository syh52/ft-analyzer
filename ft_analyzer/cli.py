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
