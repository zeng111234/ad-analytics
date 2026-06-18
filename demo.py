#!/usr/bin/env python3
"""
项目演示脚本
快速展示智能广告效果分析与优化平台的核心功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_section(title):
    """打印章节标题"""
    print(f"\n{title}")
    print("-" * 40)

def demo_data_loading():
    """演示数据加载"""
    print_header("1. 数据加载与处理")
    
    from data.data_processor import DataLoader, process_data
    
    # 加载数据
    print("加载示例数据...")
    loader = DataLoader()
    df = loader.load_sample_data()
    
    print(f"数据形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    
    # 处理数据
    print("\n处理数据...")
    processed_df = process_data(df)
    
    print(f"处理后数据形状: {processed_df.shape}")
    print(f"新增列: {[col for col in processed_df.columns if col not in df.columns]}")
    
    return processed_df

def demo_effect_prediction(df):
    """演示效果预测"""
    print_header("2. 效果预测模型")
    
    from models.effect_predictor import AdEffectPredictor
    
    print("训练点击率预测模型...")
    predictor = AdEffectPredictor()
    model = predictor.train_ctr_model(df, model_type='random_forest')
    
    # 预测
    print("\n进行预测...")
    predictions = predictor.predict_all(df.head(5))
    
    print("预测结果:")
    for key, values in predictions.items():
        print(f"  {key}: {values[:3]}...")
    
    return predictor

def demo_ab_test():
    """演示A/B测试分析"""
    print_header("3. A/B测试分析")
    
    from analysis.ab_test_analyzer import ABTestAnalyzer, ABTestDesigner
    
    # 设计测试
    print("设计A/B测试方案...")
    designer = ABTestDesigner()
    test_plan = designer.design_test(
        metric_type='click_rate',
        baseline_value=0.02,
        expected_lift=0.25,
        daily_traffic=5000,
        confidence_level=0.95,
        power=0.8
    )
    
    print(f"每组样本量: {test_plan['sample_size_per_group']:,}")
    print(f"总样本量: {test_plan['total_sample_size']:,}")
    print(f"预计测试天数: {test_plan['estimated_duration_days']} 天")
    
    # 分析测试结果
    print("\n分析测试结果...")
    analyzer = ABTestAnalyzer(alpha=0.05)
    
    result = analyzer.analyze_proportions(
        control_successes=200, control_total=10000,
        treatment_successes=250, treatment_total=10000
    )
    
    print(f"对照组点击率: {result['control_rate']:.2%}")
    print(f"实验组点击率: {result['treatment_rate']:.2%}")
    print(f"相对提升: {result['relative_lift']:.2%}")
    print(f"p值: {result['p_value']:.6f}")
    print(f"统计显著: {result['is_significant']}")

def demo_bid_optimization(df):
    """演示出价优化"""
    print_header("4. 出价优化建议")
    
    from analysis.bid_optimizer import BidOptimizer, BidSimulator
    import numpy as np
    
    # 创建当前出价
    current_bids = {f'group_{i}': np.random.uniform(1, 5) for i in range(5)}
    print(f"当前出价: {current_bids}")
    
    # 获取出价建议
    print("\n获取出价建议...")
    optimizer = BidOptimizer()
    suggestions = optimizer.calculate_bid_suggestions(df.head(5), current_bids)
    
    print("出价建议:")
    for group_id, suggestion in list(suggestions.items())[:3]:
        print(f"  {group_id}: {suggestion['current_bid']:.2f} -> {suggestion['suggested_bid']:.2f} ({suggestion['adjustment_percent']:+.1f}%)")
    
    # 出价模拟
    print("\n出价模拟...")
    simulator = BidSimulator(df)
    result = simulator.simulate_bid_change('group_0', 2.0, 2.5, days=30)
    
    print(f"广告组: group_0")
    print(f"当前出价: {result['current_bid']:.2f}")
    print(f"新出价: {result['new_bid']:.2f}")
    print(f"预计转化量变化: {result['changes']['conversions']:+.1f}%")

def demo_creative_analysis(df):
    """演示素材效果分析"""
    print_header("5. 素材效果分析")
    
    from analysis.creative_analyzer import CreativeAnalyzer, CreativeFeatureAnalyzer
    
    # 素材效果分析
    print("分析素材效果...")
    analyzer = CreativeAnalyzer()
    performance = analyzer.analyze_creative_performance(df, 'ad_format')
    
    print("各素材表现:")
    for creative_type, data in performance.items():
        efficiency = data.get('efficiency', {})
        print(f"  {creative_type}: 点击率 {efficiency.get('overall_ctr', 0):.2%}, 转化率 {efficiency.get('overall_cvr', 0):.2%}")
    
    # 识别表现最好的素材
    print("\n表现最好的素材:")
    top_performers = analyzer.identify_top_performers(df, 'ad_format', 'ctr', 3)
    for performer in top_performers:
        print(f"  {performer['rank']}. {performer['creative_type']}: {performer['metric_value']:.2%}")
    
    # 特征分析
    print("\n特征影响分析...")
    feature_analyzer = CreativeFeatureAnalyzer()
    feature_columns = ['ad_format', 'placement']
    feature_impact = feature_analyzer.analyze_feature_impact(df, feature_columns, 'ctr')
    
    print("特征影响:")
    for feature, impact in feature_impact.items():
        print(f"  {feature}: F统计量 {impact['f_statistic']:.4f}, p值 {impact['p_value']:.6f}")

def demo_visualization_info():
    """演示可视化信息"""
    print_header("6. 可视化数据看板")
    
    print("Streamlit数据看板功能:")
    print("  - 关键指标卡片")
    print("  - 时间趋势分析")
    print("  - 维度分析（广告格式、位置、人群）")
    print("  - 效果关系散点图")
    print("  - 异常检测")
    
    print("\n启动命令:")
    print("  streamlit run visualization/dashboard.py")
    
    print("\n访问地址:")
    print("  http://localhost:8501")

def main():
    """主演示函数"""
    print_header("智能广告效果分析与优化平台 - 功能演示")
    
    try:
        # 1. 数据加载
        df = demo_data_loading()
        
        # 2. 效果预测
        demo_effect_prediction(df)
        
        # 3. A/B测试分析
        demo_ab_test()
        
        # 4. 出价优化
        demo_bid_optimization(df)
        
        # 5. 素材效果分析
        demo_creative_analysis(df)
        
        # 6. 可视化信息
        demo_visualization_info()
        
        print_header("演示完成")
        print("以上展示了智能广告效果分析与优化平台的核心功能。")
        print("更多详细信息请查看项目文档。")
        
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()