# 🧠 全维度AI选股系统

基于OpenBB + AkShare的智能股票分析平台，提供**技术面 + 基本面+ 情绪面 + 突发事件**四维一体分析。

## ✨ 核心特性

### 🔧 技术面分析
- **多周期技术指标**: MA、RSI、MACD、KDJ等20+指标
- **智能信号识别**: 自动识别金叉、死叉、突破等关键信号
- **可视化图表**: 专业K线图表，支持多指标叠加显示

### 💼 基本面分析  
- **财务指标评估**: PE、ROE、负债率等关键财务数据
- **估值分析**: 基于多种估值模型的综合评估
- **行业对比**: 同行业公司对比分析

### 😊 情绪面分析
- **新闻情感分析**: 基于AI的新闻情感识别
- **市场情绪监控**: 实时跟踪市场情绪变化
- **社交媒体分析**: 集成多平台情绪数据

### ⚡ 事件面分析
- **突发事件监控**: 实时监控可能影响股价的重大事件
- **风险评估**: 多维度风险等级评估
- **政策影响**: 政策变化对股票的潜在影响分析

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/comprehensive-stock-analyzer.git
cd comprehensive-stock-analyzer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run comprehensive_stock_analyzer.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:8501

## 📊 使用指南

### 基本使用

1. **选择市场**: 在侧边栏选择要分析的市场(A股/美股/港股)
2. **输入股票代码**: 
   - A股: 输入6位数字代码(如: 000001)
   - 美股: 输入股票代码(如: AAPL)
3. **选择分析模式**: 
   - 全维度分析(推荐)
   - 技术面优先
   - 基本面优先
   - 情绪面优先
4. **开始分析**: 点击"开始全维度分析"按钮

### 高级设置

- **启用新闻情绪分析**: 开启后会分析相关新闻情感
- **启用基本面分析**: 开启后会进行财务数据分析
- **风险偏好设置**: 根据个人风险承受能力调整

## 🛠️ 技术架构

```
系统架构:
├── 数据层
│   ├── OpenBB (全球金融数据)
│   ├── AkShare (中国市场数据)
│   └── YFinance (备用数据源)
├── 分析层
│   ├── 技术指标计算引擎
│   ├── 基本面分析模块
│   ├── 情感分析引擎
│   └── 事件监控系统
├── 评分层
│   ├── 多维度评分算法
│   ├── 权重动态调整
│   └── 综合推荐引擎
└── 展示层
    ├── Streamlit Web界面
    ├── 交互式图表
    └── 实时数据更新
```

## 📈 评分算法

### 技术面评分 (40%权重)
- 均线系统: 25分
- RSI指标: 20分  
- MACD信号: 20分
- KDJ指标: 15分
- 成交量: 20分

### 基本面评分 (30%权重)
- PE估值: 30分
- ROE盈利能力: 40分
- 负债健康度: 20分
- 成长性: 10分

### 情绪面评分 (20%权重)
- 新闻情感: 60分
- 市场情绪: 40分

### 事件面评分 (10%权重)
- 突发事件影响: 70分
- 政策风险: 30分

## 🔧 配置说明

### 数据源配置

```python
# OpenBB配置
# 需要设置OpenBB的API密钥(如果使用付费数据源)

# AkShare配置  
# AkShare大部分数据免费，无需配置

# 新闻API配置(可选)
# 可以配置新闻API密钥获得更好的情感分析效果
```

### 自定义权重

可以在代码中调整各维度的权重:

```python
# 在comprehensive_analysis方法中修改
weights = {
    'technical': 0.4,    # 技术面权重
    'fundamental': 0.3,  # 基本面权重  
    'sentiment': 0.2,    # 情绪面权重
    'event': 0.1         # 事件面权重
}
```

## 📱 部署指南

### 本地部署

```bash
# 直接运行
streamlit run comprehensive_stock_analyzer.py
```

### 云端部署

#### Streamlit Cloud (推荐)
1. 将代码推送到GitHub
2. 在 [Streamlit Cloud](https://streamlit.io/cloud) 创建应用
3. 连接GitHub仓库自动部署

#### Heroku部署
1. 创建`Procfile`文件:
```
web: sh setup.sh && streamlit run comprehensive_stock_analyzer.py --server.port=$PORT --server.address=0.0.0.0
```

2. 创建`setup.sh`文件:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### Docker部署
1. 创建`Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "comprehensive_stock_analyzer.py"]
```

2. 构建和运行:
```bash
docker build -t stock-analyzer .
docker run -p 8501:8501 stock-analyzer
```

## ⚠️ 注意事项

### 数据限制
- **OpenBB**: 部分高级数据需要付费API
- **AkShare**: 免费使用，但有请求频率限制
- **实时数据**: 可能有15-20分钟延迟

### 使用限制
- 本工具仅供参考，不构成投资建议
- 投资有风险，入市需谨慎
- 建议结合多种分析方法做出投资决策

### 性能优化
- 使用了Streamlit的缓存机制提升性能
- 建议在高配置服务器上运行以获得更好体验
- 可以通过调整分析股票数量来平衡速度和准确性

## 🔄 更新日志

### v1.0.0 (2024-01-01)
- ✅ 基础技术分析功能
- ✅ OpenBB数据集成
- ✅ AkShare A股数据支持
- ✅ 基础Web界面

### v1.1.0 (计划中)
- 🔄 增强基本面分析
- 🔄 优化情感分析算法
- 🔄 添加更多技术指标
- 🔄 支持投资组合分析

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送到分支: `git push origin feature/AmazingFeature`
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页: [GitHub Repository](https://github.com/your-username/comprehensive-stock-analyzer)
- 问题反馈: [GitHub Issues](https://github.com/your-username/comprehensive-stock-analyzer/issues)
- 邮箱: your-email@example.com

## 🙏 致谢

- [OpenBB](https://openbb.co/) - 提供强大的金融数据平台
- [AkShare](https://akshare.akfamily.xyz/) - 提供优质的中文金融数据
- [Streamlit](https://streamlit.io/) - 提供优秀的Web应用框架
- [Plotly](https://plotly.com/) - 提供专业的图表组件

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！