---
id: dt-codex-rl-env
section: posttrain-data
order: 30
level: S
title: Codex 公开写了怎样的 Agent RL 环境？
quick: "Codex 的公开做法是为 agent 提供预装代码和依赖的容器，在轨迹开始后断网，让它读取文件、修改代码并迭代运行测试。正确性主要靠测试验证，风格另作评价；没有 grader 的仓库，需要先建立检查器才能进行 RL。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - OpenAI
  - Codex
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Introducing Codex
    url: https://openai.com/index/introducing-codex/
    type: primary
  - title: "Addendum to o3 and o4-mini system card: Codex"
    url: https://openai.com/index/o3-o4-mini-codex-system-card-addendum/
    type: primary
  - title: Introducing upgrades to Codex
    url: https://openai.com/index/introducing-upgrades-to-codex/
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

每个 agent 使用一个云容器，代码和依赖预先装好。轨迹开始后断网，模型读取和修改文件，并根据测试结果继续迭代。这是「环境即数据」的产品形态，见 `dt-agent-env-is-data`。公开句子在 2025-05 的 Codex 博客和 o3 system card 附录：codex-1 是 o3 为软件工程做的 强化学习（RL） 版。

训练时开放外网，agent 可能搜到标准补丁，导致奖励被污染。风格相似度也不能作为主要正确性检查。没有 grader 的仓库，先生成并固定一套检查器，再进行 RL。

## 环境合同

里面能读文件、改文件、跑测试、linter、类型检查。训练侧他们写：在多样环境里的真实编程任务上做 RL。目标三条：补丁像人、听指令、迭代跑测试直到过。GPT-5-Codex 后来把任务写得更长：从零搭项目、加功能、大重构、code review；公开演示里有过数小时独立迭代。回答时说明它支持较长任务，并通过测试反复迭代；不要推测内部时长，更不能将其当作 AFM 的数字。

`AGENTS.md` 告诉 agent 怎么跑测、仓库惯例。这是环境的一部分，不是可有可无的 README。训练中缺少这类仓库说明，模型上线后就可能选错命令或忽略惯例。

## 奖励和安全数据

过测试是主信号。另外对齐人的 code style 和 PR 偏好。system card 写了会引用终端日志和文件，让人能核。声称成功时，应提供能让人核查的日志或文件依据。风格放在「测过了」之后，和 Cosine 的门一样，见 `dt-agent-rft-recipe`。

安全训练用了扰动环境和合成环境：缺文件、容器状态和用户假设的仓库不一致。模型做了不一致的动作要罚，承认不确定要奖。这是 agent 数据集里常缺的负例：环境撒谎或过期时该停。

公开榜是评测。Codex 写的是真实任务、多样环境、断网沙箱。训练池不能等于 Verified 500 条，见 `dt-agent-verified-stale`。

苹果：许可仓库镜像、冻结依赖、无外网、测试当 oracle。用户 IDE 日志默认不进基础模型。

## 追问

- **断网是安全还是数据质量？** 两边都是。外网一开，agent 能搜金补丁，奖励被污染。我会断网。
- **风格奖励会不会压功能等价？** 会，SWE-RL 的 patch 相似是前车。我会把风格放在测过了之后。
- **没有测试的仓库怎么办？** 先合成 / 冻结一套检查器，再 RL。没有 grader 的环境只能 监督微调（SFT）。
