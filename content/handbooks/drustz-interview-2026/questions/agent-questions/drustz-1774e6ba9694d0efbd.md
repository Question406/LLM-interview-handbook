---
id: drustz-1774e6ba9694d0efbd
section: agent-questions
order: 9
level: A
title: C 类 · Live Coding / AI-assisted Coding 实操题 · 通用格式 + OpenAI/Meta（迁移备用）
quick: 作者文档章节 · C 类 · Live Coding / AI-assisted Coding 实操题 · 通用格式 + OpenAI/Meta（迁移备用）
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
## 通用格式 + OpenAI/Meta（迁移备用）

### [C15] ⭐⭐⭐ 通用 AI-allowed live coding：1000–2000 行陌生 codebase 加 feature/修漏洞/重构
- 来源: interviewing.io + Codility/CoderPad VP 访谈 + techinterview.org（CoderPad 称已 35,000+ 场） ｜ 置信度: ✅ ｜ 公司/轮次: generic（本周多家可能采用此格式，故 ⭐⭐⭐）· 60–90min 屏幕共享 · 2025–2026
- 考察点: 分解先于 prompt、prompt 迭代效率、验证习惯、全程 narration




**题面 + 参考打法 + 高频追问**



**形式**：自选 AI 工具（Cursor/Copilot/Claude Code），在 1000–2000 行陌生 codebase 限时完成真实任务。三类典型：implementing a new feature / addressing security vulnerabilities / refactoring a service for maintainability。

**评估标准**："Can you decompose the problem clearly before reaching for AI? Do you know what you want before you prompt?" + prompt 迭代效率 + 验证习惯 + 识别 AI 错误输出。**最致命失败**：pasting and shipping without checking、长时间沉默、把 AI 当不会错的 oracle。动手前先复述问题、问澄清、口头勾勒方案——"这一步没做好，代码还没写面试已经输了"。

**新形态参考**：Tutor Intelligence 公开 challenge（"Claude can 1-shot our interviews"）：60x40 仓库 5 机器人完成 1000 订单最小化 timestep，明确 "AI agent use is encouraged (probably necessary)"——考"人的创造力增量 vs 模型顺手的下一步"。开放优化题 + 全力用 AI 是 2026 agent-native 招聘新形态。

现场脚本与 narration 模板：[../02_playbook.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d48438e1a63e68f6a5)。





### [C16] ⭐⭐ OpenAI onsite 试点 agentic coding round（beta）：现有 codebase + 期望用 AI agents
- 来源: interviewing.io OpenAI 流程页（2026 更新，单源） ｜ 置信度: ⚠️ ｜ 公司/轮次: OpenAI · onsite beta 轮 · 2026-06
- 考察点: 在陌生 codebase 用 AI agent 解决"复杂到无法从零手写"的问题




**题面 + 参考打法 + 高频追问**



**形式**：候选人拿到现有 codebase，解决"复杂到无法从零手写"的问题，期望使用 AI coding agents；并非所有候选人遇到。**关键对照**：除此轮外全程严格禁 AI。其余流程：recruiter 30min → 电面 1h CoderPad → SD screen 1h Excalidraw → onsite 4–6h。SD 轮警告："点名任何具体技术就要准备好深入讲它"。

**参考打法**：用 Claude Code 在陌生 repo 做中型 feature 彩排（定位→改→测试）；v1 练习题面（per-tenant concurrency limit，draft 已改 scheduler 但缺 retry/metrics/migration）可直接用。

