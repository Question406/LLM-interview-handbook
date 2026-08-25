# Interview Atlas

一个内容驱动的面试资料库。当前 LLM handbook 的 231 道题、14 个模块都以“一题一个 Markdown 文件”的方式维护。

## 已有功能

- 全文搜索与 S / A 级、真实面经、掌握状态筛选
- 随机抽题、全部展开 / 折叠、题目深链接
- 复习进度与深色主题保存在当前浏览器
- 桌面、平板和手机自适应
- 大章答案按模块懒加载，资料库扩展后不会持续拖慢首屏
- 开机只拉手册目录；点进一章再拉卡片公式，点开一题再拉该题答案

## 内容架构

```text
content/
├── handbooks/<slug>/  # _handbook.md、questions/ 与 drafts/
├── templates/         # 新题模板
├── generated/         # 构建产物（不提交）
└── registry.ts        # 读取自动生成的资料库
public/content/        # catalog / 分手册 index / 章卡片 / 单题答案（构建产物，不提交）
components/            # 通用的学习工作台 UI
scripts/               # 内容校验、编译与静态资源准备
```

新增题目时，只需复制 `content/templates/question.md`，写入自己的 `drafts/<agent-id>/`，通过审核后移至 `questions/<section>/`。索引、统计、搜索文本和懒加载答案包会自动生成，不需要登记或改前端。详细规则见 `content/README.md`。

## 本地使用

```bash
npm install
npm run dev
```

验证成品：

```bash
npm test
```
