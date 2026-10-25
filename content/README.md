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
2. 填好 front matter、正文和至少一个可访问的来源。`section` 是主章节；可选的 `companies` 写 `content/companies.json` 里的 slug。不写的话，构建器会从公司章节名和 tags 里的公司别名推断。新内容使用普通 Markdown；公式写法见下方「公式」一节。
3. 执行 `npm run content:check`。它会校验题目 ID、模块、日期、来源、重复项和 KaTeX 公式；非法公式会直接报错，但不会写生成文件。
4. 审核通过后，将文件移动到 `questions/<section>/`，把 `status` 改为 `published`，再执行 `npm run content:build`。

`quick` 是卡片上始终可见的 30 秒回答；Markdown 正文是展开后显示的完整答案。每题的 ID 一经发布就不要改动，因为深链和复习进度都以它为键。

## 答案怎么写才容易理解

把读者当成正在学这道题的人。先直接回答，再解释为什么，最后用例子或执行步骤把方法讲清楚。`quick` 也要能独立读懂，不能只是把正文里的关键词串起来。

- 使用完整句子，写清谁做什么、为什么这么做、结果是什么。不要让读者自己补上因果关系。
- 必要的英文术语和缩写可以保留，但第一次出现时说明中文含义。“采样”“裁剪”“幂等”这类中文术语，也需要结合当前问题解释。
- 公式前说明要算什么，公式后解释变量和结果。代码前说明思路，代码后解释关键边界。
- 直接写具体机制，避免“钉死”“接地”“硬门”“主茎”等没有解释的行话。说明常见错误时，也要讲清错误原因。
- 长段落按思路拆开。追问给出完整回答，不能只写“看某题”或一个算法名。
- 改写时保留技术条件、公式、代码、来源和题间链接。公司内部实现与面经没有披露的细节，不要补成事实。

例如，“写要幂等，否则不重试”可以写成：“写操作超时后，先确认重复执行会不会重复扣款或创建两张订单。只有系统能识别同一请求、保证重复执行不会产生额外副作用时，才允许自动重试。”

## 编程题的简单测试

编程题正文必须从 `## 题目描述` 开始，先把任务写完整，再进入题解。题面包含任务目标、每个输入的含义与形状、接口、输出或原地修改效果、合法输入约束及至少一个具体输入输出示例。不要把算法思路、函数签名、测试代码或“见下文”当成题面。LeetCode 用中文重述题意并保留原题链接；面经没有披露的细节必须标为手册练习约定。

题面后用 `## 解题思路与参考答案` 与解答分开。练习页只读取这一段前置题面，构建器会拒绝缺失题面的编程题；概念题中仅用来说明机制的代码片段不自动变成编程练习。新编程题可以复制 `content/templates/coding-question.md`。

每道带参考实现的 coding 题都要有“简单测试怎么写”部分，说明输入怎么准备、怎么调用本题接口、预期结果怎么得到，以及如何在本地运行。至少选一个能手算的正常例子，再补合法边界或容易写错的分支。不要只写“测试空数组和重复值”，要给实际输入与断言。

- LeetCode 用本题函数名写小例子；链表和树先构造节点，需要时用辅助函数转换输出。返回节点身份、复制结构和环的题，还要检查对象关系。
- 原地修改题检查调用后的数组或有效前缀，每次重新准备输入。有状态接口按“新建对象、执行操作、检查状态”组织。
- 浮点计算用带容差的比较，同时检查形状；随机测试固定种子。预期值来自手算或独立参考公式。
- 标准输入输出题可以用 `StringIO` 与输出捕获，结束时恢复输入。说明测试代码放在哪里，避免读输入的入口提前执行。
- 已有“完整编程练习”的题目，在“可执行测试”之前加三级标题“简单测试怎么写”，说明如何从第一个小场景开始，保留现有实现与测试的两个代码块，供页面复制和校验脚本使用。

`python3 scripts/check-simple-tests.py` 检查覆盖与示例语法；`python3 scripts/check-simple-tests.py --execute` 实际执行展示的小例子。数值例子需要 NumPy 与 PyTorch。该命令保留已有完整测试套件各自的检查脚本；新增测试不要使用 `python3 -O`，因为它会跳过 `assert`。

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
