"""
数据收集模块
负责从不同来源收集广告投放数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

class DataCollector:
    """数据收集器"""
    
    def __init__(self, config=None):
        """
        初始化数据收集器
        
        Parameters:
        -----------
        config : dict, optional
            配置参数
        """
        self.config = config or {}
        self.data_sources = {}
        
    def add_source(self, name, source_type, **kwargs):
        """
        添加数据源
        
        Parameters:
        -----------
        name : str
            数据源名称
        source_type : str
            数据源类型 ('csv', 'api', 'database', 'mock')
        **kwargs : dict
            数据源参数
        """
        self.data_sources[name] = {
            'type': source_type,
            'params': kwargs
        }
        print(f"添加数据源: {name} ({source_type})")
        
    def collect_from_csv(self, filepath, **kwargs):
        """
        从CSV文件收集数据
        
        Parameters:
        -----------
        filepath : str
            CSV文件路径
        **kwargs : dict
            其他参数
            
        Returns:
        --------
        pandas.DataFrame
            收集的数据
        """
        try:
            df = pd.read_csv(filepath, **kwargs)
            print(f"从CSV收集数据: {filepath}, 形状: {df.shape}")
            return df
        except Exception as e:
            print(f"从CSV收集数据失败: {e}")
            return pd.DataFrame()
    
    def collect_from_api(self, url, params=None, **kwargs):
        """
        从API收集数据（模拟）
        
        Parameters:
        -----------
        url : str
            API端点
        params : dict, optional
            请求参数
        **kwargs : dict
            其他参数
            
        Returns:
        --------
        pandas.DataFrame
            收集的数据
        """
        # 这里是模拟实现，实际项目中会调用真实API
        print(f"从API收集数据: {url}")
        print(f"参数: {params}")
        
        # 返回模拟数据
        return self._generate_mock_api_data()
    
    def collect_from_database(self, connection_string, query, **kwargs):
        """
        从数据库收集数据（模拟）
        
        Parameters:
        -----------
        connection_string : str
            数据库连接字符串
        query : str
            SQL查询
        **kwargs : dict
            其他参数
            
        Returns:
        --------
        pandas.DataFrame
            收集的数据
        """
        # 这里是模拟实现，实际项目中会连接真实数据库
        print(f"从数据库收集数据")
        print(f"连接: {connection_string}")
        print(f"查询: {query}")
        
        # 返回模拟数据
        return self._generate_mock_db_data()
    
    def collect_mock_data(self, num_records=1000, days=30):
        """
        收集模拟数据
        
        Parameters:
        -----------
        num_records : int
            记录数量
        days : int
            天数跨度
            
        Returns:
        --------
        pandas.DataFrame
            模拟数据
        """
        print(f"生成模拟数据: {num_records} 条记录, {days} 天")
        return self._generate_mock_data(num_records, days)
    
    def collect_all(self):
        """
        从所有数据源收集数据
        
        Returns:
        --------
        dict
            所有收集的数据 {name: DataFrame}
        """
        collected_data = {}
        
        for name, source in self.data_sources.items():
            try:
                if source['type'] == 'csv':
                    df = self.collect_from_csv(**source['params'])
                elif source['type'] == 'api':
                    df = self.collect_from_api(**source['params'])
                elif source['type'] == 'database':
                    df = self.collect_from_database(**source['params'])
                elif source['type'] == 'mock':
                    df = self.collect_mock_data(**source['params'])
                else:
                    print(f"未知数据源类型: {source['type']}")
                    continue
                
                if not df.empty:
                    collected_data[name] = df
                    
            except Exception as e:
                print(f"从 {name} 收集数据失败: {e}")
        
        print(f"成功从 {len(collected_data)}/{len(self.data_sources)} 个数据源收集数据")
        return collected_data
    
    def _generate_mock_api_data(self):
        """生成模拟API数据"""
        # 简化的模拟数据
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        data = []
        
        for date in dates:
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'campaign': 'Campaign_A',
                'impressions': random.randint(1000, 5000),
                'clicks': random.randint(50, 250),
                'cost': round(random.uniform(100, 500), 2)
            })
        
        return pd.DataFrame(data)
    
    def _generate_mock_db_data(self):
        """生成模拟数据库数据"""
        # 简化的模拟数据
        data = []
        for i in range(100):
            data.append({
                'id': i + 1,
                'ad_group': f'Group_{i % 5}',
                'keyword': f'keyword_{i}',
                'match_type': random.choice(['exact', 'phrase', 'broad']),
                'quality_score': random.randint(1, 10),
                'avg_position': round(random.uniform(1, 5), 1)
            })
        
        return pd.DataFrame(data)
    
    def _generate_mock_data(self, num_records, days):
        """生成详细的模拟数据"""
        from data.generate_sample_data import generate_sample_data
        return generate_sample_data(num_records=num_records, days=days)

class DataValidator:
    """数据验证器"""
    
    def __init__(self, rules=None):
        """
        初始化数据验证器
        
        Parameters:
        -----------
        rules : dict, optional
            验证规则
        """
        self.rules = rules or {}
        self.validation_results = {}
        
    def add_rule(self, column, rule_type, **kwargs):
        """
        添加验证规则
        
        Parameters:
        -----------
        column : str
            列名
        rule_type : str
            规则类型 ('not_null', 'range', 'unique', 'format')
        **kwargs : dict
            规则参数
        """
        if column not in self.rules:
            self.rules[column] = []
        
        self.rules[column].append({
            'type': rule_type,
            'params': kwargs
        })
    
    def validate(self, df):
        """
        验证数据
        
        Parameters:
        -----------
        df : pandas.DataFrame
            要验证的数据
            
        Returns:
        --------
        dict
            验证结果
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # 基本统计
        results['statistics'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum()
        }
        
        # 检查重复行
        if df.duplicated().sum() > 0:
            results['warnings'].append(f"发现 {df.duplicated().sum()} 行重复数据")
        
        # 应用自定义规则
        for column, rules in self.rules.items():
            if column not in df.columns:
                results['errors'].append(f"列 '{column}' 不存在")
                results['is_valid'] = False
                continue
            
            for rule in rules:
                try:
                    if rule['type'] == 'not_null':
                        null_count = df[column].isnull().sum()
                        if null_count > 0:
                            results['errors'].append(f"列 '{column}' 有 {null_count} 个空值")
                            results['is_valid'] = False
                    
                    elif rule['type'] == 'range':
                        min_val = rule.get('min')
                        max_val = rule.get('max')
                        
                        if min_val is not None and df[column].min() < min_val:
                            results['warnings'].append(f"列 '{column}' 最小值 {df[column].min()} 低于预期 {min_val}")
                        
                        if max_val is not None and df[column].max() > max_val:
                            results['warnings'].append(f"列 '{column}' 最大值 {df[column].max()} 超过预期 {max_val}")
                    
                    elif rule['type'] == 'unique':
                        if not df[column].is_unique:
                            results['warnings'].append(f"列 '{column}' 不是唯一的")
                    
                    elif rule['type'] == 'format':
                        # 这里可以添加格式验证逻辑
                        pass
                        
                except Exception as e:
                    results['warnings'].append(f"验证列 '{column}' 规则 '{rule['type']}' 时出错: {e}")
        
        self.validation_results = results
        return results
    
    def print_report(self):
        """打印验证报告"""
        if not self.validation_results:
            print("没有验证结果，请先运行 validate()")
            return
        
        results = self.validation_results
        
        print("\n" + "="*50)
        print("数据验证报告")
        print("="*50)
        
        print(f"\n数据有效性: {'有效' if results['is_valid'] else '无效'}")
        
        print("\n统计信息:")
        for key, value in results['statistics'].items():
            print(f"  {key}: {value}")
        
        if results['errors']:
            print("\n错误:")
            for error in results['errors']:
                print(f"  - {error}")
        
        if results['warnings']:
            print("\n警告:")
            for warning in results['warnings']:
                print(f"  ! {warning}")
        
        if not results['errors'] and not results['warnings']:
            print("\n数据验证通过，没有发现问题")

