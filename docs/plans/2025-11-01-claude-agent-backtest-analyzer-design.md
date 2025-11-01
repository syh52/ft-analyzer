# Claude Agent SDK 集成 - 智能回测分析顾问

**设计文档版本**: v1.0
**创建日期**: 2025-11-01
**状态**: 设计完成，待实施

---

## 1. 概述

### 1.1 项目目标

构建一个基于 Claude Agent SDK 的智能分析顾问系统，自动分析 Freqtrade 回测结果，结合实际K线数据提供深度洞察和优化建议。

### 1.2 核心价值

- **自动化分析**: 每次回测后自动触发深度分析，无需人工干预
- **多维洞察**: 从入场质量、风险模式、参数敏感度、市场适配4个维度分析
- **可操作建议**: 生成方向性优化建议，帮助策略迭代
- **专业报告**: 生成结构化Markdown报告，便于归档和分享

### 1.3 设计约束

| 约束项 | 要求 |
|--------|------|
| **性能** | 1-3分钟/次分析 |
| **成本** | $0.15-0.25/次（使用Sonnet模型） |
| **集成方式** | 独立CLI工具，不修改Freqtrade源码 |
| **触发方式** | 自动监听 + 手动调用 |
| **输出格式** | Markdown报告 |
| **K线分析深度** | 统计分析（不做深度形态识别） |

---

## 2. 架构设计

### 2.1 方案选择

**选定方案**: 混合模式CLI工具（方案C）

**核心特点**:
- 统一的CLI入口，支持多种使用模式
- 单次分析、监听模式、批量分析、对比分析
- 可选的守护进程模式
- 渐进式功能实现

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                   ft-analyzer CLI                       │
│  ┌─────────┬──────────┬─────────┬──────────────┐       │
│  │ analyze │  watch   │  batch  │   compare    │       │
│  └─────────┴──────────┴─────────┴──────────────┘       │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    ┌─────▼──────┐      ┌──────▼────────┐
    │  Watcher   │      │   Analyzer    │
    │ (监听器)    │      │  (分析引擎)    │
    └─────┬──────┘      └──────┬────────┘
          │                    │
          │            ┌───────┴────────┐
          │            │                │
          │      ┌─────▼─────┐   ┌─────▼─────┐
          │      │  Data     │   │  Claude   │
          │      │  Loader   │   │  Agent    │
          │      └─────┬─────┘   └─────┬─────┘
          │            │                │
          │      ┌─────▼─────┐         │
          │      │  4D       │         │
          │      │ Analyzers │         │
          │      └─────┬─────┘         │
          │            │                │
          │            └────────┬───────┘
          │                     │
          └─────────────┬───────┘
                        │
                  ┌─────▼──────┐
                  │  Report    │
                  │ Generator  │
                  └─────┬──────┘
                        │
                  ┌─────▼──────┐
                  │ Markdown   │
                  │  Report    │
                  └────────────┘
```

### 2.3 目录结构

```
freqtrade/
└── ft_analyzer/                    # 新建目录
    ├── __init__.py
    ├── cli.py                      # CLI入口 (click框架)
    ├── core/
    │   ├── __init__.py
    │   ├── watcher.py              # 文件监听 (watchdog)
    │   ├── analyzer.py             # 分析引擎协调器
    │   └── agent.py                # Claude Agent SDK封装
    ├── analyzers/
    │   ├── __init__.py
    │   ├── entry_quality.py        # 入场点质量分析
    │   ├── risk_pattern.py         # 风险模式识别
    │   ├── parameter_sensitivity.py # 参数敏感度
    │   └── market_condition.py     # 市场环境适配
    ├── data/
    │   ├── __init__.py
    │   ├── loader.py               # 数据加载器
    │   └── models.py               # 数据模型 (dataclass)
    ├── reporters/
    │   ├── __init__.py
    │   └── markdown.py             # Markdown报告生成
    └── utils/
        ├── __init__.py
        ├── config.py               # 配置管理
        └── logger.py               # 日志系统
