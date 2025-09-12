# event_backtest.py - 事件影响回测分析系统

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import akshare as ak
from event_analyzer import Event, EventType, EventImpact
import warnings
warnings.filterwarnings('ignore')

class EventBacktestAnalyzer:
    """事件影响回测分析器"""
    
    def __init__(self):
        self.event_colors = {
            "重大利好": "#00C851",
            "利好": "#7CB342", 
            "中性": "#FFC107",
            "利空": "#FF8A65",
            "重大利空": "#FF4444"
        }
        
        self.event_type_colors = {
            "财报发布": "#2196F3",
            "并购重组": "#9C27B0",
            "政策变化": "#FF9800",
            "管理变动": "#795548",
            "法律诉讼": "#F44336",
            "产品发布": "#4CAF50",
            "分红派息": "#E91E63",
            "行业动态": "#607D8B"
        }
    
    def get_stock_price_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票价格数据"""
        try:
            data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if data is not None and len(data) > 0:
                data['日期'] = pd.to_datetime(data['日期'])
                data = data.sort_values('日期')
                data['涨跌幅'] = data['收盘'].pct_change() * 100
                data['累计涨跌幅'] = (data['收盘'] / data['收盘'].iloc[0] - 1) * 100
                return data
            
        except Exception as e:
            st.error(f"获取股价数据失败: {e}")
        
        return pd.DataFrame()
    
    def simulate_events(self, symbol: str, days: int = 90) -> List[Event]:
        """模拟历史事件数据"""
        from event_analyzer import Event, EventType, EventImpact, EventUrgency
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 模拟事件数据
        events = []
        
        # 财报事件
        for i in range(3):
            event_date = start_date + timedelta(days=i*30 + np.random.randint(0, 10))
            if np.random.random() > 0.5:
                events.append(Event(
                    title=f"Q{i+1}业绩超预期，净利润同比增长25%",
                    content="公司发布季度财报，各项指标均超市场预期",
                    source="公司公告",
                    timestamp=event_date,
                    event_type=EventType.FINANCIAL_REPORT,
                    impact=EventImpact.VERY_POSITIVE,
                    urgency=EventUrgency.HIGH,
                    confidence=0.9,
                    related_symbols=[symbol],
                    keywords=["财报", "超预期", "净利润"],
                    sentiment_score=0.8,
                    market_cap_impact=0.05
                ))
            else:
                events.append(Event(
                    title=f"Q{i+1}业绩不及预期，营收下滑10%",
                    content="公司发布季度财报，营收和利润均低于预期",
                    source="公司公告",
                    timestamp=event_date,
                    event_type=EventType.FINANCIAL_REPORT,
                    impact=EventImpact.NEGATIVE,
                    urgency=EventUrgency.HIGH,
                    confidence=0.9,
                    related_symbols=[symbol],
                    keywords=["财报", "不及预期", "下滑"],
                    sentiment_score=-0.6,
                    market_cap_impact=-0.03
                ))
        
        # 政策事件
        policy_date = start_date + timedelta(days=45)
        events.append(Event(
            title="行业利好政策出台，获得税收优惠",
            content="相关部门发布行业扶持政策，公司符合优惠条件",
            source="政策公告",
            timestamp=policy_date,
            event_type=EventType.POLICY_CHANGE,
            impact=EventImpact.POSITIVE,
            urgency=EventUrgency.MEDIUM,
            confidence=0.8,
            related_symbols=[symbol],
            keywords=["政策", "利好", "税收优惠"],
            sentiment_score=0.6,
            market_cap_impact=0.02
        ))
        
        # 并购事件
        merger_date = start_date + timedelta(days=60)
        events.append(Event(
            title="重大资产重组获批，业务规模大幅扩张",
            content="公司重大资产重组方案获得监管部门批准",
            source="公司公告",
            timestamp=merger_date,
            event_type=EventType.MERGER_ACQUISITION,
            impact=EventImpact.VERY_POSITIVE,
            urgency=EventUrgency.IMMEDIATE,
            confidence=0.95,
            related_symbols=[symbol],
            keywords=["重组", "获批", "扩张"],
            sentiment_score=0.9,
            market_cap_impact=0.08
        ))
        
        # 负面事件
        legal_date = start_date + timedelta(days=75)
        events.append(Event(
            title="收到监管部门调查通知书",
            content="公司因涉嫌信息披露违规收到调查通知",
            source="公司公告",
            timestamp=legal_date,
            event_type=EventType.LEGAL_ISSUE,
            impact=EventImpact.VERY_NEGATIVE,
            urgency=EventUrgency.IMMEDIATE,
            confidence=0.9,
            related_symbols=[symbol],
            keywords=["调查", "违规", "监管"],
            sentiment_score=-0.8,
            market_cap_impact=-0.06
        ))
        
        return sorted(events, key=lambda x: x.timestamp)
    
    def calculate_event_impact(self, price_data: pd.DataFrame, events: List[Event], 
                             pre_days: int = 5, post_days: int = 10) -> pd.DataFrame:
        """计算事件对股价的影响"""
        
        impact_results = []
        
        for event in events:
            event_date = event.timestamp.date()
            
            # 找到事件日期在价格数据中的位置
            price_data['日期_date'] = price_data['日期'].dt.date
            event_idx = price_data[price_data['日期_date'] == event_date].index
            
            if len(event_idx) == 0:
                # 如果事件日期不是交易日，找最近的交易日
                event_idx = price_data[price_data['日期_date'] >= event_date].index
                if len(event_idx) == 0:
                    continue
                event_idx = event_idx[0]
            else:
                event_idx = event_idx[0]
            
            # 计算事件前后的价格变化
            pre_start_idx = max(0, event_idx - pre_days)
            post_end_idx = min(len(price_data), event_idx + post_days + 1)
            
            if pre_start_idx < event_idx < post_end_idx:
                pre_price = price_data.iloc[event_idx - 1]['收盘'] if event_idx > 0 else price_data.iloc[event_idx]['开盘']
                post_prices = price_data.iloc[event_idx:post_end_idx]['收盘'].values
                
                # 计算不同时间窗口的收益率
                returns = {}
                for days in [1, 3, 5, 10]:
                    if days < len(post_prices):
                        returns[f'{days}day_return'] = (post_prices[days-1] / pre_price - 1) * 100
                    else:
                        returns[f'{days}day_return'] = (post_prices[-1] / pre_price - 1) * 100
                
                # 计算最大涨跌幅
                max_return = (np.max(post_prices) / pre_price - 1) * 100
                min_return = (np.min(post_prices) / pre_price - 1) * 100
                
                impact_results.append({
                    'event_title': event.title,
                    'event_type': event.event_type.value,
                    'event_impact': event.impact.value,
                    'event_date': event.timestamp,
                    'pre_price': pre_price,
                    'sentiment_score': event.sentiment_score,
                    'predicted_impact': event.market_cap_impact * 100,
                    'max_return': max_return,
                    'min_return': min_return,
                    **returns
                })
        
        return pd.DataFrame(impact_results)
    
    def create_price_event_chart(self, price_data: pd.DataFrame, events: List[Event]) -> go.Figure:
        """创建价格与事件的综合图表"""
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxis=True,
            vertical_spacing=0.05,
            subplot_titles=('股价走势与事件标记', '成交量', '事件影响热力图'),
            row_heights=[0.6, 0.2, 0.2],
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}], 
                   [{"secondary_y": False}]]
        )
        
        # 1. 股价K线图
        fig.add_trace(
            go.Candlestick(
                x=price_data['日期'],
                open=price_data['开盘'],
                high=price_data['最高'],
                low=price_data['最低'],
                close=price_data['收盘'],
                name='股价',
                increasing_line_color='#00C851',
                decreasing_line_color='#FF4444'
            ),
            row=1, col=1
        )
        
        # 2. 添加移动平均线
        if len(price_data) >= 20:
            price_data['MA20'] = price_data['收盘'].rolling(20).mean()
            fig.add_trace(
                go.Scatter(
                    x=price_data['日期'],
                    y=price_data['MA20'],
                    name='MA20',
                    line=dict(color='#2196F3', width=1),
                    opacity=0.7
                ),
                row=1, col=1
            )
        
        # 3. 事件标记
        for event in events:
            event_date = event.timestamp
            
            # 找到对应的价格
            price_row = price_data[price_data['日期'].dt.date == event_date.date()]
            if not price_row.empty:
                price = price_row.iloc[0]['最高'] * 1.05  # 在最高价上方标记
                
                # 根据事件影响选择颜色和符号
                color = self.event_colors.get(event.impact.value, '#FFC107')
                symbol = 'triangle-up' if event.impact.value in ['利好', '重大利好'] else 'triangle-down' if event.impact.value in ['利空', '重大利空'] else 'circle'
                
                fig.add_trace(
                    go.Scatter(
                        x=[event_date],
                        y=[price],
                        mode='markers+text',
                        marker=dict(
                            size=15,
                            color=color,
                            symbol=symbol,
                            line=dict(width=2, color='white')
                        ),
                        text=event.event_type.value,
                        textposition="top center",
                        name=f"{event.impact.value}事件",
                        hovertemplate=f"<b>{event.title}</b><br>时间: {event_date}<br>类型: {event.event_type.value}<br>影响: {event.impact.value}<extra></extra>",
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # 4. 成交量
        colors = ['#00C851' if row['收盘'] >= row['开盘'] else '#FF4444' for _, row in price_data.iterrows()]
        fig.add_trace(
            go.Bar(
                x=price_data['日期'],
                y=price_data['成交量'],
                name='成交量',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 5. 事件影响热力图数据准备
        event_impact_data = self._prepare_heatmap_data(price_data, events)
        
        fig.add_trace(
            go.Heatmap(
                z=event_impact_data['impact_matrix'],
                x=event_impact_data['dates'],
                y=['事件影响强度'],
                colorscale=[
                    [0.0, '#FF4444'],    # 重大利空
                    [0.25, '#FF8A65'],   # 利空
                    [0.5, '#FFC107'],    # 中性
                    [0.75, '#7CB342'],   # 利好
                    [1.0, '#00C851']     # 重大利好
                ],
                showscale=True,
                colorbar=dict(title="影响强度", x=1.02),
                hovertemplate="日期: %{x}<br>影响强度: %{z}<extra></extra>"
            ),
            row=3, col=1
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text="📈 股价走势与事件影响分析",
                font=dict(size=20, color='#2C3E50'),
                x=0.5
            ),
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 更新x轴
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E8E8E8',
            showline=True,
            linewidth=1,
            linecolor='#CCCCCC'
        )
        
        # 更新y轴
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E8E8E8',
            showline=True,
            linewidth=1,
            linecolor='#CCCCCC'
        )
        
        return fig
    
    def _prepare_heatmap_data(self, price_data: pd.DataFrame, events: List[Event]) -> Dict:
        """准备热力图数据"""
        
        dates = price_data['日期'].dt.strftime('%Y-%m-%d').tolist()
        impact_values = np.zeros(len(dates))
        
        # 将事件影响映射到日期
        for event in events:
            event_date_str = event.timestamp.strftime('%Y-%m-%d')
            if event_date_str in dates:
                idx = dates.index(event_date_str)
                
                # 影响强度映射 (-1 到 1 映射到 0 到 1)
                impact_mapping = {
                    "重大利空": 0.0,
                    "利空": 0.25,
                    "中性": 0.5,
                    "利好": 0.75,
                    "重大利好": 1.0
                }
                impact_values[idx] = impact_mapping.get(event.impact.value, 0.5)
        
        return {
            'dates': dates,
            'impact_matrix': [impact_values]
        }
    
    def create_event_impact_analysis_chart(self, impact_df: pd.DataFrame) -> go.Figure:
        """创建事件影响分析图表"""
        
        if impact_df.empty:
            return go.Figure()
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📊 不同类型事件的平均影响',
                '📈 事件影响 vs 实际收益对比', 
                '🎯 事件预测准确性分析',
                '⏰ 事件影响持续时间分析'
            ),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. 不同类型事件的平均影响
        event_type_impact = impact_df.groupby('event_type').agg({
            '1day_return': 'mean',
            '3day_return': 'mean', 
            '5day_return': 'mean',
            '10day_return': 'mean'
        }).round(2)
        
        for period in ['1day_return', '3day_return', '5day_return', '10day_return']:
            fig.add_trace(
                go.Bar(
                    name=f'{period.replace("day_return", "日")}',
                    x=event_type_impact.index,
                    y=event_type_impact[period],
                    text=event_type_impact[period],
                    textposition='outside',
                    marker_color=px.colors.qualitative.Set3[['1day_return', '3day_return', '5day_return', '10day_return'].index(period)]
                ),
                row=1, col=1
            )
        
        # 2. 预测 vs 实际收益对比
        fig.add_trace(
            go.Scatter(
                x=impact_df['predicted_impact'],
                y=impact_df['5day_return'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=impact_df['sentiment_score'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="情感分数", x=0.48, y=0.8, len=0.3)
                ),
                text=impact_df['event_type'],
                hovertemplate="<b>%{text}</b><br>预测影响: %{x:.2f}%<br>实际收益: %{y:.2f}%<extra></extra>",
                name="预测vs实际"
            ),
            row=1, col=2
        )
        
        # 添加对角线
        min_val = min(impact_df['predicted_impact'].min(), impact_df['5day_return'].min())
        max_val = max(impact_df['predicted_impact'].max(), impact_df['5day_return'].max())
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name="完美预测线",
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. 预测准确性分析
        impact_df['prediction_accuracy'] = 1 - abs(impact_df['predicted_impact'] - impact_df['5day_return']) / (abs(impact_df['5day_return']) + 1)
        
        fig.add_trace(
            go.Scatter(
                x=impact_df['event_date'],
                y=impact_df['prediction_accuracy'],
                mode='markers+lines',
                marker=dict(
                    size=8,
                    color=impact_df['prediction_accuracy'],
                    colorscale='Viridis',
                    cmin=0,
                    cmax=1
                ),
                line=dict(width=2),
                name="预测准确性",
                hovertemplate="日期: %{x}<br>准确性: %{y:.2%}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # 4. 影响持续时间分析
        returns_comparison = impact_df[['1day_return', '3day_return', '5day_return', '10day_return']].mean()
        
        fig.add_trace(
            go.Bar(
                x=['1日', '3日', '5日', '10日'],
                y=returns_comparison.values,
                marker=dict(
                    color=returns_comparison.values,
                    colorscale='RdYlGn',
                    cmin=-5,
                    cmax=5
                ),
                text=[f'{val:.2f}%' for val in returns_comparison.values],
                textposition='outside',
                name="平均收益率"
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text="🎯 事件影响回测分析报告",
                font=dict(size=20, color='#2C3E50'),
                x=0.5
            ),
            height=800,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 更新坐标轴标签
        fig.update_xaxes(title_text="事件类型", row=1, col=1)
        fig.update_yaxes(title_text="平均收益率 (%)", row=1, col=1)
        
        fig.update_xaxes(title_text="预测影响 (%)", row=1, col=2)
        fig.update_yaxes(title_text="实际5日收益 (%)", row=1, col=2)
        
        fig.update_xaxes(title_text="事件日期", row=2, col=1)
        fig.update_yaxes(title_text="预测准确性", row=2, col=1, tickformat='.0%')
        
        fig.update_xaxes(title_text="时间窗口", row=2, col=2)
        fig.update_yaxes(title_text="平均收益率 (%)", row=2, col=2)
        
        return fig
    
    def create_event_performance_summary(self, impact_df: pd.DataFrame) -> Dict:
        """创建事件表现总结"""
        
        if impact_df.empty:
            return {}
        
        summary = {
            'total_events': len(impact_df),
            'positive_events': len(impact_df[impact_df['5day_return'] > 0]),
            'negative_events': len(impact_df[impact_df['5day_return'] < 0]),
            'avg_return': impact_df['5day_return'].mean(),
            'best_event': impact_df.loc[impact_df['5day_return'].idxmax()],
            'worst_event': impact_df.loc[impact_df['5day_return'].idxmin()],
            'prediction_accuracy': (1 - abs(impact_df['predicted_impact'] - impact_df['5day_return']).mean() / (abs(impact_df['5day_return']).mean() + 1)) * 100,
            'event_type_performance': impact_df.groupby('event_type')['5day_return'].agg(['mean', 'std', 'count']).round(2)
        }
        
        return summary

class EventVisualizationUI:
    """事件可视化用户界面"""
    
    def __init__(self):
        self.backtest_analyzer = EventBacktestAnalyzer()
    
    def display_event_backtest_analysis(self, symbol: str, company_name: str):
        """显示事件回测分析界面"""
        
        st.markdown("### 📊 事件影响回测分析")
        st.markdown("通过历史数据分析不同类型事件对股价的实际影响效果")
        
        # 参数设置
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            backtest_days = st.selectbox("回测天数", [30, 60, 90, 180], index=2)
        with col2:
            pre_event_days = st.slider("事件前观察期", 1, 10, 5)
        with col3:
            post_event_days = st.slider("事件后观察期", 1, 20, 10)
        with col4:
            show_detailed = st.checkbox("显示详细分析", value=True)
        
        if st.button("🚀 开始回测分析", key="event_backtest"):
            with st.spinner("正在进行事件影响回测分析..."):
                
                # 获取股价数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=backtest_days)).strftime("%Y%m%d")
                
                price_data = self.backtest_analyzer.get_stock_price_data(symbol, start_date, end_date)
                
                if price_data.empty:
                    st.error("无法获取股价数据，请检查股票代码")
                    return
                
                # 模拟历史事件
                events = self.backtest_analyzer.simulate_events(symbol, backtest_days)
                
                # 计算事件影响
                impact_df = self.backtest_analyzer.calculate_event_impact(
                    price_data, events, pre_event_days, post_event_days
                )
                
                # 缓存结果
                st.session_state['backtest_data'] = {
                    'price_data': price_data,
                    'events': events,
                    'impact_df': impact_df,
                    'symbol': symbol,
                    'company_name': company_name
                }
        
        # 显示分析结果
        if 'backtest_data' in st.session_state:
            data = st.session_state['backtest_data']
            self._display_backtest_results(data, show_detailed)
    
    def _display_backtest_results(self, data: Dict, show_detailed: bool):
        """显示回测结果"""
        
        price_data = data['price_data']
        events = data['events']
        impact_df = data['impact_df']
        symbol = data['symbol']
        company_name = data['company_name']
        
        # 1. 综合表现概览
        if not impact_df.empty:
            summary = self.backtest_analyzer.create_event_performance_summary(impact_df)
            self._display_performance_summary(summary, company_name, symbol)
        
        # 2. 股价与事件综合图表
        st.markdown("### 📈 股价走势与事件影响可视化")
        price_event_chart = self.backtest_analyzer.create_price_event_chart(price_data, events)
        st.plotly_chart(price_event_chart, use_container_width=True)
        
        # 3. 详细分析图表
        if show_detailed and not impact_df.empty:
            st.markdown("### 🎯 深度分析报告")
            
            impact_analysis_chart = self.backtest_analyzer.create_event_impact_analysis_chart(impact_df)
            st.plotly_chart(impact_analysis_chart, use_container_width=True)
            
            # 4. 事件详情表格
            self._display_event_details_table(impact_df)
            
            # 5. 策略建议
            self._display_strategy_recommendations(impact_df, summary)
    
    def _display_performance_summary(self, summary: Dict, company_name: str, symbol: str):
        """显示表现总结"""
        
        st.markdown(f"### 🎯 {company_name}({symbol}) 事件影响总结")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "事件总数",
                summary['total_events'],
                help="分析期间内的重要事件数量"
            )
        
        with col2:
            positive_rate = (summary['positive_events'] / summary['total_events']) * 100
            st.metric(
                "利好事件占比",
                f"{positive_rate:.1f}%",
                delta=f"{summary['positive_events']}个",
                help="产生正面影响的事件比例"
            )
        
        with col3:
            st.metric(
                "平均5日收益",
                f"{summary['avg_return']:.2f}%",
                delta="事件后5日" if summary['avg_return'] > 0 else "事件后5日",
                help="事件发生后5个交易日的平均收益率"
            )
        
        with col4:
            st.metric(
                "预测准确性",
                f"{summary['prediction_accuracy']:.1f}%",
                help="AI预测与实际结果的匹配度"
            )
        
        with col5:
            best_return = summary['best_event']['5day_return']
            st.metric(
                "最佳事件收益",
                f"{best_return:.2f}%",
                delta="5日收益",
                help="单个事件带来的最大收益"
            )
        
        # 最佳和最差事件展示
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("🏆 **最佳表现事件**")
            best_event = summary['best_event']
            st.write(f"**事件**: {best_event['event_title']}")
            st.write(f"**类型**: {best_event['event_type']}")
            st.write(f"**5日收益**: {best_event['5day_return']:.2f}%")
            st.write(f"**日期**: {best_event['event_date'].strftime('%Y-%m-%d')}")
        
        with col2:
            st.error("📉 **最差表现事件**")
            worst_event = summary['worst_event']
            st.write(f"**事件**: {worst_event['event_title']}")
            st.write(f"**类型**: {worst_event['event_type']}")
            st.write(f"**5日收益**: {worst_event['5day_return']:.2f}%")
            st.write(f"**日期**: {worst_event['event_date'].strftime('%Y-%m-%d')}")
    
    def _display_event_details_table(self, impact_df: pd.DataFrame):
        """显示事件详情表格"""
        
        st.markdown("### 📋 事件影响详情表")
        
        # 准备显示数据
        display_df = impact_df.copy()
        display_df['事件日期'] = display_df['event_date'].dt.strftime('%Y-%m-%d')
        display_df['事件标题'] = display_df['event_title'].str[:40] + "..."
        display_df['1日收益'] = display_df['1day_return'].round(2).astype(str) + "%"
        display_df['3日收益'] = display_df['3day_return'].round(2).astype(str) + "%"
        display_df['5日收益'] = display_df['5day_return'].round(2).astype(str) + "%"
        display_df['10日收益'] = display_df['10day_return'].round(2).astype(str) + "%"
        display_df['预测影响'] = display_df['predicted_impact'].round(2).astype(str) + "%"
        
        # 选择显示列
        show_columns = [
            '事件日期', '事件标题', 'event_type', 'event_impact', 
            '预测影响', '1日收益', '3日收益', '5日收益', '10日收益'
        ]
        
        display_data = display_df[show_columns].rename(columns={
            'event_type': '事件类型',
            'event_impact': '影响程度'
        })
        
        # 使用样式化表格
        def highlight_returns(val):
            if '%' in str(val):
                num_val = float(str(val).replace('%', ''))
                if num_val > 2:
                    return 'background-color: #d4edda; color: #155724'
                elif num_val < -2:
                    return 'background-color: #f8d7da; color: #721c24'
                else:
                    return 'background-color: #fff3cd; color: #856404'
            return ''
        
        styled_df = display_data.style.applymap(
            highlight_returns,
            subset=['1日收益', '3日收益', '5日收益', '10日收益']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # 下载数据选项
        csv = impact_df.to_csv(index=False)
        st.download_button(
            label="📥 下载详细数据",
            data=csv,
            file_name=f"event_impact_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def _display_strategy_recommendations(self, impact_df: pd.DataFrame, summary: Dict):
        """显示策略建议"""
        
        st.markdown("### 💡 投资策略建议")
        
        # 基于回测结果生成建议
        avg_return = summary['avg_return']
        positive_rate = (summary['positive_events'] / summary['total_events']) * 100
        prediction_accuracy = summary['prediction_accuracy']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 事件驱动策略建议")
            
            if avg_return > 2 and positive_rate > 60:
                st.success("✅ **积极事件驱动策略**: 该股票对正面事件反应良好，建议关注重大利好事件的投资机会")
            elif avg_return > 0 and positive_rate > 50:
                st.info("ℹ️ **温和事件驱动策略**: 事件影响整体为正，可适度参与事件驱动投资")
            else:
                st.warning("⚠️ **谨慎策略**: 事件影响不稳定，建议以技术面和基本面分析为主")
            
            # 最佳事件类型
            best_event_types = impact_df.groupby('event_type')['5day_return'].mean().sort_values(ascending=False)
            st.write("**最有效的事件类型:**")
            for i, (event_type, avg_ret) in enumerate(best_event_types.head(3).items(), 1):
                st.write(f"{i}. {event_type}: 平均{avg_ret:.2f}%收益")
        
        with col2:
            st.markdown("#### ⏰ 时机选择建议")
            
            if prediction_accuracy > 70:
                st.success("🎯 **AI预测可靠**: 预测准确率较高，可以信任AI的事件影响预测")
            else:
                st.warning("🤔 **预测谨慎参考**: 预测准确率有限，建议结合其他分析方法")
            
            # 最佳持有期分析
            returns_by_period = {
                '1日': impact_df['1day_return'].mean(),
                '3日': impact_df['3day_return'].mean(),
                '5日': impact_df['5day_return'].mean(),
                '10日': impact_df['10day_return'].mean()
            }
            
            best_period = max(returns_by_period, key=returns_by_period.get)
            st.write(f"**最佳持有期**: {best_period} (平均收益: {returns_by_period[best_period]:.2f}%)")
            
            # 风险提示
            max_loss = impact_df['min_return'].min()
            st.error(f"⚠️ **最大风险**: 单次事件最大回撤 {max_loss:.2f}%")

# 使用示例
def main():
    """主函数"""
    st.title("📊 事件影响回测分析系统")
    
    # 用户输入
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代码", value="000001")
    with col2:
        company_name = st.text_input("公司名称", value="平安银行")
    
    # 显示分析界面
    ui = EventVisualizationUI()
    ui.display_event_backtest_analysis(symbol, company_name)

if __name__ == "__main__":
    main()