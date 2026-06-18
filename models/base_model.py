"""
基础模型模块
提供机器学习模型的基类和通用功能
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class BaseModel:
    """基础模型类"""
    
    def __init__(self, model_name="base_model", random_state=42):
        """
        初始化基础模型
        
        Parameters:
        -----------
        model_name : str
            模型名称
        random_state : int
            随机种子
        """
        self.model_name = model_name
        self.random_state = random_state
        self.model = None
        self.is_fitted = False
        self.feature_names = None
        self.training_history = []
        
    def fit(self, X, y):
        """
        训练模型
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据
            
        Returns:
        --------
        self
            返回自身
        """
        raise NotImplementedError("子类必须实现fit方法")
    
    def predict(self, X):
        """
        预测
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
            
        Returns:
        --------
        numpy.ndarray
            预测结果
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练，请先调用fit方法")
        
        return self.model.predict(X)
    
    def score(self, X, y):
        """
        评估模型
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            真实值
            
        Returns:
        --------
        float
            评分
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练，请先调用fit方法")
        
        return self.model.score(X, y)
    
    def save(self, filepath):
        """
        保存模型
        
        Parameters:
        -----------
        filepath : str
            保存路径
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练，无法保存")
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存模型
        joblib.dump(self, filepath)
        print(f"模型已保存到: {filepath}")
    
    @classmethod
    def load(cls, filepath):
        """
        加载模型
        
        Parameters:
        -----------
        filepath : str
            模型文件路径
            
        Returns:
        --------
        BaseModel
            加载的模型
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        model = joblib.load(filepath)
        print(f"模型已加载: {filepath}")
        return model
    
    def get_feature_importance(self):
        """
        获取特征重要性
        
        Returns:
        --------
        dict
            特征重要性字典
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            if self.feature_names:
                return dict(zip(self.feature_names, importance))
            else:
                return {f"feature_{i}": imp for i, imp in enumerate(importance)}
        else:
            print("当前模型不支持特征重要性")
            return {}

class RegressionModel(BaseModel):
    """回归模型基类"""
    
    def __init__(self, model_name="regression_model", random_state=42):
        """
        初始化回归模型
        
        Parameters:
        -----------
        model_name : str
            模型名称
        random_state : int
            随机种子
        """
        super().__init__(model_name, random_state)
        self.model_type = "regression"
        
    def evaluate(self, X_test, y_test):
        """
        评估回归模型
        
        Parameters:
        -----------
        X_test : pandas.DataFrame or numpy.ndarray
            测试特征数据
        y_test : pandas.Series or numpy.ndarray
            测试目标数据
            
        Returns:
        --------
        dict
            评估指标
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        y_pred = self.predict(X_test)
        
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100 if np.all(y_test != 0) else float('inf')
        }
        
        return metrics
    
    def cross_validate(self, X, y, cv=5):
        """
        交叉验证
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据
        cv : int
            折数
            
        Returns:
        --------
        dict
            交叉验证结果
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        # 使用R2分数进行交叉验证
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='r2')
        
        results = {
            'mean_r2': scores.mean(),
            'std_r2': scores.std(),
            'scores': scores.tolist()
        }
        
        return results

