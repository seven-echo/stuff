# comprehensive_stock_analyzer.py
# 全维度AI选股系统 - 基于OpenBB + AkShare

import streamlit as st
from openbb import obb
import akshare as ak
import pandas as pd
import numpy as np
from textblob import TextBlob
import yfinance as yf
from datetime import datetime, timedelta
import requests
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="🧠 全维度AI选股系统",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-high {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .recommendation-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .recommendation-low {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏配置
st.sidebar.title("🧠 AI选股配置")
st.sidebar.markdown("---")

analysis_mode = st.sidebar.selectbox(
    "分析模式", 
    ["全维度分析", "技术面优先", "基本面优先", "情绪面优先"],
    help="选择不同的分析重点"
)

market_selection = st.sidebar.multiselect(
    "选择市场",
    ["A股", "美股", "港股"],
    default=["A股"],
    help="支持多市场同时分析"
)

# 高级设置
st.sidebar.markdown("### 🔧 高级设置")
enable_news_analysis = st.sidebar.checkbox("启用新闻情绪分析", value=True)
enable_fundamental = st.sidebar.checkbox("启用基本面分析", value=True)
risk_tolerance = st.sidebar.selectbox("风险偏好", ["保守", "平衡", "激进"])

# 主标题
st.title("🧠 全维度AI选股系统")
st.markdown("**技术面 + 基本面 + 情绪面 + 突发事件** 四维一体智能分析")
st.markdown("---")

# 核心分析类
class ComprehensiveStockAnalyzer:
    def __init__(self):
        self.openbb = obb
        
    def get_technical_analysis(self, symbol, market="A股"):
        """技术面分析"""
        try:
            if market == "A股":
                # 使用AkShare获取A股数据
                data = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date="20240101",
                    adjust="qfq"
                )
                
                if len(data) < 20:
                    return None
                
                # 计算技术指标
                data['MA5'] = data['收盘'].rolling(5).mean()
                data['MA10'] = data['收盘'].rolling(10).mean()
                data['MA20'] = data['收盘'].rolling(20).mean()
                data['MA60'] = data['收盘'].rolling(60).mean()
                
                # RSI计算
                delta = data['收盘'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))
                
                # MACD计算
                exp1 = data['收盘'].ewm(span=12).mean()
                exp2 = data['收盘'].ewm(span=26).mean()
                data['MACD'] = exp1 - exp2
                data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
                data['MACD_histogram'] = data['MACD'] - data['MACD_signal']
                
                # KDJ计算 (简化版)
                low_list = data['最低'].rolling(9).min()
                high_list = data['最高'].rolling(9).max()
                rsv = (data['收盘'] - low_list) / (high_list - low_list) * 100
                data['KDJ_K'] = rsv.ewm(com=2).mean()
                data['KDJ_D'] = data['KDJ_K'].ewm(com=2).mean()
                data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']
                
                latest = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else latest
                
                # 技术面评分
                tech_score = 50
                signals = []
                
                # 均线评分
                if latest['收盘'] > latest['MA5'] > latest['MA20'] > latest['MA60']:
                    tech_score += 25
                    signals.append("完美多头排列")
                elif latest['收盘'] > latest['MA5'] > latest['MA20']:
                    tech_score += 15
                    signals.append("短期多头")
                elif latest['收盘'] < latest['MA5'] < latest['MA20']:
                    tech_score -= 15
                    signals.append("空头排列")
                
                # RSI评分
                if 30 <= latest['RSI'] <= 70:
                    tech_score += 15
                    signals.append("RSI健康")
                elif latest['RSI'] < 30:
                    tech_score += 20
                    signals.append("RSI超卖")
                elif latest['RSI'] > 70:
                    tech_score -= 10
                    signals.append("RSI超买")
                
                # MACD评分
                if latest['MACD'] > latest['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
                    tech_score += 20
                    signals.append("MACD金叉")
                elif latest['MACD'] > latest['MACD_signal']:
                    tech_score += 10
                    signals.append("MACD多头")
                elif latest['MACD'] < latest['MACD_signal']:
                    tech_score -= 5
                    signals.append("MACD空头")
                
                # KDJ评分
                if latest['KDJ_K'] > latest['KDJ_D'] and latest['KDJ_K'] < 80:
                    tech_score += 10
                    signals.append("KDJ金叉")
                elif latest['KDJ_K'] > 80:
                    tech_score -= 5
                    signals.append("KDJ超买")
                elif latest['KDJ_K'] < 20:
                    tech_score += 15
                    signals.append("KDJ超卖")
                
                # 成交量评分
                avg_vol = data['成交量'].tail(20).mean()
                if latest['成交量'] > avg_vol * 2:
                    tech_score += 15
                    signals.append("巨量放大")
                elif latest['成交量'] > avg_vol * 1.5:
                    tech_score += 10
                    signals.append("放量上涨")
                elif latest['成交量'] < avg_vol * 0.5:
                    tech_score -= 5
                    signals.append("缩量")
                
                return {
                    'score': max(0, min(100, tech_score)),
                    'price': latest['收盘'],
                    'change': (latest['收盘'] - prev['收盘']) / prev['收盘'] * 100,
                    'ma_trend': "多头" if latest['MA5'] > latest['MA20'] else "空头",
                    'rsi': latest['RSI'],
                    'macd': latest['MACD'],
                    'kdj_k': latest['KDJ_K'],
                    'kdj_d': latest['KDJ_D'],
                    'volume_ratio': latest['成交量'] / avg_vol,
                    'signals': signals,
                    'data': data
                }
                
            else:  # 美股、港股使用OpenBB
                try:
                    # 获取股价数据
                    historical_data = self.openbb.equity.price.historical(
                        symbol=symbol,
                        start_date="2024-01-01"
                    )
                    
                    if not historical_data or len(historical_data.results) < 20:
                        return None
                    
                    # 转换为DataFrame
                    df = pd.DataFrame([vars(result) for result in historical_data.results])
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # 计算技术指标
                    df['MA20'] = df['close'].rolling(20).mean()
                    df['MA50'] = df['close'].rolling(50).mean()
                    
                    # RSI
                    delta = df['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    latest = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else latest
                    
                    tech_score = 60  # 美股基础分稍高
                    signals = []
                    
                    if latest['close'] > latest['MA20'] > latest['MA50']:
                        tech_score += 20
                        signals.append("均线多头")
                    
                    if 30 <= latest['RSI'] <= 70:
                        tech_score += 15
                        signals.append("RSI健康")
                    elif latest['RSI'] < 30:
                        tech_score += 20
                        signals.append("RSI超卖")
                    
                    return {
                        'score': tech_score,
                        'price': latest['close'],
                        'change': (latest['close'] - prev['close']) / prev['close'] * 100,
                        'ma_trend': "多头" if latest['close'] > latest['MA20'] else "空头",
                        'rsi': latest['RSI'],
                        'signals': signals,
                        'data': df
                    }
                    
                except Exception as e:
                    st.error(f"OpenBB数据获取失败: {e}")
                    return None
                
        except Exception as e:
            st.error(f"技术分析失败: {e}")
            return None
    
    def get_fundamental_analysis(self, symbol, market="A股"):
        """基本面分析"""
        try:
            if market == "美股":
                # 使用OpenBB获取基本面数据
                try:
                    # 获取财务指标
                    metrics = self.openbb.equity.fundamental.metrics(symbol=symbol)
                    if metrics and metrics.results:
                        metrics_data = vars(metrics.results[0])
                        
                        fundamental_score = 50
                        analysis_points = []
                        
                        # PE比率评分
                        pe_ratio = metrics_data.get('pe_ratio')
                        if pe_ratio:
                            if 10 <= pe_ratio <= 25:
                                fundamental_score += 15
                                analysis_points.append(f"PE合理({pe_ratio:.1f})")
                            elif pe_ratio < 10:
                                fundamental_score += 10
                                analysis_points.append(f"PE较低({pe_ratio:.1f})")
                            elif pe_ratio > 40:
                                fundamental_score -= 10
                                analysis_points.append(f"PE偏高({pe_ratio:.1f})")
                        
                        # ROE评分
                        roe = metrics_data.get('return_on_equity')
                        if roe:
                            if roe > 0.20:
                                fundamental_score += 25
                                analysis_points.append(f"ROE优秀({roe:.1%})")
                            elif roe > 0.15:
                                fundamental_score += 15
                                analysis_points.append(f"ROE良好({roe:.1%})")
                            elif roe > 0.10:
                                fundamental_score += 5
                                analysis_points.append(f"ROE一般({roe:.1%})")
                            else:
                                fundamental_score -= 10
                                analysis_points.append(f"ROE较低({roe:.1%})")
                        
                        # 债务比率评分
                        debt_to_equity = metrics_data.get('debt_to_equity')
                        if debt_to_equity:
                            if debt_to_equity < 0.3:
                                fundamental_score += 10
                                analysis_points.append("负债率健康")
                            elif debt_to_equity > 0.7:
                                fundamental_score -= 10
                                analysis_points.append("负债率偏高")
                        
                        return {
                            'score': min(100, max(0, fundamental_score)),
                            'pe_ratio': pe_ratio,
                            'roe': roe,
                            'debt_to_equity': debt_to_equity,
                            'market_cap': metrics_data.get('market_cap'),
                            'analysis_points': analysis_points,
                            'summary': f"PE: {pe_ratio:.1f}, ROE: {roe:.1%}" if pe_ratio and roe else "数据不完整"
                        }
                        
                except Exception as e:
                    # 备选方案：使用yfinance
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    fundamental_score = 50
                    analysis_points = []
                    
                    pe_ratio = info.get('trailingPE')
                    if pe_ratio and 10 <= pe_ratio <= 25:
                        fundamental_score += 15
                        analysis_points.append(f"PE合理({pe_ratio:.1f})")
                    
                    roe = info.get('returnOnEquity')
                    if roe and roe > 0.15:
                        fundamental_score += 15
                        analysis_points.append(f"ROE良好({roe:.1%})")
                    
                    return {
                        'score': fundamental_score,
                        'pe_ratio': pe_ratio,
                        'roe': roe,
                        'market_cap': info.get('marketCap'),
                        'analysis_points': analysis_points,
                        'summary': f"PE: {pe_ratio:.1f}" if pe_ratio else "基本面数据有限"
                    }
                    
            else:  # A股基本面
                try:
                    # 获取A股财务数据
                    # 这里可以使用更多AkShare的财务数据接口
                    fundamental_score = 55  # A股基础分
                    analysis_points = ["A股基本面分析(简化版)"]
                    
                    # 可以添加更多A股特有的基本面指标
                    # 例如：市盈率、市净率、ROE等
                    
                    return {
                        'score': fundamental_score,
                        'analysis_points': analysis_points,
                        'summary': "A股基本面数据待完善"
                    }
                except:
                    return {
                        'score': 50,
                        'analysis_points': ["基本面数据获取失败"],
                        'summary': "数据暂时不可用"
                    }
                    
        except Exception as e:
            return {
                'score': 50,
                'analysis_points': [f"分析出错: {str(e)[:30]}"],
                'summary': "基本面分析失败"
            }
    
    def get_sentiment_analysis(self, symbol, company_name, market="A股"):
        """情绪面分析"""
        try:
            if market == "美股":
                try:
                    # 使用OpenBB获取新闻
                    news = self.openbb.news.company(symbol=symbol)
                    
                    if news and news.results:
                        sentiments = []
                        news_titles = []
                        
                        for article in news.results[:15]:  # 分析最近15条新闻
                            title = article.title
                            news_titles.append(title)
                            
                            # 使用TextBlob进行情感分析
                            blob = TextBlob(title)
                            sentiment = blob.sentiment.polarity
                            sentiments.append(sentiment)
                        
                        if sentiments:
                            avg_sentiment = np.mean(sentiments)
                            sentiment_std = np.std(sentiments)
                            
                            # 情绪评分 (-1到1转换为0到100)
                            sentiment_score = (avg_sentiment + 1) * 50
                            
                            # 根据情绪波动调整评分
                            if sentiment_std > 0.5:  # 情绪波动大
                                sentiment_score -= 10
                            
                            # 分类情绪
                            if avg_sentiment > 0.2:
                                mood = "积极"
                            elif avg_sentiment < -0.2:
                                mood = "消极"
                            else:
                                mood = "中性"
                            
                            return {
                                'score': max(0, min(100, sentiment_score)),
                                'avg_sentiment': avg_sentiment,
                                'sentiment_std': sentiment_std,
                                'news_count': len(news_titles),
                                'sample_news': news_titles[:5],
                                'mood': mood,
                                'analysis': f"新闻情绪{mood} (分析了{len(news_titles)}条新闻)"
                            }
                        
                except Exception as e:
                    st.warning(f"新闻获取失败: {e}")
            
            # 备选方案：基于关键词的简单情绪分析
            positive_keywords = ['增长', '盈利', '突破', '上涨', '利好', '收购', '合作', 'growth', 'profit', 'breakthrough']
            negative_keywords = ['下跌', '亏损', '风险', '调查', '诉讼', '减持', '预警', 'loss', 'risk', 'decline']
            
            sentiment_score = 50  # 中性基础分
            
            # 这里可以集成更多新闻API
            # 例如：新浪财经、东方财富、雪球等
            
            return {
                'score': sentiment_score,
                'mood': "中性",
                'analysis': "情绪分析功能待完善 - 建议集成更多新闻源"
            }
            
        except Exception as e:
            return {
                'score': 50,
                'mood': "未知",
                'analysis': f"情绪分析出错: {str(e)[:50]}"
            }
    
    def get_event_analysis(self, symbol, market="A股"):
        """突发事件分析"""
        try:
            event_score = 70  # 默认无重大事件
            risk_events = []
            positive_events = []
            
            # 这里可以集成多种事件监控API:
            # 1. 公司公告监控
            # 2. 行业政策监控  
            # 3. 宏观经济事件
            # 4. 国际市场事件
            
            # 简化版事件风险评估
            current_date = datetime.now()
            
            # 检查是否临近财报季
            if current_date.month in [1, 4, 7, 10]:
                risk_events.append("临近财报发布期")
                event_score -= 5
            
            # 检查是否为月末/季末
            if current_date.day > 25:
                risk_events.append("月末资金面紧张")
                event_score -= 3
            
            # 风险等级评估
            if event_score >= 80:
                risk_level = "低风险"
            elif event_score >= 60:
                risk_level = "中风险"
            else:
                risk_level = "高风险"
            
            return {
                'score': event_score,
                'risk_level': risk_level,
                'risk_events': risk_events,
                'positive_events': positive_events,
                'analysis': f"事件风险等级: {risk_level}"
            }
            
        except Exception as e:
            return {
                'score': 70,
                'risk_level': "未知",
                'analysis': "事件分析功能待完善"
            }
    
    def comprehensive_analysis(self, symbol, company_name, market="A股", mode="全维度分析"):
        """综合分析"""
        
        # 根据分析模式调整权重
        if mode == "技术面优先":
            weights = {'technical': 0.6, 'fundamental': 0.2, 'sentiment': 0.1, 'event': 0.1}
        elif mode == "基本面优先":
            weights = {'technical': 0.2, 'fundamental': 0.6, 'sentiment': 0.1, 'event': 0.1}
        elif mode == "情绪面优先":
            weights = {'technical': 0.3, 'fundamental': 0.2, 'sentiment': 0.4, 'event': 0.1}
        else:  # 全维度分析
            weights = {'technical': 0.4, 'fundamental': 0.3, 'sentiment': 0.2, 'event': 0.1}
        
        # 获取各维度分析
        technical = self.get_technical_analysis(symbol, market)
        fundamental = self.get_fundamental_analysis(symbol, market) if enable_fundamental else None
        sentiment = self.get_sentiment_analysis(symbol, company_name, market) if enable_news_analysis else None
        event = self.get_event_analysis(symbol, market)
        
        # 计算综合评分
        scores = {
            'technical': technical['score'] if technical else 50,
            'fundamental': fundamental['score'] if fundamental else 50,
            'sentiment': sentiment['score'] if sentiment else 50,
            'event': event['score'] if event else 50
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            'final_score': final_score,
            'technical': technical,
            'fundamental': fundamental,
            'sentiment': sentiment,
            'event': event,
            'recommendation': self._get_recommendation(final_score),
            'weights': weights
        }
    
    def _get_recommendation(self, score):
        """根据评分给出建议"""
        if score >= 85:
            return {"level": "强烈推荐", "emoji": "🚀", "color": "success", "action": "积极买入"}
        elif score >= 75:
            return {"level": "推荐买入", "emoji": "📈", "color": "success", "action": "买入"}
        elif score >= 65:
            return {"level": "值得关注", "emoji": "👀", "color": "warning", "action": "关注"}
        elif score >= 50:
            return {"level": "中性观望", "emoji": "⚖️", "color": "info", "action": "观望"}
        elif score >= 35:
            return {"level": "谨慎观望", "emoji": "⚠️", "color": "warning", "action": "谨慎"}
        else:
            return {"level": "建议回避", "emoji": "❌", "color": "error", "action": "回避"}

# 创建分析器实例
@st.cache_resource
def get_analyzer():
    return ComprehensiveStockAnalyzer()

analyzer = get_analyzer()

# 主界面
col1, col2 = st.columns([3, 1])

with col1:
    if "A股" in market_selection:
        stock_input = st.text_input(
            "输入A股代码", 
            value="000001",
            placeholder="例如: 000001, 000002, 600036",
            help="输入6位A股代码"
        )
        company_name = "平安银行"  # 实际使用中可以通过API获取公司名称
    else:
        stock_input = st.text_input(
            "输入美股代码", 
            value="AAPL",
            placeholder="例如: AAPL, GOOGL, MSFT",
            help="输入美股代码"
        )
        company_name = "Apple Inc."

with col2:
    analyze_button = st.button("🧠 开始全维度分析", type="primary", use_container_width=True)

# 分析结果显示
if analyze_button and stock_input:
    with st.spinner("🔍 正在进行全维度智能分析..."):
        
        # 确定主要市场
        primary_market = market_selection[0] if market_selection else "A股"
        
        # 进行综合分析
        result = analyzer.comprehensive_analysis(
            stock_input, 
            company_name, 
            primary_market, 
            analysis_mode
        )
        
        if result['technical'] is None:
            st.error("❌ 无法获取股票数据，请检查股票代码是否正确")
        else:
            st.success("✅ 分析完成！")
            
            # 显示综合评分和建议
            rec = result['recommendation']
            
            # 大标题显示结果
            st.markdown(f"""
            <div class="recommendation-{'high' if result['final_score'] >= 70 else 'medium' if result['final_score'] >= 50 else 'low'}">
                <h2>{rec['emoji']} {rec['level']}</h2>
                <h3>综合评分: {result['final_score']:.1f}/100</h3>
                <p>投资建议: {rec['action']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 各维度评分卡片
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                tech_score = result['technical']['score'] if result['technical'] else 0
                st.metric(
                    "📊 技术面",
                    f"{tech_score:.0f}/100",
                    delta=f"权重: {result['weights']['technical']:.0%}",
                    help="基于K线、均线、RSI、MACD、KDJ等技术指标"
                )
            
            with col2:
                fund_score = result['fundamental']['score'] if result['fundamental'] else 0
                st.metric(
                    "💼 基本面", 
                    f"{fund_score:.0f}/100",
                    delta=f"权重: {result['weights']['fundamental']:.0%}",
                    help="基于PE、ROE、负债率等财务指标"
                )
            
            with col3:
                sent_score = result['sentiment']['score'] if result['sentiment'] else 0
                st.metric(
                    "😊 情绪面",
                    f"{sent_score:.0f}/100",
                    delta=f"权重: {result['weights']['sentiment']:.0%}",
                    help="基于新闻情感分析和市场情绪"
                )
            
            with col4:
                event_score = result['event']['score']
                st.metric(
                    "⚡ 事件面",
                    f"{event_score:.0f}/100",
                    delta=f"权重: {result['weights']['event']:.0%}",
                    help="基于突发事件和风险评估"
                )
            
            # 详细分析标签页
            tab1, tab2, tab3, tab4 = st.tabs(["📊 技术分析", "💼 基本面分析", "😊 情绪分析", "⚡ 事件分析"])
            
            with tab1:
                if result['technical']:
                    tech = result['technical']
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # K线图
                        if 'data' in tech and len(tech['data']) > 0:
                            fig = make_subplots(
                                rows=2, cols=1,
                                shared_xaxis=True,
                                vertical_spacing=0.1,
                                subplot_titles=('K线图', 'RSI'),
                                row_heights=[0.7, 0.3]
                            )
                            
                            data = tech['data'].tail(60)  # 最近60天
                            
                            # K线图
                            fig.add_trace(
                                go.Candlestick(
                                    x=data['日期'] if '日期' in data.columns else data.index,
                                    open=data['开盘'] if '开盘' in data.columns else data['open'],
                                    high=data['最高'] if '最高' in data.columns else data['high'],
                                    low=data['最低'] if '最低' in data.columns else data['low'],
                                    close=data['收盘'] if '收盘' in data.columns else data['close'],
                                    name="K线"
                                ),
                                row=1, col=1
                            )
                            
                            # 均线
                            close_col = '收盘' if '收盘' in data.columns else 'close'
                            date_col = '日期' if '日期' in data.columns else data.index
                            
                            if 'MA5' in data.columns:
                                fig.add_trace(
                                    go.Scatter(
                                        x=date_col,
                                        y=data['MA5'],
                                        name="MA5",
                                        line=dict(color='orange', width=1)
                                    ),
                                    row=1, col=1
                                )
                            
                            if 'MA20' in data.columns:
                                fig.add_trace(
                                    go.Scatter(
                                        x=date_col,
                                        y=data['MA20'],
                                        name="MA20",
                                        line=dict(color='blue', width=1)
                                    ),
                                    row=1, col=1
                                )
                            
                            # RSI
                            if 'RSI' in data.columns:
                                fig.add_trace(
                                    go.Scatter(
                                        x=date_col,
                                        y=data['RSI'],
                                        name="RSI",
                                        line=dict(color='purple')
                                    ),
                                    row=2, col=1
                                )
                                
                                # RSI超买超卖线
                                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                            
                            fig.update_layout(
                                title=f"{company_name}({stock_input}) 技术分析图",
                                height=600,
                                xaxis_rangeslider_visible=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.subheader("技术指标")
                        
                        # 当前价格和涨跌幅
                        st.metric(
                            "当前价格",
                            f"¥{tech['price']:.2f}",
                            delta=f"{tech.get('change', 0):.2f}%"
                        )
                        
                        # 技术指标数值
                        if 'rsi' in tech:
                            st.metric("RSI", f"{tech['rsi']:.1f}")
                        
                        if 'macd' in tech:
                            st.metric("MACD", f"{tech['macd']:.4f}")
                        
                        if 'kdj_k' in tech and 'kdj_d' in tech:
                            st.metric("KDJ", f"K:{tech['kdj_k']:.1f} D:{tech['kdj_d']:.1f}")
                        
                        if 'volume_ratio' in tech:
                            st.metric("量比", f"{tech['volume_ratio']:.1f}")
                        
                        # 技术信号
                        if 'signals' in tech and tech['signals']:
                            st.subheader("技术信号")
                            for signal in tech['signals']:
                                st.write(f"• {signal}")
                else:
                    st.error("技术分析数据获取失败")
            
            with tab2:
                if result['fundamental']:
                    fund = result['fundamental']
                    
                    st.subheader("基本面评估")
                    st.write(fund.get('summary', '基本面数据不可用'))
                    
                    if 'analysis_points' in fund:
                        st.subheader("分析要点")
                        for point in fund['analysis_points']:
                            st.write(f"• {point}")
                    
                    # 财务指标表格
                    if any(key in fund for key in ['pe_ratio', 'roe', 'debt_to_equity']):
                        st.subheader("关键财务指标")
                        
                        metrics_data = []
                        if 'pe_ratio' in fund and fund['pe_ratio']:
                            metrics_data.append(["市盈率(PE)", f"{fund['pe_ratio']:.1f}"])
                        if 'roe' in fund and fund['roe']:
                            metrics_data.append(["净资产收益率(ROE)", f"{fund['roe']:.1%}"])
                        if 'debt_to_equity' in fund and fund['debt_to_equity']:
                            metrics_data.append(["债务股本比", f"{fund['debt_to_equity']:.2f}"])
                        if 'market_cap' in fund and fund['market_cap']:
                            metrics_data.append(["市值", f"{fund['market_cap']:,.0f}"])
                        
                        if metrics_data:
                            df_metrics = pd.DataFrame(metrics_data, columns=["指标", "数值"])
                            st.table(df_metrics)
                else:
                    st.info("基本面分析已禁用或数据不可用")
            
            with tab3:
                if result['sentiment']:
                    sent = result['sentiment']
                    
                    st.subheader("市场情绪分析")
                    st.write(sent.get('analysis', '情绪分析不可用'))
                    
                    if 'mood' in sent:
                        mood_color = {
                            '积极': 'success',
                            '消极': 'error', 
                            '中性': 'info'
                        }
                        st.success(f"整体情绪: {sent['mood']}")
                    
                    if 'sample_news' in sent and sent['sample_news']:
                        st.subheader("相关新闻标题")
                        for i, news in enumerate(sent['sample_news'][:5], 1):
                            st.write(f"{i}. {news}")
                    
                    if 'avg_sentiment' in sent:
                        st.metric(
                            "情绪指数",
                            f"{sent['avg_sentiment']:.2f}",
                            help="范围: -1(极度消极) 到 +1(极度积极)"
                        )
                else:
                    st.info("情绪分析已禁用或数据不可用")
            
            with tab4:
                if result['event']:
                    event = result['event']
                    
                    st.subheader("事件风险评估")
                    st.write(event.get('analysis', '事件分析不可用'))
                    
                    risk_color = {
                        '低风险': 'success',
                        '中风险': 'warning',
                        '高风险': 'error'
                    }
                    
                    if 'risk_level' in event:
                        st.metric("风险等级", event['risk_level'])
                    
                    if 'risk_events' in event and event['risk_events']:
                        st.subheader("风险事件")
                        for event_item in event['risk_events']:
                            st.warning(f"⚠️ {event_item}")
                    
                    if 'positive_events' in event and event['positive_events']:
                        st.subheader("利好事件") 
                        for event_item in event['positive_events']:
                            st.success(f"✅ {event_item}")

# 侧边栏功能
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 快速选股")

if st.sidebar.button("🔥 今日热门股票"):
    st.sidebar.info("功能开发中...")

if st.sidebar.button("📊 技术指标筛选"):
    st.sidebar.info("功能开发中...")

# 付费升级提示
st.sidebar.markdown("---")
st.sidebar.markdown("### 💎 升级到专业版")
st.sidebar.markdown("""
**免费版限制:**
- 每日5次分析
- 基础技术指标
- 简化基本面分析

**专业版特权:**
- 无限次分析  
- 50+技术指标
- 深度基本面分析
- 实时预警提醒
- 投资组合管理
- AI投资建议

**仅需 ¥99/月**
""")

if st.sidebar.button("🚀 立即升级"):
    st.sidebar.success("跳转到支付页面...")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚠️ <strong>风险提示</strong>: 本工具仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
    <p>请根据自身情况做出投资决策，本平台不承担任何投资损失责任。</p>
    <p>© 2024 全维度AI选股系统 | 基于OpenBB + AkShare构建</p>
</div>
""", unsafe_allow_html=True)