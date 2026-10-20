---
id: dt-agent-rl-map
section: posttrain-data
order: 17
level: S
title: Agent RL 数据：怎么判断这批环境是好的，怎么把它造出来？
quick: "Agent RL 的数据需要包含任务、可执行环境和可复现的奖励。质量检查包括说明是否完整、测试是否稳定、奖励能否被钻空子，以及当前模型是否偶尔能成功。扩展时先筛选或按任务维度合成环境，再并行运行 rollout。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-11
sources:
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: Qwen3-Coder
    url: https://qwenlm.github.io/blog/qwen3-coder/
    type: primary
  - title: "Karpathy: in the era of RL it is environments"
    url: https://x.com/karpathy/status/1960803117689397543
    type: secondary
  - title: "The Second Half (Shunyu Yao)"
    url: https://ysymyth.github.io/The-Second-Half/
    type: secondary
---

回答 Agent RL 数据问题时，先区分两件事：SFT 轨迹用于冷启动，RL 则需要可执行的环境和奖励。下面按问题列出对应的判断和题卡，公开资料用于解释这些判断的依据。

SFT 那组在 `dt-agent-fireact`、`dt-agent-swegym`。苹果侧用户交互默认不进基础模型，燃料是许可环境里的执行反馈。

| 他问 | 我先答 | 卡 |
| --- | --- | --- |
| 数据集是什么 | 环境，不是 jsonl | `dt-agent-env-is-data` |
| 一条任务好不好 | fail-to-pass、说明够、测在考说明里的事 | `dt-agent-task-quality` |
| 2 万条怎么剪 | 炸引用、太复杂、质量分差、flaky | `dt-agent-rl-filter` |
| 奖励怎么写 | 隐藏测 / 状态；别用 patch 相似 | `dt-agent-reward-spec` |
| 怎么打包 | 任务 + harness + rubric，可安装 | `dt-agent-env-stack` |
| 怎么扩 | 先单环境复现，再并行沙箱 | `dt-agent-scale-env` |
| 门禁涨了算赢吗 | 先查测和泄漏 | `dt-agent-verified-stale` |
| 一组全零 | 丢掉；留 pass@$k$ 中间带 | `dt-agent-passk-zero` |
| GUI | 状态检查器，不是点击示范 | `dt-gui-agent-rl` |
| 没有 issue 池 | 按轴合成 Docker + 验证器（verifier） | `dt-agent-tmax-synth` |
| 配方怎么讲 | 先验 + 环境，算法靠后 | `dt-shunyu-second-half` |
| 客户环境 | 对齐生产、隔离 VM、正确性当门 | `dt-agent-rft-recipe` |
| Codex | 断网容器、测到过 | `dt-codex-rl-env` |
| Llama 4 / Gemini | 在线滤题；可验证奖励 | `dt-llama4-rl-recipe`、`dt-gemini-rl-env` |
| 电脑使用 | 少环境、断网、数像素 | `dt-anthropic-cu-recipe` |
| 写成代码 | Env / Harbor / rubric | `dt-tinker-agent-rl` |

## 追问

- **和数学 基于可验证奖励的强化学习（RLVR） 差在哪？** 数学题通常根据最终答案评分。Agent 有多步操作，还要处理不稳定测试和钻奖励漏洞的问题。我会先问奖励会不会被改测试，再谈 GRPO。
- **SFT 轨迹还要吗？** 要，冷启动格式。RL 不靠把 500 条 GPT 轨迹再标一遍。
