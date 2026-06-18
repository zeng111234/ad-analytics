"""
效果预测模型
用于预测广告点击率、转化率等效果指标
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

from .base_model import RegressionModel, ModelTrainer, split_data

class CTRPredictionModel(RegressionModel):
    """点击率预测模型"""
    
    def __init__(self, model_type='random_forest', random_state=42):
        """
        初始化点击率预测模型
        
        Parameters:
        -----------
        model_type : str
            模型类型 ('linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting')
        random_state : int
            随机种子
        """
        super().__init__(f"ctr_prediction_{model_type}", random_state)
        self.model_type_name = model_type
        
        # 根据模型类型创建模型
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0, random_state=random_state)
        elif model_type == 'lasso':
            self.model = Lasso(alpha=0.1, random_state=random_state)
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=random_state
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 特征缩放器
        self.scaler = StandardScaler()
        
    def fit(self, X, y):
        """
        训练点击率预测模型
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据（点击率）
            
        Returns:
        --------
        self
            返回自身
        """
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        
        if isinstance(y, pd.Series):
            y = y.values
        
        # 特征缩放
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        print(f"点击率预测模型训练完成，样本数: {len(X)}")
        
        return self
    
    def predict(self, X):
        """
        预测点击率
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
            
        Returns:
        --------
        numpy.ndarray
            预测的点击率
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # 特征缩放
        X_scaled = self.scaler.transform(X)
        
        # 预测
        predictions = self.model.predict(X_scaled)
        
        # 确保预测值在合理范围内 (0-1)
        predictions = np.clip(predictions, 0, 1)
        
        return predictions

class ConversionPredictionModel(RegressionModel):
    """转化率预测模型"""
    
    def __init__(self, model_type='gradient_boosting', random_state=42):
        """
        初始化转化率预测模型
        
        Parameters:
        -----------
        model_type : str
            模型类型
        random_state : int
            随机种子
        """
        super().__init__(f"conversion_prediction_{model_type}", random_state)
        self.model_type_name = model_type
        
        # 根据模型类型创建模型
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=random_state
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 特征缩放器
        self.scaler = StandardScaler()
        
    def fit(self, X, y):
        """
        训练转化率预测模型
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据（转化率）
            
        Returns:
        --------
        self
            返回自身
        """
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        
        if isinstance(y, pd.Series):
            y = y.values
        
        # 特征缩放
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        print(f"转化率预测模型训练完成，样本数: {len(X)}")
        
        return self
    
    def predict(self, X):
        """
        预测转化率
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
            
        Returns:
        --------
        numpy.ndarray
            预测的转化率
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # 特征缩放
        X_scaled = self.scaler.transform(X)
        
        # 预测
        predictions = self.model.predict(X_scaled)
        
        # 确保预测值在合理范围内 (0-1)
        predictions = np.clip(predictions, 0, 1)
        
        return predictions

class CostPredictionModel(RegressionModel):
    """成本预测模型"""
    
    def __init__(self, model_type='random_forest', random_state=42):
        """
        初始化成本预测模型
        
        Parameters:
        -----------
        model_type : str
            模型类型
        random_state : int
            随机种子
        """
        super().__init__(f"cost_prediction_{model_type}", random_state)
        self.model_type_name = model_type
        
        # 根据模型类型创建模型
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=random_state
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 特征缩放器
        self.scaler = StandardScaler()
        
    def fit(self, X, y):
        """
        训练成本预测模型
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据（成本）
            
        Returns:
        --------
        self
            返回自身
        """
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        
        if isinstance(y, pd.Series):
            y = y.values
        
        # 特征缩放
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        print(f"成本预测模型训练完成，样本数: {len(X)}")
        
        return self
    
    def predict(self, X):
        """
        预测成本
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
            
        Returns:
        --------
        numpy.ndarray
            预测的成本
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # 特征缩放
        X_scaled = self.scaler.transform(X)
        
        # 预测
        predictions = self.model.predict(X_scaled)
        
        # 确保预测值非负
        predictions = np.maximum(predictions, 0)
        
        return predictions

