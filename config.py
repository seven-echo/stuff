# config.py - 配置文件

import os
from typing import Dict, Any

class Config:
    """系统配置类"""
    
    # 应用基础配置
    APP_NAME = "全维度AI选股系统"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Streamlit配置
    STREAMLIT_CONFIG = {
        "page_title": "🧠 全维度AI选股系统",
        "page_icon": "🧠",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # 数据源配置
    DATA_SOURCES = {
        "openbb": {
            "enabled": True,
            "api_key": os.getenv("OPENBB_API_KEY", ""),
            "base_url": "https://api.openbb.co"
        },
        "akshare": {
            "enabled": True,
            "timeout": 30,
            "retry_times": 3
        },
        "yfinance": {
            "enabled": True,
            "timeout": 15
        }
    }
    
    # 分析权重配置
    ANALYSIS_WEIGHTS = {
        "全维度分析": {
            "technical": 0.4,
            "fundamental": 0.3,
            "sentiment": 0.2,
            "event": 0.1
        },
        "技术面优先": {
            "technical": 0.6,
            "fundamental": 0.2,
            "sentiment": 0.1,
            "event": 0.1
        },
        "基本面优先": {
            "technical": 0.2,
            "fundamental": 0.6,
            "sentiment": 0.1,
            "event": 0.1
        },
        "情绪面优先": {
            "technical": 0.3,
            "fundamental": 0.2,
            "sentiment": 0.4,
            "event": 0.1
        }
    }
    
    # 技术指标配置
    TECHNICAL_CONFIG = {
        "ma_periods": [5, 10, 20, 60, 120, 250],
        "rsi_period": 14,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "kdj_period": 9,
        "volume_ma_period": 20
    }
    
    # 评分阈值配置
    SCORING_THRESHOLDS = {
        "recommendation": {
            "强烈推荐": 85,
            "推荐买入": 75,
            "值得关注": 65,
            "中性观望": 50,
            "谨慎观望": 35,
            "建议回避": 0
        },
        "rsi": {
            "oversold": 30,
            "overbought": 70
        },
        "pe_ratio": {
            "low": 10,
            "high": 25,
            "very_high": 40
        },
        "roe": {
            "excellent": 0.20,
            "good": 0.15,
            "average": 0.10
        }
    }
    
    # 缓存配置
    CACHE_CONFIG = {
        "stock_data_ttl": 1800,  # 30分钟
        "news_data_ttl": 3600,   # 1小时
        "fundamental_ttl": 86400  # 24小时
    }
    
    # 新闻和情感分析配置
    NEWS_CONFIG = {
        "max_articles": 15,
        "sentiment_threshold": {
            "positive": 0.2,
            "negative": -0.2
        },
        "news_sources": [
            "openbb",
            "reuters", 
            "bloomberg",
            "cnbc"
        ]
    }
    
    # 风险控制配置
    RISK_CONFIG = {
        "max_daily_requests": 1000,
        "rate_limit_per_minute": 60,
        "max_symbols_per_request": 10,
        "timeout_seconds": 30
    }
    
    # 用户界面配置
    UI_CONFIG = {
        "default_symbols": {
            "A股": "000001",
            "美股": "AAPL",
            "港股": "00700"
        },
        "chart_height": 600,
        "max_chart_points": 200,
        "color_scheme": {
            "positive": "#00C851",
            "negative": "#FF4444", 
            "neutral": "#33B5E5"
        }
    }
    
    # 免费版限制
    FREE_TIER_LIMITS = {
        "daily_analysis": 5,
        "symbols_per_analysis": 1,
        "historical_days": 60,
        "technical_indicators": 10
    }
    
    # 专业版功能
    PRO_FEATURES = {
        "unlimited_analysis": True,
        "advanced_indicators": True,
        "portfolio_analysis": True,
        "real_time_alerts": True,
        "api_access": True,
        "priority_support": True
    }

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # 生产环境缓存配置
    REDIS_URL = os.getenv("REDIS_URL", "")
    
    # 生产环境安全配置
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/stock_analyzer.log"

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    # 开发环境缓存配置
    CACHE_CONFIG = {
        "stock_data_ttl": 300,   # 5分钟
        "news_data_ttl": 600,    # 10分钟
        "fundamental_ttl": 3600  # 1小时
    }
    
    # 开发环境限制更宽松
    FREE_TIER_LIMITS = {
        "daily_analysis": 50,
        "symbols_per_analysis": 5,
        "historical_days": 365,
        "technical_indicators": 50
    }
    
    # 日志配置
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "stock_analyzer.log"

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 测试环境使用模拟数据
    USE_MOCK_DATA = True
    
    # 测试环境缓存配置
    CACHE_CONFIG = {
        "stock_data_ttl": 60,
        "news_data_ttl": 60,
        "fundamental_ttl": 60
    }

# 根据环境变量选择配置
def get_config() -> Config:
    """根据环境变量返回对应的配置类"""
    env = os.getenv("FLASK_ENV", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# 导出当前配置
current_config = get_config()