```

---

## 3. 数据流设计

### 3.1 完整数据流

```
触发 → 数据加载 → 预处理 → AI分析 → 报告生成 → 保存/通知
```

### 3.2 各阶段详解

#### 阶段1: 触发分析

**触发源**:
- 文件监听: 检测 `.last_result.json` 变化
- 手动命令: `ft-analyzer analyze latest`
- 批量处理: `ft-analyzer batch <dir>`

**创建分析请求**:
```python
@dataclass
class AnalysisRequest:
    backtest_result_path: Path      # 回测结果JSON路径
    strategy_name: str              # 策略名称
    timerange: tuple[str, str]     # 时间范围
    pairs: list[str]               # 交易对列表
```

#### 阶段2: 数据加载

**数据源**:
1. **回测结果JSON**: 交易记录、元数据
2. **K线数据**: feather格式，按需加载
3. **策略代码**: 读取策略参数配置

**数据模型**:
```python
@dataclass
class BacktestData:
    trades: list[Trade]            # 所有交易记录
    metadata: dict                 # 回测元数据
    strategy_code: str             # 策略源码
    strategy_params: dict          # 策略参数

    def get_ohlcv(self, pair: str, timeframe: str,
                  start: datetime, end: datetime) -> pd.DataFrame:
        """按需加载K线数据"""
        pass

@dataclass
class Trade:
    pair: str                      # 交易对
    open_date: datetime            # 开仓时间
    close_date: datetime           # 平仓时间
    open_rate: float               # 开仓价格
    close_rate: float              # 平仓价格
    profit_abs: float              # 绝对盈亏
    profit_ratio: float            # 盈亏比例
    enter_tag: str                 # 入场模式标记
    trade_duration: int            # 持仓时长（分钟）
```

#### 阶段3: 预处理与统计

**基础统计** (本地计算，不消耗API):
```python
@dataclass
class BasicStats:
    strategy_name: str
    timerange: tuple[str, str]
    pairs: list[str]

    total_trades: int
    total_profit: float
    win_rate: float
    avg_duration: timedelta
    max_drawdown: float
    liquidations: int

    # 分组统计
    stats_by_pair: dict[str, dict]
    stats_by_mode: dict[str, dict]
```

**上下文准备** (为AI分析准备结构化数据):
```python
contexts = {
    'entry_quality': {
        'modes_summary': [...],
        'sample_trades': [...]  # 包含K线指标
    },
    'risk_pattern': {
        'risk_events': [...],
        'patterns': [...]
    },
    'parameter': {
        'strategy_params': {...},
        'mode_performance': {...}
    },
    'market': {
        'market_phases': [...],
        'performance_by_phase': {...}
    }
}
```

#### 阶段4: AI分析

**单次综合调用策略**:
```python
# 构建完整prompt，包含所有上下文
prompt = f"""
你是一个专业的量化交易分析师。以下是一次回测的完整数据。

## 基础统计
{format_stats(stats)}

## 交易明细
{format_trades(contexts['entry_quality']['trades'])}

## K线数据摘要
{format_ohlcv_summary(contexts['entry_quality']['ohlcv'])}

## 风险事件
{format_risk_events(contexts['risk_pattern'])}

请从以下4个维度进行分析：
1. 入场点质量：分析每个入场模式的成功率和K线环境
2. 风险模式识别：找出爆仓、连亏等危险模式
3. 参数敏感度：判断哪些参数对结果影响最大
4. 市场环境适配：分析策略在不同市况下的表现

针对每个维度，给出：
- 发现的问题（如果有）
- 优化方向建议
- 风险等级评估

请以结构化的方式输出分析结果。
"""

# 调用Claude Agent SDK
response = await claude_agent.query(prompt)
```

**Token估算**:
- Prompt: ~30K-40K tokens (包含统计数据、示例交易、K线摘要)
- Response: ~10K-20K tokens
- 总计: ~50K tokens × $0.003/1K ≈ $0.15-0.25

#### 阶段5: 报告生成

**报告结构**:
```markdown
# 📊 Freqtrade 回测分析报告

