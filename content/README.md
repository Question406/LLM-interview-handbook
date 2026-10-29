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

题面来源用简短的肯定句说明，例如“来源：本手册原创练习”“参考某课程改编”“来源：一亩三分地候选人报告的二手摘要”。保留来源链接、改编范围与 `realInterview` 标记；题面不再反复添加“不是原题”“不代表公司确认”等否定式说明。算法限制、输入约束和测试范围照常写清。

## 代码块 Formatting

代码块在 `content:build` / `content:check` 中先格式化、再做 syntax highlighting；`npm run dev` 和 `npm run build` 已通过 `content:build` 使用同一流程。支持 Markdown fences 和历史 `legacy-html` 的 `<pre><code>`。构建只写生成内容，不改题目源文件。

- Python 使用固定版本的 Ruff WASM：4 spaces、88 columns、保留引号风格，不做 lint fixes、import sorting 或执行代码。不需要安装额外 Python formatter。
- JS/TS、JSON、YAML、HTML/CSS、GraphQL、Markdown 使用 Prettier；Shell 使用 Prettier Shell plugin。依赖版本在 package lock 中固定。
- `text` / `plaintext`、输出示例、ASCII 图和不支持的语言保留原布局。无标签、具有明显 Python declarations/imports 的片段按 Python 处理；新代码请显式写语言。
- 标为可执行语言的语法错误会阻止构建，并给出题目 ID 与语言。故意错误的 syntax 示例、伪代码和非程序输出请标为 `text`。
- 只格式化 block contents，inline code、正文、公式、题目 ID 与代码字符串里的 HTML 不参与重写。

需要整理源文件时执行：

```bash
npm run content:format
npm run content:format:check
```

第一条写回题库源文件，第二条用于检查或 CI，存在未格式化代码时返回非零 exit status。`drafts/` 不在源文件批处理范围；真正渲染的代码仍会在 build 时格式化。

## 答案怎么写才容易理解

把读者当成正在学这道题的人。先直接回答，再解释为什么，最后用例子或执行步骤把方法讲清楚。`quick` 也要能独立读懂，不能只是把正文里的关键词串起来。

- 使用完整句子，写清谁做什么、为什么这么做、结果是什么。不要让读者自己补上因果关系。
- 专业术语直接使用英文，中文用于解释作用、选择与具体例子。例如统一使用 negative log likelihood、cross entropy、importance sampling、policy gradient 和 calibration。相同英文全称不在括号里重复；有帮助的缩写可以保留。inference/reasoning、normalization/standardization 等按实际含义区分。
- 公式前说明要算什么，公式后解释变量和结果。代码前说明思路，代码后解释关键边界。
- 直接写具体机制，避免“钉死”“接地”“硬门”“主茎”等没有解释的行话。说明常见错误时，也要讲清错误原因。
- 长段落按思路拆开。追问给出完整回答，不能只写“看某题”或一个算法名。
- 改写时保留技术条件、公式、代码、来源和题间链接。公司内部实现与面经没有披露的细节，不要补成事实。

例如，“写要幂等，否则不重试”可以写成：“写操作超时后，先确认重复执行会不会重复扣款或创建两张订单。只有系统能识别同一请求、保证重复执行不会产生额外副作用时，才允许自动重试。”

## 面试口述题的表达

非编程的面试口述题，主回答先直接回应问题，再围绕一个具体例子解释选择、理由和怎样验证。第一轮不要同时罗列所有字段、过滤器、指标与训练方法。完整公式、样本schema和实验清单可以放在技术备查中，追问时再展开。主回答要能读出声，避免把设计文档的小标题改成一串术语来代替解释。

项目题只写真实职责和结果，设计方案用“我会”；没有测量就不补收益数字。参考公开培训示范的表达方式时，保存出处，保留原始技术来源，不把示范里的履历改写成用户经历。当前示例见 `sources/afm-answer-style-2026-10-27/README.md`。

非编程口述题可用二级标题 `## 技术备查` 标记补充内容。构建器将该标题之后的内容默认折叠，之前的口述回答保持可见；Markdown源文件仍不允许原始HTML。代码块中的同名标题不会触发折叠。

## 编程题的简单测试

编程题正文必须从 `## 题目描述` 开始，先把任务写完整，再进入题解。题面包含任务目标、每个输入的含义与形状、接口、输出或原地修改效果、合法输入约束及至少一个具体输入输出示例。不要把算法思路、函数签名、测试代码或“见下文”当成题面。LeetCode 用中文重述题意并保留原题链接；面经没有披露的细节必须标为手册练习约定。

题面需要独立回答六个问题：给定的现实对象是什么、每个输入字段代表什么、要实现哪个接口、返回哪些字段、哪些规则必须一致、具体例子的预期结果是什么。只列 `[N,D]` 不足以解释样本与特征；q、weight、reward、log probability 等输入必须区分含义。复杂训练题还要明确初始化、preprocessing 拟合范围、optimizer、update 次数、loss / reduction 和 evaluation protocol，不能只要求“标准 loss”或“输出指标”。

