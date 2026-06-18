# 智能广告效果分析与优化平台

## 项目状态

✅ **已完成部署并运行中**

- GitHub仓库：https://github.com/zeng111234/ad-analytics
- 本地访问：http://localhost:8501
- 网络访问：http://192.168.124.9:8501

## 核心功能

1. **效果预测模型**：点击率预测（R² = 0.98）
2. **A/B测试分析**：样本量计算、统计显著性检验
3. **出价优化**：出价建议、预算分配
4. **素材效果分析**：效果比较、特征分析
5. **数据看板**：交互式可视化、多维度分析

## 如何使用

```bash
# 克隆项目
git clone https://github.com/zeng111234/ad-analytics.git
cd ad-analytics

# 安装依赖
pip install -r requirements.txt

# 生成示例数据
python data/generate_sample_data.py

# 启动数据看板
streamlit run visualization/dashboard.py

# 运行演示程序
python demo.py
```

## 项目结构

```
ad-analytics/
├── data/           # 数据层模块
├── models/         # 机器学习模型
├── analysis/       # 分析工具
├── visualization/  # 可视化界面
├── docs/           # 项目文档
├── demo.py         # 演示程序
├── main.py         # 主程序
└── README.md       # 项目说明
```

## 技术栈

- Python, Pandas, NumPy
- Scikit-learn (机器学习)
- Streamlit, Plotly (可视化)
- SciPy, Statsmodels (统计分析)

## 联系方式

- GitHub: [@zeng111234](https://github.com/zeng111234)