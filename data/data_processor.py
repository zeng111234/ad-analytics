"""
数据处理模块
负责加载、清洗和处理广告投放数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config import DATA_CONFIG, BUSINESS_CONFIG

class DataLoader:
    """数据加载器"""
    
    def __init__(self, data_dir=None):
        """
        初始化数据加载器
        
        Parameters:
        -----------
        data_dir : str, optional
            数据目录路径，默认使用配置文件中的路径
        """
        self.data_dir = data_dir or DATA_CONFIG['data_dir']
        self.data_dir = Path(self.data_dir)
        
    def load_csv(self, filename):
        """
        加载CSV文件
        
        Parameters:
        -----------
        filename : str
            文件名
            
        Returns:
        --------
        pandas.DataFrame
            加载的数据
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"成功加载数据: {file_path}")
            print(f"数据形状: {df.shape}")
            return df
        except Exception as e:
            print(f"加载数据失败: {e}")
            raise
    
    def load_sample_data(self):
        """
        加载示例数据
        
        Returns:
        --------
        pandas.DataFrame
            示例数据
        """
        filename = DATA_CONFIG['sample_data_file']
        return self.load_csv(filename)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, df):
        """
        初始化数据处理器
        
        Parameters:
        -----------
        df : pandas.DataFrame
            要处理的数据
        """
        self.df = df.copy()
        self.original_shape = df.shape
        
    def clean_data(self):
        """
        清洗数据
        
        Returns:
        --------
        DataProcessor
            返回自身，支持链式调用
        """
        # 删除重复行
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        print(f"删除重复行: {initial_rows - len(self.df)} 行")
        
        # 处理缺失值
        missing_values = self.df.isnull().sum()
        if missing_values.any():
            print("缺失值统计:")
            print(missing_values[missing_values > 0])
            
            # 对于数值列，用中位数填充
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    median_val = self.df[col].median()
                    self.df[col].fillna(median_val, inplace=True)
                    print(f"用中位数填充 {col}: {median_val}")
        
        return self
    
    def convert_types(self):
        """
        转换数据类型
        
        Returns:
        --------
        DataProcessor
            返回自身，支持链式调用
        """
        # 转换日期列
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            print("已转换日期列类型")
        
        # 确保数值列为正确类型
        numeric_cols = ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'cpc', 'cpa']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        return self
    
    def add_calculated_metrics(self):
        """
        添加计算指标
        
        Returns:
        --------
        DataProcessor
            返回自身，支持链式调用
        """
        # 计算点击率 (CTR)
        if 'impressions' in self.df.columns and 'clicks' in self.df.columns:
            self.df['ctr_calculated'] = np.where(
                self.df['impressions'] > 0,
                self.df['clicks'] / self.df['impressions'],
                0
            )
        
        # 计算每次点击成本 (CPC)
        if 'cost' in self.df.columns and 'clicks' in self.df.columns:
            self.df['cpc_calculated'] = np.where(
                self.df['clicks'] > 0,
                self.df['cost'] / self.df['clicks'],
                0
            )
        
        # 计算每次转化成本 (CPA)
        if 'cost' in self.df.columns and 'conversions' in self.df.columns:
            self.df['cpa_calculated'] = np.where(
                self.df['conversions'] > 0,
                self.df['cost'] / self.df['conversions'],
                0
            )
        
        # 计算转化率 (CVR)
        if 'clicks' in self.df.columns and 'conversions' in self.df.columns:
            self.df['cvr'] = np.where(
                self.df['clicks'] > 0,
                self.df['conversions'] / self.df['clicks'],
                0
            )
        
        print("已添加计算指标")
        return self
    
    def filter_by_date_range(self, start_date=None, end_date=None):
        """
        按日期范围筛选数据
        
        Parameters:
        -----------
        start_date : str, optional
            开始日期 (YYYY-MM-DD)
        end_date : str, optional
            结束日期 (YYYY-MM-DD)
            
        Returns:
        --------
        DataProcessor
            返回自身，支持链式调用
        """
        if 'date' not in self.df.columns:
            print("警告: 数据中没有日期列")
            return self
        
        initial_rows = len(self.df)
        
        if start_date:
            start_dt = pd.to_datetime(start_date)
            self.df = self.df[self.df['date'] >= start_dt]
        
        if end_date:
            end_dt = pd.to_datetime(end_date)
            self.df = self.df[self.df['date'] <= end_dt]
        
        print(f"日期筛选: {initial_rows} -> {len(self.df)} 行")
        return self
    
    def aggregate_by_dimension(self, dimension, metrics=None):
        """
        按维度聚合数据
        
        Parameters:
        -----------
        dimension : str
            聚合维度列名
        metrics : list, optional
            要聚合的指标列表
            
        Returns:
        --------
        pandas.DataFrame
            聚合后的数据
        """
        if metrics is None:
            metrics = BUSINESS_CONFIG['metrics']
        
        # 确保指标列存在
        available_metrics = [m for m in metrics if m in self.df.columns]
        
        if not available_metrics:
            print("警告: 没有可用的指标列")
            return pd.DataFrame()
        
        # 聚合数据
        agg_dict = {metric: 'sum' for metric in available_metrics}
        
        # 对于比率指标，需要重新计算
        ratio_metrics = ['ctr', 'cpc', 'cpa']
        for metric in ratio_metrics:
            if metric in available_metrics:
                if metric == 'ctr':
                    agg_dict[metric] = lambda x: (x * self.df.loc[x.index, 'impressions']).sum() / self.df.loc[x.index, 'impressions'].sum() if self.df.loc[x.index, 'impressions'].sum() > 0 else 0
                elif metric == 'cpc':
                    agg_dict[metric] = lambda x: self.df.loc[x.index, 'cost'].sum() / self.df.loc[x.index, 'clicks'].sum() if self.df.loc[x.index, 'clicks'].sum() > 0 else 0
                elif metric == 'cpa':
                    agg_dict[metric] = lambda x: self.df.loc[x.index, 'cost'].sum() / self.df.loc[x.index, 'conversions'].sum() if self.df.loc[x.index, 'conversions'].sum() > 0 else 0
        
        aggregated = self.df.groupby(dimension).agg(agg_dict).reset_index()
        
        print(f"按 {dimension} 聚合完成，共 {len(aggregated)} 组")
        return aggregated
    
    def get_processed_data(self):
        """
        获取处理后的数据
        
        Returns:
        --------
        pandas.DataFrame
            处理后的数据
        """
        return self.df.copy()
    
    def get_summary(self):
        """
        获取数据摘要
        
        Returns:
        --------
        dict
            数据摘要信息
        """
        summary = {
            'original_shape': self.original_shape,
            'current_shape': self.df.shape,
            'date_range': {
                'start': self.df['date'].min() if 'date' in self.df.columns else None,
                'end': self.df['date'].max() if 'date' in self.df.columns else None
            },
            'missing_values': self.df.isnull().sum().sum(),
            'memory_usage': self.df.memory_usage(deep=True).sum()
        }
        
        return summary

def process_data(df):
    """
    处理数据的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        原始数据
        
    Returns:
    --------
    pandas.DataFrame
        处理后的数据
    """
    processor = DataProcessor(df)
    processed_df = (processor
                   .clean_data()
                   .convert_types()
                   .add_calculated_metrics()
                   .get_processed_data())
    
    return processed_df

if __name__ == "__main__":
    # 测试数据处理
    try:
        # 加载数据
        loader = DataLoader()
        df = loader.load_sample_data()
        
        # 处理数据
        processed_df = process_data(df)
        
        # 显示结果
        print("\n处理后的数据预览:")
        print(processed_df.head())
        
        print("\n数据摘要:")
        processor = DataProcessor(df)
        processor.clean_data().convert_types().add_calculated_metrics()
        summary = processor.get_summary()
        
        for key, value in summary.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()