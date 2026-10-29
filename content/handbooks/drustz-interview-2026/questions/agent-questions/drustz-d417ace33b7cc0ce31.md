---
id: drustz-d417ace33b7cc0ce31
section: agent-questions
order: 8
level: A
title: C 类 · Live Coding / AI-assisted Coding 实操题 · Sierra（7/15）
quick: 作者文档章节 · C 类 · Live Coding / AI-assisted Coding 实操题 · Sierra（7/15）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Interview Questions & Solutions
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md
    type: primary
---
## Sierra（7/15）

### [C9] ⭐⭐⭐ Sierra onsite debugging round：TS/React buggy 代码库找 bug（禁 AI）
- 来源: Exponent 经历+guide + gaijineer + 1p3a 2026-05 面经 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · onsite 60min（多人称 "the real gate"）· 2025–2026-05 在考
- 考察点: 读代码 > 写代码；hypothesis-driven 排障；TS/React 硬性熟练度；无 AI 原生 debug




**题面 + 参考打法 + 高频追问**



**题面两变体**：(1) TypeScript+React 应用（如客服 bot 聊天界面），4–6 个 bug，明确 no AI tools/resources；(2) 约 4–5 文件的 agent 实现小代码库 + 参考架构图，约 3 个 bug，修完讨论优化。

**警告**（多位候选人）："Do not believe the language-agnostic framing"——只写 Python 的候选人 onsite 第一轮就是 TS/React debugging 直接挂。评估：代码理解、复现→定位→假设→验证、修复不破坏其他功能、UX 影响的产品意识（只让测试通过不够）。

**备考 checklist**：
- React hooks 坑：stale closure、useEffect 依赖数组、setState 异步/批处理、列表 key
- TS：类型窄化、可选链、async/await 与 promise 错误处理（未 await、吞异常）
- API 调用层：竞态（旧请求覆盖新结果）、loading/error 状态、abort

**高频追问**：这个修复会不会影响别的功能？ ｜ 还有时间的话你会优化什么？





→ **完整解答：[solutions/C9_debugging_round.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-84edd1277eae5e2399)**

### [C10] ⭐⭐⭐ Sierra 电面：Markdown 按 header 层级分块（size limit + 父 header 重复）
- 来源: PracHub 完整题面 + 1p3a 2026-05-15 同题面经互证 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · 电面 60min CoderPad（Python/TS）· 2026-04~05
- 考察点: 实用文本处理 + 状态机 + multi-part 递进下的可扩展代码；与 RAG chunking 直接相关




**题面 + 参考打法 + 高频追问**



**题面**：`split_markdown(markdown: str, max_size: int) -> list[str]`：切成有序 chunks，每个 ≤ max_size。Header = 1–6 个 `#` + 空格开头；非 header 行属当前层级。**关键规则**：chunk 在 section 中间开始时，须在首个内容行前重复所有 active 父 headers（重复的 header 计入 size limit）；遇 level-L header 清空 level L–6 的 active headers。约束：len ≤ 200,000；保证任意单行+所需父 header 能放进 max_size；保持原顺序，说明空行/换行假设。例：`("", 10) -> []`；`("# Title\nHello\n## Section\nWorld", 100)` → 整篇一个 chunk。

**参考打法**：
- 按 level 维护 active header 栈 + 贪心逐行追加；拼接长度要含换行分隔符——先写 `chunk_len(lines)` helper 避免 off-by-one
- Sierra 电面是 multi-part 递进（每个 follow-up 在已有代码上叠需求）——**结构干净可扩展 > 一次写完**：把"开新 chunk 时注入父 headers"抽成函数
- 先跑空文档/单行超长/连续 header 三个边界

**高频追问**：start 相同的排序？ ｜ code block 里的 `#` 要不要当 header（澄清假设）？





→ **完整解答：[solutions/C10_markdown_chunking.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-ae067731a574d11a60)**

### [C11] ⭐⭐⭐ Sierra OA：Debug 日志时间区间合并 + overlap/gap 检测
- 来源: PracHub 完整题面 + 1p3a 2025-11-25 "Debug View Problem" 互证 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · OA/take-home 附属题 · 2025-11
- 考察点: 区间基本功 + 半开区间边界 + agent debug 日志视图的建模




**题面 + 参考打法 + 高频追问**



**题面**：n 个 debug 日志段 `(start, end, text)`，半开区间 `[start, end)`，n ≤ 200,000。**Task 1**：合并重叠区间为 `[min_start, max_end)`，text 按时间顺序空格拼接，按 start 升序返回。例：`[(0,5,"A"),(3,10,"B"),(12,15,"C")] -> [(0,10,"A B"),(12,15,"C")]`。**Task 2**：返回两个 bool——是否存在任意一对区间相交（交集非空）；最早 start 与最晚 end 之间是否存在 gap。同例输出 `(True, True)`。

**边界**：相邻区间 `[1,4)` 和 `[4,6)` **既不算 overlap 也不算 gap**——半开区间语义要开场说清。打法：排序 O(n log n) + 单遍扫描；Task 2 的 overlap 用"排序后相邻对 `prev_end > cur_start`"判定。

