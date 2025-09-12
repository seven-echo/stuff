# event_analyzer.py - 全面事件分析系统

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
import logging
from dataclasses import dataclass
from enum import Enum
import akshare as ak
import feedparser
import asyncio
import aiohttp
from textblob import TextBlob
import jieba
import jieba.analyse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """事件类型枚举"""
    FINANCIAL_REPORT = "财报发布"
    DIVIDEND = "分红派息"
    MERGER_ACQUISITION = "并购重组"
    POLICY_CHANGE = "政策变化"
    INDUSTRY_NEWS = "行业动态"
    MANAGEMENT_CHANGE = "管理层变动"
    LEGAL_ISSUE = "法律诉讼"
    PRODUCT_LAUNCH = "产品发布"
    PARTNERSHIP = "战略合作"
    INVESTMENT = "投资事件"
    MARKET_SENTIMENT = "市场情绪"
    MACRO_ECONOMIC = "宏观经济"
    REGULATORY = "监管政策"
    TECHNOLOGY = "技术突破"
    NATURAL_DISASTER = "自然灾害"
    GEOPOLITICAL = "地缘政治"

class EventImpact(Enum):
    """事件影响程度"""
    VERY_POSITIVE = "重大利好"
    POSITIVE = "利好"
    NEUTRAL = "中性"
    NEGATIVE = "利空"
    VERY_NEGATIVE = "重大利空"

class EventUrgency(Enum):
    """事件紧急程度"""
    IMMEDIATE = "立即"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

@dataclass
class Event:
    """事件数据类"""
    title: str
    content: str
    source: str
    timestamp: datetime
    event_type: EventType
    impact: EventImpact
    urgency: EventUrgency
    confidence: float  # 0-1, 事件识别置信度
    related_symbols: List[str]
    keywords: List[str]
    sentiment_score: float  # -1到1
    market_cap_impact: float  # 预估市值影响百分比