**相邻数据点**：OpenAI Support Engineer 有正式 "vibe coding" 轮——debug 间歇性失败的 Python 脚本（根因 race condition）、写自动化；同帖强调 HM 轮 bar 极高，建议深学 OpenAI API 产品细节。

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-openai-coding-harness`





### [C17] ⭐⭐ Meta AI-enabled coding round：多文件 codebase + 内置 AI 助手
- 来源: interviewing.io 官方博客 + designgurus ｜ 置信度: ✅ ｜ 公司/轮次: Meta · onsite（替换两轮 coding 之一）· 2025-10 试点，2026 预计推广
- 考察点: 怎么向 AI 提问、理解后再采纳、发现 AI 输出错误




**题面 + 参考打法 + 高频追问**



**形式**：60 分钟定制 CoderPad，三面板：文件浏览器/编辑器/AI 聊天窗；**AI 只能在聊天面板回答、不能直接编辑文件**（候选人必须自己搬运和验证）。多文件 codebase 按阶段推进：修 bug → 实现核心功能 → 优化。另一轮仍是无 AI 传统算法。

**参考打法**：因为 AI 不能动文件，粘贴前必须逐行理解——评的就是这个动作；练限时"陌生库定位-修复-扩展"并出声叙述与 AI 的分工。





### [C18] ⭐⭐ OpenAI Chatbot OOD 家族：可扩展多 bot ChatApp / refactor messy chatbot
- 来源: hack2hire（OpenAI 8/10）+ PracHub 同族两题 + coditioning 确认 ｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · coding · 2025-11~2026-06
- 考察点: OOD/开闭原则/pub-sub、防 bot 互触发递归；重构不改行为——"从零写"向"读改现有代码"转向




**题面 + 参考打法 + 高频追问**



**题 1（ChatApp）**：人类用户 + 自动 bot 共享 channel；用户消息先入 channel 日志，各 bot 可响应并把输出加入同一日志；三种 bot 类型含跨 bot 交互（MeetBot 影响 AwayBot 状态）；新增 bot 类型不改现有逻辑。**题 2（refactor）**：给 messy chatbot 代码，保持行为不变重构（PracHub 2026-06-22）。

**参考打法**：
- 公共 bot 接口 + pub-sub：channel 广播解析后的事件，bot 消费自己需要的；跨 bot 交互通过发布状态变更事件解耦，**别让 bot 直接互调**
- 防无限递归：bot 产生的消息标记 origin，bot 不响应 bot 消息（或深度计数）
- 重构题：先补测试锁行为再动刀，边讲边归纳 code smell；路由用 registry/strategy（handler + can_handle）

**高频追问**：多 bot 对同一消息的执行顺序？ ｜ 数千并发 channel 不同路由规则？ ｜ 历史持久化与 bot 逻辑解耦？





### [C19] ⭐⭐ OpenAI Fullstack tech screen：看视频复刻 ChatGPT 式流式聊天 UI
- 来源: 1p3a 三帖交叉（2026-03~05） ｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 背靠背两轮 tech screen（FE coding + SD）· 2026
- 考察点: 消费 token 流渲染、loading/error/retry；**主动讨论边界是显式评分项**




**题面 + 参考打法 + 高频追问**



**题面**：给一个视频——简单输入框+submit 的 ChatGPT 式界面，照着实现；含 streaming text 处理（有提供 utility，不用手写 SSE 解析）。第二轮 SD 聚焦 ChatGPT 功能与异常处理。**挂点提示**（原帖）："要把情况都主动讨论出来，而不是面试官提出 follow-ups 让我们解决"。

**参考打法**：React 消息列表 + 受控输入 + streaming append；主动讨论 loading/error/retry、乱序 chunk、自动滚动（用户上滚时暂停）、防抖、可访问性；SD 轮讲 SSE vs WebSocket、断流恢复、token 计费显示——见 [../03_gaps/streaming.md](?book=drustz-interview-2026&section=agent-core&question=drustz-306f658b7cd85b430e)。2026-07 新变体：PracHub "Build a Reliable Streaming Chat UI"（断线清理/backpressure）。





> 高分句：AI-assisted 轮评的不是代码而是工作流——分解先于 prompt，验证先于接受，全程出声。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/C_live_ai_coding.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md)。作者整理资料；许可和第三方来源范围见阅读指南。