class AdEffectPredictor:
    """广告效果预测器"""
    
    def __init__(self, random_state=42):
        """
        初始化广告效果预测器
        
        Parameters:
        -----------
        random_state : int
            随机种子
        """
        self.random_state = random_state
        self.models = {}
        self.trainer = ModelTrainer(test_size=0.2, random_state=random_state)
        self.feature_columns = None
        
    def prepare_features(self, df, is_training=True):
        """
        准备特征数据
        
        Parameters:
        -----------
        df : pandas.DataFrame
            原始数据
        is_training : bool
            是否是训练阶段（如果是，会存储特征列）
            
        Returns:
        --------
        pandas.DataFrame
            处理后的特征数据
        """
        # 选择特征列
        feature_columns = []
        
        # 数值特征
        numeric_features = ['impressions', 'clicks', 'cost']
        for col in numeric_features:
            if col in df.columns:
                feature_columns.append(col)
        
        # 类别特征（需要编码）
        categorical_features = ['ad_format', 'placement', 'audience']
        for col in categorical_features:
            if col in df.columns:
                # 独热编码
                dummies = pd.get_dummies(df[col], prefix=col)
                feature_columns.extend(dummies.columns.tolist())
        
        # 创建特征矩阵
        features = pd.DataFrame()
        
        # 添加数值特征
        for col in numeric_features:
            if col in df.columns:
                features[col] = df[col]
        
        # 添加编码后的类别特征
        for col in categorical_features:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col)
                features = pd.concat([features, dummies], axis=1)
        
        # 添加时间特征（如果有日期列）
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            features['day_of_week'] = df['date'].dt.dayofweek
            features['month'] = df['date'].dt.month
            features['day_of_month'] = df['date'].dt.day
        
        # 如果是训练阶段，存储特征列
        if is_training:
            self.feature_columns = features.columns.tolist()
        else:
            # 如果是预测阶段，确保存储的特征列存在
            if self.feature_columns is None:
                raise ValueError("模型尚未训练，无法准备预测特征")
            
            # 添加缺失的特征列（用0填充）
            for col in self.feature_columns:
                if col not in features.columns:
                    features[col] = 0
            
            # 只保留训练时的特征列
            features = features[self.feature_columns]
        
        return features
    
    def train_ctr_model(self, df, model_type='random_forest'):
        """
        训练点击率预测模型
        
        Parameters:
        -----------
        df : pandas.DataFrame
            训练数据
        model_type : str
            模型类型
            
        Returns:
        --------
        CTRPredictionModel
            训练好的模型
        """
        print("训练点击率预测模型...")
        
        # 准备特征和目标
        features = self.prepare_features(df)
        
        # 计算点击率作为目标
        if 'ctr' in df.columns:
            target = df['ctr']
        elif 'clicks' in df.columns and 'impressions' in df.columns:
            target = df['clicks'] / df['impressions']
        else:
            raise ValueError("数据中缺少点击率相关信息")
        
        # 划分数据
        X_train, X_test, y_train, y_test, feature_names = self.trainer.prepare_data(
            features, target, feature_names=features.columns.tolist()
        )
        
        # 创建并训练模型
        model = CTRPredictionModel(model_type=model_type, random_state=self.random_state)
        model.feature_names = feature_names
        
        self.trainer.train_model(model, X_train, y_train)
        
        # 评估模型
        metrics = self.trainer.evaluate_model(model, X_test, y_test)
        print(f"点击率预测模型评估: {metrics}")
        
        self.models['ctr'] = model
        
        return model
    
    def train_conversion_model(self, df, model_type='gradient_boosting'):
        """
        训练转化率预测模型
        
        Parameters:
        -----------
        df : pandas.DataFrame
            训练数据
        model_type : str
            模型类型
            
        Returns:
        --------
        ConversionPredictionModel
            训练好的模型
        """
        print("训练转化率预测模型...")
        
        # 准备特征和目标
        features = self.prepare_features(df)
        
        # 计算转化率作为目标
        if 'cvr' in df.columns:
            target = df['cvr']
        elif 'conversions' in df.columns and 'clicks' in df.columns:
            target = df['conversions'] / df['clicks']
        else:
            raise ValueError("数据中缺少转化率相关信息")
        
        # 划分数据
        X_train, X_test, y_train, y_test, feature_names = self.trainer.prepare_data(
            features, target, feature_names=features.columns.tolist()
        )
        
        # 创建并训练模型
        model = ConversionPredictionModel(model_type=model_type, random_state=self.random_state)
        model.feature_names = feature_names
        
        self.trainer.train_model(model, X_train, y_train)
        
        # 评估模型
        metrics = self.trainer.evaluate_model(model, X_test, y_test)
        print(f"转化率预测模型评估: {metrics}")
        
        self.models['conversion'] = model
        
        return model
    
    def train_cost_model(self, df, model_type='random_forest'):
        """
        训练成本预测模型
        
        Parameters:
        -----------
        df : pandas.DataFrame
            训练数据
        model_type : str
            模型类型
            
        Returns:
        --------
        CostPredictionModel
            训练好的模型
        """
        print("训练成本预测模型...")
        
        # 准备特征和目标
        features = self.prepare_features(df)
        
        # 使用成本作为目标
        if 'cost' in df.columns:
            target = df['cost']
        else:
            raise ValueError("数据中缺少成本信息")
        
        # 划分数据
        X_train, X_test, y_train, y_test, feature_names = self.trainer.prepare_data(
            features, target, feature_names=features.columns.tolist()
        )
        
        # 创建并训练模型
        model = CostPredictionModel(model_type=model_type, random_state=self.random_state)
        model.feature_names = feature_names
        
        self.trainer.train_model(model, X_train, y_train)
        
        # 评估模型
        metrics = self.trainer.evaluate_model(model, X_test, y_test)
        print(f"成本预测模型评估: {metrics}")
        
        self.models['cost'] = model
        
        return model
    
    def predict_all(self, df):
        """
        预测所有指标
        
        Parameters:
        -----------
        df : pandas.DataFrame
            预测数据
            
        Returns:
        --------
        dict
            预测结果
        """
        predictions = {}
        
        # 准备特征
        features = self.prepare_features(df, is_training=False)
        
        # 预测点击率
        if 'ctr' in self.models:
            predictions['ctr'] = self.models['ctr'].predict(features)
        
        # 预测转化率
        if 'conversion' in self.models:
            predictions['conversion'] = self.models['conversion'].predict(features)
        
        # 预测成本
        if 'cost' in self.models:
            predictions['cost'] = self.models['cost'].predict(features)
        
        return predictions
    
    def save_models(self, directory='models/saved'):
        """
        保存所有模型
        
        Parameters:
        -----------
        directory : str
            保存目录
        """
        import os
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            filepath = os.path.join(directory, f"{name}_prediction_model.pkl")
            model.save(filepath)
    
    def load_models(self, directory='models/saved'):
        """
        加载所有模型
        
        Parameters:
        -----------
        directory : str
            模型目录
        """
        import os
        
        model_files = {
            'ctr': 'ctr_prediction_model.pkl',
            'conversion': 'conversion_prediction_model.pkl',
            'cost': 'cost_prediction_model.pkl'
        }
        
        for name, filename in model_files.items():
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                self.models[name] = CTRPredictionModel.load(filepath)
                print(f"加载 {name} 模型")