class ComprehensiveEventAnalyzer:
    """全面事件分析器"""
    
    def __init__(self):
        self.event_keywords = self._init_event_keywords()
        self.impact_weights = self._init_impact_weights()
        self.news_sources = self._init_news_sources()
        
        # 初始化中文分词
        jieba.initialize()
        
    def _init_event_keywords(self) -> Dict[EventType, Dict[str, List[str]]]:
        """初始化事件关键词库"""
        return {
            EventType.FINANCIAL_REPORT: {
                "positive": ["业绩超预期", "净利润增长", "营收增长", "盈利能力提升", "业绩大增"],
                "negative": ["业绩下滑", "亏损", "营收下降", "业绩不及预期", "财务造假"],
                "neutral": ["财报发布", "业绩公告", "年报", "季报", "中报"]
            },
            EventType.DIVIDEND: {
                "positive": ["高分红", "分红增加", "特别股息", "现金分红"],
                "negative": ["取消分红", "分红减少"],
                "neutral": ["分红方案", "股息", "派息"]
            },
            EventType.MERGER_ACQUISITION: {
                "positive": ["收购", "并购", "重组成功", "战略整合", "资产注入"],
                "negative": ["收购失败", "重组失败", "资产剥离"],
                "neutral": ["重大资产重组", "股权转让", "控制权变更"]
            },
            EventType.POLICY_CHANGE: {
                "positive": ["政策利好", "减税", "补贴", "扶持政策", "放开限制"],
                "negative": ["政策收紧", "限制政策", "加税", "监管加强"],
                "neutral": ["政策调整", "新政策", "监管政策"]
            },
            EventType.MANAGEMENT_CHANGE: {
                "positive": ["新CEO上任", "管理层优化", "引入人才"],
                "negative": ["高管离职", "管理层动荡", "CEO辞职"],
                "neutral": ["人事变动", "董事会", "管理层调整"]
            },
            EventType.LEGAL_ISSUE: {
                "positive": ["胜诉", "和解", "撤诉"],
                "negative": ["被起诉", "败诉", "罚款", "调查", "违规"],
                "neutral": ["诉讼", "法律纠纷", "合规检查"]
            },
            EventType.PRODUCT_LAUNCH: {
                "positive": ["新产品发布", "技术突破", "专利获得", "产品获奖"],
                "negative": ["产品召回", "技术故障", "产品下架"],
                "neutral": ["产品更新", "新品发布", "技术升级"]
            }
        }
    
    def _init_impact_weights(self) -> Dict[EventType, float]:
        """初始化事件影响权重"""
        return {
            EventType.FINANCIAL_REPORT: 0.9,
            EventType.MERGER_ACQUISITION: 0.8,
            EventType.POLICY_CHANGE: 0.7,
            EventType.LEGAL_ISSUE: 0.6,
            EventType.MANAGEMENT_CHANGE: 0.5,
            EventType.DIVIDEND: 0.4,
            EventType.PRODUCT_LAUNCH: 0.3,
            EventType.PARTNERSHIP: 0.3,
            EventType.INDUSTRY_NEWS: 0.2,
            EventType.MARKET_SENTIMENT: 0.6,
            EventType.MACRO_ECONOMIC: 0.8,
            EventType.REGULATORY: 0.7,
            EventType.TECHNOLOGY: 0.4,
            EventType.GEOPOLITICAL: 0.9
        }
    
    def _init_news_sources(self) -> Dict[str, Dict[str, str]]:
        """初始化新闻源配置"""
        return {
            "sina_finance": {
                "url": "https://feed.mix.sina.com.cn/api/roll/get",
                "type": "api",
                "encoding": "utf-8"
            },
            "eastmoney": {
                "url": "http://finance.eastmoney.com/news/",
                "type": "rss",
                "encoding": "utf-8"
            },
            "cnstock": {
                "url": "http://www.cnstock.com/",
                "type": "web",
                "encoding": "utf-8"
            },
            "securities_times": {
                "url": "http://www.stcn.com/",
                "type": "web", 
                "encoding": "utf-8"
            }
        }
    
    async def get_company_announcements(self, symbol: str, days: int = 7) -> List[Event]:
        """获取公司公告"""
        events = []
        
        try:
            # 使用AkShare获取公司公告
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            # 获取公告数据
            announcements = ak.stock_notice_report(symbol=symbol)
            
            if announcements is not None and len(announcements) > 0:
                for _, announcement in announcements.head(20).iterrows():
                    try:
                        event = self._parse_announcement(announcement, symbol)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"解析公告失败: {e}")
                        
        except Exception as e:
            logger.error(f"获取公司公告失败: {e}")
        
        return events
    
    def _parse_announcement(self, announcement: pd.Series, symbol: str) -> Optional[Event]:
        """解析公告内容"""
        try:
            title = str(announcement.get('公告标题', ''))
            content = str(announcement.get('公告摘要', title))
            pub_date = announcement.get('公告日期', datetime.now())
            
            if isinstance(pub_date, str):
                pub_date = datetime.strptime(pub_date, "%Y-%m-%d")
            
            # 事件类型识别
            event_type = self._classify_event_type(title + " " + content)
            
            # 影响分析
            impact = self._analyze_impact(title + " " + content, event_type)
            
            # 情感分析
            sentiment_score = self._analyze_sentiment(title + " " + content)
            
            # 关键词提取
            keywords = self._extract_keywords(title + " " + content)
            
            # 紧急程度评估
            urgency = self._assess_urgency(event_type, impact, sentiment_score)
            
            # 置信度评估
            confidence = self._calculate_confidence(event_type, impact, keywords)
            
            return Event(
                title=title,
                content=content,
                source="公司公告",
                timestamp=pub_date,
                event_type=event_type,
                impact=impact,
                urgency=urgency,
                confidence=confidence,
                related_symbols=[symbol],
                keywords=keywords,
                sentiment_score=sentiment_score,
                market_cap_impact=self._estimate_market_impact(impact, event_type)
            )
            
        except Exception as e:
            logger.error(f"解析公告失败: {e}")
            return None
    
    async def get_industry_news(self, industry: str, days: int = 3) -> List[Event]:
        """获取行业新闻"""
        events = []
        
        try:
            # 这里可以集成多个新闻源API
            # 示例：使用新浪财经API
            
            industry_keywords = {
                "科技": ["人工智能", "5G", "芯片", "互联网", "软件"],
                "医药": ["医药", "生物", "疫苗", "医疗", "制药"],
                "金融": ["银行", "保险", "证券", "基金", "金融科技"],
                "地产": ["房地产", "建筑", "基建", "城建"],
                "消费": ["消费", "零售", "食品", "饮料", "服装"],
                "能源": ["石油", "天然气", "煤炭", "新能源", "电力"]
            }
            
            keywords = industry_keywords.get(industry, [industry])
            
            for keyword in keywords[:3]:  # 限制关键词数量
                try:
                    news_events = await self._fetch_news_by_keyword(keyword, days)
                    events.extend(news_events)
                except Exception as e:
                    logger.warning(f"获取{keyword}新闻失败: {e}")
            
        except Exception as e:
            logger.error(f"获取行业新闻失败: {e}")
        
        return events[:10]  # 返回最相关的10条
    
    async def _fetch_news_by_keyword(self, keyword: str, days: int) -> List[Event]:
        """根据关键词获取新闻"""
        events = []
        
        try:
            # 模拟新闻获取 - 实际使用中应该集成真实的新闻API
            # 例如：新浪财经、东方财富、证券时报等
            
            sample_news = [
                {
                    "title": f"{keyword}行业迎来重大政策利好",
                    "content": f"相关部门发布{keyword}行业扶持政策，预计将对行业发展产生积极影响。",
                    "timestamp": datetime.now() - timedelta(hours=2),
                    "source": "财经新闻"
                },
                {
                    "title": f"{keyword}板块表现强劲",
                    "content": f"今日{keyword}板块整体上涨，多只个股涨停。",
                    "timestamp": datetime.now() - timedelta(hours=5),
                    "source": "市场快讯"
                }
            ]
            
            for news_item in sample_news:
                event = Event(
                    title=news_item["title"],
                    content=news_item["content"],
                    source=news_item["source"],
                    timestamp=news_item["timestamp"],
                    event_type=EventType.INDUSTRY_NEWS,
                    impact=self._analyze_impact(news_item["title"] + " " + news_item["content"], EventType.INDUSTRY_NEWS),
                    urgency=EventUrgency.MEDIUM,
                    confidence=0.7,
                    related_symbols=[],
                    keywords=[keyword],
                    sentiment_score=self._analyze_sentiment(news_item["title"] + " " + news_item["content"]),
                    market_cap_impact=0.02
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"获取关键词新闻失败: {e}")
        
        return events
    
    async def get_macro_events(self, days: int = 7) -> List[Event]:
        """获取宏观经济事件"""
        events = []
        
        try:
            # 获取宏观经济数据
            macro_events = [
                {
                    "title": "央行降准释放流动性",
                    "content": "央行宣布下调存款准备金率0.25个百分点，释放长期资金约5000亿元。",
                    "event_type": EventType.MACRO_ECONOMIC,
                    "impact": EventImpact.POSITIVE,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "title": "CPI数据超预期",
                    "content": "11月CPI同比上涨2.3%，超出市场预期的2.1%。",
                    "event_type": EventType.MACRO_ECONOMIC,
                    "impact": EventImpact.NEGATIVE,
                    "timestamp": datetime.now() - timedelta(days=2)
                },
                {
                    "title": "GDP数据符合预期",
                    "content": "三季度GDP同比增长5.2%，符合市场预期。",
                    "event_type": EventType.MACRO_ECONOMIC,
                    "impact": EventImpact.NEUTRAL,
                    "timestamp": datetime.now() - timedelta(days=3)
                }
            ]
            
            for macro_event in macro_events:
                event = Event(
                    title=macro_event["title"],
                    content=macro_event["content"],
                    source="宏观数据",
                    timestamp=macro_event["timestamp"],
                    event_type=macro_event["event_type"],
                    impact=macro_event["impact"],
                    urgency=EventUrgency.HIGH,
                    confidence=0.9,
                    related_symbols=[],
                    keywords=self._extract_keywords(macro_event["title"] + " " + macro_event["content"]),
                    sentiment_score=self._impact_to_sentiment(macro_event["impact"]),
                    market_cap_impact=self._estimate_macro_impact(macro_event["impact"])
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"获取宏观事件失败: {e}")
        
        return events
    
    async def get_regulatory_events(self, days: int = 7) -> List[Event]:
        """获取监管政策事件"""
        events = []
        
        try:
            # 监管事件示例
            regulatory_events = [
                {
                    "title": "证监会发布新规加强上市公司监管",
                    "content": "证监会发布新的上市公司信息披露规定，要求更加严格的财务披露。",
                    "impact": EventImpact.NEGATIVE,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "title": "银保监会放宽保险资金投资限制",
                    "content": "银保监会发布新规，允许保险资金投资更多类型的资产。",
                    "impact": EventImpact.POSITIVE,
                    "timestamp": datetime.now() - timedelta(days=2)
                }
            ]
            
            for reg_event in regulatory_events:
                event = Event(
                    title=reg_event["title"],
                    content=reg_event["content"],
                    source="监管公告",
                    timestamp=reg_event["timestamp"],
                    event_type=EventType.REGULATORY,
                    impact=reg_event["impact"],
                    urgency=EventUrgency.HIGH,
                    confidence=0.95,
                    related_symbols=[],
                    keywords=self._extract_keywords(reg_event["title"] + " " + reg_event["content"]),
                    sentiment_score=self._impact_to_sentiment(reg_event["impact"]),
                    market_cap_impact=self._estimate_regulatory_impact(reg_event["impact"])
                )
                events.append(event)
                
        except Exception as e:
            logger.error(f"获取监管事件失败: {e}")
        
        return events
    
    def _classify_event_type(self, text: str) -> EventType:
        """事件类型分类"""
        text_lower = text.lower()
        
        # 基于关键词的简单分类
        for event_type, keywords_dict in self.event_keywords.items():
            all_keywords = []
            for keyword_list in keywords_dict.values():
                all_keywords.extend(keyword_list)
            
            for keyword in all_keywords:
                if keyword.lower() in text_lower:
                    return event_type
        
        return EventType.INDUSTRY_NEWS  # 默认类型
    
    def _analyze_impact(self, text: str, event_type: EventType) -> EventImpact:
        """分析事件影响"""
        text_lower = text.lower()
        
        if event_type in self.event_keywords:
            keywords_dict = self.event_keywords[event_type]
            
            positive_score = sum(1 for keyword in keywords_dict.get("positive", []) 
                               if keyword.lower() in text_lower)
            negative_score = sum(1 for keyword in keywords_dict.get("negative", []) 
                               if keyword.lower() in text_lower)
            
            if positive_score > negative_score:
                return EventImpact.POSITIVE if positive_score == 1 else EventImpact.VERY_POSITIVE
            elif negative_score > positive_score:
                return EventImpact.NEGATIVE if negative_score == 1 else EventImpact.VERY_NEGATIVE
        
        return EventImpact.NEUTRAL
    
    def _analyze_sentiment(self, text: str) -> float:
        """情感分析"""
        try:
            # 中文情感分析
            if self._is_chinese(text):
                return self._chinese_sentiment_analysis(text)
            else:
                # 英文情感分析
                blob = TextBlob(text)
                return blob.sentiment.polarity
        except:
            return 0.0
    
    def _is_chinese(self, text: str) -> bool:
        """判断是否为中文文本"""
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars) > len(text) * 0.3
    
    def _chinese_sentiment_analysis(self, text: str) -> float:
        """中文情感分析"""
        # 简化的中文情感分析
        positive_words = ["好", "利好", "增长", "上涨", "成功", "突破", "优秀", "强劲", "超预期"]
        negative_words = ["坏", "利空", "下跌", "失败", "问题", "风险", "亏损", "下滑", "不及预期"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_words = len(text)
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / max(1, total_words / 10)
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        try:
            if self._is_chinese(text):
                # 中文关键词提取
                keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=False)
                return keywords
            else:
                # 英文关键词提取
                blob = TextBlob(text)
                words = [word.lower() for word in blob.words if len(word) > 3]
                # 简单的频率统计
                from collections import Counter
                word_freq = Counter(words)
                return [word for word, freq in word_freq.most_common(5)]
        except:
            return []
    
    def _assess_urgency(self, event_type: EventType, impact: EventImpact, sentiment_score: float) -> EventUrgency:
        """评估紧急程度"""
        urgency_score = 0
        
        # 基于事件类型
        high_urgency_types = [EventType.FINANCIAL_REPORT, EventType.MERGER_ACQUISITION, 
                             EventType.LEGAL_ISSUE, EventType.MACRO_ECONOMIC, EventType.REGULATORY]
        if event_type in high_urgency_types:
            urgency_score += 2
        
        # 基于影响程度
        if impact in [EventImpact.VERY_POSITIVE, EventImpact.VERY_NEGATIVE]:
            urgency_score += 3
        elif impact in [EventImpact.POSITIVE, EventImpact.NEGATIVE]:
            urgency_score += 1
        
        # 基于情感强度
        if abs(sentiment_score) > 0.5:
            urgency_score += 1
        
        if urgency_score >= 4:
            return EventUrgency.IMMEDIATE
        elif urgency_score >= 2:
            return EventUrgency.HIGH
        elif urgency_score >= 1:
            return EventUrgency.MEDIUM
        else:
            return EventUrgency.LOW
    
    def _calculate_confidence(self, event_type: EventType, impact: EventImpact, keywords: List[str]) -> float:
        """计算识别置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于关键词匹配度
        if len(keywords) > 0:
            confidence += 0.1 * len(keywords)
        
        # 基于事件类型权重
        if event_type in self.impact_weights:
            confidence += 0.2 * self.impact_weights[event_type]
        
        # 基于影响明确性
        if impact != EventImpact.NEUTRAL:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _estimate_market_impact(self, impact: EventImpact, event_type: EventType) -> float:
        """估算市值影响"""
        base_impact = {
            EventImpact.VERY_POSITIVE: 0.08,
            EventImpact.POSITIVE: 0.03,
            EventImpact.NEUTRAL: 0.0,
            EventImpact.NEGATIVE: -0.03,
            EventImpact.VERY_NEGATIVE: -0.08
        }
        
        type_multiplier = self.impact_weights.get(event_type, 0.5)
        
        return base_impact[impact] * type_multiplier
    
    def _impact_to_sentiment(self, impact: EventImpact) -> float:
        """影响转情感分数"""
        impact_to_sentiment_map = {
            EventImpact.VERY_POSITIVE: 0.8,
            EventImpact.POSITIVE: 0.4,
            EventImpact.NEUTRAL: 0.0,
            EventImpact.NEGATIVE: -0.4,
            EventImpact.VERY_NEGATIVE: -0.8
        }
        return impact_to_sentiment_map[impact]
    
    def _estimate_macro_impact(self, impact: EventImpact) -> float:
        """估算宏观事件影响"""
        macro_multiplier = 1.5  # 宏观事件影响更大
        return self._estimate_market_impact(impact, EventType.MACRO_ECONOMIC) * macro_multiplier
    
    def _estimate_regulatory_impact(self, impact: EventImpact) -> float:
        """估算监管事件影响"""
        regulatory_multiplier = 1.2  # 监管事件影响较大
        return self._estimate_market_impact(impact, EventType.REGULATORY) * regulatory_multiplier
    
    async def comprehensive_event_analysis(self, symbol: str, company_name: str = "", 
                                         industry: str = "", days: int = 7) -> Dict[str, Any]:
        """综合事件分析"""
        
        all_events = []
        
        try:
            # 并发获取各类事件
            tasks = [
                self.get_company_announcements(symbol, days),
                self.get_industry_news(industry, days) if industry else asyncio.sleep(0),
                self.get_macro_events(days),
                self.get_regulatory_events(days)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            for result in results:
                if isinstance(result, list):
                    all_events.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"获取事件失败: {result}")
            
            # 事件去重和排序
            all_events = self._deduplicate_events(all_events)
            all_events.sort(key=lambda x: (x.urgency.value, x.timestamp), reverse=True)
            
            # 计算综合评分
            event_score = self._calculate_event_score(all_events)
            
            # 生成分析报告
            analysis_report = self._generate_analysis_report(all_events, symbol, company_name)
            
            return {
                "score": event_score,
                "total_events": len(all_events),
                "events": all_events[:20],  # 返回最重要的20个事件
                "analysis_report": analysis_report,
                "risk_level": self._assess_overall_risk(all_events),
                "opportunity_level": self._assess_opportunity_level(all_events),
                "summary": self._generate_summary(all_events)
            }
            
        except Exception as e:
            logger.error(f"综合事件分析失败: {e}")
            return {
                "score": 50,
                "total_events": 0,
                "events": [],
                "analysis_report": "事件分析暂时不可用",
                "risk_level": "未知",
                "opportunity_level": "未知",
                "summary": "无法获取事件数据"
            }
    
    def _deduplicate_events(self, events: List[Event]) -> List[Event]:
        """事件去重"""
        seen_titles = set()
        unique_events = []
        
        for event in events:
            title_key = event.title.strip().lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_events.append(event)
        
        return unique_events
    
    def _calculate_event_score(self, events: List[Event]) -> float:
        """计算事件综合评分"""
        if not events:
            return 50.0
        
        total_impact = 0.0
        total_weight = 0.0
        
        for event in events:
            # 时间衰减因子
            days_ago = (datetime.now() - event.timestamp).days
            time_decay = max(0.1, 1.0 - days_ago * 0.1)
            
            # 事件权重
            event_weight = self.impact_weights.get(event.event_type, 0.5) * event.confidence * time_decay
            
            # 影响分数
            impact_score = {
                EventImpact.VERY_POSITIVE: 90,
                EventImpact.POSITIVE: 70,
                EventImpact.NEUTRAL: 50,
                EventImpact.NEGATIVE: 30,
                EventImpact.VERY_NEGATIVE: 10
            }[event.impact]
            
            total_impact += impact_score * event_weight
            total_weight += event_weight
        
        if total_weight == 0:
            return 50.0
        
        final_score = total_impact / total_weight
        return max(0, min(100, final_score))
    
    def _assess_overall_risk(self, events: List[Event]) -> str:
        """评估整体风险等级"""
        negative_events = [e for e in events if e.impact in [EventImpact.NEGATIVE, EventImpact.VERY_NEGATIVE]]
        
        if not negative_events:
            return "低风险"
        
        high_risk_count = sum(1 for e in negative_events if e.urgency in [EventUrgency.IMMEDIATE, EventUrgency.HIGH])
        
        if high_risk_count >= 3:
            return "高风险"
        elif high_risk_count >= 1:
            return "中风险"
        else:
            return "低风险"
    
    def _assess_opportunity_level(self, events: List[Event]) -> str:
        """评估机会等级"""
        positive_events = [e for e in events if e.impact in [EventImpact.POSITIVE, EventImpact.VERY_POSITIVE]]
        
        if not positive_events:
            return "机会较少"
        
        high_opportunity_count = sum(1 for e in positive_events if e.urgency in [EventUrgency.IMMEDIATE, EventUrgency.HIGH])
        
        if high_opportunity_count >= 3:
            return "机会丰富"
        elif high_opportunity_count >= 1:
            return "机会适中"
        else:
            return "机会较少"
    
    def _generate_analysis_report(self, events: List[Event], symbol: str, company_name: str) -> str:
        """生成分析报告"""
        if not events:
            return f"{company_name}({symbol}) 近期无重大事件"
        
        # 统计各类事件
        event_stats = {}
        for event in events:
            event_type = event.event_type.value
            if event_type not in event_stats:
                event_stats[event_type] = {"positive": 0, "negative": 0, "neutral": 0}
            
            if event.impact in [EventImpact.POSITIVE, EventImpact.VERY_POSITIVE]:
                event_stats[event_type]["positive"] += 1
            elif event.impact in [EventImpact.NEGATIVE, EventImpact.VERY_NEGATIVE]:
                event_stats[event_type]["negative"] += 1
            else:
                event_stats[event_type]["neutral"] += 1
        
        # 生成报告
        report_lines = [f"{company_name}({symbol}) 事件分析报告："]
        
        for event_type, stats in event_stats.items():
            total = sum(stats.values())
            if total > 0:
                report_lines.append(f"• {event_type}: {total}条事件 (利好{stats['positive']}条, 利空{stats['negative']}条)")
        
        # 添加重要事件
        important_events = [e for e in events[:5] if e.urgency in [EventUrgency.IMMEDIATE, EventUrgency.HIGH]]
        if important_events:
            report_lines.append("\n重要事件:")
            for event in important_events:
                impact_emoji = {
                    EventImpact.VERY_POSITIVE: "🚀",
                    EventImpact.POSITIVE: "📈",
                    EventImpact.NEUTRAL: "➡️",
                    EventImpact.NEGATIVE: "📉",
                    EventImpact.VERY_NEGATIVE: "⚠️"
                }[event.impact]
                report_lines.append(f"  {impact_emoji} {event.title}")
        
        return "\n".join(report_lines)
    
    def _generate_summary(self, events: List[Event]) -> str:
        """生成事件摘要"""
        if not events:
            return "近期无重大事件"
        
        positive_count = sum(1 for e in events if e.impact in [EventImpact.POSITIVE, EventImpact.VERY_POSITIVE])
        negative_count = sum(1 for e in events if e.impact in [EventImpact.NEGATIVE, EventImpact.VERY_NEGATIVE])
        
        if positive_count > negative_count:
            return f"近期利好事件较多({positive_count}条利好 vs {negative_count}条利空)，整体偏向积极"
        elif negative_count > positive_count:
            return f"近期利空事件较多({negative_count}条利空 vs {positive_count}条利好)，需要谨慎关注"
        else:
            return f"近期正负面事件基本平衡({positive_count}条利好 vs {negative_count}条利空)"

# 使用示例
async def example_usage():
    """使用示例"""
    analyzer = ComprehensiveEventAnalyzer()
    
    # 分析特定股票的事件
    result = await analyzer.comprehensive_event_analysis(
        symbol="000001",
        company_name="平安银行",
        industry="金融",
        days=7
    )
    
    print(f"事件评分: {result['score']}")
    print(f"风险等级: {result['risk_level']}")
    print(f"机会等级: {result['opportunity_level']}")
    print(f"分析报告: {result['analysis_report']}")
    
    print("\n重要事件:")
    for event in result['events'][:5]:
        print(f"- {event.title} ({event.impact.value})")

if __name__ == "__main__":
    asyncio.run(example_usage())