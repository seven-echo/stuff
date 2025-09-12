# event_integration.py - 事件分析集成模块

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
from event_analyzer import ComprehensiveEventAnalyzer, Event, EventType, EventImpact, EventUrgency

class EventAnalysisUI:
    """事件分析用户界面"""
    
    def __init__(self):
        self.analyzer = ComprehensiveEventAnalyzer()
    
    def display_event_analysis(self, symbol: str, company_name: str, industry: str = ""):
        """显示事件分析界面"""
        
        st.subheader("⚡ 全面事件分析")
        
        # 分析设置
        col1, col2, col3 = st.columns(3)
        with col1:
            days = st.selectbox("分析时间范围", [3, 7, 14, 30], index=1)
        with col2:
            event_types = st.multiselect(
                "事件类型筛选",
                [e.value for e in EventType],
                default=[EventType.FINANCIAL_REPORT.value, EventType.POLICY_CHANGE.value, EventType.MERGER_ACQUISITION.value]
            )
        with col3:
            min_impact = st.selectbox("最小影响等级", ["全部", "利好", "重大利好"], index=0)
        
        # 开始分析按钮
        if st.button("🔍 开始事件分析", key="event_analysis"):
            with st.spinner("正在分析相关事件..."):
                # 运行异步分析
                result = asyncio.run(
                    self.analyzer.comprehensive_event_analysis(symbol, company_name, industry, days)
                )
                
                # 缓存结果
                st.session_state['event_analysis_result'] = result
        
        # 显示分析结果
        if 'event_analysis_result' in st.session_state:
            result = st.session_state['event_analysis_result']
            self._display_analysis_results(result, symbol, company_name)
    
    def _display_analysis_results(self, result: dict, symbol: str, company_name: str):
        """显示分析结果"""
        
        # 总体评分和状态
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = result['score']
            score_color = "success" if score >= 70 else "warning" if score >= 50 else "error"
            st.metric("事件评分", f"{score:.1f}/100")
        
        with col2:
            st.metric("事件总数", result['total_events'])
        
        with col3:
            risk_color = {"低风险": "success", "中风险": "warning", "高风险": "error"}
            risk_level = result['risk_level']
            st.markdown(f"**风险等级:** :{risk_color.get(risk_level, 'info')}[{risk_level}]")
        
        with col4:
            opp_color = {"机会丰富": "success", "机会适中": "warning", "机会较少": "info"}
            opp_level = result['opportunity_level']
            st.markdown(f"**机会等级:** :{opp_color.get(opp_level, 'info')}[{opp_level}]")
        
        # 分析摘要
        st.markdown("### 📋 分析摘要")
        st.info(result['summary'])
        
        # 详细分析报告
        if result['analysis_report']:
            st.markdown("### 📊 详细分析报告")
            st.text(result['analysis_report'])
        
        # 事件时间线
        if result['events']:
            self._display_event_timeline(result['events'])
            
            # 事件详情表格
            self._display_event_table(result['events'])
            
            # 事件统计图表
            self._display_event_charts(result['events'])
    
    def _display_event_timeline(self, events: list):
        """显示事件时间线"""
        st.markdown("### 📅 事件时间线")
        
        # 准备时间线数据
        timeline_data = []
        for event in events[:15]:  # 显示最近15个事件
            timeline_data.append({
                'date': event.timestamp,
                'title': event.title[:50] + "..." if len(event.title) > 50 else event.title,
                'impact': event.impact.value,
                'type': event.event_type.value,
                'urgency': event.urgency.value,
                'sentiment': event.sentiment_score
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            
            # 创建时间线图
            fig = go.Figure()
            
            # 根据影响程度设置颜色
            colors = {
                "重大利好": "green",
                "利好": "lightgreen", 
                "中性": "gray",
                "利空": "orange",
                "重大利空": "red"
            }
            
            for impact in df['impact'].unique():
                mask = df['impact'] == impact
                fig.add_trace(go.Scatter(
                    x=df[mask]['date'],
                    y=[impact] * sum(mask),
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=colors.get(impact, 'gray'),
                        symbol='circle'
                    ),
                    text=df[mask]['title'],
                    textposition="middle right",
                    name=impact,
                    hovertemplate="<b>%{text}</b><br>时间: %{x}<br>影响: " + impact + "<extra></extra>"
                ))
            
            fig.update_layout(
                title="事件影响时间线",
                xaxis_title="时间",
                yaxis_title="影响程度",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _display_event_table(self, events: list):
        """显示事件详情表格"""
        st.markdown("### 📋 事件详情")
        
        # 准备表格数据
        table_data = []
        for i, event in enumerate(events[:10], 1):
            # 影响等级emoji
            impact_emoji = {
                "重大利好": "🚀",
                "利好": "📈",
                "中性": "➡️", 
                "利空": "📉",
                "重大利空": "⚠️"
            }
            
            # 紧急程度emoji
            urgency_emoji = {
                "立即": "🔴",
                "高": "🟡",
                "中": "🟢",
                "低": "⚪"
            }
            
            table_data.append({
                "序号": i,
                "时间": event.timestamp.strftime("%m-%d %H:%M"),
                "标题": event.title[:40] + "..." if len(event.title) > 40 else event.title,
                "类型": event.event_type.value,
                "影响": f"{impact_emoji.get(event.impact.value, '➡️')} {event.impact.value}",
                "紧急度": f"{urgency_emoji.get(event.urgency.value, '⚪')} {event.urgency.value}",
                "置信度": f"{event.confidence:.1%}",
                "来源": event.source
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 选择事件查看详情
            selected_event_idx = st.selectbox(
                "选择事件查看详情",
                range(len(events[:10])),
                format_func=lambda x: f"{x+1}. {events[x].title[:30]}..."
            )
            
            if selected_event_idx is not None:
                selected_event = events[selected_event_idx]
                self._display_event_details(selected_event)
    
    def _display_event_details(self, event: Event):
        """显示单个事件的详细信息"""
        st.markdown("#### 📖 事件详情")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**标题:** {event.title}")
            st.markdown(f"**内容:** {event.content}")
            
            if event.keywords:
                st.markdown(f"**关键词:** {', '.join(event.keywords)}")
        
        with col2:
            st.markdown(f"**事件类型:** {event.event_type.value}")
            st.markdown(f"**影响程度:** {event.impact.value}")
            st.markdown(f"**紧急程度:** {event.urgency.value}")
            st.markdown(f"**情感分数:** {event.sentiment_score:.2f}")
            st.markdown(f"**置信度:** {event.confidence:.1%}")
            st.markdown(f"**预估市值影响:** {event.market_cap_impact:.1%}")
            st.markdown(f"**信息来源:** {event.source}")
            st.markdown(f"**发布时间:** {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _display_event_charts(self, events: list):
        """显示事件统计图表"""
        st.markdown("### 📊 事件统计分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 事件类型分布
            type_counts = {}
            for event in events:
                event_type = event.event_type.value
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            if type_counts:
                fig_pie = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title="事件类型分布"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 影响程度分布
            impact_counts = {}
            for event in events:
                impact = event.impact.value
                impact_counts[impact] = impact_counts.get(impact, 0) + 1
            
            if impact_counts:
                fig_bar = px.bar(
                    x=list(impact_counts.keys()),
                    y=list(impact_counts.values()),
                    title="影响程度分布",
                    color=list(impact_counts.values()),
                    color_continuous_scale="RdYlGn"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # 事件情感趋势
        if len(events) > 1:
            st.markdown("#### 📈 事件情感趋势")
            
            sentiment_data = []
            for event in sorted(events, key=lambda x: x.timestamp):
                sentiment_data.append({
                    'date': event.timestamp,
                    'sentiment': event.sentiment_score,
                    'title': event.title[:30] + "..."
                })
            
            df_sentiment = pd.DataFrame(sentiment_data)
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=df_sentiment['date'],
                y=df_sentiment['sentiment'],
                mode='lines+markers',
                name='情感分数',
                text=df_sentiment['title'],
                hovertemplate="<b>%{text}</b><br>时间: %{x}<br>情感分数: %{y:.2f}<extra></extra>"
            ))
            
            # 添加零线
            fig_trend.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="中性线")
            
            fig_trend.update_layout(
                title="事件情感分数趋势",
                xaxis_title="时间",
                yaxis_title="情感分数 (-1到1)",
                height=400
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)

# 事件监控预警系统
class EventAlertSystem:
    """事件监控预警系统"""
    
    def __init__(self):
        self.analyzer = ComprehensiveEventAnalyzer()
        self.alert_rules = self._init_alert_rules()
    
    def _init_alert_rules(self):
        """初始化预警规则"""
        return {
            "high_impact_events": {
                "condition": lambda event: event.impact in [EventImpact.VERY_POSITIVE, EventImpact.VERY_NEGATIVE],
                "message": "检测到重大影响事件",
                "priority": "high"
            },
            "urgent_events": {
                "condition": lambda event: event.urgency == EventUrgency.IMMEDIATE,
                "message": "检测到紧急事件",
                "priority": "urgent"
            },
            "financial_events": {
                "condition": lambda event: event.event_type == EventType.FINANCIAL_REPORT,
                "message": "检测到财报相关事件",
                "priority": "medium"
            },
            "regulatory_events": {
                "condition": lambda event: event.event_type == EventType.REGULATORY,
                "message": "检测到监管政策事件",
                "priority": "high"
            }
        }
    
    async def monitor_events(self, symbols: list, check_interval: int = 300):
        """监控事件 (check_interval: 检查间隔，秒)"""
        
        st.markdown("### 🚨 事件监控预警")
        
        # 监控设置
        col1, col2, col3 = st.columns(3)
        with col1:
            enable_monitoring = st.checkbox("启用事件监控", value=False)
        with col2:
            alert_types = st.multiselect(
                "预警类型",
                ["重大影响", "紧急事件", "财报事件", "监管事件"],
                default=["重大影响", "紧急事件"]
            )
        with col3:
            notification_method = st.selectbox("通知方式", ["页面提醒", "邮件通知", "微信通知"])
        
        if enable_monitoring:
            # 显示监控状态
            status_placeholder = st.empty()
            alerts_placeholder = st.empty()
            
            # 模拟监控循环
            if st.button("开始监控"):
                with status_placeholder:
                    st.info("🟢 监控中... 每5分钟检查一次")
                
                # 这里应该是实际的监控循环
                # 为了演示，我们只做一次检查
                alerts = await self._check_alerts(symbols)
                
                if alerts:
                    with alerts_placeholder:
                        st.warning(f"⚠️ 检测到 {len(alerts)} 个预警事件")
                        for alert in alerts:
                            st.error(f"🚨 {alert['message']}: {alert['event'].title}")
                else:
                    with alerts_placeholder:
                        st.success("✅ 暂无预警事件")
    
    async def _check_alerts(self, symbols: list) -> list:
        """检查预警"""
        alerts = []
        
        for symbol in symbols:
            try:
                result = await self.analyzer.comprehensive_event_analysis(symbol, days=1)
                events = result.get('events', [])
                
                for event in events:
                    for rule_name, rule in self.alert_rules.items():
                        if rule['condition'](event):
                            alerts.append({
                                'rule': rule_name,
                                'message': rule['message'],
                                'priority': rule['priority'],
                                'event': event,
                                'symbol': symbol
                            })
            except Exception as e:
                logger.error(f"检查{symbol}预警失败: {e}")
        
        return alerts

# 事件分析配置界面
def display_event_config():
    """显示事件分析配置界面"""
    st.sidebar.markdown("### ⚡ 事件分析设置")
    
    # 数据源配置
    st.sidebar.markdown("#### 📡 数据源配置")
    enable_announcements = st.sidebar.checkbox("公司公告", value=True)
    enable_news = st.sidebar.checkbox("新闻资讯", value=True)
    enable_macro = st.sidebar.checkbox("宏观事件", value=True)
    enable_regulatory = st.sidebar.checkbox("监管政策", value=True)
    
    # 分析参数
    st.sidebar.markdown("#### 🔧 分析参数")
    sentiment_threshold = st.sidebar.slider("情感分析阈值", -1.0, 1.0, 0.0, 0.1)
    confidence_threshold = st.sidebar.slider("置信度阈值", 0.0, 1.0, 0.5, 0.1)
    time_decay_factor = st.sidebar.slider("时间衰减因子", 0.0, 1.0, 0.1, 0.05)
    
    # 预警设置
    st.sidebar.markdown("#### 🚨 预警设置")
    enable_alerts = st.sidebar.checkbox("启用预警", value=False)
    if enable_alerts:
        alert_email = st.sidebar.text_input("预警邮箱")
        alert_phone = st.sidebar.text_input("预警手机")
    
    return {
        "data_sources": {
            "announcements": enable_announcements,
            "news": enable_news,
            "macro": enable_macro,
            "regulatory": enable_regulatory
        },
        "analysis_params": {
            "sentiment_threshold": sentiment_threshold,
            "confidence_threshold": confidence_threshold,
            "time_decay_factor": time_decay_factor
        },
        "alert_settings": {
            "enabled": enable_alerts,
            "email": alert_email if enable_alerts else "",
            "phone": alert_phone if enable_alerts else ""
        }
    }

# 使用示例
def main():
    """主函数示例"""
    st.title("⚡ 全面事件分析系统")
    
    # 配置界面
    config = display_event_config()
    
    # 主分析界面
    ui = EventAnalysisUI()
    
    # 输入股票信息
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("股票代码", value="000001")
    with col2:
        company_name = st.text_input("公司名称", value="平安银行")
    
    industry = st.text_input("所属行业", value="金融")
    
    # 显示事件分析
    ui.display_event_analysis(symbol, company_name, industry)
    
    # 事件监控
    alert_system = EventAlertSystem()
    asyncio.run(alert_system.monitor_events([symbol]))

if __name__ == "__main__":
    main()