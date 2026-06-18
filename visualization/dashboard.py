"""
广告效果数据看板
使用Streamlit创建交互式数据可视化界面
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.data_processor import DataLoader, process_data
from config import BUSINESS_CONFIG

# 页面配置
st.set_page_config(
    page_title="广告效果分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载数据（带缓存）"""
    try:
        loader = DataLoader()
        df = loader.load_sample_data()
        processed_df = process_data(df)
        return processed_df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

def create_metrics_cards(df):
    """创建指标卡片"""
    if df.empty:
        return
    
    # 计算关键指标
    total_impressions = df['impressions'].sum()
    total_clicks = df['clicks'].sum()
    total_cost = df['cost'].sum()
    total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0
    
    # 计算衍生指标
    overall_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    overall_cpc = total_cost / total_clicks if total_clicks > 0 else 0
    overall_cpa = total_cost / total_conversions if total_conversions > 0 else 0
    
    # 显示指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总展示量",
            value=f"{total_impressions:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="总点击量",
            value=f"{total_clicks:,.0f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="总成本",
            value=f"¥{total_cost:,.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="总转化量",
            value=f"{total_conversions:,.0f}",
            delta=None
        )
    
    # 第二行指标
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="平均点击率",
            value=f"{overall_ctr:.2%}",
            delta=None
        )
    
    with col6:
        st.metric(
            label="平均每次点击成本",
            value=f"¥{overall_cpc:.2f}",
            delta=None
        )
    
    with col7:
        st.metric(
            label="平均每次转化成本",
            value=f"¥{overall_cpa:.2f}",
            delta=None
        )
    
    with col8:
        # 计算转化率
        conversion_rate = total_conversions / total_clicks if total_clicks > 0 else 0
        st.metric(
            label="平均转化率",
            value=f"{conversion_rate:.2%}",
            delta=None
        )

def create_time_series_chart(df):
    """创建时间序列图表"""
    if df.empty or 'date' not in df.columns:
        return
    
    # 按日期聚合数据
    daily_data = df.groupby('date').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'cost': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    # 计算衍生指标
    daily_data['ctr'] = daily_data['clicks'] / daily_data['impressions']
    daily_data['cpc'] = daily_data['cost'] / daily_data['clicks']
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('展示量趋势', '点击量趋势', '成本趋势', '点击率趋势'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 添加展示量趋势
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['impressions'],
            name='展示量',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ),
        row=1, col=1
    )
    
    # 添加点击量趋势
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['clicks'],
            name='点击量',
            line=dict(color='#ff7f0e', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 127, 14, 0.1)'
        ),
        row=1, col=2
    )
    
    # 添加成本趋势
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['cost'],
            name='成本',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.1)'
        ),
        row=2, col=1
    )
    
    # 添加点击率趋势
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['ctr'],
            name='点击率',
            line=dict(color='#d62728', width=2),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.1)'
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="关键指标时间趋势",
        title_x=0.5
    )
    
    # 更新y轴格式
    fig.update_yaxes(title_text="展示量", row=1, col=1)
    fig.update_yaxes(title_text="点击量", row=1, col=2)
    fig.update_yaxes(title_text="成本 (¥)", row=2, col=1)
    fig.update_yaxes(title_text="点击率", row=2, col=2, tickformat='.2%')
    
    st.plotly_chart(fig, use_container_width=True)

