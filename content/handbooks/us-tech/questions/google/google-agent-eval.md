---
id: google-agent-eval
section: google
order: 32
level: A
title: Google：Agent 基准和 Gemini 产品评测切片（公开口径）
quick: "Agent 用执行后的任务成功率评测，再按环境、步数、延迟、安全确认和引用质量切片。Gemini 公开 computer use 口径偏浏览器，桌面 OS 任务需单独测试，MMLU 或视频 QA 不能代替真实操作验收。"
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

Agent 评测先看执行后的任务是否成功，再按环境和产品约束拆分。浏览器操作、桌面任务、搜索问答测的内容不同，不能用同一个总分代表全部能力。比如同一任务走 40 步才完成，产品上可能还不如 8 步、成功率稍低的策略，需要把成本一起报。

OSWorld 在真实操作系统中做跨应用开放任务，由执行脚本验收，模型说“已完成”不算成功。论文规模约几百题，人类准确率约七成，追问中常引用约 72%，中位耗时明显高于纯网页的 WebArena。它适合做环境难度锚和回归，但开放桌面集本身人类也做不满，100% 并非合理产品目标。

WebArena 用自托管模拟网站，强调网页导航与信息抽取，可复现；Mind2Web / 在线变体来自真实网站与开放指令，域名、登录墙和 DOM 改版都会影响可比性；GAIA 一类则偏工具与多跳问答，未必涉及像素点击。Gemini 2.5 Computer Use 的公开博客主要在网页 / 移动控制榜上介绍，并说明当时未针对桌面 OS 级控制优化。因此浏览器用 WebArena / 在线 Mind2Web 一类测试，桌面另开集并标明环境。

产品侧把搜索问答、表格、内部工具、浏览器操作分开。主指标由执行器判断最终状态，辅助看步数、实际耗时、检索次数、每步截图分辨率、工具失败后的恢复，以及不可行任务是否会停止。轨迹坐标匹配只适合调试，因为同一目标可能有多条合法路径。

安全要检查购买、删除、发信是否真正走过确认，并有日志，另外统计误拦正常流程。搜索问答还要抽查引用是否支持句子，尤其源里没有的数字、过期页面，以及带指令的检索文本。长轨迹和截图会占窗口，任务中后段失败要单独报。MMLU、针和视频 QA 可以继续测模型能力，但不能代替活环境里的执行验收。

回归用冻结镜像或自建站，在线集则观察网站改版、验证码、实验分流和反爬的影响，两张表分别报告。协议固定 prompt、动作表、最大步数和延迟分位数，防止把 harness 变化当能力变化。还要测工具超时、空结果和权限拒绝，隔离网页内容进入 prompt 的方式，防止 agent 读到评测脚本或 flag。演示视频、模型自述和单一榜首都不足以验收。

公开材料不足以支持 Gemini 的内部成功率或未公开 OSWorld 百分比，就应停在公开范围：浏览器优先、桌面另测、执行式成功，附上步数、安全与注入探针。最小上线切片也应包含固定域、最大步数、确认覆盖和注入测试。

相关：`google-gemini-agent`、`google-eval-mmlu`、`google-vit-patch`、`google-gemini-longctx`