使用 `### 接口与输入`、`### 输出与规则`、`### 输入输出示例` 等小节。示例要给实际输入和可核对的结果；返回复杂字典时至少有一个完整示例或逐字段的验证约定。随机结果给分布或不变量，不伪造唯一输出。多接口题要明确默认交付与扩展阅读，测试不能要求题面未定义的接口。题面、starter、参考实现与默认测试需要交叉检查。构建检查会拒绝缺少独立示例小节、只写“运行参考答案”的题面；含义是否清楚仍需要编辑复核。

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

## 引用已有题目的汇编手册

汇编手册可在 `_handbook.md` 声明 `questionRefs: question-refs.json`，清单元素为 `{ "book": "源手册目录", "question": "源题ID", "section": "本册章节", "order": 1 }`。源题必须在对应手册 `questions/` 中已发布；不允许自引用或重复题号，也不会递归读取源手册的引用清单。新题仍放本册 `questions/`，清单只负责引用和分类，不复制答案。

构建后完整答案在汇编手册内展示，附原手册链接；已收录题之间在本册跳转，未收录的相关题回到源手册。编程运行器通过固定的 `question-refs.json` 读取原实现与测试。原手册链接、进度与草稿保持独立，汇编手册使用自己的进度与草稿。

Apple 汇编入口为 `content/handbooks/apple-interview/`。执行 `npm run apple:sync` 更新收录清单和全部题目的 README 摘要，再执行 `npm run content:build`。收录规则包含整本 Data Team、全部 Apple 公司标签题及明确列出的 tensor 迁移题。

## 命令

```sh
npm run content:check  # 只校验所有 Markdown 源
npm run content:build  # 生成索引与按模块答案包
npm run dev            # 先生成内容，再启动本地站点
npm test               # 生成、构建前端并跑内容回归测试
```

已迁移的历史内容标注为 `format: legacy-html` 和 `provenance: legacy-handbook-v2`，用以保留旧公式 SVG 与原有排版。新增题目不能使用 raw HTML，以避免不安全内容进入页面。

## 系统设计题与隐藏参考讨论

System Design 手册位于 `content/handbooks/system-design/`。设计题保留独立的 `## 题目描述`，其后再写参考讨论；`collapseAnswer: true` 让题面保持可见，参考答案默认折叠，并隐藏题卡上的30秒答案摘要。该选项只用于有前置题面的Markdown题卡，不会增加编程运行入口。

公司来源分为候选人原帖核对记录、站内二手题卡与通用练习。原帖未披露的规模、接口和架构必须标成手册约定；只有主题摘要时不声称拥有完整原题。新来源要保留URL、先前/本轮采集日期与实际可见范围，不根据题型汇总数量推断出现频率。

## 全题回答思路

手册可在 `_handbook.md` 声明 `answerGuides: answer-guides`。目录内每题一个 `<id>.md`，front matter 为 `id`、`kind`（coding/design/concept/project/guide）、`situation`、`task`、`approach`、`result`，正文是口述答案。构建器要求本手册每道题都有且仅有匹配稿，未知题号与缺字段会报错。

完整回答顶部先渲染“回答思路”callout，再显示口述稿。非编程题的原始细节折叠保留；编程题原始题面、实现和测试继续显示，练习runner仍读取原题源码。引用其他手册的题使用本册的回答稿，不修改源题及其他题本的展示。

Apple全题稿在 `handbooks/apple-interview/answer-guides/`，逐题内容以这里为准。新增题时也需要新增回答稿；执行内容构建后，可用 `node scripts/export-apple-answer-guides.mjs` 导出 `AFM-ANSWER-GUIDES.md` 阅读稿。设计题写验收条件，项目故事写真实证据，不能从示例填造个人经历或成绩。

## Apple 题本的英文术语

专业名词直接使用英文，中文用于解释含义、判断和原因，约定见 `handbooks/apple-interview/TERMINOLOGY.md`。例如使用 reward model、verifier、data mix、evaluation slices、ablation study、negative transfer。避免“门禁”“锚点”“托底”“主门”等不清楚的隐喻；按语境写 release gate、held-out evaluation set、regression tasks 或明确的中文动作。inference/reasoning、validation/verification 不机械合并。代码、公式、接口及测试字面值保持准确，不为了术语统一而修改。

该表达偏好适用于所有题本的 question cards。质量检查使用 data quality checks，发布条件使用 release criteria；编程特殊情况使用 edge cases，文档分隔使用 document boundaries，访问权限使用 authorization rules，方法适用条件使用 applicability / limitations。先确认实际含义，再调整整句，不将所有“边界”统一翻成 boundary，也不将所有检查称为 gate。fallback 仅指失败后的替代路径，不能替代必须执行的 validation 或 authorization checks。

## DrustZ Interview Book

DrustZ 的完整资料整理在 `handbooks/drustz-interview-2026/`，与原有题本并列。源版本、文件覆盖清单、许可证及可重复执行的导入步骤见 `sources/drustz-interview-2026/README.md`；code / tests / data 的下载入口在该书阅读指南中。上游新增内容需显式更新 pinned revision 后重新导入，不在普通 build 时联网拉取。