# 便捷函数
def train_ctr_model(df, model_type='random_forest', random_state=42):
    """
    训练点击率预测模型的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        训练数据
    model_type : str
        模型类型
    random_state : int
        随机种子
        
    Returns:
    --------
    CTRPredictionModel
        训练好的模型
    """
    predictor = AdEffectPredictor(random_state=random_state)
    return predictor.train_ctr_model(df, model_type)

def train_conversion_model(df, model_type='gradient_boosting', random_state=42):
    """
    训练转化率预测模型的便捷函数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        训练数据
    model_type : str
        模型类型
    random_state : int
        随机种子
        
    Returns:
    --------
    ConversionPredictionModel
        训练好的模型
    """
    predictor = AdEffectPredictor(random_state=random_state)
    return predictor.train_conversion_model(df, model_type)

if __name__ == "__main__":
    # 测试效果预测模型
    print("测试效果预测模型...")
    
    # 生成模拟数据
    np.random.seed(42)
    n_samples = 1000
    
    # 创建模拟数据
    data = {
        'impressions': np.random.randint(100, 1000, n_samples),
        'ad_format': np.random.choice(['图片', '视频', '信息流'], n_samples),
        'placement': np.random.choice(['首页', '侧边栏', '底部'], n_samples),
        'audience': np.random.choice(['18-24岁', '25-34岁', '35-44岁'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # 生成目标变量
    base_ctr = 0.02
    format_effect = {'图片': 0, '视频': 0.01, '信息流': 0.005}
    placement_effect = {'首页': 0.005, '侧边栏': -0.002, '底部': -0.003}
    
    df['ctr'] = base_ctr
    for i, row in df.iterrows():
        df.loc[i, 'ctr'] += format_effect[row['ad_format']]
        df.loc[i, 'ctr'] += placement_effect[row['placement']]
        df.loc[i, 'ctr'] += np.random.normal(0, 0.005)
    
    df['ctr'] = np.clip(df['ctr'], 0, 0.1)
    
    # 训练模型
    predictor = AdEffectPredictor()
    model = predictor.train_ctr_model(df, model_type='random_forest')
    
    # 预测
    predictions = predictor.predict_all(df.head(10))
    print(f"预测结果: {predictions}")
    
    # 保存模型
    predictor.save_models()
    print("模型已保存")