"""
数值预测任务 - 阶段性验证程序
流程: 数据处理 → 特征选择 → 模型自动选择 → 训练 → 预测
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 尝试导入深度学习库
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[INFO] PyTorch not available, deep learning mode disabled")

# ============================================================================
# 阶段 0: 配置和日志
# ============================================================================

class StageLogger:
    """阶段验证日志器"""
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.stages = []
        
    def log(self, stage, message, data=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [Stage {stage}] {message}"
        print(log_entry)
        if data is not None:
            print(f"  Data: {data}")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
            if data is not None:
                f.write(f"  Data: {json.dumps(str(data), ensure_ascii=False)}\n")
        self.stages.append({"stage": stage, "message": message, "timestamp": timestamp})
        
    def save_report(self, report_data, filename="report.json"):
        report_path = os.path.join(self.log_dir, filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        return report_path

# ============================================================================
# 阶段 1: 数据加载与预处理
# ============================================================================

class DataProcessor:
    """数据处理模块"""
    
    def __init__(self, logger):
        self.logger = logger
        self.raw_data = None
        self.processed_data = None
        self.feature_columns = []
        self.target_columns = []
        
    def load_data(self, file_path, sheet_name=0):
        """加载数据文件 (支持 csv, excel)"""
        self.logger.log(1, f"Loading data from {file_path}")
        
        if file_path.endswith('.csv'):
            self.raw_data = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            self.raw_data = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
        
        self.logger.log(1, f"Data loaded successfully", {
            "shape": self.raw_data.shape,
            "columns": list(self.raw_data.columns),
            "dtypes": {k: str(v) for k, v in self.raw_data.dtypes.items()}
        })
        return self.raw_data
    
    def analyze_data(self):
        """数据分析，检测数据特征"""
        self.logger.log(1, "Analyzing data characteristics")
        
        analysis = {
            "total_rows": len(self.raw_data),
            "total_columns": len(self.raw_data.columns),
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "missing_values": {},
            "statistics": {}
        }
        
        for col in self.raw_data.columns:
            missing = self.raw_data[col].isnull().sum()
            if missing > 0:
                analysis["missing_values"][col] = int(missing)
            
            if pd.api.types.is_numeric_dtype(self.raw_data[col]):
                analysis["numeric_columns"].append(col)
                analysis["statistics"][col] = {
                    "mean": float(self.raw_data[col].mean()),
                    "std": float(self.raw_data[col].std()),
                    "min": float(self.raw_data[col].min()),
                    "max": float(self.raw_data[col].max())
                }
            elif pd.api.types.is_datetime64_any_dtype(self.raw_data[col]):
                analysis["datetime_columns"].append(col)
            else:
                unique_count = self.raw_data[col].nunique()
                if unique_count < len(self.raw_data) * 0.1:  # 少于10%唯一值视为分类
                    analysis["categorical_columns"].append(col)
                else:
                    analysis["numeric_columns"].append(col)  # 可能是ID或其他数值
        
        self.logger.log(1, "Data analysis complete", analysis)
        return analysis
    
    def preprocess(self, feature_cols=None, target_cols=None, auto_detect=True):
        """
        数据预处理
        :param feature_cols: 特征列名列表
        :param target_cols: 目标列名列表
        :param auto_detect: 是否自动检测特征和目标
        """
        self.logger.log(1, "Starting preprocessing")
        
        df = self.raw_data.copy()
        
        # 自动检测特征和目标
        if auto_detect and (feature_cols is None or target_cols is None):
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if target_cols is None:
                # 假设最后一列是目标
                target_cols = [numeric_cols[-1]] if numeric_cols else []
            
            if feature_cols is None:
                # 其他数值列作为特征
                feature_cols = [c for c in numeric_cols if c not in target_cols]
        
        self.feature_columns = feature_cols
        self.target_columns = target_cols
        
        self.logger.log(1, f"Detected features: {feature_cols}")
        self.logger.log(1, f"Detected targets: {target_cols}")
        
        # 处理缺失值
        for col in feature_cols + target_cols:
            if col in df.columns:
                if df[col].isnull().sum() > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col].fillna(df[col].median(), inplace=True)
                    else:
                        df[col].fillna(df[col].mode()[0], inplace=True)
        
        # 编码分类变量
        self.encoders = {}
        for col in df.columns:
            if col in feature_cols and not pd.api.types.is_numeric_dtype(df[col]):
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
        
        # 标准化数值特征
        self.scaler = StandardScaler()
        numeric_features = [c for c in feature_cols if c in df.columns]
        if numeric_features:
            df[numeric_features] = self.scaler.fit_transform(df[numeric_features])
        
        self.processed_data = df
        
        self.logger.log(1, "Preprocessing complete", {
            "feature_shape": (len(df), len(feature_cols)),
            "samples": len(df)
        })
        
        return df

# ============================================================================
# 阶段 2: 特征选择与数据对构建
# ============================================================================

class FeatureSelector:
    """特征选择模块"""
    
    def __init__(self, logger):
        self.logger = logger
        self.selected_features = []
        self.feature_importance = {}
        
    def select_features(self, df, feature_cols, target_cols, method='correlation', threshold=0.1):
        """
        特征选择
        :param method: 'correlation', 'mutual_info', 'all'
        """
        self.logger.log(2, f"Selecting features using {method}")
        
        X = df[feature_cols].values
        y = df[target_cols[0]].values if len(target_cols) == 1 else df[target_cols].values
        
        if method == 'correlation':
            # 基于相关性选择
            correlations = []
            for i, col in enumerate(feature_cols):
                corr = np.abs(np.corrcoef(X[:, i], y if y.ndim == 1 else y[:, 0])[0, 1])
                if not np.isnan(corr):
                    correlations.append((col, corr))
            
            correlations.sort(key=lambda x: x[1], reverse=True)
            self.selected_features = [c for c, v in correlations if v >= threshold]
            self.feature_importance = {c: float(v) for c, v in correlations}
            
        elif method == 'all':
            self.selected_features = feature_cols
            self.feature_importance = {c: 1.0 for c in feature_cols}
        
        self.logger.log(2, f"Selected {len(self.selected_features)} features", {
            "selected": self.selected_features,
            "importance": self.feature_importance
        })
        
        return self.selected_features
    
    def prepare_data_pairs(self, df, feature_cols, target_cols, test_size=0.2, val_size=0.1):
        """
        准备数据对 (训练/验证/测试集)
        """
        self.logger.log(2, "Preparing data pairs")
        
        X = df[feature_cols].values
        y = df[target_cols].values if len(target_cols) > 1 else df[target_cols[0]].values
        
        # 先划分训练+验证 / 测试
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 再划分训练 / 验证
        if val_size > 0:
            val_ratio = val_size / (1 - test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_train_val, y_train_val, test_size=val_ratio, random_state=42
            )
        else:
            X_train, y_train = X_train_val, y_train_val
            X_val, y_val = None, None
        
        data_pairs = {
            'train': (X_train, y_train),
            'val': (X_val, y_val),
            'test': (X_test, y_test)
        }
        
        self.logger.log(2, "Data pairs prepared", {
            "train_samples": len(X_train),
            "val_samples": len(X_val) if X_val is not None else 0,
            "test_samples": len(X_test),
            "feature_dim": X_train.shape[1],
            "target_dim": 1 if y.ndim == 1 else y.shape[1]
        })
        
        return data_pairs

# ============================================================================
# 阶段 3: 模型自动选择
# ============================================================================

class ModelSelector:
    """模型自动选择模块"""
    
    def __init__(self, logger):
        self.logger = logger
        self.selected_model_type = None
        self.model_config = {}
        
    def analyze_data_characteristics(self, X_train, y_train):
        """
        分析数据特征，决定使用统计方法还是深度学习方法
        """
        self.logger.log(3, "Analyzing data characteristics for model selection")
        
        n_samples = len(X_train)
        n_features = X_train.shape[1]
        
        # 检测目标类型
        if y_train.ndim > 1 and y_train.shape[1] > 1:
            target_type = "multi_output"
        else:
            target_type = "single_output"
        
        # 检测非线性程度 (通过简单线性模型拟合度)
        from sklearn.linear_model import LinearRegression
        lr = LinearRegression()
        lr.fit(X_train[:min(1000, n_samples)], y_train[:min(1000, n_samples)])
        r2 = lr.score(X_train[:min(1000, n_samples)], y_train[:min(1000, n_samples)])
        
        characteristics = {
            "n_samples": n_samples,
            "n_features": n_features,
            "target_type": target_type,
            "linear_fit_r2": float(r2),
            "samples_per_feature": n_samples / n_features if n_features > 0 else 0,
            "is_high_dimensional": n_features > n_samples * 0.1,
            "is_nonlinear": r2 < 0.7  # R2低说明非线性
        }
        
        self.logger.log(3, "Data characteristics", characteristics)
        return characteristics
    
    def select_model(self, characteristics, force_dl=False):
        """
        根据数据特征选择模型
        """
        self.logger.log(3, "Selecting appropriate model")
        
        n_samples = characteristics["n_samples"]
        n_features = characteristics["n_features"]
        is_nonlinear = characteristics["is_nonlinear"]
        is_high_dimensional = characteristics["is_high_dimensional"]
        
        candidates = []
        
        # 统计模型候选
        if n_samples < 1000 or not is_nonlinear:
            candidates.extend(['ridge', 'lasso'])
        if not is_high_dimensional:
            candidates.extend(['random_forest', 'gradient_boosting'])
        
        # 深度学习候选 (样本足够且非线性)
        if TORCH_AVAILABLE and force_dl or (n_samples >= 1000 and is_nonlinear and n_features > 5):
            candidates.append('neural_network')
        
        self.selected_model_type = candidates[0] if candidates else 'random_forest'
        
        self.model_config = {
            'model_type': self.selected_model_type,
            'candidates': candidates,
            'rationale': self._get_rationale(characteristics)
        }
        
        self.logger.log(3, f"Selected model: {self.selected_model_type}", self.model_config)
        return self.model_config
    
    def _get_rationale(self, chars):
        """获取模型选择理由"""
        reasons = []
        if chars["n_samples"] < 1000:
            reasons.append("小样本，优先使用统计模型")
        if chars["is_nonlinear"]:
            reasons.append("数据非线性特征明显")
        if chars["is_high_dimensional"]:
            reasons.append("高维数据，使用正则化模型")
        return reasons

# ============================================================================
# 阶段 4: 模型训练
# ============================================================================

# 仅在PyTorch可用时定义神经网络类
if TORCH_AVAILABLE:
    class NeuralNetworkRegressor(nn.Module):
        """简单的神经网络回归模型"""
        
        def __init__(self, input_dim, output_dim, hidden_dims=[128, 64, 32]):
            super().__init__()
            layers = []
            prev_dim = input_dim
            for hidden_dim in hidden_dims:
                layers.extend([
                    nn.Linear(prev_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.BatchNorm1d(hidden_dim)
                ])
                prev_dim = hidden_dim
            layers.append(nn.Linear(prev_dim, output_dim))
            self.network = nn.Sequential(*layers)
        
        def forward(self, x):
            return self.network(x)


class ModelTrainer:
    """模型训练模块"""
    
    def __init__(self, logger):
        self.logger = logger
        self.model = None
        self.training_history = {}
        
    def create_model(self, model_type, input_dim, output_dim=1):
        """创建模型实例"""
        self.logger.log(4, f"Creating {model_type} model")
        
        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        elif model_type == 'lasso':
            self.model = Lasso(alpha=0.1)
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == 'neural_network' and TORCH_AVAILABLE:
            self.model = NeuralNetworkRegressor(input_dim, output_dim)
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        
        return self.model
    
    def train(self, data_pairs, model_type='auto', epochs=100, batch_size=32, lr=0.001):
        """
        训练模型
        """
        X_train, y_train = data_pairs['train']
        X_val, y_val = data_pairs['val'] if data_pairs['val'][0] is not None else (None, None)
        
        input_dim = X_train.shape[1]
        output_dim = 1 if y_train.ndim == 1 else y_train.shape[1]
        
        # 创建模型
        self.create_model(model_type, input_dim, output_dim)
        
        self.logger.log(4, f"Starting training with {model_type}")
        
        if model_type == 'neural_network' and TORCH_AVAILABLE:
            return self._train_neural_network(X_train, y_train, X_val, y_val, epochs, batch_size, lr)
        else:
            return self._train_sklearn_model(X_train, y_train, X_val, y_val)
    
    def _train_sklearn_model(self, X_train, y_train, X_val, y_val):
        """训练 sklearn 模型"""
        self.model.fit(X_train, y_train)
        
        # 评估
        train_pred = self.model.predict(X_train)
        train_metrics = self._calculate_metrics(y_train, train_pred)
        
        val_metrics = None
        if X_val is not None:
            val_pred = self.model.predict(X_val)
            val_metrics = self._calculate_metrics(y_val, val_pred)
        
        self.training_history = {
            'train_metrics': train_metrics,
            'val_metrics': val_metrics
        }
        
        self.logger.log(4, "Training complete", self.training_history)
        return self.training_history
    
    def _train_neural_network(self, X_train, y_train, X_val, y_val, epochs, batch_size, lr):
        """训练神经网络"""
        # 转换为 torch tensors
        X_train_t = torch.FloatTensor(X_train)
        y_train_t = torch.FloatTensor(y_train).reshape(-1, 1) if y_train.ndim == 1 else torch.FloatTensor(y_train)
        
        train_dataset = TensorDataset(X_train_t, y_train_t)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)
        
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(epochs):
            self.model.train()
            train_losses = []
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())
            
            avg_train_loss = np.mean(train_losses)
            history['train_loss'].append(avg_train_loss)
            
            # 验证
            if X_val is not None:
                self.model.eval()
                with torch.no_grad():
                    X_val_t = torch.FloatTensor(X_val)
                    y_val_t = torch.FloatTensor(y_val).reshape(-1, 1) if y_val.ndim == 1 else torch.FloatTensor(y_val)
                    val_pred = self.model(X_val_t)
                    val_loss = criterion(val_pred, y_val_t).item()
                    history['val_loss'].append(val_loss)
                    scheduler.step(val_loss)
            
            if (epoch + 1) % 20 == 0:
                self.logger.log(4, f"Epoch {epoch+1}/{epochs}, Loss: {avg_train_loss:.6f}")
        
        self.training_history = history
        return history
    
    def _calculate_metrics(self, y_true, y_pred):
        """计算评估指标"""
        return {
            'mse': float(mean_squared_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'r2': float(r2_score(y_true, y_pred))
        }
    
    def save_model(self, path):
        """保存模型"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # 检查是否为PyTorch神经网络模型
        is_nn_model = TORCH_AVAILABLE and hasattr(self.model, 'forward') and callable(getattr(self.model, 'forward', None))
        
        if is_nn_model:
            torch.save(self.model.state_dict(), path)
        else:
            import joblib
            joblib.dump(self.model, path)
        
        self.logger.log(4, f"Model saved to {path}")
        return path

