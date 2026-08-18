# Content system

题库的唯一人工维护源是 `content/handbooks/<handbook>/` 下的 Markdown。前端使用的索引、搜索文本、统计数字和按模块懒加载的答案包，全部由构建器生成；不要手改 `content/generated/` 或 `public/content/`。

```text
content/
  handbooks/
    llm-interview/
      _handbook.md                 # 手册元数据与模块清单
      questions/<section>/<id>.md  # 已发布：一题一个文件
      drafts/<agent-id>/<id>.md    # 多 agent 各自的草稿区
  templates/question.md            # 新题模板
```

## 新增题目

1. 复制 `content/templates/question.md` 到自己的 `drafts/<agent-id>/` 子目录。
2. 填好 front matter、正文和至少一个可访问的来源。新内容使用普通 Markdown；行内公式使用 `$...$` 或 `\(...\)`，块公式使用 `$$...$$` 或 `\[...\]`。反引号和代码块中的公式定界符会保留为普通代码。
3. 执行 `npm run content:check`。它会校验题目 ID、模块、日期、来源、重复项和 KaTeX 公式；非法公式会直接报错，但不会写生成文件。
4. 审核通过后，将文件移动到 `questions/<section>/`，把 `status` 改为 `published`，再执行 `npm run content:build`。

`quick` 是卡片上始终可见的 30 秒回答；Markdown 正文是展开后显示的完整答案。每题的 ID 一经发布就不要改动，因为深链和复习进度都以它为键。

## 多个 LLM / sub-agent 并行出题

- 每个 agent 只创建或修改 `drafts/<自己的唯一名称>/` 下的文件；不要修改 `_handbook.md`、已发布题目或任何生成文件。
- 使用全局唯一、稳定的 kebab-case `id`，例如 `grpo-clip-range`。提交前运行 `npm run content:check`，CI 会阻止重复 ID 和无效来源。
- 一个 reviewer 负责把草稿移入 `questions/`、排序（可选 `order`）和发布。这样作者之间不会写同一个文件，也不需要维护集中式 JSON 数组。
- 新增一个全新的 handbook 时，创建 `content/handbooks/<slug>/_handbook.md` 和至少一个 `questions/<section>/` 文件即可。构建器会自动发现它，并写入资料库切换器。

## 命令

```sh
npm run content:check  # 只校验所有 Markdown 源
npm run content:build  # 生成索引与按模块答案包
npm run dev            # 先生成内容，再启动本地站点
npm test               # 生成、构建前端并跑内容回归测试
```

已迁移的历史内容标注为 `format: legacy-html` 和 `provenance: legacy-handbook-v2`，用以保留旧公式 SVG 与原有排版。新增题目不能使用 raw HTML，以避免不安全内容进入页面。