def create_dimension_analysis(df):
    """创建维度分析图表"""
    if df.empty:
        return
    
    # 选择分析维度
    dimension = st.selectbox(
        "选择分析维度",
        ['ad_format', 'placement', 'audience'],
        format_func=lambda x: {
            'ad_format': '广告格式',
            'placement': '广告位置',
            'audience': '目标人群'
        }[x]
    )
    
    if dimension not in df.columns:
        return
    
    # 按维度聚合数据
    dim_data = df.groupby(dimension).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'cost': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    # 计算衍生指标
    dim_data['ctr'] = dim_data['clicks'] / dim_data['impressions']
    dim_data['cpc'] = dim_data['cost'] / dim_data['clicks']
    
    # 创建图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 展示量分布饼图
        fig_pie = px.pie(
            dim_data,
            values='impressions',
            names=dimension,
            title=f'各{dimension}展示量分布',
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 点击率对比柱状图
        fig_bar = px.bar(
            dim_data,
            x=dimension,
            y='ctr',
            title=f'各{dimension}点击率对比',
            color=dimension,
            text_auto='.2%'
        )
        fig_bar.update_layout(yaxis_tickformat='.2%')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 详细数据表格
    st.subheader(f"各{dimension}详细数据")
    
    # 格式化数据
    display_data = dim_data.copy()
    display_data['ctr'] = display_data['ctr'].apply(lambda x: f"{x:.2%}")
    display_data['cpc'] = display_data['cpc'].apply(lambda x: f"¥{x:.2f}")
    
    # 重命名列
    column_names = {
        dimension: '维度',
        'impressions': '展示量',
        'clicks': '点击量',
        'cost': '成本',
        'conversions': '转化量',
        'ctr': '点击率',
        'cpc': '每次点击成本'
    }
    display_data = display_data.rename(columns=column_names)
    
    st.dataframe(display_data, use_container_width=True)

def create_performance_scatter(df):
    """创建效果散点图"""
    if df.empty:
        return
    
    # 选择X轴和Y轴指标
    col1, col2 = st.columns(2)
    
    with col1:
        x_metric = st.selectbox(
            "X轴指标",
            ['impressions', 'clicks', 'cost'],
            format_func=lambda x: {
                'impressions': '展示量',
                'clicks': '点击量',
                'cost': '成本'
            }[x]
        )
    
    with col2:
        y_metric = st.selectbox(
            "Y轴指标",
            ['clicks', 'cost', 'ctr'],
            format_func=lambda x: {
                'clicks': '点击量',
                'cost': '成本',
                'ctr': '点击率'
            }[x]
        )
    
    # 创建散点图
    fig = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        color='ad_format' if 'ad_format' in df.columns else None,
        size='impressions',
        hover_data=['date', 'placement', 'audience'],
        title=f'{x_metric} vs {y_metric} 关系图',
        labels={
            x_metric: x_metric,
            y_metric: y_metric,
            'ad_format': '广告格式'
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_anomaly_detection(df):
    """创建异常检测图表"""
    if df.empty or 'date' not in df.columns:
        return
    
    # 按日期聚合数据
    daily_data = df.groupby('date').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # 计算点击率
    daily_data['ctr'] = daily_data['clicks'] / daily_data['impressions']
    
    # 计算移动平均和标准差
    window = 7
    daily_data['ctr_ma'] = daily_data['ctr'].rolling(window=window).mean()
    daily_data['ctr_std'] = daily_data['ctr'].rolling(window=window).std()
    
    # 计算上下界
    daily_data['ctr_upper'] = daily_data['ctr_ma'] + 2 * daily_data['ctr_std']
    daily_data['ctr_lower'] = daily_data['ctr_ma'] - 2 * daily_data['ctr_std']
    
    # 标记异常点
    daily_data['is_anomaly'] = (
        (daily_data['ctr'] > daily_data['ctr_upper']) | 
        (daily_data['ctr'] < daily_data['ctr_lower'])
    )
    
    # 创建图表
    fig = go.Figure()
    
    # 添加点击率线
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['ctr'],
            name='点击率',
            line=dict(color='#1f77b4', width=2),
            mode='lines+markers'
        )
    )
    
    # 添加移动平均线
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['ctr_ma'],
            name=f'{window}日移动平均',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        )
    )
    
    # 添加置信区间
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['ctr_upper'],
            name='上界',
            line=dict(color='rgba(255, 127, 14, 0.3)', width=0),
            showlegend=False
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['ctr_lower'],
            name='下界',
            line=dict(color='rgba(255, 127, 14, 0.3)', width=0),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.1)',
            showlegend=False
        )
    )
    
    # 标记异常点
    anomalies = daily_data[daily_data['is_anomaly']]
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies['date'],
                y=anomalies['ctr'],
                name='异常点',
                mode='markers',
                marker=dict(color='red', size=10, symbol='x')
            )
        )
    
    # 更新布局
    fig.update_layout(
        title='点击率异常检测',
        xaxis_title='日期',
        yaxis_title='点击率',
        yaxis_tickformat='.2%',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示异常统计
    if not anomalies.empty:
        st.warning(f"检测到 {len(anomalies)} 个异常点")
        st.dataframe(anomalies[['date', 'ctr', 'ctr_ma']].reset_index(drop=True))
    else:
        st.success("未检测到异常点")

def main():
    """主函数"""
    # 页面标题
    st.markdown('<h1 class="main-header">广告效果分析看板</h1>', unsafe_allow_html=True)
    
    # 加载数据
    df = load_data()
    
    if df.empty:
        st.error("无法加载数据，请检查数据文件")
        return
    
    # 侧边栏
    st.sidebar.title("数据筛选")
    
    # 日期范围选择
    if 'date' in df.columns:
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        date_range = st.sidebar.date_input(
            "选择日期范围",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['date'] >= pd.Timestamp(start_date)) & 
                    (df['date'] <= pd.Timestamp(end_date))]
    
    # 广告格式筛选
    if 'ad_format' in df.columns:
        ad_formats = st.sidebar.multiselect(
            "选择广告格式",
            options=df['ad_format'].unique(),
            default=df['ad_format'].unique()
        )
        df = df[df['ad_format'].isin(ad_formats)]
    
    # 广告位置筛选
    if 'placement' in df.columns:
        placements = st.sidebar.multiselect(
            "选择广告位置",
            options=df['placement'].unique(),
            default=df['placement'].unique()
        )
        df = df[df['placement'].isin(placements)]
    
    # 显示数据概览
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**数据概览**")
    st.sidebar.markdown(f"- 记录数: {len(df):,}")
    st.sidebar.markdown(f"- 日期范围: {df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
    
    # 主体内容
    if df.empty:
        st.warning("筛选后无数据，请调整筛选条件")
        return
    
    # 指标卡片
    st.subheader("关键指标概览")
    create_metrics_cards(df)
    
    # 时间趋势
    st.markdown("---")
    st.subheader("时间趋势分析")
    create_time_series_chart(df)
    
    # 维度分析
    st.markdown("---")
    st.subheader("维度分析")
    create_dimension_analysis(df)
    
    # 效果散点图
    st.markdown("---")
    st.subheader("效果关系分析")
    create_performance_scatter(df)
    
    # 异常检测
    st.markdown("---")
    st.subheader("异常检测")
    create_anomaly_detection(df)
    
    # 页脚
    st.markdown("---")
    st.markdown("### 数据说明")
    st.markdown("""
    - **展示量**: 广告被展示的次数
    - **点击量**: 广告被点击的次数
    - **点击率 (CTR)**: 点击量 / 展示量
    - **成本**: 广告投放总花费
    - **每次点击成本 (CPC)**: 成本 / 点击量
    - **转化量**: 广告带来的转化次数
    - **每次转化成本 (CPA)**: 成本 / 转化量
    """)

if __name__ == "__main__":
    main()