# ============================================================================
# 阶段 5: 预测与评估
# ============================================================================

class Predictor:
    """预测模块"""
    
    def __init__(self, logger, model, scaler=None):
        self.logger = logger
        self.model = model
        self.scaler = scaler
        
    def predict(self, X):
        """执行预测"""
        self.logger.log(5, f"Making predictions on {len(X)} samples")
        
        # 检查是否为PyTorch神经网络模型
        is_nn_model = TORCH_AVAILABLE and hasattr(self.model, 'forward') and callable(getattr(self.model, 'forward', None))
        
        if is_nn_model:
            self.model.eval()
            with torch.no_grad():
                X_t = torch.FloatTensor(X)
                predictions = self.model(X_t).numpy()
        else:
            predictions = self.model.predict(X)
        
        return predictions
    
    def evaluate(self, X_test, y_test):
        """评估模型性能"""
        self.logger.log(5, "Evaluating model performance")
        
        predictions = self.predict(X_test)
        
        metrics = {
            'mse': float(mean_squared_error(y_test, predictions)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, predictions))),
            'mae': float(mean_absolute_error(y_test, predictions)),
            'r2': float(r2_score(y_test, predictions)),
            'mape': float(np.mean(np.abs((y_test - predictions) / (y_test + 1e-8))) * 100)
        }
        
        self.logger.log(5, "Evaluation complete", metrics)
        return metrics, predictions
    
    def cross_validate(self, X, y, cv=5):
        """交叉验证"""
        self.logger.log(5, f"Running {cv}-fold cross-validation")
        
        # 检查是否为PyTorch神经网络模型
        is_nn_model = TORCH_AVAILABLE and hasattr(self.model, 'forward') and callable(getattr(self.model, 'forward', None))
        
        if is_nn_model:
            self.logger.log(5, "Skipping CV for neural network (use train/val split instead)")
            return None
        
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='r2')
        
        cv_results = {
            'cv_scores': scores.tolist(),
            'mean_cv_score': float(scores.mean()),
            'std_cv_score': float(scores.std())
        }
        
        self.logger.log(5, "Cross-validation complete", cv_results)
        return cv_results

