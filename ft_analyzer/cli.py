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
