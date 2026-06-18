# 广告分析平台配置文件

# 数据配置
DATA_CONFIG = {
    "data_dir": "data",
    "sample_data_file": "sample_ad_data.csv",
    "output_dir": "output"
}

# 模型配置
MODEL_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "model_dir": "models"
}

# 可视化配置
VISUALIZATION_CONFIG = {
    "theme": "default",
    "color_palette": "husl",
    "figure_size": (12, 8)
}

# 业务配置
BUSINESS_CONFIG = {
    "default_currency": "CNY",
    "default_time_zone": "Asia/Shanghai",
    "metrics": ["impressions", "clicks", "conversions", "cost", "ctr", "cpc", "cpa"]
}