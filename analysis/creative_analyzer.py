"""
素材效果分析模块
用于分析不同广告素材的效果差异，识别高绩效素材特征
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class CreativeAnalyzer:
    """素材效果分析器"""
    
    def __init__(self):
        """初始化素材效果分析器"""
        self.analysis_results = {}
        self.creative_features = {}
        
    def analyze_creative_performance(self, df, creative_column='ad_format', 
                                    metrics=None):
        """
        分析素材效果
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
        metrics : list, optional
            要分析的指标列表
            
        Returns:
        --------
        dict
            分析结果
        """
        if metrics is None:
            metrics = ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'cvr', 'cpc', 'cpa']
        
        # 检查列是否存在
        available_metrics = [m for m in metrics if m in df.columns]
        if not available_metrics:
            return {}
        
        # 按素材类型分组分析
        creative_groups = df.groupby(creative_column)
        
        results = {}
        for creative_type, group_data in creative_groups:
            # 计算基本统计量
            stats_dict = {}
            for metric in available_metrics:
                if metric in group_data.columns:
                    values = group_data[metric].dropna()
                    if len(values) > 0:
                        stats_dict[metric] = {
                            'mean': values.mean(),
                            'median': values.median(),
                            'std': values.std(),
                            'min': values.min(),
                            'max': values.max(),
                            'count': len(values),
                            'sum': values.sum()
                        }
            
            # 计算效率指标
            efficiency_metrics = {}
            if 'impressions' in group_data.columns and 'clicks' in group_data.columns:
                total_impressions = group_data['impressions'].sum()
                total_clicks = group_data['clicks'].sum()
                efficiency_metrics['overall_ctr'] = total_clicks / total_impressions if total_impressions > 0 else 0
            
            if 'clicks' in group_data.columns and 'conversions' in group_data.columns:
                total_clicks = group_data['clicks'].sum()
                total_conversions = group_data['conversions'].sum()
                efficiency_metrics['overall_cvr'] = total_conversions / total_clicks if total_clicks > 0 else 0
            
            if 'cost' in group_data.columns and 'conversions' in group_data.columns:
                total_cost = group_data['cost'].sum()
                total_conversions = group_data['conversions'].sum()
                efficiency_metrics['overall_cpa'] = total_cost / total_conversions if total_conversions > 0 else float('inf')
            
            results[creative_type] = {
                'statistics': stats_dict,
                'efficiency': efficiency_metrics,
                'sample_size': len(group_data)
            }
        
        self.analysis_results = results
        return results
    
    def compare_creatives(self, df, creative_column='ad_format', metric='ctr'):
        """
        比较不同素材的效果
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
        metric : str
            比较指标
            
        Returns:
        --------
        dict
            比较结果
        """
        if metric not in df.columns:
            return {}
        
        # 按素材类型分组
        creative_groups = df.groupby(creative_column)[metric].apply(list).to_dict()
        
        # 进行统计检验
        comparison_results = {}
        creative_types = list(creative_groups.keys())
        
        # 如果只有两组，进行t检验
        if len(creative_types) == 2:
            group1 = creative_groups[creative_types[0]]
            group2 = creative_groups[creative_types[1]]
            
            t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
            
            comparison_results = {
                'test_type': 't-test',
                'groups': creative_types,
                'group1_mean': np.mean(group1),
                'group2_mean': np.mean(group2),
                't_statistic': t_stat,
                'p_value': p_value,
                'is_significant': p_value < 0.05,
                'effect_size': (np.mean(group2) - np.mean(group1)) / np.sqrt(
                    (np.std(group1)**2 + np.std(group2)**2) / 2
                ) if np.std(group1) > 0 or np.std(group2) > 0 else 0
            }
        
        # 如果多于两组，进行方差分析
        elif len(creative_types) > 2:
            groups = [creative_groups[ct] for ct in creative_types]
            f_stat, p_value = stats.f_oneway(*groups)
            
            comparison_results = {
                'test_type': 'ANOVA',
                'groups': creative_types,
                'group_means': {ct: np.mean(creative_groups[ct]) for ct in creative_types},
                'f_statistic': f_stat,
                'p_value': p_value,
                'is_significant': p_value < 0.05
            }
        
        return comparison_results
    
    def identify_top_performers(self, df, creative_column='ad_format', 
                               metric='ctr', top_n=3):
        """
        识别表现最好的素材
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
        metric : str
            评估指标
        top_n : int
            返回前N个表现最好的素材
            
        Returns:
        --------
        list
            表现最好的素材列表
        """
        if metric not in df.columns:
            return []
        
        # 计算每个素材的平均指标
        creative_performance = df.groupby(creative_column)[metric].mean()
        
        # 排序
        sorted_performance = creative_performance.sort_values(ascending=False)
        
        # 返回前N个
        top_performers = []
        for i, (creative_type, value) in enumerate(sorted_performance.head(top_n).items()):
            top_performers.append({
                'rank': i + 1,
                'creative_type': creative_type,
                'metric_value': value,
                'metric': metric
            })
        
        return top_performers
    
    def analyze_creative_trends(self, df, creative_column='ad_format', 
                               date_column='date', metric='ctr'):
        """
        分析素材效果趋势
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
        date_column : str
            日期列名
        metric : str
            分析指标
            
        Returns:
        --------
        dict
            趋势分析结果
        """
        if metric not in df.columns or date_column not in df.columns:
            return {}
        
        # 转换日期列
        df[date_column] = pd.to_datetime(df[date_column])
        
        # 按素材和日期分组
        trend_data = df.groupby([creative_column, date_column])[metric].mean().reset_index()
        
        # 计算趋势
        trends = {}
        for creative_type in df[creative_column].unique():
            creative_data = trend_data[trend_data[creative_column] == creative_type]
            
            if len(creative_data) > 1:
                # 计算线性趋势
                x = np.arange(len(creative_data))
                y = creative_data[metric].values
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                trends[creative_type] = {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                    'trend_strength': abs(r_value),
                    'data_points': len(creative_data)
                }
        
        return trends
    
    def generate_creative_recommendations(self, df, creative_column='ad_format'):
        """
        生成素材优化建议
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
            
        Returns:
        --------
        dict
            优化建议
        """
        recommendations = {}
        
        # 分析各素材效果
        performance = self.analyze_creative_performance(df, creative_column)
        
        # 计算整体平均值
        overall_ctr = df['clicks'].sum() / df['impressions'].sum() if 'impressions' in df.columns and 'clicks' in df.columns else 0
        overall_cvr = df['conversions'].sum() / df['clicks'].sum() if 'clicks' in df.columns and 'conversions' in df.columns else 0
        
        for creative_type, data in performance.items():
            efficiency = data.get('efficiency', {})
            ctr = efficiency.get('overall_ctr', 0)
            cvr = efficiency.get('overall_cvr', 0)
            
            # 生成建议
            creative_recommendations = []
            
            # CTR建议
            if ctr < overall_ctr * 0.8:
                creative_recommendations.append({
                    'metric': 'CTR',
                    'current_value': ctr,
                    'benchmark': overall_ctr,
                    'status': 'below_average',
                    'suggestion': '点击率低于平均水平，建议优化素材吸引力'
                })
            elif ctr > overall_ctr * 1.2:
                creative_recommendations.append({
                    'metric': 'CTR',
                    'current_value': ctr,
                    'benchmark': overall_ctr,
                    'status': 'above_average',
                    'suggestion': '点击率表现优秀，可考虑增加投放'
                })
            
            # CVR建议
            if cvr < overall_cvr * 0.8:
                creative_recommendations.append({
                    'metric': 'CVR',
                    'current_value': cvr,
                    'benchmark': overall_cvr,
                    'status': 'below_average',
                    'suggestion': '转化率低于平均水平，建议优化落地页或素材相关性'
                })
            elif cvr > overall_cvr * 1.2:
                creative_recommendations.append({
                    'metric': 'CVR',
                    'current_value': cvr,
                    'benchmark': overall_cvr,
                    'status': 'above_average',
                    'suggestion': '转化率表现优秀，可考虑增加预算'
                })
            
            recommendations[creative_type] = {
                'performance': data,
                'recommendations': creative_recommendations
            }
        
        return recommendations
    
    def generate_analysis_report(self, df, creative_column='ad_format'):
        """
        生成素材分析报告
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
            
        Returns:
        --------
        str
            分析报告
        """
        # 进行分析
        performance = self.analyze_creative_performance(df, creative_column)
        top_performers = self.identify_top_performers(df, creative_column, 'ctr', 3)
        recommendations = self.generate_creative_recommendations(df, creative_column)
        
        report = []
        report.append("=" * 60)
        report.append("素材效果分析报告")
        report.append("=" * 60)
        
        # 总体统计
        report.append(f"\n1. 总体统计:")
        report.append(f"   素材类型数量: {len(performance)}")
        report.append(f"   总记录数: {len(df):,}")
        
        # 各素材表现
        report.append(f"\n2. 各素材表现:")
        
        for creative_type, data in performance.items():
            efficiency = data.get('efficiency', {})
            report.append(f"\n   {creative_type}:")
            report.append(f"     样本量: {data['sample_size']:,}")
            report.append(f"     整体点击率: {efficiency.get('overall_ctr', 0):.2%}")
            report.append(f"     整体转化率: {efficiency.get('overall_cvr', 0):.2%}")
            
            # 关键指标统计
            if 'ctr' in data['statistics']:
                ctr_stats = data['statistics']['ctr']
                report.append(f"     点击率均值: {ctr_stats['mean']:.2%}")
                report.append(f"     点击率标准差: {ctr_stats['std']:.2%}")
        
        # 表现最好的素材
        report.append(f"\n3. 表现最好的素材 (按点击率):")
        for performer in top_performers:
            report.append(f"   {performer['rank']}. {performer['creative_type']}: {performer['metric_value']:.2%}")
        
        # 统计检验结果
        comparison = self.compare_creatives(df, creative_column, 'ctr')
        if comparison:
            report.append(f"\n4. 统计检验结果:")
            report.append(f"   检验类型: {comparison['test_type']}")
            report.append(f"   p值: {comparison['p_value']:.6f}")
            report.append(f"   统计显著: {'是' if comparison['is_significant'] else '否'}")
            
            if comparison['test_type'] == 'ANOVA':
                report.append(f"   各组均值:")
                for group, mean in comparison['group_means'].items():
                    report.append(f"     {group}: {mean:.2%}")
        
        # 优化建议
        report.append(f"\n5. 优化建议:")
        for creative_type, rec_data in recommendations.items():
            recs = rec_data['recommendations']
            if recs:
                report.append(f"\n   {creative_type}:")
                for rec in recs:
                    report.append(f"     - {rec['suggestion']}")
            else:
                report.append(f"\n   {creative_type}: 表现良好，无特别建议")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_analysis_report(self, df, creative_column='ad_format'):
        """
        打印素材分析报告
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        creative_column : str
            素材类型列名
        """
        report = self.generate_analysis_report(df, creative_column)
        print(report)

class CreativeFeatureAnalyzer:
    """素材特征分析器"""
    
    def __init__(self):
        """初始化素材特征分析器"""
        self.feature_importance = {}
        
    def analyze_feature_impact(self, df, feature_columns, target_metric='ctr'):
        """
        分析特征对效果的影响
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        feature_columns : list
            特征列名列表
        target_metric : str
            目标指标
            
        Returns:
        --------
        dict
            特征影响分析结果
        """
        if target_metric not in df.columns:
            return {}
        
        results = {}
        
        for feature in feature_columns:
            if feature not in df.columns:
                continue
            
            # 按特征分组分析
            feature_groups = df.groupby(feature)[target_metric].apply(list).to_dict()
            
            # 计算特征重要性
            if len(feature_groups) > 1:
                groups = [feature_groups[f] for f in feature_groups.keys()]
                f_stat, p_value = stats.f_oneway(*groups)
                
                # 计算效应大小 (eta-squared)
                grand_mean = df[target_metric].mean()
                ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
                ss_total = sum((x - grand_mean)**2 for group in groups for x in group)
                eta_squared = ss_between / ss_total if ss_total > 0 else 0
                
                results[feature] = {
                    'f_statistic': f_stat,
                    'p_value': p_value,
                    'is_significant': p_value < 0.05,
                    'eta_squared': eta_squared,
                    'effect_size': 'large' if eta_squared > 0.14 else 'medium' if eta_squared > 0.06 else 'small',
                    'group_means': {f: np.mean(feature_groups[f]) for f in feature_groups.keys()}
                }
        
        self.feature_importance = results
        return results
    
    def identify_optimal_features(self, df, feature_columns, target_metric='ctr'):
        """
        识别最优特征组合
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        feature_columns : list
            特征列名列表
        target_metric : str
            目标指标
            
        Returns:
        --------
        dict
            最优特征组合
        """
        if target_metric not in df.columns:
            return {}
        
        # 分析每个特征的影响
        feature_impact = self.analyze_feature_impact(df, feature_columns, target_metric)
        
        # 按效应大小排序
        sorted_features = sorted(
            feature_impact.items(),
            key=lambda x: x[1]['eta_squared'],
            reverse=True
        )
        
        # 识别最优特征值
        optimal_features = {}
        for feature, impact in sorted_features:
            if impact['is_significant']:
                # 找到效果最好的特征值
                group_means = impact['group_means']
                best_feature_value = max(group_means.items(), key=lambda x: x[1])
                
                optimal_features[feature] = {
                    'best_value': best_feature_value[0],
                    'best_performance': best_feature_value[1],
                    'impact_strength': impact['effect_size'],
                    'eta_squared': impact['eta_squared']
                }
        
        return optimal_features
    
    def generate_feature_report(self, df, feature_columns, target_metric='ctr'):
        """
        生成特征分析报告
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        feature_columns : list
            特征列名列表
        target_metric : str
            目标指标
            
        Returns:
        --------
        str
            特征分析报告
        """
        # 分析特征影响
        feature_impact = self.analyze_feature_impact(df, feature_columns, target_metric)
        
        # 识别最优特征
        optimal_features = self.identify_optimal_features(df, feature_columns, target_metric)
        
        report = []
        report.append("=" * 60)
        report.append("素材特征分析报告")
        report.append("=" * 60)
        
        report.append(f"\n1. 特征影响分析 (目标指标: {target_metric}):")
        
        # 按效应大小排序
        sorted_features = sorted(
            feature_impact.items(),
            key=lambda x: x[1]['eta_squared'],
            reverse=True
        )
        
        for i, (feature, impact) in enumerate(sorted_features):
            report.append(f"\n   {i+1}. {feature}:")
            report.append(f"      F统计量: {impact['f_statistic']:.4f}")
            report.append(f"      p值: {impact['p_value']:.6f}")
            report.append(f"      统计显著: {'是' if impact['is_significant'] else '否'}")
            report.append(f"      效应大小 (eta²): {impact['eta_squared']:.4f}")
            report.append(f"      效应强度: {impact['effect_size']}")
            
            # 显示各组均值
            report.append(f"      各组均值:")
            for group, mean in impact['group_means'].items():
                report.append(f"        {group}: {mean:.4f}")
        
        # 最优特征
        report.append(f"\n2. 最优特征组合:")
        
        if optimal_features:
            for feature, optimal in optimal_features.items():
                report.append(f"\n   {feature}:")
                report.append(f"      最优值: {optimal['best_value']}")
                report.append(f"      最优表现: {optimal['best_performance']:.4f}")
                report.append(f"      影响强度: {optimal['impact_strength']}")
                report.append(f"      效应大小: {optimal['eta_squared']:.4f}")
        else:
            report.append("   没有发现统计显著的特征影响")
        
        # 优化建议
        report.append(f"\n3. 优化建议:")
        
        if optimal_features:
            report.append("   基于分析结果，建议:")
            for feature, optimal in optimal_features.items():
                report.append(f"   - 优先使用 {feature} = {optimal['best_value']} 的素材")
        else:
            report.append("   - 各特征间效果差异不显著，建议测试更多素材组合")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_feature_report(self, df, feature_columns, target_metric='ctr'):
        """
        打印特征分析报告
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        feature_columns : list
            特征列名列表
        target_metric : str
            目标指标
        """
        report = self.generate_feature_report(df, feature_columns, target_metric)
        print(report)

# 便捷函数
def analyze_creative_performance(df, creative_column='ad_format', metrics=None):
    """
    分析素材效果的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        广告效果数据
    creative_column : str
        素材类型列名
    metrics : list, optional
        要分析的指标列表
        
    Returns:
    --------
    dict
        分析结果
    """
    analyzer = CreativeAnalyzer()
    return analyzer.analyze_creative_performance(df, creative_column, metrics)

def identify_top_creatives(df, creative_column='ad_format', metric='ctr', top_n=3):
    """
    识别表现最好的素材的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        广告效果数据
    creative_column : str
        素材类型列名
    metric : str
        评估指标
    top_n : int
        返回前N个表现最好的素材
        
    Returns:
    --------
    list
        表现最好的素材列表
    """
    analyzer = CreativeAnalyzer()
    return analyzer.identify_top_performers(df, creative_column, metric, top_n)

if __name__ == "__main__":
    # 测试素材效果分析
    print("测试素材效果分析...")
    
    # 创建模拟数据
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'ad_format': np.random.choice(['图片', '视频', '信息流', '横幅'], n_samples),
        'placement': np.random.choice(['首页', '侧边栏', '底部'], n_samples),
        'impressions': np.random.randint(100, 1000, n_samples),
        'clicks': np.random.randint(5, 50, n_samples),
        'conversions': np.random.randint(0, 10, n_samples),
        'cost': np.random.uniform(10, 100, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # 计算衍生指标
    df['ctr'] = df['clicks'] / df['impressions']
    df['cvr'] = df['conversions'] / df['clicks']
    df['cpc'] = df['cost'] / df['clicks']
    df['cpa'] = df['cost'] / df['conversions']
    
    print(f"数据形状: {df.shape}")
    print(f"素材类型: {df['ad_format'].unique()}")
    
    # 测试素材效果分析
    print("\n1. 素材效果分析:")
    analyzer = CreativeAnalyzer()
    performance = analyzer.analyze_creative_performance(df, 'ad_format')
    
    for creative_type, data in performance.items():
        efficiency = data.get('efficiency', {})
        print(f"\n{creative_type}:")
        print(f"  样本量: {data['sample_size']}")
        print(f"  整体点击率: {efficiency.get('overall_ctr', 0):.2%}")
        print(f"  整体转化率: {efficiency.get('overall_cvr', 0):.2%}")
    
    # 测试素材比较
    print("\n2. 素材比较:")
    comparison = analyzer.compare_creatives(df, 'ad_format', 'ctr')
    print(f"检验类型: {comparison.get('test_type', 'N/A')}")
    print(f"p值: {comparison.get('p_value', 'N/A'):.6f}")
    print(f"统计显著: {comparison.get('is_significant', False)}")
    
    # 测试识别表现最好的素材
    print("\n3. 表现最好的素材:")
    top_performers = analyzer.identify_top_performers(df, 'ad_format', 'ctr', 3)
    for performer in top_performers:
        print(f"  {performer['rank']}. {performer['creative_type']}: {performer['metric_value']:.2%}")
    
    # 测试特征分析
    print("\n4. 特征分析:")
    feature_analyzer = CreativeFeatureAnalyzer()
    feature_columns = ['ad_format', 'placement']
    feature_impact = feature_analyzer.analyze_feature_impact(df, feature_columns, 'ctr')
    
    for feature, impact in feature_impact.items():
        print(f"\n{feature}:")
        print(f"  F统计量: {impact['f_statistic']:.4f}")
        print(f"  p值: {impact['p_value']:.6f}")
        print(f"  效应大小: {impact['effect_size']}")