class DataTransformer:
    """数据转换器"""
    
    def __init__(self, df):
        """
        初始化数据转换器
        
        Parameters:
        -----------
        df : pandas.DataFrame
            要转换的数据
        """
        self.df = df.copy()
        self.transformations = []
    
    def add_column(self, column_name, formula, **kwargs):
        """
        添加新列
        
        Parameters:
        -----------
        column_name : str
            新列名
        formula : callable
            计算公式
        **kwargs : dict
            其他参数
        """
        self.transformations.append({
            'type': 'add_column',
            'column': column_name,
            'formula': formula,
            'params': kwargs
        })
        return self
    
    def rename_columns(self, mapping):
        """
        重命名列
        
        Parameters:
        -----------
        mapping : dict
            列名映射 {old_name: new_name}
        """
        self.transformations.append({
            'type': 'rename',
            'mapping': mapping
        })
        return self
    
    def filter_rows(self, condition):
        """
        筛选行
        
        Parameters:
        -----------
        condition : callable
            筛选条件
        """
        self.transformations.append({
            'type': 'filter',
            'condition': condition
        })
        return self
    
    def sort_by(self, columns, ascending=True):
        """
        排序
        
        Parameters:
        -----------
        columns : list
            排序列
        ascending : bool
            是否升序
        """
        self.transformations.append({
            'type': 'sort',
            'columns': columns,
            'ascending': ascending
        })
        return self
    
    def transform(self):
        """
        执行所有转换
        
        Returns:
        --------
        pandas.DataFrame
            转换后的数据
        """
        result = self.df.copy()
        
        for transformation in self.transformations:
            try:
                if transformation['type'] == 'add_column':
                    column = transformation['column']
                    formula = transformation['formula']
                    result[column] = result.apply(formula, axis=1)
                    print(f"添加列: {column}")
                
                elif transformation['type'] == 'rename':
                    mapping = transformation['mapping']
                    result = result.rename(columns=mapping)
                    print(f"重命名列: {mapping}")
                
                elif transformation['type'] == 'filter':
                    condition = transformation['condition']
                    initial_rows = len(result)
                    result = result[condition(result)]
                    print(f"筛选行: {initial_rows} -> {len(result)}")
                
                elif transformation['type'] == 'sort':
                    columns = transformation['columns']
                    ascending = transformation['ascending']
                    result = result.sort_values(columns, ascending=ascending)
                    print(f"排序: {columns}")
                    
            except Exception as e:
                print(f"转换失败: {e}")
        
        return result