## 📈 总体表现
[表格: 核心指标 + 评级]

## 🎯 维度一：入场点质量分析
- 总结
- 各模式表现
- 关键发现
- 优化建议

## ⚠️ 维度二：风险模式识别
- 总结
- 风险事件列表
- 危险模式
- 风险控制建议

## 🔧 维度三：参数敏感度分析
- 总结
- 关键参数影响评估
- 参数优化方向

## 🌍 维度四：市场环境适配
- 总结
- 不同市况下的表现
- 适配性建议

## 🎯 综合结论
- 整体评估
- 优先级行动清单
```

**保存策略**:
- 路径: `user_data/analysis_reports/`
- 文件名: `analysis-{strategy}-{timestamp}.md`
- 同时更新: `latest.md` 软链接

---

## 4. 四维分析器详细设计

### 4.1 入场点质量分析

**目标**: 评估每个 `enter_tag` 模式的质量，结合K线验证。

**分析步骤**:
1. 按 `enter_tag` 分组交易
2. 统计每个模式的胜率、平均盈利、持仓时长
3. 选取代表性交易（盈利、亏损、最大盈利各1笔）
4. 加载入场时刻前后的K线数据（前20根+后5根）
5. 计算关键指标：
   - 价格相对SMA20的位置
   - 成交量相对平均值
   - RSI值
   - 趋势方向（短期vs长期均线）

**输出示例**:
```python
{
    'modes_summary': [
        {
            'mode': '120 (Grind)',
            'count': 4,
            'win_rate': 100.0,
            'avg_profit': 2466,
            'avg_duration': '7.5天'
        },
        ...
    ],
    'sample_trades': [
        {
            'pair': 'DOGE/USDT',
            'mode': '120',
            'outcome': 'profit',
            'price_vs_sma20': 0.98,  # 略低于均线
            'volume_vs_avg': 1.45,   # 成交量放大
            'rsi': 42,               # 超卖区
            'trend': 'up'            # 上升趋势
        },
        ...
    ]
}
```

### 4.2 风险模式识别

**目标**: 自动发现危险信号（爆仓、连亏、大回撤）。

**检测规则**:
1. **爆仓检测**: `profit_ratio < -0.90`
2. **连续亏损**: 连续3笔或以上亏损
3. **大回撤交易**: 单笔亏损超过5%本金
4. **高风险模式**: 某个 `enter_tag` 爆仓率超过10%

**输出示例**:
```python
{
    'risk_events': [
        {
            'type': 'liquidation',
            'pair': 'BNB/USDT',
            'enter_mode': '141',
            'loss_amount': -1245,
            'date': '2024-08-15'
        },
        ...
    ],
    'patterns': [
        {
            'type': 'high_risk_mode',
            'mode': '141',
            'liquidation_rate': 0.167,
            'total_trades': 6
        }
    ]
}
```

### 4.3 参数敏感度分析

**目标**: 识别对结果影响最大的参数。

**分析方法**:
- 基于单次回测数据的推断
- 从交易结果反推参数影响
- 例如：如果TC Mode大量爆仓 → 止损参数是关键

**输出示例**:
```python
{
    'strategy_params': {
        'stoploss': -0.99,
        'use_custom_stoploss': True,
        ...
    },
    'mode_performance': {
        '141': {'profit': -500, 'win_rate': 0.67},
        '120': {'profit': 9865, 'win_rate': 1.0}
    },
    'inferred_sensitivities': [
        {
            'parameter': 'custom_stoploss for mode 141',
            'reason': 'Mode 141 表现不佳，止损参数可能需要调整',
            'current_impact': 'negative'
        }
    ]
}
```

### 4.4 市场环境适配

**目标**: 分析策略在不同市况（牛/熊/震荡）下的表现。

**分类标准**:
- 使用BTC作为市场基准
- 牛市: 30日涨幅 > 10%
- 熊市: 30日跌幅 > 10%
- 震荡: 其他

**输出示例**:
```python
{
    'market_phases': [
        {'date': '2024-01-15', 'phase': 'bull', 'pct_change': 15.2},
        {'date': '2024-08-10', 'phase': 'bear', 'pct_change': -12.5},
        ...
    ],
    'performance_by_phase': {
        'bull': {'trade_count': 15, 'total_profit': 8500, 'win_rate': 0.93},
        'bear': {'trade_count': 10, 'total_profit': 4200, 'win_rate': 0.90},
        'sideways': {'trade_count': 9, 'total_profit': 4800, 'win_rate': 1.0}
    }
}
```

---

## 5. CLI命令设计

### 5.1 命令列表

```bash
# 核心命令
ft-analyzer analyze <result_file|"latest">  # 分析指定结果
ft-analyzer watch [--daemon]                # 监听模式
ft-analyzer batch <directory>               # 批量分析（Phase 3）
ft-analyzer compare <result1> <result2>     # 对比分析（Phase 3）

