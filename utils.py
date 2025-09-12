# utils.py - 工具函数

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
import time
import functools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_stock_code(code: str, market: str = "A股") -> bool:
        """验证股票代码格式"""
        if not code or not isinstance(code, str):
            return False
        
        code = code.strip().upper()
        
        if market == "A股":
            # A股代码：6位数字
            return len(code) == 6 and code.isdigit()
        elif market == "美股":
            # 美股代码：1-5位字母
            return 1 <= len(code) <= 5 and code.isalpha()
        elif market == "港股":
            # 港股代码：5位数字或带HK后缀
            return (len(code) == 5 and code.isdigit()) or code.endswith('.HK')
        
        return False
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """验证DataFrame是否包含必需的列"""
        if df is None or df.empty:
            return False
        
        return all(col in df.columns for col in required_columns)
    
    @staticmethod
    def clean_numeric_data(data: pd.Series) -> pd.Series:
        """清理数值数据"""
        # 移除非数值
        data = pd.to_numeric(data, errors='coerce')
        
        # 移除异常值 (使用IQR方法)
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        data = data.clip(lower=lower_bound, upper=upper_bound)
        
        return data

class PerformanceMonitor:
    """性能监控器"""
    
    @staticmethod
    def timer(func):
        """函数执行时间装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} 执行时间: {execution_time:.2f}秒")
            
            return result
        return wrapper
    
    @staticmethod
    def cache_performance(cache_key: str, hit: bool, execution_time: float):
        """记录缓存性能"""
        status = "HIT" if hit else "MISS"
        logger.info(f"Cache {status}: {cache_key}, 执行时间: {execution_time:.2f}秒")

class TechnicalIndicators:
    """技术指标计算工具类"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, window: int) -> pd.Series:
        """计算简单移动平均"""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, window: int) -> pd.Series:
        """计算指数移动平均"""
        return data.ewm(span=window).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD指标"""
        exp1 = data.ewm(span=fast).mean()
        exp2 = data.ewm(span=slow).mean()
        
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        
        return macd, macd_signal, macd_histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, window: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算布林带"""
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """计算KDJ指标"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return k_percent, d_percent

class MarketUtils:
    """市场工具类"""
    
    @staticmethod
    def is_trading_day(date: datetime = None) -> bool:
        """判断是否为交易日"""
        if date is None:
            date = datetime.now()
        
        # 简单判断：周一到周五为交易日
        # 实际应该考虑节假日
        return date.weekday() < 5
    
    @staticmethod
    def get_trading_hours(market: str = "A股") -> Dict[str, str]:
        """获取交易时间"""
        trading_hours = {
            "A股": {
                "morning_start": "09:30",
                "morning_end": "11:30",
                "afternoon_start": "13:00", 
                "afternoon_end": "15:00"
            },
            "美股": {
                "regular_start": "09:30",  # EST
                "regular_end": "16:00"     # EST
            },
            "港股": {
                "morning_start": "09:30",
                "morning_end": "12:00",
                "afternoon_start": "13:00",
                "afternoon_end": "16:00"
            }
        }
        
        return trading_hours.get(market, {})
    
    @staticmethod
    def format_market_cap(market_cap: float) -> str:
        """格式化市值显示"""
        if market_cap >= 1e12:
            return f"{market_cap/1e12:.2f}万亿"
        elif market_cap >= 1e8:
            return f"{market_cap/1e8:.2f}亿"
        elif market_cap >= 1e4:
            return f"{market_cap/1e4:.2f}万"
        else:
            return f"{market_cap:.2f}"
    
    @staticmethod
    def calculate_change_percent(current: float, previous: float) -> float:
        """计算涨跌幅"""
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100

class UIHelper:
    """UI辅助工具类"""
    
    @staticmethod
    def display_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
        """显示指标卡片"""
        st.metric(
            label=title,
            value=value,
            delta=delta,
            help=help_text
        )
    
    @staticmethod
    def display_score_badge(score: float, label: str = "评分"):
        """显示评分徽章"""
        if score >= 80:
            color = "success"
            emoji = "🟢"
        elif score >= 60:
            color = "warning"
            emoji = "🟡"
        else:
            color = "error"
            emoji = "🔴"
        
        st.markdown(f"""
        <div style="
            background-color: {'#d4edda' if color == 'success' else '#fff3cd' if color == 'warning' else '#f8d7da'};
            color: {'#155724' if color == 'success' else '#856404' if color == 'warning' else '#721c24'};
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
        ">
            {emoji} <strong>{label}: {score:.1f}/100</strong>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_recommendation(recommendation: Dict[str, Any]):
        """显示推荐建议"""
        rec = recommendation
        
        color_map = {
            "success": "#d4edda",
            "warning": "#fff3cd", 
            "error": "#f8d7da",
            "info": "#d1ecf1"
        }
        
        text_color_map = {
            "success": "#155724",
            "warning": "#856404",
            "error": "#721c24", 
            "info": "#0c5460"
        }
        
        bg_color = color_map.get(rec.get('color', 'info'), color_map['info'])
        text_color = text_color_map.get(rec.get('color', 'info'), text_color_map['info'])
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            border-left: 5px solid {text_color};
        ">
            <h2>{rec.get('emoji', '📊')} {rec.get('level', '未知')}</h2>
            <h3>投资建议: {rec.get('action', '观望')}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_progress_bar(current: int, total: int, label: str = "进度"):
        """创建进度条"""
        progress = current / total if total > 0 else 0
        st.progress(progress)
        st.caption(f"{label}: {current}/{total} ({progress:.1%})")

class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle_api_error(func):
        """API错误处理装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API调用失败: {func.__name__}, 错误: {str(e)}")
                st.error(f"数据获取失败: {str(e)[:100]}")
                return None
        return wrapper
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
        """安全除法"""
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except:
            return default
    
    @staticmethod
    def safe_get_dict_value(data: Dict, key: str, default: Any = None) -> Any:
        """安全获取字典值"""
        try:
            return data.get(key, default)
        except:
            return default

class DataFormatter:
    """数据格式化器"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "CNY") -> str:
        """格式化货币"""
        if currency == "CNY":
            if amount >= 1e8:
                return f"¥{amount/1e8:.2f}亿"
            elif amount >= 1e4:
                return f"¥{amount/1e4:.2f}万"
            else:
                return f"¥{amount:.2f}"
        else:  # USD
            if amount >= 1e9:
                return f"${amount/1e9:.2f}B"
            elif amount >= 1e6:
                return f"${amount/1e6:.2f}M"
            elif amount >= 1e3:
                return f"${amount/1e3:.2f}K"
            else:
                return f"${amount:.2f}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """格式化百分比"""
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def format_large_number(number: float) -> str:
        """格式化大数字"""
        if number >= 1e12:
            return f"{number/1e12:.2f}T"
        elif number >= 1e9:
            return f"{number/1e9:.2f}B"
        elif number >= 1e6:
            return f"{number/1e6:.2f}M"
        elif number >= 1e3:
            return f"{number/1e3:.2f}K"
        else:
            return f"{number:.2f}"
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化日期时间"""
        try:
            return dt.strftime(format_str)
        except:
            return "未知时间"

# 全局工具实例
validator = DataValidator()
performance_monitor = PerformanceMonitor()
technical_indicators = TechnicalIndicators()
market_utils = MarketUtils()
ui_helper = UIHelper()
error_handler = ErrorHandler()
data_formatter = DataFormatter()