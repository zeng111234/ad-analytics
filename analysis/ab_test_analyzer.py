"""
A/B测试分析工具
用于分析广告A/B测试结果，提供统计显著性检验和优化建议
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

class ABTestAnalyzer:
    """A/B测试分析器"""
    
    def __init__(self, alpha=0.05):
        """
        初始化A/B测试分析器
        
        Parameters:
        -----------
        alpha : float
            显著性水平（默认0.05）
        """
        self.alpha = alpha
        self.results = {}
        
    def analyze_proportions(self, control_successes, control_total, 
                           treatment_successes, treatment_total):
        """
        分析比例型指标（如点击率、转化率）
        
        Parameters:
        -----------
        control_successes : int
            对照组成功次数
        control_total : int
            对照组总数
        treatment_successes : int
            实验组成功次数
        treatment_total : int
            实验组总数
            
        Returns:
        --------
        dict
            分析结果
        """
        # 计算比例
        control_rate = control_successes / control_total if control_total > 0 else 0
        treatment_rate = treatment_successes / treatment_total if treatment_total > 0 else 0
        
        # 计算相对提升
        relative_lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else float('inf')
        
        # 卡方检验
        contingency_table = np.array([
            [control_successes, control_total - control_successes],
            [treatment_successes, treatment_total - treatment_successes]
        ])
        
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # 计算置信区间
        se = np.sqrt(
            (control_rate * (1 - control_rate) / control_total) +
            (treatment_rate * (1 - treatment_rate) / treatment_total)
        )
        
        z_score = stats.norm.ppf(1 - self.alpha / 2)
        ci_lower = (treatment_rate - control_rate) - z_score * se
        ci_upper = (treatment_rate - control_rate) + z_score * se
        
        # 判断是否显著
        is_significant = p_value < self.alpha
        
        result = {
            'control_rate': control_rate,
            'treatment_rate': treatment_rate,
            'absolute_difference': treatment_rate - control_rate,
            'relative_lift': relative_lift,
            'p_value': p_value,
            'chi2_statistic': chi2,
            'confidence_interval': (ci_lower, ci_upper),
            'is_significant': is_significant,
            'alpha': self.alpha,
            'sample_sizes': {
                'control': control_total,
                'treatment': treatment_total
            }
        }
        
        self.results['proportions'] = result
        return result
    
    def analyze_means(self, control_data, treatment_data):
        """
        分析均值型指标（如成本、展示量）
        
        Parameters:
        -----------
        control_data : array-like
            对照组数据
        treatment_data : array-like
            实验组数据
            
        Returns:
        --------
        dict
            分析结果
        """
        control_data = np.array(control_data)
        treatment_data = np.array(treatment_data)
        
        # 计算基本统计量
        control_mean = np.mean(control_data)
        treatment_mean = np.mean(treatment_data)
        control_std = np.std(control_data, ddof=1)
        treatment_std = np.std(treatment_data, ddof=1)
        
        # 计算相对提升
        relative_lift = (treatment_mean - control_mean) / control_mean if control_mean != 0 else float('inf')
        
        # t检验
        t_stat, p_value = ttest_ind(control_data, treatment_data, equal_var=False)
        
        # Mann-Whitney U检验（非参数检验）
        u_stat, u_p_value = mannwhitneyu(control_data, treatment_data, alternative='two-sided')
        
        # 计算效应量（Cohen's d）
        pooled_std = np.sqrt(
            ((len(control_data) - 1) * control_std**2 + 
             (len(treatment_data) - 1) * treatment_std**2) /
            (len(control_data) + len(treatment_data) - 2)
        )
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std != 0 else 0
        
        # 计算置信区间
        se = np.sqrt(
            (control_std**2 / len(control_data)) +
            (treatment_std**2 / len(treatment_data))
        )
        
        df = len(control_data) + len(treatment_data) - 2
        t_critical = stats.t.ppf(1 - self.alpha / 2, df)
        
        ci_lower = (treatment_mean - control_mean) - t_critical * se
        ci_upper = (treatment_mean - control_mean) + t_critical * se
        
        # 判断是否显著
        is_significant = p_value < self.alpha
        
        result = {
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'control_std': control_std,
            'treatment_std': treatment_std,
            'absolute_difference': treatment_mean - control_mean,
            'relative_lift': relative_lift,
            't_statistic': t_stat,
            'p_value': p_value,
            'u_statistic': u_stat,
            'u_p_value': u_p_value,
            'cohens_d': cohens_d,
            'confidence_interval': (ci_lower, ci_upper),
            'is_significant': is_significant,
            'alpha': self.alpha,
            'sample_sizes': {
                'control': len(control_data),
                'treatment': len(treatment_data)
            }
        }
        
        self.results['means'] = result
        return result
    
    def calculate_sample_size(self, baseline_rate, mde, alpha=None, power=0.8):
        """
        计算所需样本量
        
        Parameters:
        -----------
        baseline_rate : float
            基线比例（如当前点击率）
        mde : float
            最小可检测效应（相对提升）
        alpha : float, optional
            显著性水平
        power : float
            统计功效（1-β）
            
        Returns:
        --------
        dict
            样本量计算结果
        """
        if alpha is None:
            alpha = self.alpha
        
        # 计算效应大小
        effect_size = baseline_rate * mde
        
        # 使用公式计算样本量
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        p1 = baseline_rate
        p2 = baseline_rate + effect_size
        p_avg = (p1 + p2) / 2
        
        n = (
            (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + 
             z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 /
            (effect_size ** 2)
        )
        
        n_per_group = int(np.ceil(n))
        
        result = {
            'baseline_rate': baseline_rate,
            'minimum_detectable_effect': mde,
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'sample_size_per_group': n_per_group,
            'total_sample_size': 2 * n_per_group,
            'estimated_duration_days': None  # 需要根据日流量计算
        }
        
        self.results['sample_size'] = result
        return result
    
    def calculate_test_duration(self, daily_traffic, sample_size_per_group):
        """
        计算测试所需天数
        
        Parameters:
        -----------
        daily_traffic : int
            每日总流量
        sample_size_per_group : int
            每组所需样本量
            
        Returns:
        --------
        int
            所需天数
        """
        total_sample_needed = 2 * sample_size_per_group
        days_needed = int(np.ceil(total_sample_needed / daily_traffic))
        
        return days_needed
    
    def generate_report(self, test_type='proportions'):
        """
        生成测试报告
        
        Parameters:
        -----------
        test_type : str
            测试类型 ('proportions' 或 'means')
            
        Returns:
        --------
        str
            测试报告
        """
        if test_type not in self.results:
            return "没有可用的测试结果"
        
        result = self.results[test_type]
        
        report = []
        report.append("=" * 60)
        report.append("A/B测试分析报告")
        report.append("=" * 60)
        
        if test_type == 'proportions':
            report.append("\n1. 基本统计:")
            report.append(f"   对照组比例: {result['control_rate']:.4f} ({result['control_rate']:.2%})")
            report.append(f"   实验组比例: {result['treatment_rate']:.4f} ({result['treatment_rate']:.2%})")
            report.append(f"   绝对差异: {result['absolute_difference']:.4f}")
            report.append(f"   相对提升: {result['relative_lift']:.2%}")
            
            report.append("\n2. 统计检验:")
            report.append(f"   卡方统计量: {result['chi2_statistic']:.4f}")
            report.append(f"   p值: {result['p_value']:.6f}")
            report.append(f"   显著性水平: {result['alpha']}")
            
            ci = result['confidence_interval']
            report.append(f"   95%置信区间: [{ci[0]:.4f}, {ci[1]:.4f}]")
            
            report.append("\n3. 结论:")
            if result['is_significant']:
                report.append("   ✓ 结果统计显著")
                if result['relative_lift'] > 0:
                    report.append("   ✓ 实验组表现优于对照组")
                else:
                    report.append("   ✗ 实验组表现不如对照组")
            else:
                report.append("   ✗ 结果统计不显著")
                report.append("   建议: 增加样本量或延长测试时间")
            
        elif test_type == 'means':
            report.append("\n1. 基本统计:")
            report.append(f"   对照组均值: {result['control_mean']:.4f}")
            report.append(f"   实验组均值: {result['treatment_mean']:.4f}")
            report.append(f"   对照组标准差: {result['control_std']:.4f}")
            report.append(f"   实验组标准差: {result['treatment_std']:.4f}")
            report.append(f"   绝对差异: {result['absolute_difference']:.4f}")
            report.append(f"   相对提升: {result['relative_lift']:.2%}")
            
            report.append("\n2. 统计检验:")
            report.append(f"   t统计量: {result['t_statistic']:.4f}")
            report.append(f"   p值: {result['p_value']:.6f}")
            report.append(f"   U统计量: {result['u_statistic']:.4f}")
            report.append(f"   U检验p值: {result['u_p_value']:.6f}")
            report.append(f"   效应量 (Cohen's d): {result['cohens_d']:.4f}")
            
            ci = result['confidence_interval']
            report.append(f"   95%置信区间: [{ci[0]:.4f}, {ci[1]:.4f}]")
            
            report.append("\n3. 效应量解释:")
            d = abs(result['cohens_d'])
            if d < 0.2:
                report.append("   效应量: 小")
            elif d < 0.5:
                report.append("   效应量: 中等")
            elif d < 0.8:
                report.append("   效应量: 大")
            else:
                report.append("   效应量: 非常大")
            
            report.append("\n4. 结论:")
            if result['is_significant']:
                report.append("   ✓ 结果统计显著")
                if result['relative_lift'] > 0:
                    report.append("   ✓ 实验组表现优于对照组")
                else:
                    report.append("   ✗ 实验组表现不如对照组")
            else:
                report.append("   ✗ 结果统计不显著")
                report.append("   建议: 增加样本量或延长测试时间")
        
        # 样本量信息
        sample_sizes = result['sample_sizes']
        report.append("\n5. 样本量:")
        report.append(f"   对照组: {sample_sizes['control']:,}")
        report.append(f"   实验组: {sample_sizes['treatment']:,}")
        report.append(f"   总样本量: {sum(sample_sizes.values()):,}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_report(self, test_type='proportions'):
        """
        打印测试报告
        
        Parameters:
        -----------
        test_type : str
            测试类型
        """
        report = self.generate_report(test_type)
        print(report)

class ABTestDesigner:
    """A/B测试设计器"""
    
    def __init__(self):
        """初始化A/B测试设计器"""
        self.test_plans = []
        
    def design_test(self, metric_type, baseline_value, expected_lift, 
                   daily_traffic=None, confidence_level=0.95, power=0.8):
        """
        设计A/B测试
        
        Parameters:
        -----------
        metric_type : str
            指标类型 ('conversion_rate', 'click_rate', 'mean_value')
        baseline_value : float
            基线值
        expected_lift : float
            预期提升（相对值）
        daily_traffic : int, optional
            每日流量
        confidence_level : float
            置信水平
        power : float
            统计功效
            
        Returns:
        --------
        dict
            测试设计方案
        """
        alpha = 1 - confidence_level
        
        if metric_type in ['conversion_rate', 'click_rate']:
            # 比例型指标
            analyzer = ABTestAnalyzer(alpha=alpha)
            sample_size_result = analyzer.calculate_sample_size(
                baseline_value, expected_lift, alpha=alpha, power=power
            )
            
            test_plan = {
                'metric_type': metric_type,
                'baseline_value': baseline_value,
                'expected_lift': expected_lift,
                'expected_treatment_value': baseline_value * (1 + expected_lift),
                'confidence_level': confidence_level,
                'power': power,
                'alpha': alpha,
                'sample_size_per_group': sample_size_result['sample_size_per_group'],
                'total_sample_size': sample_size_result['total_sample_size'],
                'daily_traffic': daily_traffic,
                'estimated_duration_days': None
            }
            
            # 计算测试时长
            if daily_traffic:
                test_plan['estimated_duration_days'] = analyzer.calculate_test_duration(
                    daily_traffic, sample_size_result['sample_size_per_group']
                )
            
        else:
            # 均值型指标（简化处理）
            # 假设标准差为基线值的20%
            std_dev = baseline_value * 0.2
            
            # 计算样本量
            effect_size = baseline_value * expected_lift
            z_alpha = stats.norm.ppf(1 - alpha / 2)
            z_beta = stats.norm.ppf(power)
            
            n = (
                (z_alpha + z_beta) ** 2 * 2 * std_dev ** 2 /
                effect_size ** 2
            )
            
            sample_size_per_group = int(np.ceil(n))
            
            test_plan = {
                'metric_type': metric_type,
                'baseline_value': baseline_value,
                'expected_lift': expected_lift,
                'expected_treatment_value': baseline_value * (1 + expected_lift),
                'confidence_level': confidence_level,
                'power': power,
                'alpha': alpha,
                'sample_size_per_group': sample_size_per_group,
                'total_sample_size': 2 * sample_size_per_group,
                'daily_traffic': daily_traffic,
                'estimated_duration_days': None,
                'assumed_std_dev': std_dev
            }
            
            # 计算测试时长
            if daily_traffic:
                test_plan['estimated_duration_days'] = int(np.ceil(
                    2 * sample_size_per_group / daily_traffic
                ))
        
        self.test_plans.append(test_plan)
        return test_plan
    
    def generate_test_plan_report(self, test_plan):
        """
        生成测试计划报告
        
        Parameters:
        -----------
        test_plan : dict
            测试计划
            
        Returns:
        --------
        str
            测试计划报告
        """
        report = []
        report.append("=" * 60)
        report.append("A/B测试设计方案")
        report.append("=" * 60)
        
        report.append("\n1. 测试目标:")
        report.append(f"   指标类型: {test_plan['metric_type']}")
        report.append(f"   基线值: {test_plan['baseline_value']:.4f}")
        report.append(f"   预期提升: {test_plan['expected_lift']:.2%}")
        report.append(f"   预期实验组值: {test_plan['expected_treatment_value']:.4f}")
        
        report.append("\n2. 统计参数:")
        report.append(f"   置信水平: {test_plan['confidence_level']:.2%}")
        report.append(f"   统计功效: {test_plan['power']:.2%}")
        report.append(f"   显著性水平: {test_plan['alpha']:.4f}")
        
        report.append("\n3. 样本量要求:")
        report.append(f"   每组样本量: {test_plan['sample_size_per_group']:,}")
        report.append(f"   总样本量: {test_plan['total_sample_size']:,}")
        
        if test_plan['daily_traffic']:
            report.append(f"   每日流量: {test_plan['daily_traffic']:,}")
            if test_plan['estimated_duration_days']:
                report.append(f"   预计测试天数: {test_plan['estimated_duration_days']} 天")
        
        report.append("\n4. 测试建议:")
        report.append("   - 确保随机分配用户到对照组和实验组")
        report.append("   - 避免在测试期间改变其他变量")
        report.append("   - 监控测试过程中的数据质量")
        report.append("   - 提前确定测试停止规则")
        
        if test_plan['estimated_duration_days'] and test_plan['estimated_duration_days'] > 30:
            report.append("\n5. 注意事项:")
            report.append("   ⚠ 测试时间较长，建议:")
            report.append("     - 考虑增加每日流量")
            report.append("     - 或者接受更大的最小可检测效应")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_test_plan_report(self, test_plan):
        """
        打印测试计划报告
        
        Parameters:
        -----------
        test_plan : dict
            测试计划
        """
        report = self.generate_test_plan_report(test_plan)
        print(report)

# 便捷函数
def analyze_ab_test(control_data, treatment_data, test_type='proportions', alpha=0.05):
    """
    分析A/B测试的便捷函数
    
    Parameters:
    -----------
    control_data : tuple or array-like
        对照组数据。如果是比例型，格式为 (成功次数, 总次数)
        如果是均值型，直接传入数据数组
    treatment_data : tuple or array-like
        实验组数据
    test_type : str
        测试类型 ('proportions' 或 'means')
    alpha : float
        显著性水平
        
    Returns:
    --------
    dict
        分析结果
    """
    analyzer = ABTestAnalyzer(alpha=alpha)
    
    if test_type == 'proportions':
        control_successes, control_total = control_data
        treatment_successes, treatment_total = treatment_data
        return analyzer.analyze_proportions(
            control_successes, control_total,
            treatment_successes, treatment_total
        )
    else:
        return analyzer.analyze_means(control_data, treatment_data)

def design_ab_test(metric_type, baseline_value, expected_lift, 
                  daily_traffic=None, confidence_level=0.95, power=0.8):
    """
    设计A/B测试的便捷函数
    
    Parameters:
    -----------
    metric_type : str
        指标类型
    baseline_value : float
        基线值
    expected_lift : float
        预期提升
    daily_traffic : int, optional
        每日流量
    confidence_level : float
        置信水平
    power : float
        统计功效
        
    Returns:
    --------
    dict
        测试设计方案
    """
    designer = ABTestDesigner()
    return designer.design_test(
        metric_type, baseline_value, expected_lift,
        daily_traffic, confidence_level, power
    )

if __name__ == "__main__":
    # 测试A/B测试分析
    print("测试A/B测试分析...")
    
    # 测试比例型指标
    print("\n1. 测试比例型指标（点击率）:")
    analyzer = ABTestAnalyzer(alpha=0.05)
    
    # 模拟数据：对照组点击率2%，实验组点击率2.5%
    control_successes = 200  # 对照组点击次数
    control_total = 10000   # 对照组展示次数
    treatment_successes = 250  # 实验组点击次数
    treatment_total = 10000    # 实验组展示次数
    
    result = analyzer.analyze_proportions(
        control_successes, control_total,
        treatment_successes, treatment_total
    )
    
    analyzer.print_report('proportions')
    
    # 测试均值型指标
    print("\n2. 测试均值型指标（成本）:")
    
    # 模拟数据
    np.random.seed(42)
    control_costs = np.random.normal(100, 20, 1000)  # 对照组成本
    treatment_costs = np.random.normal(95, 20, 1000)   # 实验组成本
    
    result = analyzer.analyze_means(control_costs, treatment_costs)
    analyzer.print_report('means')
    
    # 测试样本量计算
    print("\n3. 测试样本量计算:")
    sample_size_result = analyzer.calculate_sample_size(
        baseline_rate=0.02,  # 2%点击率
        mde=0.25,            # 25%相对提升
        alpha=0.05,
        power=0.8
    )
    
    print(f"每组所需样本量: {sample_size_result['sample_size_per_group']:,}")
    print(f"总样本量: {sample_size_result['total_sample_size']:,}")
    
    # 测试A/B测试设计
    print("\n4. 测试A/B测试设计:")
    designer = ABTestDesigner()
    test_plan = designer.design_test(
        metric_type='click_rate',
        baseline_value=0.02,
        expected_lift=0.25,
        daily_traffic=5000,
        confidence_level=0.95,
        power=0.8
    )
    
    designer.print_test_plan_report(test_plan)