**高频追问**：start 相同时 text 拼接定序？ ｜ gap 定义是否含首尾之外？





→ **完整解答：[solutions/C11_log_intervals.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-ea71b8b4d979233d94)**

### [C12] ⭐⭐⭐ Sierra 官方 AI-native onsite：Plan→Build→Review（2h 自选 AI 工具从想法到 demo）
- 来源: Sierra 官方博客 the-ai-native-interview ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: Sierra · onsite 三段 · 2025–2026 现行
- 考察点: 官方明说：agency（卡住会不会 pivot）、judgment（scope 裁剪）、product sense、系统理解、数据模型与 extensibility、如何用 AI 本身




**题面 + 参考打法 + 高频追问**



**形式**：(1) Plan——与面试官共同构思产品；(2) Build——2 小时，"the AI tooling and frameworks of their choice"，官方明确可裁 scope、可跳过 boilerplate（CRUD/auth）聚焦独特部分；(3) Review——现场 demo、产品决策讨论、code review、**解释自己怎么用的 AI**。官方案例：候选人做了让用户保持心流的 AI 游戏，demo 即面试官试玩。

**参考打法**：
- 预先练熟自己的 AI 编码环境（Claude Code/Cursor），彩排 2h 从零到 demo 的节奏（30min 骨架 / 60min 核心 slice / 30min 打磨 demo 路径）
- 准备一个能秀 agent 专长的产品 idea 库（客服 agent、trace viewer、eval 面板）
- Review 时说清"哪些是 AI 写的、我怎么验证的"——对 AI 输出的批判性验证是他们看的信号
- 注意：社区面经报告的仍是 take-home+debugging 旧流程，两种可能并存，**向 recruiter 确认场次格式**

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-sierra-plan-build-review`





→ **完整解答：[solutions/C12_plan_build_review.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-b79f6b2a35b4cc0c0f)**

### [C13] ⭐⭐⭐ Sierra 官方试点：接手中型代码库 + 同事 draft PR，用 coding agents 改进
- 来源: Sierra 官方博客（piloting） ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: Sierra · onsite debugging 新形态 · 2026
- 考察点: code review 判断力 + 与 coding agent 协作迭代




**题面 + 参考打法 + 高频追问**



**题面**：medium-sized codebase + 一位"同事"的 draft PR（引入 cross-cutting feature），任务："review and improve it——pulling down the code, inspecting the output, and iterating with coding agents"。与禁 AI 的 TS/React debugging 轮形成对照——Sierra 正从裸写 debug 转向带 agent debug。

**参考打法**：
- 工作流：让 agent 生成 codebase map → 定位 PR 触点 → 跑测试建基线 → 逐项 review（正确性 > 设计 > 风格）→ 用 agent 做窄修改 → 保留验证证据链
- cross-cutting 变更的典型风险清单：一致性（各层语义对齐）、遗漏调用点、回填/migration、测试覆盖、权限绕过
- 核心信号：给 agent 的指令质量、对产出的甄别、review 意见是否切中要害
- v1 自拟练习场景（ticket priority 功能跨 API/DB/queue/UI）可直接拿来彩排

**高频追问**：AI 建议重写整个模块时你怎么判断？ ｜ 哪些问题你选择不修、为什么？

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-sierra-cross-cutting-pr`





→ **完整解答：[solutions/C13_draft_pr_round.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-4a07cf1ba370057d96)**

### [C14] ⭐⭐⭐ Sierra 电面递进风格样本：Excel 循环引用检测 / keyboard undo-redo
- 来源: Exponent 面经 2025-05（同期同题问所有人）+ norahq guide 汇编 ｜ 置信度: ✅（circular ref）/ ⚠️（keyboard） ｜ 公司/轮次: Sierra · 电面 60min · 2025（可能已轮换，作风格样本）
- 考察点: 从产品描述抽象图/OO 模型；每个 follow-up 在现有代码上叠需求




**题面 + 参考打法 + 高频追问**



**题 1**："Excel 式电子表格，单元格可引用其他单元格，如何检测循环引用？"——cell 为节点、引用为有向边，DFS 三色标记或 Kahn 拓扑。递进：返回具体环路径 → 增量更新只查受影响子图 → 从 `"=A1+B2"` 解析依赖 → 大规模性能。面经注："同一道电面题问所有人"（2025 上半年，或已轮换）。

**题 2**："Implement a keyboard object with expansion to support undo/redo."——按键输入 + 文本缓冲起手，递进加 undo/redo（两个操作栈或 command 模式记录逆操作）、光标移动、选区、组合操作原子化。

**打法**：这两题是 Sierra 电面风格样本——不背算法，练"flexible, extensible code + 递进叠需求"；每写一段先说扩展点。





> 高分句：Sierra 评的是接手陌生代码的判断力——先跑测试建基线，再按正确性>设计>风格逐项 review，每个修复都留验证证据。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/C_live_ai_coding.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md)。作者整理资料；许可和第三方来源范围见阅读指南。
