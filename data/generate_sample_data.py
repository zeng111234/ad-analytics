"""
示例数据生成器
用于生成模拟的广告投放数据，便于测试和演示
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_records=1000, start_date='2024-01-01', days=30):
    """
    生成示例广告数据
    
    Parameters:
    -----------
    num_records : int
        生成记录数量
    start_date : str
        开始日期 (YYYY-MM-DD)
    days : int
        天数跨度
        
    Returns:
    --------
    pandas.DataFrame
        包含模拟广告数据的DataFrame
    """
    
    # 设置随机种子以便结果可重现
    np.random.seed(42)
    random.seed(42)
    
    # 生成日期序列
    start = datetime.strptime(start_date, '%Y-%m-%d')
    dates = [start + timedelta(days=i) for i in range(days)]
    
    # 广告素材类型
    ad_formats = ['图片', '视频', '信息流', '横幅', '原生']
    
    # 广告位置
    placements = ['首页', '侧边栏', '底部', '信息流', '开屏']
    
    # 目标人群
    audiences = ['18-24岁', '25-34岁', '35-44岁', '45-54岁', '55岁以上']
    
    data = []
    
    for i in range(num_records):
        # 随机选择日期
        date = random.choice(dates)
        
        # 随机选择广告参数
        ad_format = random.choice(ad_formats)
        placement = random.choice(placements)
        audience = random.choice(audiences)
        
        # 基础展示量 (不同广告类型有不同的基础值)
        base_impressions = {
            '图片': 1000,
            '视频': 800,
            '信息流': 1200,
            '横幅': 600,
            '原生': 900
        }[ad_format]
        
        # 生成展示量 (带有一些随机性)
        impressions = int(base_impressions * (0.8 + 0.4 * random.random()))
        
        # 点击率 (不同广告类型和位置有不同的基础CTR)
        base_ctr = {
            '图片': 0.02,
            '视频': 0.03,
            '信息流': 0.025,
            '横幅': 0.015,
            '原生': 0.022
        }[ad_format]
        
        # 位置对CTR的影响
        placement_multiplier = {
            '首页': 1.2,
            '侧边栏': 0.9,
            '底部': 0.8,
            '信息流': 1.1,
            '开屏': 1.3
        }[placement]
        
        ctr = base_ctr * placement_multiplier * (0.9 + 0.2 * random.random())
        clicks = int(impressions * ctr)
        
        # 转化率 (约为点击率的10-30%)
        conversion_rate = random.uniform(0.1, 0.3) * ctr
        conversions = int(clicks * conversion_rate)
        
        # 每次点击成本 (CPC)
        base_cpc = 2.5  # 基础CPC 2.5元
        cpc = base_cpc * (0.8 + 0.4 * random.random())
        cost = clicks * cpc
        
        # 计算每次转化成本 (CPA)
        cpa = cost / conversions if conversions > 0 else 0
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'ad_format': ad_format,
            'placement': placement,
            'audience': audience,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'cost': round(cost, 2),
            'ctr': round(ctr, 4),
            'cpc': round(cpc, 2),
            'cpa': round(cpa, 2)
        })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 按日期排序
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

def save_sample_data(df, filename='sample_ad_data.csv'):
    """
    保存示例数据到CSV文件
    
    Parameters:
    -----------
    df : pandas.DataFrame
        要保存的数据
    filename : str
        文件名
    """
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"示例数据已保存到: {filename}")
    print(f"数据形状: {df.shape}")
    print(f"日期范围: {df['date'].min()} 到 {df['date'].max()}")

if __name__ == "__main__":
    # 生成示例数据
    sample_data = generate_sample_data(num_records=2000, days=60)
    
    # 保存到data目录
    import os
    os.makedirs('data', exist_ok=True)
    save_sample_data(sample_data, 'data/sample_ad_data.csv')
    
    # 显示数据基本信息
    print("\n数据预览:")
    print(sample_data.head())
    print("\n数据统计:")
    print(sample_data.describe())