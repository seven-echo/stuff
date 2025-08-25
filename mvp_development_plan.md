# MVP开发计划（4周完成）

## 技术栈选择（极简方案）

### 前端技术
- **框架**: Next.js 14 (React)
- **UI库**: Tailwind CSS
- **状态管理**: React Hooks
- **部署**: Vercel (免费)

### 后端技术
- **框架**: Next.js API Routes
- **数据库**: SQLite (本地文件)
- **AI API**: OpenAI GPT-4
- **认证**: NextAuth.js

### 开发工具
- **代码编辑器**: VS Code
- **版本控制**: Git + GitHub
- **设计工具**: Figma (免费版)
- **项目管理**: Notion (免费)

## 第1周：基础架构搭建

### Day 1-2: 项目初始化
```bash
# 创建项目
npx create-next-app@latest literature-review-ai --typescript --tailwind --eslint
cd literature-review-ai

# 安装依赖
npm install openai next-auth sqlite3
npm install @types/sqlite3 --save-dev
```

### Day 3-4: 数据库设计
```sql
-- 用户表
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 文献表
CREATE TABLE papers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  title TEXT NOT NULL,
  authors TEXT,
  year INTEGER,
  abstract TEXT,
  keywords TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 生成的综述表
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  topic TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Day 5-7: 基础界面设计
```typescript
// pages/index.tsx
export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          智能文献综述生成器
        </h1>
        
        <div className="grid md:grid-cols-3 gap-6">
          <FeatureCard 
            title="文献综述生成"
            description="输入研究主题，AI自动生成高质量文献综述"
            icon="📝"
          />
          <FeatureCard 
            title="研究方向推荐"
            description="智能识别研究空白，推荐创新方向"
            icon="🎯"
          />
          <FeatureCard 
            title="文献管理"
            description="简单高效的文献管理和引用生成"
            icon="📚"
          />
        </div>
      </div>
    </div>
  );
}
```

## 第2周：核心功能开发

### Day 8-10: 文献综述生成功能
```typescript
// pages/api/generate-review.ts
import { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { topic, papers } = req.body;

    const prompt = `
      请基于以下研究主题和相关文献，生成一篇高质量的文献综述：

      研究主题：${topic}

      相关文献：
      ${papers.map((paper: any) => `
        - ${paper.title} (${paper.authors}, ${paper.year})
          ${paper.abstract}
      `).join('\n')}

      请按照以下结构生成文献综述：
      1. 研究背景和意义
      2. 主要研究方向概述
      3. 关键研究发现总结
      4. 研究空白和局限性
      5. 未来研究方向建议

      要求：
      - 语言学术化，逻辑清晰
      - 重点突出，结构合理
      - 字数控制在2000-3000字
    `;

    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 3000,
      temperature: 0.7,
    });

    const review = completion.choices[0].message.content;

    res.status(200).json({ review });
  } catch (error) {
    console.error('Error generating review:', error);
    res.status(500).json({ message: '生成失败，请重试' });
  }
}
```

### Day 11-12: 研究方向推荐功能
```typescript
// pages/api/recommend-research.ts
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { field, currentResearch } = req.body;

  const prompt = `
    基于以下研究领域和当前研究现状，推荐潜在的研究方向和问题：

    研究领域：${field}
    当前研究现状：${currentResearch}

    请从以下角度提供建议：
    1. 当前研究热点和趋势
    2. 潜在的研究空白
    3. 交叉学科机会
    4. 具体的研究问题建议
    5. 技术发展方向

    每个建议请包含：
    - 研究问题描述
    - 研究意义
    - 可行性分析
    - 预期贡献
  `;

  // AI API调用逻辑
}
```

### Day 13-14: 用户界面开发
```typescript
// components/ReviewGenerator.tsx
export default function ReviewGenerator() {
  const [topic, setTopic] = useState('');
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/generate-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, papers }),
      });
      
      const data = await response.json();
      setReview(data.review);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">文献综述生成</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              研究主题
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full p-3 border rounded-lg"
              placeholder="例如：人工智能在教育领域的应用"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              相关文献
            </label>
            <PaperInput papers={papers} setPapers={setPapers} />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !topic}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '生成中...' : '生成文献综述'}
          </button>

          {review && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">生成的文献综述</h3>
              <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
                {review}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

## 第3周：功能完善

### Day 15-17: 文献管理功能
```typescript
// components/PaperManager.tsx
export default function PaperManager() {
  const [papers, setPapers] = useState([]);
  const [newPaper, setNewPaper] = useState({
    title: '',
    authors: '',
    year: '',
    abstract: '',
    keywords: ''
  });

  const addPaper = () => {
    setPapers([...papers, { ...newPaper, id: Date.now() }]);
    setNewPaper({ title: '', authors: '', year: '', abstract: '', keywords: '' });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">文献管理</h2>
        
        {/* 添加文献表单 */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <input
            type="text"
            placeholder="论文标题"
            value={newPaper.title}
            onChange={(e) => setNewPaper({...newPaper, title: e.target.value})}
            className="p-2 border rounded"
          />
          <input
            type="text"
            placeholder="作者"
            value={newPaper.authors}
            onChange={(e) => setNewPaper({...newPaper, authors: e.target.value})}
            className="p-2 border rounded"
          />
          <input
            type="number"
            placeholder="年份"
            value={newPaper.year}
            onChange={(e) => setNewPaper({...newPaper, year: e.target.value})}
            className="p-2 border rounded"
          />
          <input
            type="text"
            placeholder="关键词"
            value={newPaper.keywords}
            onChange={(e) => setNewPaper({...newPaper, keywords: e.target.value})}
            className="p-2 border rounded"
          />
          <textarea
            placeholder="摘要"
            value={newPaper.abstract}
            onChange={(e) => setNewPaper({...newPaper, abstract: e.target.value})}
            className="p-2 border rounded col-span-2"
            rows={3}
          />
          <button
            onClick={addPaper}
            className="col-span-2 bg-green-600 text-white py-2 rounded hover:bg-green-700"
          >
            添加文献
          </button>
        </div>

        {/* 文献列表 */}
        <div className="space-y-4">
          {papers.map((paper) => (
            <div key={paper.id} className="border rounded p-4">
              <h3 className="font-semibold">{paper.title}</h3>
              <p className="text-gray-600">{paper.authors} ({paper.year})</p>
              <p className="text-sm mt-2">{paper.abstract}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Day 18-21: 用户体验优化
- 添加加载状态和错误处理
- 优化响应式设计
- 添加用户反馈功能
- 实现数据持久化

## 第4周：测试发布

### Day 22-24: 功能测试
```typescript
// 测试用例
describe('Review Generator', () => {
  test('should generate review for valid input', async () => {
    const response = await fetch('/api/generate-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: '机器学习',
        papers: [
          {
            title: '深度学习综述',
            authors: '张三',
            year: 2023,
            abstract: '本文综述了深度学习的发展...'
          }
        ]
      })
    });

    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.review).toBeDefined();
  });
});
```

### Day 25-26: 性能优化
- 添加缓存机制
- 优化API响应时间
- 实现分页加载
- 添加错误边界

### Day 27-28: 部署上线
```bash
# 部署到Vercel
npm run build
vercel --prod