# 辅助命令
ft-analyzer status                          # 查看运行状态
ft-analyzer config [--init]                 # 配置管理
ft-analyzer version                         # 版本信息
```

### 5.2 使用示例

**场景1: 开发时快速验证**
```bash
# 运行回测
freqtrade backtesting --strategy MyStrategy -c user_data/config.json

# 立即分析
ft-analyzer analyze latest

# 输出:
# 正在分析: backtest-result-2025-11-01_15-30-45.json
# ✅ 分析完成!
# 报告已保存: user_data/analysis_reports/analysis-MyStrategy-20251101-153245.md
```

**场景2: 长期回测优化（自动监听）**
```bash
# 启动监听（前台）
ft-analyzer watch
# 开始监听目录: /path/to/user_data/backtest_results
# 监听已启动 (按 Ctrl+C 停止)

# 或启动守护进程
ft-analyzer watch --daemon
# 守护进程已启动，PID: 12345

# 在另一个终端运行多次回测
freqtrade backtesting ...  # 自动分析
freqtrade backtesting ...  # 自动分析
```

**场景3: 查看状态**
```bash
ft-analyzer status
# ✅ 守护进程正在运行 (PID: 12345)
# 最后分析: 2025-11-01 15:45:23
# 今日分析次数: 5
```

---

## 6. 配置管理

### 6.1 配置文件位置

- 全局配置: `~/.ft_analyzer/config.yaml`
- 项目配置: `<freqtrade_root>/ft_analyzer.yaml` (可选，优先级更高)

### 6.2 配置示例

```yaml
# Claude API配置
claude:
  api_key: ${ANTHROPIC_API_KEY}  # 从环境变量读取
  model: claude-sonnet-4-5        # 主力模型
  max_tokens: 50000
  timeout: 300  # 超时时间（秒）

# Freqtrade路径配置
freqtrade:
  user_data_dir: /path/to/freqtrade/user_data
  backtest_results_dir: user_data/backtest_results
  data_dir: user_data/data

# 分析配置
analysis:
  # 启用的分析维度
  enabled_analyzers:
    - entry_quality
    - risk_pattern
    - parameter_sensitivity
    - market_condition

  # 报告输出
  report_output_dir: user_data/analysis_reports

  # K线数据加载策略
  ohlcv_lookback_candles: 20  # 入场前加载多少根K线
  ohlcv_lookahead_candles: 5  # 入场后加载多少根K线

# 监听配置
watch:
  poll_interval: 5  # 文件检查间隔（秒）
  auto_analyze: true

# 通知配置（可选）
notifications:
  enabled: false
  telegram:
    bot_token: ""
    chat_id: ""

# 日志配置
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file: ~/.ft_analyzer/logs/ft-analyzer.log
```

### 6.3 初始化配置

```bash
# 生成默认配置文件
ft-analyzer config --init

# 输出:
# 配置文件已创建: ~/.ft_analyzer/config.yaml
# 请编辑配置文件，设置 ANTHROPIC_API_KEY
```

---

## 7. 错误处理与降级策略

### 7.1 错误类型

```python
class AnalysisError(Exception):
    """分析过程中的错误基类"""
    pass

