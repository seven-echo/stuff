# enhanced_visualization.py - 增强数据可视化模块

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class EnhancedVisualization:
    """增强数据可视化类"""
    
    def __init__(self):
        # 定义配色方案
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        # 股票相关颜色
        self.stock_colors = {
            'up': '#00C851',
            'down': '#FF4444',
            'neutral': '#FFC107'
        }
        
        # 评分颜色映射
        self.score_colors = {
            'excellent': '#00C851',  # 85+
            'good': '#7CB342',       # 70-84
            'average': '#FFC107',    # 50-69
            'poor': '#FF8A65',       # 35-49
            'bad': '#FF4444'         # <35
        }
    
    def get_score_color(self, score: float) -> str:
        """根据评分获取颜色"""
        if score >= 85:
            return self.score_colors['excellent']
        elif score >= 70:
            return self.score_colors['good']
        elif score >= 50:
            return self.score_colors['average']
        elif score >= 35:
            return self.score_colors['poor']
        else:
            return self.score_colors['bad']
    
    def create_comprehensive_dashboard(self, analysis_result: Dict) -> go.Figure:
        """创建综合仪表板"""
        
        # 创建4x4子图布局
        fig = make_subplots(
            rows=4, cols=4,
            subplot_titles=(
                '综合评分', '技术面评分', '基本面评分', '情绪面评分',
                '事件影响', 'RSI指标', 'MACD信号', '成交量分析',
                '价格趋势', '支撑阻力', '波动率', '相对强弱',
                '风险评估', '机会评级', '投资建议', '市场情绪'
            ),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}, {"type": "scatter"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.05
        )
        
        # 第一行：核心评分指标
        scores = {
            'final_score': analysis_result.get('final_score', 50),
            'technical_score': analysis_result['technical']['score'] if analysis_result.get('technical') else 50,
            'fundamental_score': analysis_result['fundamental']['score'] if analysis_result.get('fundamental') else 50,
            'sentiment_score': analysis_result['sentiment']['score'] if analysis_result.get('sentiment') else 50
        }
        
        score_positions = [(1, 1), (1, 2), (1, 3), (1, 4)]
        score_titles = ['综合评分', '技术面', '基本面', '情绪面']
        
        for i, (key, score) in enumerate(scores.items()):
            row, col = score_positions[i]
            color = self.get_score_color(score)
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': score_titles[i], 'font': {'size': 16}},
                    delta={'reference': 50, 'increasing': {'color': self.colors['success']}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 35], 'color': '#ffebee'},
                            {'range': [35, 50], 'color': '#fff3e0'},
                            {'range': [50, 70], 'color': '#f3e5f5'},
                            {'range': [70, 85], 'color': '#e8f5e8'},
                            {'range': [85, 100], 'color': '#e0f2f1'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=row, col=col
            )
        
        # 第二行：技术指标详情
        if analysis_result.get('technical') and 'data' in analysis_result['technical']:
            tech_data = analysis_result['technical']['data']
            if len(tech_data) > 0:
                latest_data = tech_data.iloc[-20:]  # 最近20天数据
                
                # RSI图表
                if 'RSI' in latest_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=latest_data.index,
                            y=latest_data['RSI'],
                            mode='lines+markers',
                            name='RSI',
                            line=dict(color=self.colors['primary'], width=2)
                        ),
                        row=2, col=2
                    )
                    
                    # RSI超买超卖线
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=2)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=2)
                
                # MACD图表
                if 'MACD' in latest_data.columns and 'MACD_signal' in latest_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=latest_data.index,
                            y=latest_data['MACD'],
                            mode='lines',
                            name='MACD',
                            line=dict(color=self.colors['primary'])
                        ),
                        row=2, col=3
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=latest_data.index,
                            y=latest_data['MACD_signal'],
                            mode='lines',
                            name='Signal',
                            line=dict(color=self.colors['secondary'])
                        ),
                        row=2, col=3
                    )
        
        # 成交量分析
        if analysis_result.get('technical') and 'volume_ratio' in analysis_result['technical']:
            volume_ratio = analysis_result['technical']['volume_ratio']
            fig.add_trace(
                go.Bar(
                    x=['成交量比'],
                    y=[volume_ratio],
                    marker_color=self.stock_colors['up'] if volume_ratio > 1 else self.stock_colors['down'],
                    text=[f'{volume_ratio:.1f}x'],
                    textposition='outside'
                ),
                row=2, col=4
            )
        
        # 更新布局
        fig.update_layout(
            title={
                'text': '📊 全维度股票分析仪表板',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': self.colors['dark']}
            },
            height=1000,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        return fig
    
    def create_interactive_candlestick_chart(self, stock_data: pd.DataFrame, 
                                           events: List = None, 
                                           technical_indicators: Dict = None) -> go.Figure:
        """创建交互式K线图"""
        
        # 创建子图
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxis=True,
            vertical_spacing=0.03,
            subplot_titles=('价格走势', '成交量', '技术指标', '事件影响'),
            row_heights=[0.5, 0.2, 0.2, 0.1]
        )
        
        # 1. K线图
        fig.add_trace(
            go.Candlestick(
                x=stock_data.index,
                open=stock_data['开盘'] if '开盘' in stock_data.columns else stock_data['open'],
                high=stock_data['最高'] if '最高' in stock_data.columns else stock_data['high'],
                low=stock_data['最低'] if '最低' in stock_data.columns else stock_data['low'],
                close=stock_data['收盘'] if '收盘' in stock_data.columns else stock_data['close'],
                name='股价',
                increasing_line_color=self.stock_colors['up'],
                decreasing_line_color=self.stock_colors['down'],
                increasing_fillcolor=self.stock_colors['up'],
                decreasing_fillcolor=self.stock_colors['down']
            ),
            row=1, col=1
        )
        
        # 2. 添加移动平均线
        if technical_indicators:
            for ma_period, ma_values in technical_indicators.get('moving_averages', {}).items():
                fig.add_trace(
                    go.Scatter(
                        x=stock_data.index,
                        y=ma_values,
                        mode='lines',
                        name=f'MA{ma_period}',
                        line=dict(width=1.5),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
        
        # 3. 成交量
        volume_col = '成交量' if '成交量' in stock_data.columns else 'volume'
        if volume_col in stock_data.columns:
            colors = []
            for i in range(len(stock_data)):
                if i == 0:
                    colors.append(self.stock_colors['neutral'])
                else:
                    close_col = '收盘' if '收盘' in stock_data.columns else 'close'
                    if stock_data[close_col].iloc[i] >= stock_data[close_col].iloc[i-1]:
                        colors.append(self.stock_colors['up'])
                    else:
                        colors.append(self.stock_colors['down'])
            
            fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data[volume_col],
                    name='成交量',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # 4. 技术指标
        if 'RSI' in stock_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=self.colors['primary'])
                ),
                row=3, col=1
            )
            
            # RSI超买超卖线
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # 5. 事件标记
        if events:
            for event in events:
                event_date = event.timestamp
                if event_date.date() in [d.date() for d in stock_data.index]:
                    # 找到对应的价格
                    price_data = stock_data[stock_data.index.date == event_date.date()]
                    if not price_data.empty:
                        high_col = '最高' if '最高' in stock_data.columns else 'high'
                        price = price_data[high_col].iloc[0] * 1.02
                        
                        # 事件标记
                        color = '#00C851' if '利好' in event.impact.value else '#FF4444' if '利空' in event.impact.value else '#FFC107'
                        
                        fig.add_trace(
                            go.Scatter(
                                x=[event_date],
                                y=[price],
                                mode='markers+text',
                                marker=dict(
                                    size=12,
                                    color=color,
                                    symbol='triangle-up' if '利好' in event.impact.value else 'triangle-down' if '利空' in event.impact.value else 'circle',
                                    line=dict(width=2, color='white')
                                ),
                                text=event.event_type.value[:2],
                                textposition="middle center",
                                name=event.impact.value,
                                hovertemplate=f"<b>{event.title}</b><br>时间: {event_date}<br>影响: {event.impact.value}<extra></extra>",
                                showlegend=False
                            ),
                            row=1, col=1
                        )
                        
                        # 事件影响热力图
                        impact_value = 0.8 if '重大利好' in event.impact.value else 0.6 if '利好' in event.impact.value else 0.4 if '中性' in event.impact.value else 0.2 if '利空' in event.impact.value else 0.0
                        
                        fig.add_trace(
                            go.Scatter(
                                x=[event_date],
                                y=[impact_value],
                                mode='markers',
                                marker=dict(
                                    size=15,
                                    color=impact_value,
                                    colorscale='RdYlGn',
                                    cmin=0,
                                    cmax=1,
                                    showscale=True,
                                    colorbar=dict(title="事件影响", x=1.02, len=0.3)
                                ),
                                name="事件影响",
                                showlegend=False
                            ),
                            row=4, col=1
                        )
        
        # 更新布局
        fig.update_layout(
            title={
                'text': '📈 智能股票分析图表',
                'x': 0.5,
                'font': {'size': 20, 'color': self.colors['dark']}
            },
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        # 更新坐标轴
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E8E8E8')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E8E8E8')
        
        return fig
    
    def create_risk_return_scatter(self, portfolio_data: List[Dict]) -> go.Figure:
        """创建风险收益散点图"""
        
        fig = go.Figure()
        
        # 提取数据
        risks = [stock.get('risk_score', 50) for stock in portfolio_data]
        returns = [stock.get('expected_return', 0) for stock in portfolio_data]
        names = [stock.get('name', 'Unknown') for stock in portfolio_data]
        scores = [stock.get('final_score', 50) for stock in portfolio_data]
        
        # 创建散点图
        fig.add_trace(
            go.Scatter(
                x=risks,
                y=returns,
                mode='markers+text',
                marker=dict(
                    size=[score/3 for score in scores],  # 根据评分调整大小
                    color=scores,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="综合评分"),
                    line=dict(width=2, color='white')
                ),
                text=names,
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                hovertemplate="<b>%{text}</b><br>风险评分: %{x}<br>预期收益: %{y:.2f}%<br>综合评分: %{marker.color}<extra></extra>"
            )
        )
        
        # 添加象限分割线
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
        
        # 添加象限标签
        fig.add_annotation(x=25, y=8, text="低风险<br>高收益", showarrow=False, 
                          bgcolor="rgba(0,200,81,0.1)", bordercolor="rgba(0,200,81,0.3)")
        fig.add_annotation(x=75, y=8, text="高风险<br>高收益", showarrow=False,
                          bgcolor="rgba(255,193,7,0.1)", bordercolor="rgba(255,193,7,0.3)")
        fig.add_annotation(x=25, y=-8, text="低风险<br>低收益", showarrow=False,
                          bgcolor="rgba(108,117,125,0.1)", bordercolor="rgba(108,117,125,0.3)")
        fig.add_annotation(x=75, y=-8, text="高风险<br>低收益", showarrow=False,
                          bgcolor="rgba(255,68,68,0.1)", bordercolor="rgba(255,68,68,0.3)")
        
        # 更新布局
        fig.update_layout(
            title={
                'text': '🎯 风险收益分析图',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['dark']}
            },
            xaxis_title="风险评分",
            yaxis_title="预期收益率 (%)",
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        return fig
    
    def create_sector_analysis_chart(self, sector_data: Dict) -> go.Figure:
        """创建行业分析图表"""
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('行业表现排名', '行业资金流向', '行业估值水平', '行业情绪指数'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        sectors = list(sector_data.keys())
        
        # 1. 行业表现排名
        performance = [sector_data[sector].get('performance', 0) for sector in sectors]
        colors_perf = [self.stock_colors['up'] if p > 0 else self.stock_colors['down'] for p in performance]
        
        fig.add_trace(
            go.Bar(
                x=sectors,
                y=performance,
                marker_color=colors_perf,
                text=[f'{p:.1f}%' for p in performance],
                textposition='outside',
                name='涨跌幅'
            ),
            row=1, col=1
        )
        
        # 2. 资金流向
        money_flow = [sector_data[sector].get('money_flow', 0) for sector in sectors]
        colors_flow = [self.stock_colors['up'] if f > 0 else self.stock_colors['down'] for f in money_flow]
        
        fig.add_trace(
            go.Bar(
                x=sectors,
                y=money_flow,
                marker_color=colors_flow,
                text=[f'{f:.1f}亿' for f in money_flow],
                textposition='outside',
                name='资金净流入'
            ),
            row=1, col=2
        )
        
        # 3. 估值水平
        pe_ratios = [sector_data[sector].get('pe_ratio', 20) for sector in sectors]
        pb_ratios = [sector_data[sector].get('pb_ratio', 2) for sector in sectors]
        
        fig.add_trace(
            go.Scatter(
                x=pe_ratios,
                y=pb_ratios,
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=performance,
                    colorscale='RdYlGn',
                    showscale=False
                ),
                text=sectors,
                textposition="middle center",
                name='估值分布'
            ),
            row=2, col=1
        )
        
        # 4. 情绪指数饼图
        sentiment_scores = [sector_data[sector].get('sentiment', 50) for sector in sectors]
        
        fig.add_trace(
            go.Pie(
                labels=sectors,
                values=sentiment_scores,
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title={
                'text': '🏭 行业分析仪表板',
                'x': 0.5,
                'font': {'size': 20, 'color': self.colors['dark']}
            },
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        return fig
    
    def create_performance_metrics_card(self, metrics: Dict) -> None:
        """创建性能指标卡片"""
        
        st.markdown("### 📊 关键性能指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._create_metric_card(
                "年化收益率",
                f"{metrics.get('annual_return', 0):.2f}%",
                metrics.get('annual_return', 0) - 10,  # 相对基准的差值
                "相对沪深300"
            )
        
        with col2:
            self._create_metric_card(
                "最大回撤",
                f"{metrics.get('max_drawdown', 0):.2f}%",
                None,
                "风险控制指标"
            )
        
        with col3:
            self._create_metric_card(
                "夏普比率",
                f"{metrics.get('sharpe_ratio', 0):.2f}",
                None,
                "风险调整收益"
            )
        
        with col4:
            self._create_metric_card(
                "胜率",
                f"{metrics.get('win_rate', 0):.1f}%",
                None,
                "交易成功率"
            )
    
    def _create_metric_card(self, title: str, value: str, delta: float = None, help_text: str = ""):
        """创建指标卡片"""
        
        if delta is not None:
            st.metric(
                label=title,
                value=value,
                delta=f"{delta:+.2f}%",
                help=help_text
            )
        else:
            st.metric(
                label=title,
                value=value,
                help=help_text
            )

def create_beautiful_summary_cards(analysis_result: Dict) -> None:
    """创建美观的总结卡片"""
    
    # 获取评分
    final_score = analysis_result.get('final_score', 50)
    recommendation = analysis_result.get('recommendation', {})
    
    # 主要评分卡片
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; font-size: 3rem;">{final_score:.1f}</h1>
        <h3 style="margin: 0.5rem 0; opacity: 0.9;">综合评分</h3>
        <h2 style="margin: 0;">{recommendation.get('emoji', '📊')} {recommendation.get('level', '分析中')}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 详细评分卡片
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [
        ("技术面", analysis_result['technical']['score'] if analysis_result.get('technical') else 50, "📊"),
        ("基本面", analysis_result['fundamental']['score'] if analysis_result.get('fundamental') else 50, "💼"),
        ("情绪面", analysis_result['sentiment']['score'] if analysis_result.get('sentiment') else 50, "😊"),
        ("事件面", analysis_result['event']['score'] if analysis_result.get('event') else 50, "⚡")
    ]
    
    for i, (col, (name, score, emoji)) in enumerate(zip([col1, col2, col3, col4], scores)):
        color = "#00C851" if score >= 70 else "#FFC107" if score >= 50 else "#FF4444"
        
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                text-align: center;
                border-left: 4px solid {color};
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
            ">
                <div style="font-size: 2rem;">{emoji}</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{score:.0f}</div>
                <div style="color: #666; font-size: 0.9rem;">{name}</div>
            </div>
            """, unsafe_allow_html=True)

# 使用示例
def main():
    """主函数示例"""
    st.title("📊 增强数据可视化演示")
    
    # 模拟数据
    analysis_result = {
        'final_score': 75.5,
        'technical': {'score': 80},
        'fundamental': {'score': 70},
        'sentiment': {'score': 65},
        'event': {'score': 85},
        'recommendation': {
            'level': '推荐买入',
            'emoji': '📈',
            'action': '买入'
        }
    }
    
    # 显示美观的总结卡片
    create_beautiful_summary_cards(analysis_result)
    
    # 创建可视化实例
    viz = EnhancedVisualization()
    
    # 显示综合仪表板
    dashboard = viz.create_comprehensive_dashboard(analysis_result)
    st.plotly_chart(dashboard, use_container_width=True)

if __name__ == "__main__":
    main()