# 配置环境变量
OPENAI_API_KEY=your_api_key
NEXTAUTH_SECRET=your_secret
```

## 成本控制策略

### 开发阶段成本
- **开发工具**: 0元（全部免费）
- **服务器**: 0元（Vercel免费）
- **数据库**: 0元（SQLite本地）
- **设计工具**: 0元（Figma免费版）

### 运营阶段成本
- **AI API**: 100-500元/月（根据用户量）
- **域名**: 50元/年
- **总成本**: 100-500元/月

### 成本控制措施
1. **API调用限制**: 设置用户每日使用次数限制
2. **缓存机制**: 缓存相同请求的结果
3. **批量处理**: 优化API调用频率
4. **用户分层**: 免费版限制功能，付费版无限制

## 快速验证方法

### 第1周验证
- 制作简单的演示页面
- 在学术群分享测试链接
- 收集用户反馈和需求

### 第2周验证
- 邀请10-20个种子用户测试
- 收集使用数据和反馈
- 快速迭代优化

### 第3周验证
- 扩大测试用户范围
- 验证付费意愿
- 优化产品功能

### 第4周验证
- 正式发布MVP
- 开始用户获取
- 收集市场反馈

## 成功指标

### 技术指标
- 页面加载时间 < 3秒
- API响应时间 < 10秒
- 系统可用性 > 99%

### 用户指标
- 用户注册转化率 > 10%
- 功能使用率 > 60%
- 用户满意度 > 80%

### 业务指标
- 月活跃用户 > 100
- 付费转化率 > 5%
- 月收入 > 1000元

## 结论

**个人开发者完全可行**，关键成功因素：

1. **专注核心功能** - 文献综述生成
2. **简化技术实现** - 避免PDF解析
3. **快速迭代** - 4周完成MVP
4. **成本控制** - 月成本100-500元
5. **用户验证** - 持续收集反馈

**建议立即开始**，4周内完成MVP上线测试。