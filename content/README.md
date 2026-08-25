# Content system

题库的唯一人工维护源是 `content/handbooks/<handbook>/` 下的 Markdown。前端使用的目录、搜索文本、统计数字、卡片公式和按题懒加载的答案，全部由构建器生成；不要手改 `content/generated/` 或 `public/content/`。

```text
content/
  handbooks/
    llm-interview/
      _handbook.md                 # 手册元数据与模块清单
      questions/<section>/<id>.md  # 已发布：一题一个文件
      drafts/<agent-id>/<id>.md    # 多 agent 各自的草稿区
  templates/question.md            # 新题模板
public/content/
  catalog.json                     # 手册列表（开机只拉这一份）
  <handbook-id>/
    index.json                     # 本题库目录：纯文本 title / quick / searchText
    <section>.cards.json           # 进章后才拉的 titleHtml / quickHtml
    <section>.json                 # 整章答案（全部展开时用）
    <section>/<id>.json            # 单题答案（点开一张卡才拉）
```

## 新增题目

1. 复制 `content/templates/question.md` 到自己的 `drafts/<agent-id>/` 子目录。
2. 填好 front matter、正文和至少一个可访问的来源。新内容使用普通 Markdown；公式写法见下方「公式」一节。
3. 执行 `npm run content:check`。它会校验题目 ID、模块、日期、来源、重复项和 KaTeX 公式；非法公式会直接报错，但不会写生成文件。
4. 审核通过后，将文件移动到 `questions/<section>/`，把 `status` 改为 `published`，再执行 `npm run content:build`。

`quick` 是卡片上始终可见的 30 秒回答；Markdown 正文是展开后显示的完整答案。每题的 ID 一经发布就不要改动，因为深链和复习进度都以它为键。

## 题间跳转

答案里提到本手册其他题时，构建器会自动变成可点击链接，不必手写 HTML：

- 清单或正文里出现**另一题的完整标题**（导航卡最常见）
- 反引号题号，例如 `` `pt-opsd` ``、`` `fund-kl-directions` ``
- 显式写法：`[[fund-kl-directions]]`、`[[fund-kl-directions|自定义文案]]`，或 `[自定义文案](question:fund-kl-directions)`

未知的 `[[id]]` 会让 `content:check` 失败。代码块里的标题和题号保持原样，不会误链。

## 公式

`title`、`quick` 和正文都走同一条公式管线，任何该是公式的地方都写 `$...$`（行内）或 `$$...$$`（块级），构建时由 KaTeX 渲染。`format: legacy-html` 的正文同样支持，替换会自动跳过 `<pre>`、`<code>`、HTML 标签内部和已迁移的预渲染 SVG。

- **不要用 Unicode 拼凑公式**（`δₜ`、`y₁⁻`、`Vπ(s)`、`X∈ℝ^(T×d)`）。它们在页面上是一串错位的怪符号，应写成 `$\delta_t$`、`$y_1^-$`、`$V^\pi(s)$`、`$X\in\mathbb{R}^{T\times d}$`。
- **代码标识符不是公式**：`send_email`、`batch_size`、`max_position_embeddings`、`d_model` 这类程序变量或配置项保持原样，放进反引号或 `<code>` 里。
- `title` 和 `quick` 是纯文本 + `$...$`，不能含 HTML 标签；`quick` 在 legacy 正文的 `<div class="quick">` 里通常还有一份副本，两处要一起改。
- **legacy 正文里的 TeX 不能含裸 `<` 或 `>`**，会破坏 HTML。写 `\lt`、`\gt`，或写 `&lt;`、`&gt;`（管线会在送进 KaTeX 前解码实体）。
- KaTeX 用 `throwOnError: true`，非法 LaTeX 会让构建直接失败。回归测试还会检查渲染产物里没有残留的未渲染记法（未消费的 `$`、`_{`、`^π`、Unicode 上下标）。

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