# ============================================================================
# 主控管道
# ============================================================================

class PredictionPipeline:
    """完整预测管道"""
    
    def __init__(self, log_dir="./logs"):
        self.logger = StageLogger(log_dir)
        self.data_processor = DataProcessor(self.logger)
        self.feature_selector = FeatureSelector(self.logger)
        self.model_selector = ModelSelector(self.logger)
        self.model_trainer = ModelTrainer(self.logger)
        self.predictor = None
        self.results = {}
        
    def run(self, file_path, feature_cols=None, target_cols=None, 
            test_size=0.2, val_size=0.1, force_model=None,
            output_dir="./output"):
        """
        运行完整流程
        
        :param file_path: 数据文件路径
        :param feature_cols: 特征列名 (None=自动检测)
        :param target_cols: 目标列名 (None=自动检测)
        :param test_size: 测试集比例
        :param val_size: 验证集比例
        :param force_model: 强制使用特定模型 (None=自动选择)
        :param output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.log(0, "=" * 50)
        self.logger.log(0, "Starting Prediction Pipeline")
        self.logger.log(0, f"Input file: {file_path}")
        
        try:
            # 阶段 1: 数据处理
            self.data_processor.load_data(file_path)
            analysis = self.data_processor.analyze_data()
            df_processed = self.data_processor.preprocess(
                feature_cols, target_cols, auto_detect=True
            )
            
            # 阶段 2: 特征选择与数据对构建
            selected_features = self.feature_selector.select_features(
                df_processed, 
                self.data_processor.feature_columns,
                self.data_processor.target_columns,
                method='correlation',
                threshold=0.05
            )
            
            data_pairs = self.feature_selector.prepare_data_pairs(
                df_processed, selected_features, 
                self.data_processor.target_columns,
                test_size, val_size
            )
            
            # 阶段 3: 模型选择
            X_train, _ = data_pairs['train']
            y_train = data_pairs['train'][1]
            
            characteristics = self.model_selector.analyze_data_characteristics(X_train, y_train)
            
            model_config = self.model_selector.select_model(characteristics)
            model_type = force_model if force_model else model_config['model_type']
            
            # 阶段 4: 训练
            self.model_trainer.train(data_pairs, model_type=model_type)
            
            # 阶段 5: 预测与评估
            self.predictor = Predictor(
                self.logger, 
                self.model_trainer.model,
                self.data_processor.scaler
            )
            
            X_test, y_test = data_pairs['test']
            metrics, predictions = self.predictor.evaluate(X_test, y_test)
            
            # 交叉验证
            X_full = np.vstack([data_pairs['train'][0], data_pairs['test'][0]])
            y_full = np.concatenate([data_pairs['train'][1], data_pairs['test'][1]])
            cv_results = self.predictor.cross_validate(X_full, y_full)
            
            # 保存结果
            self.results = {
                'input_file': file_path,
                'data_analysis': analysis,
                'selected_features': selected_features,
                'model_type': model_type,
                'model_config': model_config,
                'test_metrics': metrics,
                'cv_results': cv_results,
                'predictions_sample': predictions[:10].tolist() if len(predictions) > 10 else predictions.tolist()
            }
            
            # 保存模型
            model_path = os.path.join(output_dir, f"model_{model_type}.pkl")
            self.model_trainer.save_model(model_path)
            
            # 保存报告
            report_path = self.logger.save_report(self.results, "final_report.json")
            
            self.logger.log(0, "=" * 50)
            self.logger.log(0, "Pipeline completed successfully!")
            self.logger.log(0, f"Model saved to: {model_path}")
            self.logger.log(0, f"Report saved to: {report_path}")
            
            return self.results
            
        except Exception as e:
            self.logger.log(0, f"ERROR: {str(e)}")
            raise
    
    def predict_new(self, new_data_path):
        """对新的数据进行预测"""
        if self.predictor is None:
            raise ValueError("Model not trained yet. Run pipeline first.")
        
        # 加载并预处理新数据
        new_df = pd.read_csv(new_data_path)
        
        # 应用相同的预处理（只使用原始特征列，不包含目标列）
        for col, encoder in self.data_processor.encoders.items():
            if col in new_df.columns:
                new_df[col] = encoder.transform(new_df[col].astype(str))
        
        # 使用原始特征列（训练时使用的全部特征，不是选择后的子集）
        # scaler是在全部特征上训练的，所以需要使用原始特征
        original_features = self.data_processor.feature_columns
        X_new_all = new_df[original_features].values
        X_new_all = self.data_processor.scaler.transform(X_new_all)
        
        # 转换为DataFrame以便选择子集
        X_new_df = pd.DataFrame(X_new_all, columns=original_features)
        
        # 只使用选中的特征
        selected_features = self.feature_selector.selected_features
        X_new = X_new_df[selected_features].values
        
        predictions = self.predictor.predict(X_new)
        return predictions


# ============================================================================
# 自测函数
# ============================================================================

def generate_test_data(n_samples=1000, n_features=10, output_dir="./test_data"):
    """生成测试数据用于自测"""
    os.makedirs(output_dir, exist_ok=True)
    
    np.random.seed(42)
    
    # 生成特征
    X = np.random.randn(n_samples, n_features)
    
    # 生成目标 (带一些非线性关系)
    y = (
        2 * X[:, 0] + 
        3 * X[:, 1]**2 + 
        np.sin(X[:, 2]) + 
        X[:, 3] * X[:, 4] + 
        0.5 * np.random.randn(n_samples)  # 噪声
    )
    
    # 创建DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # 保存
    train_path = os.path.join(output_dir, "train_data.csv")
    df.to_csv(train_path, index=False)
    
    # 生成测试数据
    X_test = np.random.randn(200, n_features)
    y_test = (
        2 * X_test[:, 0] + 
        3 * X_test[:, 1]**2 + 
        np.sin(X_test[:, 2]) + 
        X_test[:, 3] * X_test[:, 4] + 
        0.5 * np.random.randn(200)
    )
    df_test = pd.DataFrame(X_test, columns=feature_names)
    df_test['target'] = y_test
    
    test_path = os.path.join(output_dir, "test_data.csv")
    df_test.to_csv(test_path, index=False)
    
    print(f"[TEST] Generated test data: {train_path}")
    return train_path, test_path


def run_self_test():
    """运行自测"""
    print("\n" + "=" * 60)
    print("RUNNING SELF-TEST")
    print("=" * 60)
    
    # 生成测试数据
    train_path, test_path = generate_test_data(n_samples=1000, n_features=10)
    
    # 运行管道
    pipeline = PredictionPipeline(log_dir="./test_logs")
    
    results = pipeline.run(
        file_path=train_path,
        feature_cols=None,  # 自动检测
        target_cols=None,   # 自动检测
        test_size=0.2,
        val_size=0.1,
        output_dir="./test_output"
    )
    
    # 验证结果
    print("\n" + "-" * 60)
    print("SELF-TEST RESULTS:")
    print("-" * 60)
    print(f"✓ Data processed: {results['data_analysis']['total_rows']} samples")
    print(f"✓ Features selected: {len(results['selected_features'])}")
    print(f"✓ Model type: {results['model_type']}")
    print(f"✓ Test R² score: {results['test_metrics']['r2']:.4f}")
    print(f"✓ Test RMSE: {results['test_metrics']['rmse']:.4f}")
    
    if results['cv_results']:
        print(f"✓ CV R² score: {results['cv_results']['mean_cv_score']:.4f} (+/- {results['cv_results']['std_cv_score']:.4f})")
    
    # 测试新数据预测
    print("\n[TEST] Testing prediction on new data...")
    new_predictions = pipeline.predict_new(test_path)
    print(f"✓ Predictions shape: {new_predictions.shape}")
    print(f"✓ Sample predictions: {new_predictions[:5]}")
    
    print("\n" + "=" * 60)
    print("SELF-TEST PASSED ✓")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 运行自测
    run_self_test()