class ClassificationModel(BaseModel):
    """分类模型基类"""
    
    def __init__(self, model_name="classification_model", random_state=42):
        """
        初始化分类模型
        
        Parameters:
        -----------
        model_name : str
            模型名称
        random_state : int
            随机种子
        """
        super().__init__(model_name, random_state)
        self.model_type = "classification"
        
    def evaluate(self, X_test, y_test):
        """
        评估分类模型
        
        Parameters:
        -----------
        X_test : pandas.DataFrame or numpy.ndarray
            测试特征数据
        y_test : pandas.Series or numpy.ndarray
            测试目标数据
            
        Returns:
        --------
        dict
            评估指标
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        y_pred = self.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted')
        }
        
        return metrics
    
    def cross_validate(self, X, y, cv=5):
        """
        交叉验证
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据
        cv : int
            折数
            
        Returns:
        --------
        dict
            交叉验证结果
        """
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        # 使用准确率进行交叉验证
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
        
        results = {
            'mean_accuracy': scores.mean(),
            'std_accuracy': scores.std(),
            'scores': scores.tolist()
        }
        
        return results

class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, test_size=0.2, random_state=42):
        """
        初始化模型训练器
        
        Parameters:
        -----------
        test_size : float
            测试集比例
        random_state : int
            随机种子
        """
        self.test_size = test_size
        self.random_state = random_state
        self.models = {}
        self.results = {}
        
    def prepare_data(self, X, y, feature_names=None):
        """
        准备训练数据
        
        Parameters:
        -----------
        X : pandas.DataFrame or numpy.ndarray
            特征数据
        y : pandas.Series or numpy.ndarray
            目标数据
        feature_names : list, optional
            特征名称
            
        Returns:
        --------
        tuple
            (X_train, X_test, y_train, y_test)
        """
        # 转换为numpy数组
        if isinstance(X, pd.DataFrame):
            if feature_names is None:
                feature_names = X.columns.tolist()
            X = X.values
        
        if isinstance(y, pd.Series):
            y = y.values
        
        # 划分训练测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        print(f"数据准备完成:")
        print(f"  训练集: {X_train.shape}")
        print(f"  测试集: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test, feature_names
    
    def train_model(self, model, X_train, y_train, **kwargs):
        """
        训练模型
        
        Parameters:
        -----------
        model : BaseModel
            模型实例
        X_train : numpy.ndarray
            训练特征数据
        y_train : numpy.ndarray
            训练目标数据
        **kwargs : dict
            其他参数
            
        Returns:
        --------
        BaseModel
            训练好的模型
        """
        print(f"训练模型: {model.model_name}")
        
        # 训练模型
        model.fit(X_train, y_train)
        
        # 记录训练历史
        model.training_history.append({
            'timestamp': pd.Timestamp.now(),
            'training_samples': len(X_train),
            'features': X_train.shape[1]
        })
        
        self.models[model.model_name] = model
        
        return model
    
    def evaluate_model(self, model, X_test, y_test):
        """
        评估模型
        
        Parameters:
        -----------
        model : BaseModel
            模型实例
        X_test : numpy.ndarray
            测试特征数据
        y_test : numpy.ndarray
            测试目标数据
            
        Returns:
        --------
        dict
            评估结果
        """
        print(f"评估模型: {model.model_name}")
        
        # 获取评估指标
        if model.model_type == "regression":
            metrics = model.evaluate(X_test, y_test)
        else:
            metrics = model.evaluate(X_test, y_test)
        
        # 记录结果
        self.results[model.model_name] = {
            'metrics': metrics,
            'model': model
        }
        
        return metrics
    
    def compare_models(self):
        """
        比较所有训练过的模型
        
        Returns:
        --------
        pandas.DataFrame
            模型比较结果
        """
        if not self.results:
            print("没有训练结果可比较")
            return pd.DataFrame()
        
        comparison = []
        
        for model_name, result in self.results.items():
            metrics = result['metrics']
            
            row = {'model': model_name}
            row.update(metrics)
            comparison.append(row)
        
        df = pd.DataFrame(comparison)
        
        # 按R2分数排序（如果是回归模型）
        if 'r2' in df.columns:
            df = df.sort_values('r2', ascending=False)
        elif 'accuracy' in df.columns:
            df = df.sort_values('accuracy', ascending=False)
        
        return df
    
    def get_best_model(self, metric='r2'):
        """
        获取最佳模型
        
        Parameters:
        -----------
        metric : str
            评估指标
            
        Returns:
        --------
        BaseModel
            最佳模型
        """
        if not self.results:
            print("没有训练结果")
            return None
        
        best_score = -float('inf')
        best_model = None
        
        for model_name, result in self.results.items():
            score = result['metrics'].get(metric, -float('inf'))
            
            if score > best_score:
                best_score = score
                best_model = result['model']
        
        return best_model

# 工具函数
def split_data(X, y, test_size=0.2, random_state=42):
    """
    划分数据的便捷函数
    
    Parameters:
    -----------
    X : pandas.DataFrame or numpy.ndarray
        特征数据
    y : pandas.Series or numpy.ndarray
        目标数据
    test_size : float
        测试集比例
    random_state : int
        随机种子
        
    Returns:
    --------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def evaluate_regression(y_true, y_pred):
    """
    评估回归模型的便捷函数
    
    Parameters:
    -----------
    y_true : numpy.ndarray
        真实值
    y_pred : numpy.ndarray
        预测值
        
    Returns:
    --------
    dict
        评估指标
    """
    metrics = {
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred)
    }
    
    return metrics

def evaluate_classification(y_true, y_pred):
    """
    评估分类模型的便捷函数
    
    Parameters:
    -----------
    y_true : numpy.ndarray
        真实值
    y_pred : numpy.ndarray
        预测值
        
    Returns:
    --------
    dict
        评估指标
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted')
    }
    
    return metrics

if __name__ == "__main__":
    # 测试基础模型
    print("测试基础模型...")
    
    # 创建模拟数据
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = 3 * X[:, 0] + 2 * X[:, 1] - X[:, 2] + np.random.randn(100) * 0.1
    
    # 划分数据
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # 创建回归模型
    from sklearn.linear_model import LinearRegression
    
    class LinearRegressionModel(RegressionModel):
        def __init__(self, random_state=42):
            super().__init__("linear_regression", random_state)
            self.model = LinearRegression()
        
        def fit(self, X, y):
            self.model.fit(X, y)
            self.is_fitted = True
            return self
    
    # 训练和评估
    model = LinearRegressionModel()
    model.fit(X_train, y_train)
    
    metrics = model.evaluate(X_test, y_test)
    print(f"评估指标: {metrics}")
    
    # 获取特征重要性
    importance = model.get_feature_importance()
    print(f"特征重要性: {importance}")