---
id: google-agent-eval
section: google
order: 32
level: A
title: Google：Agent 基准和 Gemini 产品评测切片（公开口径）
quick: >-
  Agent 分数不是 MMLU。OSWorld 一类看真实电脑上执行式成功；WebArena / Mind2Web
  看网页任务。Gemini 公开的 computer use 偏浏览器，桌面 OS 任务不能当唯一 KPI。产品切片是成功、步数、延迟、引用、确认和拦截，不是单项榜首。
tags:
  - Google
  - Agents
  - Evaluation
  - OSWorld
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OSWorld — Benchmarking Multimodal Agents in Real Computer Environments
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: Mind2Web — Towards a Generalist Agent for the Web
    url: https://arxiv.org/abs/2306.06070
    type: secondary
  - title: Introducing the Gemini 2.5 Computer Use model
    url: https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-computer-use-model/
    type: primary
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: secondary
---

Google 问 agent 评测，要把学术执行基准和产品切片拆开。工具循环的公开层见 `google-gemini-agent`。不要把 Gemini 技术报告里的 MMMU / 长视频分数拿来当「会用电脑」。MMLU 的坑见 `google-eval-mmlu`。不要编内部成功率和未公开的 OSWorld 数字。

## 执行式基准：环境决定你在测什么

OSWorld：真实操作系统里的开式任务，跨应用，用执行脚本判成功，而不是看模型是否说「已经完成」。论文规模大约几百题，人类也做不满：公开人类准确率大约七成量级，中位耗时明显高于 WebArena 一类纯网页集。这说明难度来自环境，不来自题面措辞。

对照：

- **WebArena**：自托管模拟站点，可复现，动作空间是网页。测的是导航和信息抽取，不是桌面套件菜单。
- **Mind2Web / 在线变体**：真实网站、开放指令。域名漂移、登录墙、DOM 改版都会让分数不可比。
- **GAIA 一类**：工具 + 多跳问答，常常不是像素级点击。

Computer Use 的公开博客把模型放在网页 / 移动控制榜上讲，并写明当时 不是为桌面 OS 级控制优化。面试若把 OSWorld 的 Ubuntu 桌面任务当成 Gemini computer use 的唯一验收，等于用错切片。该报的是：浏览器任务用 WebArena / 在线 Mind2Web 一类；桌面任务单独开集，标明环境。跨环境平均分会把失败模式洗掉。

主指标用任务成功（执行器说通过）。辅助：步数、墙钟、工具失败后是否恢复、不可行任务是否认输。人类在 OSWorld 上也会错，100% 不是合理目标。轨迹匹配（是否点了和标注一样的坐标）只能当调试，不能当产品：同一目标往往有多条合法路径。

视觉环每步都在花 token，分辨率见 `google-vit-patch`；长轨迹占窗口见 `google-gemini-longctx`。

## 产品切片：公开口径能说什么

Gemini 产品不是刷一条学术榜。公开能讲、面试也该主动切的轴：

- **任务成功 × 域。** 搜索问答、表格、内部工具、浏览器操作分开。搜接地看引用是否撑住句子；computer use 看最终状态，不看中间自我汇报。
- **成本。** 步数、每步截图分辨率（视觉 token 见 `google-vit-patch`）、检索次数、墙钟。成功但 40 步的路径在产品上可能输给 8 步稍差的策略。
- **安全。** 购买 / 删除 / 发信是否走到确认；拦截是否误杀正常流程。没有确认日志的「模型说它问过」不算。
- **接地诚信。** 有 citation 不等于句子被源支持。要抽查：源里没有的数字、过期页面、检索到的指令型文本（注入）。
- **长程。** 轨迹和截图占窗口。中后段失败单独报，不要只报短任务。

能力基准（MMLU、针、视频 QA）仍要跑，但它们回答的是「模型懂不懂」，不是「环能不能在活环境里结束」。混报是最常见的错法。

在线评测会漂：网站改版、验证码、实验分流。要冻结镜像或自建站做回归，在线集当探活。提示词、允许的动作表、最大步数必须写进协议，否则分数是 harness 的分。

## 常见坑

把演示视频当评测。把模型自述「已完成」当成功。用同一条 OSWorld 分数对比一个浏览器专用模型和一个桌面通用模型。不报步数预算。让 agent 读到评测脚本或 flag。网页内容进 prompt 不加隔离。这些会让分数好看、产品上线翻车。

工具错误要当一等 case：超时、空结果、权限拒绝。只测 happy path 的 function calling，上线第一周就会在观察格式上死循环。工具循环见 `google-gemini-agent`。

不要编 Gemini 在 OSWorld 上的具体百分比。公开口径只够说到「浏览器优先、桌面另测、执行式成功、带步数和安全切片」。内部数没有来源就不要报。

## 追问

- **OSWorld 人类都只有约 72%，模型低是不是没意义？** 有意义，当回归和环境难度锚。产品验收要用域内任务和更干净的执行器，不要用人类不满的开放桌面集当发版门禁。
- **离线和在线哪张当真？** 离线冻结环境当真回归；在线当真漂移和反爬。两张表，不要合成一个「SOTA」。
- **和 MMLU 怎么分工？** MMLU 回归知识污染和 prompt 敏感，见 `google-eval-mmlu`。Agent 评闭环任务。两套都要，不能互相替代。
- **最小可上线切片？** 固定域、固定最大步、执行式成功、确认覆盖、注入探针、延迟分位数。榜首数字排在这张表后面。