class DataLoadError(AnalysisError):
    """数据加载错误"""
    pass

class ClaudeAPIError(AnalysisError):
    """Claude API调用错误"""
    pass
```

### 7.2 降级策略

**场景1: AI分析失败**
- 降级为：仅基于本地统计生成简化报告
- 包含：基础统计表格、风险事件列表
- 标注：⚠️ AI分析失败，仅包含基础统计

**场景2: 部分数据加载失败**
- 继续处理可用数据
- 在报告中标注：部分数据不可用
- 记录警告日志

**场景3: API限流**
- 自动重试（指数退避）
- 最多重试3次
- 失败后降级为简化报告

### 7.3 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def analyze_with_context(self, stats, contexts):
    """带重试机制的分析调用"""
    # API调用
    pass
```

---

## 8. 技术栈

### 8.1 核心依赖

```toml
[tool.poetry.dependencies]
python = "^3.10"
claude-agent-sdk = "^0.1.0"        # Claude Agent SDK
anthropic = "^0.18.0"              # Anthropic API client
click = "^8.1.0"                   # CLI框架
watchdog = "^3.0.0"                # 文件监听
pandas = "^2.1.0"                  # 数据处理
pyarrow = "^14.0.0"                # 读取feather格式
pyyaml = "^6.0"                    # 配置文件
tenacity = "^8.2.0"                # 重试机制

# 可选依赖
python-daemon = "^3.0.0"           # 守护进程
```

### 8.2 开发依赖

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
ruff = "^0.1.0"
mypy = "^1.7.0"
```

---

## 9. 实施计划

### Phase 1: 核心功能（2-3天）

**目标**: 实现基本可用的分析功能

**任务**:
- [ ] 搭建项目结构
- [ ] 实现数据加载器（BacktestData, Trade models）
- [ ] 实现4个分析器（预处理逻辑）
- [ ] 集成Claude Agent SDK
- [ ] 实现Markdown报告生成
- [ ] 实现 `analyze` 命令
- [ ] 编写基础测试

**验收标准**:
```bash
ft-analyzer analyze latest
# 能生成完整的分析报告
```

### Phase 2: 监听模式（1-2天）

**目标**: 实现自动监听和分析

**任务**:
- [ ] 实现文件监听器（watchdog）
- [ ] 实现 `watch` 前台模式
- [ ] 添加配置管理
- [ ] 完善错误处理和日志
- [ ] 编写监听测试

**验收标准**:
```bash
ft-analyzer watch
# 能检测新回测结果并自动分析
```

### Phase 3: 扩展功能（可选，2-3天）

**目标**: 增强工具的实用性

**任务**:
- [ ] 实现 `watch --daemon` 守护进程
- [ ] 实现 `batch` 批量分析
- [ ] 实现 `compare` 对比分析
- [ ] 实现 `status` 状态查询
- [ ] 添加Telegram通知（可选）
- [ ] Web Dashboard（可选）

---

## 10. 测试策略

### 10.1 单元测试

**测试覆盖**:
- 数据加载器: 测试各种回测结果格式
- 分析器: 测试边界情况（空数据、异常值）
- 报告生成: 测试格式化逻辑

**示例**:
```python
def test_risk_pattern_liquidation_detection():
    """测试爆仓检测"""
    trades = [
        Trade(profit_ratio=-0.95, ...),  # 爆仓
        Trade(profit_ratio=0.10, ...),   # 正常
    ]

    context = risk_pattern.prepare_risk_context(trades)

    assert len(context['risk_events']) == 1
    assert context['risk_events'][0]['type'] == 'liquidation'
```

### 10.2 集成测试

**测试场景**:
1. 端到端分析流程
2. 文件监听触发
3. API调用和重试
4. 报告生成和保存

### 10.3 手动测试

**测试清单**:
- [ ] 使用真实回测数据运行分析
- [ ] 验证报告内容准确性
- [ ] 测试监听模式稳定性
- [ ] 测试各种错误场景
- [ ] 测试性能和成本

---

## 11. 部署和使用

### 11.1 安装

```bash
# 进入Freqtrade项目根目录
cd /path/to/freqtrade

