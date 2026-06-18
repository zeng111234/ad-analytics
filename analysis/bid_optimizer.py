"""
出价优化建议模块
基于广告效果数据提供智能出价调整建议
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class BidOptimizer:
    """出价优化器"""
    
    def __init__(self, budget_constraint=None, target_metric='conversions'):
        """
        初始化出价优化器
        
        Parameters:
        -----------
        budget_constraint : float, optional
            预算约束
        target_metric : str
            优化目标指标 ('conversions', 'clicks', 'impressions')
        """
        self.budget_constraint = budget_constraint
        self.target_metric = target_metric
        self.optimization_results = {}
        
    def calculate_bid_suggestions(self, df, current_bids, 
                                 performance_data=None):
        """
        计算出价建议
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        current_bids : dict
            当前出价 {ad_group_id: bid_amount}
        performance_data : dict, optional
            历史表现数据
            
        Returns:
        --------
        dict
            出价建议
        """
        suggestions = {}
        
        for ad_group_id, current_bid in current_bids.items():
            # 获取该广告组的历史数据
            if ad_group_id in df.index:
                group_data = df.loc[ad_group_id]
            else:
                # 如果没有历史数据，使用默认建议
                suggestions[ad_group_id] = {
                    'current_bid': current_bid,
                    'suggested_bid': current_bid,
                    'adjustment': 0,
                    'adjustment_percent': 0,
                    'reason': '无历史数据，保持当前出价',
                    'confidence': 'low'
                }
                continue
            
            # 计算关键指标
            impressions = group_data.get('impressions', 0)
            clicks = group_data.get('clicks', 0)
            conversions = group_data.get('conversions', 0)
            cost = group_data.get('cost', 0)
            
            ctr = clicks / impressions if impressions > 0 else 0
            cvr = conversions / clicks if clicks > 0 else 0
            cpc = cost / clicks if clicks > 0 else 0
            cpa = cost / conversions if conversions > 0 else float('inf')
            
            # 基于表现计算建议出价
            suggested_bid, reason, confidence = self._calculate_suggested_bid(
                current_bid, ctr, cvr, cpc, cpa, 
                impressions, clicks, conversions, cost
            )
            
            # 计算调整幅度
            adjustment = suggested_bid - current_bid
            adjustment_percent = (adjustment / current_bid) * 100 if current_bid > 0 else 0
            
            suggestions[ad_group_id] = {
                'current_bid': current_bid,
                'suggested_bid': suggested_bid,
                'adjustment': adjustment,
                'adjustment_percent': adjustment_percent,
                'reason': reason,
                'confidence': confidence,
                'metrics': {
                    'ctr': ctr,
                    'cvr': cvr,
                    'cpc': cpc,
                    'cpa': cpa,
                    'impressions': impressions,
                    'clicks': clicks,
                    'conversions': conversions,
                    'cost': cost
                }
            }
        
        self.optimization_results = suggestions
        return suggestions
    
    def _calculate_suggested_bid(self, current_bid, ctr, cvr, cpc, cpa,
                                impressions, clicks, conversions, cost):
        """
        计算建议出价
        
        Parameters:
        -----------
        current_bid : float
            当前出价
        ctr : float
            点击率
        cvr : float
            转化率
        cpc : float
            每次点击成本
        cpa : float
            每次转化成本
        impressions : int
            展示量
        clicks : int
            点击量
        conversions : int
            转化量
        cost : float
            成本
            
        Returns:
        --------
        tuple
            (suggested_bid, reason, confidence)
        """
        # 初始化
        suggested_bid = current_bid
        reason = "保持当前出价"
        confidence = "medium"
        
        # 规则1: 如果点击率高但转化率低，可能需要降低出价
        if ctr > 0.03 and cvr < 0.01:  # 高点击率，低转化率
            suggested_bid = current_bid * 0.9
            reason = "点击率高但转化率低，建议降低出价"
            confidence = "medium"
        
        # 规则2: 如果转化率高但展示量低，可能需要提高出价
        elif cvr > 0.05 and impressions < 1000:
            suggested_bid = current_bid * 1.2
            reason = "转化率高但展示量低，建议提高出价"
            confidence = "high"
        
        # 规则3: 如果CPA过高，降低出价
        elif cpa > 100:  # 假设CPA阈值为100
            suggested_bid = current_bid * 0.8
            reason = "每次转化成本过高，建议降低出价"
            confidence = "high"
        
        # 规则4: 如果CPC过高，降低出价
        elif cpc > 5:  # 假设CPC阈值为5
            suggested_bid = current_bid * 0.85
            reason = "每次点击成本过高，建议降低出价"
            confidence = "medium"
        
        # 规则5: 如果效果良好且预算充足，可以提高出价
        elif cvr > 0.03 and cpa < 50:
            suggested_bid = current_bid * 1.1
            reason = "效果良好，建议适当提高出价"
            confidence = "high"
        
        # 规则6: 如果展示量很低，可能需要提高出价
        elif impressions < 500:
            suggested_bid = current_bid * 1.15
            reason = "展示量过低，建议提高出价"
            confidence = "medium"
        
        # 确保出价在合理范围内
        suggested_bid = max(0.1, min(suggested_bid, current_bid * 2))
        
        return suggested_bid, reason, confidence
    
    def optimize_budget_allocation(self, df, total_budget, 
                                  min_budget_per_group=100):
        """
        优化预算分配
        
        Parameters:
        -----------
        df : pandas.DataFrame
            广告效果数据
        total_budget : float
            总预算
        min_budget_per_group : float
            每个广告组最小预算
            
        Returns:
        --------
        dict
            预算分配建议
        """
        if df.empty:
            return {}
        
        # 计算每个广告组的效率得分
        efficiency_scores = {}
        
        for idx, row in df.iterrows():
            impressions = row.get('impressions', 0)
            clicks = row.get('clicks', 0)
            conversions = row.get('conversions', 0)
            cost = row.get('cost', 0)
            
            # 计算效率指标
            ctr = clicks / impressions if impressions > 0 else 0
            cvr = conversions / clicks if clicks > 0 else 0
            cpa = cost / conversions if conversions > 0 else float('inf')
            
            # 计算综合效率得分 (0-100)
            # 权重: CTR 30%, CVR 40%, CPA 30%
            ctr_score = min(ctr * 1000, 100)  # CTR标准化
            cvr_score = min(cvr * 1000, 100)  # CVR标准化
            cpa_score = max(0, 100 - cpa) if cpa != float('inf') else 0  # CPA标准化
            
            efficiency_score = (ctr_score * 0.3 + 
                              cvr_score * 0.4 + 
                              cpa_score * 0.3)
            
            efficiency_scores[idx] = {
                'efficiency_score': efficiency_score,
                'ctr': ctr,
                'cvr': cvr,
                'cpa': cpa,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'cost': cost
            }
        
        # 按效率得分排序
        sorted_groups = sorted(efficiency_scores.items(), 
                              key=lambda x: x[1]['efficiency_score'], 
                              reverse=True)
        
        # 分配预算
        budget_allocation = {}
        remaining_budget = total_budget
        allocated_groups = 0
        
        # 首先确保每个广告组有最小预算
        for group_id, metrics in sorted_groups:
            if remaining_budget >= min_budget_per_group:
                budget_allocation[group_id] = {
                    'allocated_budget': min_budget_per_group,
                    'efficiency_score': metrics['efficiency_score'],
                    'metrics': metrics
                }
                remaining_budget -= min_budget_per_group
                allocated_groups += 1
            else:
                break
        
        # 将剩余预算按效率得分分配
        if remaining_budget > 0 and allocated_groups > 0:
            # 计算总效率得分
            total_efficiency = sum(
                budget_allocation[group_id]['efficiency_score'] 
                for group_id in budget_allocation
            )
            
            # 按比例分配剩余预算
            for group_id in budget_allocation:
                efficiency = budget_allocation[group_id]['efficiency_score']
                proportion = efficiency / total_efficiency if total_efficiency > 0 else 1 / allocated_groups
                additional_budget = remaining_budget * proportion
                
                budget_allocation[group_id]['allocated_budget'] += additional_budget
                budget_allocation[group_id]['budget_proportion'] = (
                    budget_allocation[group_id]['allocated_budget'] / total_budget
                )
        
        return budget_allocation
    
    def generate_bid_optimization_report(self):
        """
        生成出价优化报告
        
        Returns:
        --------
        str
            优化报告
        """
        if not self.optimization_results:
            return "没有可用的优化结果"
        
        report = []
        report.append("=" * 60)
        report.append("出价优化建议报告")
        report.append("=" * 60)
        
        # 统计调整建议
        total_groups = len(self.optimization_results)
        increase_count = sum(1 for r in self.optimization_results.values() 
                           if r['adjustment'] > 0)
        decrease_count = sum(1 for r in self.optimization_results.values() 
                           if r['adjustment'] < 0)
        maintain_count = sum(1 for r in self.optimization_results.values() 
                           if r['adjustment'] == 0)
        
        report.append(f"\n1. 总体统计:")
        report.append(f"   广告组总数: {total_groups}")
        report.append(f"   建议提高出价: {increase_count} 个")
        report.append(f"   建议降低出价: {decrease_count} 个")
        report.append(f"   建议保持出价: {maintain_count} 个")
        
        # 显示具体建议
        report.append(f"\n2. 具体建议:")
        
        # 按调整幅度排序
        sorted_results = sorted(
            self.optimization_results.items(),
            key=lambda x: abs(x[1]['adjustment_percent']),
            reverse=True
        )
        
        for i, (group_id, result) in enumerate(sorted_results[:10]):  # 只显示前10个
            report.append(f"\n   {i+1}. 广告组 {group_id}:")
            report.append(f"      当前出价: {result['current_bid']:.2f}")
            report.append(f"      建议出价: {result['suggested_bid']:.2f}")
            report.append(f"      调整幅度: {result['adjustment_percent']:+.1f}%")
            report.append(f"      调整原因: {result['reason']}")
            report.append(f"      置信度: {result['confidence']}")
            
            # 显示关键指标
            metrics = result['metrics']
            report.append(f"      关键指标:")
            report.append(f"        点击率: {metrics['ctr']:.2%}")
            report.append(f"        转化率: {metrics['cvr']:.2%}")
            report.append(f"        每次点击成本: {metrics['cpc']:.2f}")
            report.append(f"        每次转化成本: {metrics['cpa']:.2f}")
        
        # 优化建议
        report.append(f"\n3. 优化建议:")
        
        if decrease_count > increase_count:
            report.append("   - 整体建议降低出价，可能预算使用效率不高")
            report.append("   - 重点关注转化率低的广告组")
        elif increase_count > decrease_count:
            report.append("   - 整体建议提高出价，可能有提升空间")
            report.append("   - 重点关注展示量低的广告组")
        else:
            report.append("   - 出价策略相对平衡")
            report.append("   - 建议关注高CPA的广告组")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_bid_optimization_report(self):
        """
        打印出价优化报告
        """
        report = self.generate_bid_optimization_report()
        print(report)

class BidSimulator:
    """出价模拟器"""
    
    def __init__(self, historical_data):
        """
        初始化出价模拟器
        
        Parameters:
        -----------
        historical_data : pandas.DataFrame
            历史广告效果数据
        """
        self.historical_data = historical_data
        self.simulation_results = {}
        
    def simulate_bid_change(self, ad_group_id, current_bid, new_bid, 
                           days=30):
        """
        模拟出价变化的效果
        
        Parameters:
        -----------
        ad_group_id : str
            广告组ID
        current_bid : float
            当前出价
        new_bid : float
            新出价
        days : int
            模拟天数
            
        Returns:
        --------
        dict
            模拟结果
        """
        # 获取历史数据
        if ad_group_id in self.historical_data.index:
            group_data = self.historical_data.loc[ad_group_id]
        else:
            # 使用平均数据
            group_data = self.historical_data.mean()
        
        # 计算历史平均指标
        avg_impressions = group_data.get('impressions', 0)
        avg_clicks = group_data.get('clicks', 0)
        avg_conversions = group_data.get('conversions', 0)
        avg_cost = group_data.get('cost', 0)
        
        # 计算出价变化比例
        bid_change_ratio = new_bid / current_bid if current_bid > 0 else 1
        
        # 模拟展示量变化（假设出价与展示量正相关）
        # 使用弹性系数0.5（出价提高10%，展示量提高5%）
        elasticity = 0.5
        impression_change = 1 + (bid_change_ratio - 1) * elasticity
        
        # 模拟点击率变化（假设出价对点击率影响较小）
        ctr_change = 1  # 假设点击率不变
        
        # 模拟转化率变化（假设出价对转化率影响较小）
        cvr_change = 1  # 假设转化率不变
        
        # 计算模拟指标
        simulated_impressions = avg_impressions * impression_change * days
        simulated_clicks = avg_clicks * impression_change * ctr_change * days
        simulated_conversions = avg_conversions * impression_change * ctr_change * cvr_change * days
        simulated_cost = simulated_clicks * new_bid
        
        # 计算效率指标
        simulated_ctr = simulated_clicks / simulated_impressions if simulated_impressions > 0 else 0
        simulated_cvr = simulated_conversions / simulated_clicks if simulated_clicks > 0 else 0
        simulated_cpc = simulated_cost / simulated_clicks if simulated_clicks > 0 else 0
        simulated_cpa = simulated_cost / simulated_conversions if simulated_conversions > 0 else float('inf')
        
        # 计算变化百分比
        impression_change_pct = (impression_change - 1) * 100
        click_change_pct = (impression_change * ctr_change - 1) * 100
        conversion_change_pct = (impression_change * ctr_change * cvr_change - 1) * 100
        cost_change_pct = (bid_change_ratio * impression_change * ctr_change - 1) * 100
        
        result = {
            'ad_group_id': ad_group_id,
            'current_bid': current_bid,
            'new_bid': new_bid,
            'bid_change_ratio': bid_change_ratio,
            'simulation_days': days,
            'current_metrics': {
                'impressions': avg_impressions * days,
                'clicks': avg_clicks * days,
                'conversions': avg_conversions * days,
                'cost': avg_cost * days,
                'ctr': avg_clicks / avg_impressions if avg_impressions > 0 else 0,
                'cvr': avg_conversions / avg_clicks if avg_clicks > 0 else 0,
                'cpc': avg_cost / avg_clicks if avg_clicks > 0 else 0,
                'cpa': avg_cost / avg_conversions if avg_conversions > 0 else float('inf')
            },
            'simulated_metrics': {
                'impressions': simulated_impressions,
                'clicks': simulated_clicks,
                'conversions': simulated_conversions,
                'cost': simulated_cost,
                'ctr': simulated_ctr,
                'cvr': simulated_cvr,
                'cpc': simulated_cpc,
                'cpa': simulated_cpa
            },
            'changes': {
                'impressions': impression_change_pct,
                'clicks': click_change_pct,
                'conversions': conversion_change_pct,
                'cost': cost_change_pct,
                'ctr': (simulated_ctr - (avg_clicks / avg_impressions if avg_impressions > 0 else 0)) * 100,
                'cvr': (simulated_cvr - (avg_conversions / avg_clicks if avg_clicks > 0 else 0)) * 100,
                'cpc': (simulated_cpc - (avg_cost / avg_clicks if avg_clicks > 0 else 0)) * 100,
                'cpa': (simulated_cpa - (avg_cost / avg_conversions if avg_conversions > 0 else float('inf'))) * 100
            },
            'assumptions': {
                'impression_elasticity': elasticity,
                'ctr_change': ctr_change,
                'cvr_change': cvr_change
            }
        }
        
        self.simulation_results[ad_group_id] = result
        return result
    
    def generate_simulation_report(self, ad_group_id):
        """
        生成模拟报告
        
        Parameters:
        -----------
        ad_group_id : str
            广告组ID
            
        Returns:
        --------
        str
            模拟报告
        """
        if ad_group_id not in self.simulation_results:
            return f"没有广告组 {ad_group_id} 的模拟结果"
        
        result = self.simulation_results[ad_group_id]
        
        report = []
        report.append("=" * 60)
        report.append(f"出价模拟报告 - 广告组 {ad_group_id}")
        report.append("=" * 60)
        
        report.append(f"\n1. 出价变化:")
        report.append(f"   当前出价: {result['current_bid']:.2f}")
        report.append(f"   新出价: {result['new_bid']:.2f}")
        report.append(f"   变化比例: {result['bid_change_ratio']:.2f}x")
        report.append(f"   模拟天数: {result['simulation_days']} 天")
        
        report.append(f"\n2. 预期效果变化:")
        
        current = result['current_metrics']
        simulated = result['simulated_metrics']
        changes = result['changes']
        
        report.append(f"   展示量: {current['impressions']:,.0f} -> {simulated['impressions']:,.0f} ({changes['impressions']:+.1f}%)")
        report.append(f"   点击量: {current['clicks']:,.0f} -> {simulated['clicks']:,.0f} ({changes['clicks']:+.1f}%)")
        report.append(f"   转化量: {current['conversions']:,.0f} -> {simulated['conversions']:,.0f} ({changes['conversions']:+.1f}%)")
        report.append(f"   成本: {current['cost']:,.2f} -> {simulated['cost']:,.2f} ({changes['cost']:+.1f}%)")
        
        report.append(f"\n3. 效率指标变化:")
        report.append(f"   点击率: {current['ctr']:.2%} -> {simulated['ctr']:.2%} ({changes['ctr']:+.2f}%)")
        report.append(f"   转化率: {current['cvr']:.2%} -> {simulated['cvr']:.2%} ({changes['cvr']:+.2f}%)")
        report.append(f"   每次点击成本: {current['cpc']:.2f} -> {simulated['cpc']:.2f} ({changes['cpc']:+.2f}%)")
        report.append(f"   每次转化成本: {current['cpa']:.2f} -> {simulated['cpa']:.2f} ({changes['cpa']:+.2f}%)")
        
        report.append(f"\n4. 模拟假设:")
        assumptions = result['assumptions']
        report.append(f"   展示量弹性系数: {assumptions['impression_elasticity']}")
        report.append(f"   点击率变化: {assumptions['ctr_change']}x")
        report.append(f"   转化率变化: {assumptions['cvr_change']}x")
        
        report.append(f"\n5. 建议:")
        if changes['conversions'] > 0 and changes['cost'] < changes['conversions']:
            report.append("   ✓ 建议提高出价，预计转化量提升大于成本增加")
        elif changes['conversions'] < 0 and changes['cost'] > changes['conversions']:
            report.append("   ✗ 不建议提高出价，预计转化量下降或成本增加过多")
        else:
            report.append("   - 出价变化影响中性，建议根据实际效果调整")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def print_simulation_report(self, ad_group_id):
        """
        打印模拟报告
        
        Parameters:
        -----------
        ad_group_id : str
            广告组ID
        """
        report = self.generate_simulation_report(ad_group_id)
        print(report)

# 便捷函数
def get_bid_suggestions(df, current_bids, target_metric='conversions'):
    """
    获取出价建议的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        广告效果数据
    current_bids : dict
        当前出价
    target_metric : str
        优化目标指标
        
    Returns:
    --------
    dict
        出价建议
    """
    optimizer = BidOptimizer(target_metric=target_metric)
    return optimizer.calculate_bid_suggestions(df, current_bids)

def simulate_bid_change(historical_data, ad_group_id, current_bid, new_bid, days=30):
    """
    模拟出价变化的便捷函数
    
    Parameters:
    -----------
    historical_data : pandas.DataFrame
        历史数据
    ad_group_id : str
        广告组ID
    current_bid : float
        当前出价
    new_bid : float
        新出价
    days : int
        模拟天数
        
    Returns:
    --------
    dict
        模拟结果
    """
    simulator = BidSimulator(historical_data)
    return simulator.simulate_bid_change(ad_group_id, current_bid, new_bid, days)

if __name__ == "__main__":
    # 测试出价优化
    print("测试出价优化建议...")
    
    # 创建模拟数据
    np.random.seed(42)
    n_groups = 10
    
    data = {
        'impressions': np.random.randint(1000, 10000, n_groups),
        'clicks': np.random.randint(50, 500, n_groups),
        'conversions': np.random.randint(5, 50, n_groups),
        'cost': np.random.uniform(100, 1000, n_groups)
    }
    
    df = pd.DataFrame(data, index=[f'group_{i}' for i in range(n_groups)])
    
    # 计算衍生指标
    df['ctr'] = df['clicks'] / df['impressions']
    df['cvr'] = df['conversions'] / df['clicks']
    df['cpc'] = df['cost'] / df['clicks']
    df['cpa'] = df['cost'] / df['conversions']
    
    # 创建当前出价
    current_bids = {f'group_{i}': np.random.uniform(1, 5) for i in range(n_groups)}
    
    # 获取出价建议
    print("\n1. 出价建议:")
    optimizer = BidOptimizer()
    suggestions = optimizer.calculate_bid_suggestions(df, current_bids)
    
    for group_id, suggestion in list(suggestions.items())[:3]:  # 只显示前3个
        print(f"\n{group_id}:")
        print(f"  当前出价: {suggestion['current_bid']:.2f}")
        print(f"  建议出价: {suggestion['suggested_bid']:.2f}")
        print(f"  调整幅度: {suggestion['adjustment_percent']:+.1f}%")
        print(f"  原因: {suggestion['reason']}")
    
    # 测试预算分配
    print("\n2. 预算分配优化:")
    budget_allocation = optimizer.optimize_budget_allocation(df, total_budget=5000)
    
    for group_id, allocation in list(budget_allocation.items())[:3]:  # 只显示前3个
        print(f"\n{group_id}:")
        print(f"  分配预算: {allocation['allocated_budget']:.2f}")
        print(f"  效率得分: {allocation['efficiency_score']:.1f}")
    
    # 测试出价模拟
    print("\n3. 出价模拟:")
    simulator = BidSimulator(df)
    result = simulator.simulate_bid_change('group_0', 2.0, 2.5, days=30)
    
    print(f"广告组: group_0")
    print(f"当前出价: {result['current_bid']:.2f}")
    print(f"新出价: {result['new_bid']:.2f}")
    print(f"预计转化量变化: {result['changes']['conversions']:+.1f}%")
    print(f"预计成本变化: {result['changes']['cost']:+.1f}%")