# 便捷函数
def collect_data(source_type='mock', **kwargs):
    """
    收集数据的便捷函数
    
    Parameters:
    -----------
    source_type : str
        数据源类型
    **kwargs : dict
        数据源参数
        
    Returns:
    --------
    pandas.DataFrame
        收集的数据
    """
    collector = DataCollector()
    
    if source_type == 'mock':
        return collector.collect_mock_data(**kwargs)
    elif source_type == 'csv':
        return collector.collect_from_csv(**kwargs)
    else:
        print(f"不支持的数据源类型: {source_type}")
        return pd.DataFrame()

def validate_data(df, rules=None):
    """
    验证数据的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        要验证的数据
    rules : dict, optional
        验证规则
        
    Returns:
    --------
    dict
        验证结果
    """
    validator = DataValidator(rules)
    return validator.validate(df)

if __name__ == "__main__":
    # 测试数据收集
    print("测试数据收集...")
    
    collector = DataCollector()
    
    # 添加数据源
    collector.add_source('mock_data', 'mock', num_records=500, days=15)
    
    # 收集数据
    data = collector.collect_all()
    
    for name, df in data.items():
        print(f"\n{name}: {df.shape}")
        print(df.head())
    
    # 测试数据验证
    print("\n" + "="*50)
    print("测试数据验证...")
    
    if data:
        df = list(data.values())[0]
        
        rules = {
            'impressions': [
                {'type': 'not_null'},
                {'type': 'range', 'min': 0}
            ],
            'clicks': [
                {'type': 'not_null'},
                {'type': 'range', 'min': 0}
            ]
        }
        
        validator = DataValidator(rules)
        results = validator.validate(df)
        validator.print_report()
    
    # 测试数据转换
    print("\n" + "="*50)
    print("测试数据转换...")
    
    if data:
        df = list(data.values())[0]
        
        transformer = DataTransformer(df)
        transformed_df = (transformer
                        .add_column('efficiency_score', 
                                   lambda row: row['clicks'] / row['impressions'] if row['impressions'] > 0 else 0)
                        .sort_by(['date', 'impressions'], ascending=[True, False])
                        .transform())
        
        print(f"转换后数据形状: {transformed_df.shape}")
        print(transformed_df.head())