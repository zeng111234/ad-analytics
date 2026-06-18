# 智能广告效果分析与优化平台 - 用户手册

## 目录
1. [项目概述](#项目概述)
2. [安装指南](#安装指南)
3. [快速开始](#快速开始)
4. [功能详解](#功能详解)
5. [使用示例](#使用示例)
6. [常见问题](#常见问题)
7. [技术支持](#技术支持)

## 项目概述

智能广告效果分析与优化平台是一个基于Python的广告效果分析工具，旨在帮助广告投放人员做出数据驱动的决策。本平台集成了数据收集、效果预测、A/B测试分析、出价优化和素材效果分析等核心功能。

### 核心功能

1. **广告效果数据看板**：实时查看广告效果数据，支持多维度分析
2. **智能效果预测**：基于机器学习预测广告点击率、转化率等关键指标
3. **A/B测试分析**：自动化A/B测试分析，提供统计显著性检验
4. **出价优化建议**：基于效果数据提供智能出价调整建议
5. **素材效果分析**：分析不同广告素材的效果差异，识别高绩效素材

### 技术栈

- **数据处理**：Python, Pandas, NumPy
- **机器学习**：Scikit-learn
- **可视化**：Matplotlib, Seaborn, Streamlit, Plotly
- **统计分析**：SciPy, Statsmodels
- **数据存储**：CSV/SQLite

## 安装指南

### 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows, macOS, Linux

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd ad-analytics
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

4. **验证安装**
   ```bash
   python main.py
   ```

### 依赖包说明

主要依赖包包括：
- pandas：数据处理和分析
- numpy：数值计算
- scikit-learn：机器学习算法
- matplotlib：基础可视化
- seaborn：统计可视化
- streamlit：Web应用框架
- plotly：交互式可视化
- scipy：科学计算
- statsmodels：统计建模

## 快速开始

### 1. 生成示例数据

```bash
cd ad-analytics
python data/generate_sample_data.py
```

这将生成示例广告数据文件 `data/sample_ad_data.csv`。

### 2. 启动数据看板

```bash
streamlit run visualization/dashboard.py
```

这将在浏览器中打开交互式数据看板。

### 3. 运行主程序

```bash
python main.py
```

这将启动命令行界面，提供各种功能选项。

## 功能详解

### 1. 数据层模块

#### 数据收集器 (DataCollector)
支持多种数据源：
- CSV文件
- API接口
- 数据库
- 模拟数据

```python
from data.data_collector import DataCollector

collector = DataCollector()
collector.add_source('csv_data', 'csv', filepath='data/sample_ad_data.csv')
data = collector.collect_all()
```

#### 数据处理器 (DataProcessor)
数据清洗、转换和特征工程：

```python
from data.data_processor import DataProcessor

processor = DataProcessor(df)
processed_df = (processor
               .clean_data()
               .convert_types()
               .add_calculated_metrics()
               .get_processed_data())
```

### 2. 分析层模块

#### 效果预测模型
预测广告点击率、转化率等指标：

```python
from models.effect_predictor import AdEffectPredictor

predictor = AdEffectPredictor()
predictor.train_ctr_model(df, model_type='random_forest')
predictions = predictor.predict_all(new_data)
```

#### A/B测试分析器
分析A/B测试结果：

```python
from analysis.ab_test_analyzer import ABTestAnalyzer

analyzer = ABTestAnalyzer(alpha=0.05)
result = analyzer.analyze_proportions(
    control_successes=200, control_total=10000,
    treatment_successes=250, treatment_total=10000
)
```

#### 出价优化器
提供出价调整建议：

```python
from analysis.bid_optimizer import BidOptimizer

optimizer = BidOptimizer()
suggestions = optimizer.calculate_bid_suggestions(df, current_bids)
```

#### 素材效果分析器
分析不同广告素材的效果：

```python
from analysis.creative_analyzer import CreativeAnalyzer

analyzer = CreativeAnalyzer()
performance = analyzer.analyze_creative_performance(df, 'ad_format')
top_performers = analyzer.identify_top_performers(df, 'ad_format', 'ctr', 3)
```

### 3. 可视化模块

#### 数据看板
Streamlit交互式数据看板，包含：
- 关键指标卡片
- 时间趋势分析
- 维度分析
- 效果关系散点图
- 异常检测

启动命令：
```bash
streamlit run visualization/dashboard.py
```

## 使用示例

### 示例1：完整分析流程

```python
# 1. 加载和处理数据
from data.data_processor import DataLoader, process_data
loader = DataLoader()
df = loader.load_sample_data()
processed_df = process_data(df)

# 2. 训练预测模型
from models.effect_predictor import AdEffectPredictor
predictor = AdEffectPredictor()
predictor.train_ctr_model(processed_df, model_type='random_forest')

# 3. 分析素材效果
from analysis.creative_analyzer import CreativeAnalyzer
creative_analyzer = CreativeAnalyzer()
performance = creative_analyzer.analyze_creative_performance(processed_df, 'ad_format')

# 4. 获取出价建议
from analysis.bid_optimizer import BidOptimizer
bid_optimizer = BidOptimizer()
current_bids = {'group_1': 2.5, 'group_2': 3.0, 'group_3': 2.0}
suggestions = bid_optimizer.calculate_bid_suggestions(processed_df, current_bids)

# 5. 生成报告
bid_optimizer.print_bid_optimization_report()
```

### 示例2：A/B测试分析

```python
from analysis.ab_test_analyzer import ABTestAnalyzer, ABTestDesigner

# 设计测试
designer = ABTestDesigner()
test_plan = designer.design_test(
    metric_type='click_rate',
    baseline_value=0.02,  # 2%点击率
    expected_lift=0.25,   # 25%提升
    daily_traffic=5000,
    confidence_level=0.95,
    power=0.8
)

# 分析测试结果
analyzer = ABTestAnalyzer(alpha=0.05)
result = analyzer.analyze_proportions(
    control_successes=200, control_total=10000,
    treatment_successes=250, treatment_total=10000
)

# 打印报告
analyzer.print_report('proportions')
```

### 示例3：出价优化

```python
from analysis.bid_optimizer import BidOptimizer, BidSimulator
import pandas as pd

# 加载数据
df = pd.read_csv('data/sample_ad_data.csv')

# 获取出价建议
optimizer = BidOptimizer()
current_bids = {f'group_{i}': 2.0 + i * 0.5 for i in range(10)}
suggestions = optimizer.calculate_bid_suggestions(df, current_bids)

# 模拟出价变化
simulator = BidSimulator(df)
result = simulator.simulate_bid_change('group_0', 2.0, 2.5, days=30)
simulator.print_simulation_report('group_0')
```

## 常见问题

### Q1: 如何添加自己的数据？

A1: 将您的数据保存为CSV文件，放在 `data/` 目录下，然后使用 `DataLoader` 加载：

```python
from data.data_processor import DataLoader

loader = DataLoader()
df = loader.load_csv('your_data.csv')
```

### Q2: 如何自定义模型参数？

A2: 在创建模型时可以指定参数：

```python
from models.effect_predictor import CTRPredictionModel

model = CTRPredictionModel(
    model_type='gradient_boosting',
    random_state=42
)
```

### Q3: 如何扩展新的分析功能？

A3: 您可以在 `analysis/` 目录下创建新的分析模块，然后更新 `analysis/__init__.py` 文件。

### Q4: 数据看板无法启动怎么办？

A4: 请检查：
1. 是否正确安装了所有依赖包
2. 数据文件是否存在
3. 端口8501是否被占用

## 技术支持

### 项目结构

```
ad-analytics/
├── data/                    # 数据文件和处理模块
├── models/                  # 机器学习模型
├── analysis/                # 分析工具
├── visualization/           # 可视化界面
├── utils/                   # 工具函数
├── tests/                   # 测试代码
├── docs/                    # 文档
├── main.py                  # 主程序
├── config.py                # 配置文件
├── requirements.txt         # 依赖包
└── README.md                # 项目说明
```

### 配置说明

配置文件 `config.py` 包含：
- 数据配置：数据目录、文件路径
- 模型配置：测试集比例、随机种子
- 可视化配置：主题、颜色、图表尺寸
- 业务配置：货币、时区、指标列表

### 开发指南

1. **代码风格**：遵循PEP 8规范
2. **文档字符串**：使用Google风格的文档字符串
3. **测试**：为关键功能编写测试用例
4. **版本控制**：使用Git进行版本控制

### 更新日志

#### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现核心功能模块
- 创建Streamlit数据看板

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues：[GitHub Issues]
- 邮箱：[your-email@example.com]

---

**感谢使用智能广告效果分析与优化平台！**