# 安装依赖
pip install -e ./ft_analyzer

# 初始化配置
ft-analyzer config --init

# 设置API密钥
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 11.2 日常使用

**开发阶段**:
```bash
# 运行回测
freqtrade backtesting --strategy MyStrategy

# 手动分析
ft-analyzer analyze latest
```

**优化阶段**:
```bash
# 启动监听
ft-analyzer watch --daemon

# 批量运行回测
for param in 1 2 3 4 5; do
    freqtrade backtesting --strategy MyStrategy --param $param
done

# 查看所有分析报告
ls -lh user_data/analysis_reports/
```

---

## 12. 未来扩展

### 12.1 短期扩展

- **批量对比分析**: 对比多次回测，找出最优参数
- **趋势追踪**: 跨时间追踪策略表现变化
- **实时监控**: 监控实盘交易，发现异常

### 12.2 长期扩展

- **自动优化建议**: 基于分析结果自动生成代码建议
- **A/B测试框架**: 系统化测试参数变化的影响
- **策略评分系统**: 建立策略评价标准
- **知识库构建**: 积累分析洞察，形成策略优化知识库

---

## 13. 风险和限制

### 13.1 已知限制

1. **单次回测分析**: 无法对比历史，只能分析单次结果
2. **统计K线分析**: 不做深度形态识别，可能遗漏复杂模式
3. **方向性建议**: 不生成具体代码，需要人工实施
4. **API依赖**: 需要稳定的网络和Claude API访问

### 13.2 成本控制

- **Token优化**: 只传递结构化数据，不传原始K线
- **智能缓存**: 相同数据不重复加载
- **分层分析**: 基础统计本地计算，只用AI做洞察

### 13.3 安全考虑

- **API密钥**: 通过环境变量管理，不硬编码
- **数据隐私**: 所有分析在本地进行，不上传原始数据
- **错误隔离**: 分析失败不影响回测流程

---

## 14. 参考资料

- Claude Agent SDK 文档: https://docs.claude.com/en/api/agent-sdk/overview
- Freqtrade 文档: https://www.freqtrade.io
- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Watchdog: https://python-watchdog.readthedocs.io

---

## 附录

### A. 数据模型完整定义

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

@dataclass
class Trade:
    """单笔交易记录"""
    pair: str
    stake_amount: float
    amount: float
    open_date: datetime
    close_date: datetime
    open_rate: float
    close_rate: float
    fee_open: float
    fee_close: float
    trade_duration: int  # 分钟
    profit_ratio: float
    profit_abs: float
    exit_reason: str
    initial_stop_loss_abs: float
    initial_stop_loss_ratio: float
    stop_loss_abs: float
    stop_loss_ratio: float
    min_rate: float
    max_rate: float
    is_open: bool
    enter_tag: str
    leverage: float
    is_short: bool

@dataclass
class BacktestMetadata:
    """回测元数据"""
    strategy_name: str
    timeframe: str
    timerange_start: datetime
    timerange_end: datetime
    max_open_trades: int
    stake_amount: str
    dry_run_wallet: float

@dataclass
class BacktestData:
    """完整的回测数据"""
    trades: list[Trade]
    metadata: BacktestMetadata
    strategy_code: str
    strategy_params: dict

    # K线数据懒加载
    _data_dir: Path

    def get_ohlcv(self, pair: str, timeframe: str,
                  start: datetime = None, end: datetime = None) -> pd.DataFrame:
        """加载K线数据"""
        # 从feather文件读取
        filename = f"{pair.replace('/', '_')}-{timeframe}-futures.feather"
        filepath = self._data_dir / filename

        df = pd.read_feather(filepath)

        if start:
            df = df[df.timestamp >= start]
        if end:
            df = df[df.timestamp <= end]

        return df
```

### B. 报告模板示例

详见第四部分报告生成设计。

---

**文档结束**

此设计文档将随着实施过程中的反馈持续更新和完善。
