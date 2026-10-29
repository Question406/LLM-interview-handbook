---
id: dt-agent-swegym
section: posttrain-data
order: 14
level: S
title: SWE-Gym：用可执行仓库当数据工厂，trajectories 怎么留、verifier 怎么训？
quick: >-
  SWE-Gym 把真实 Python 任务、可执行环境和单测做成一个训练工厂：current policy sampling，测试判成败，成功
  trajectories 做 SFT，成败 trajectories 一起训 outcome
  verifier。任务池要和评测隔开。过测只是必要条件，改测试、漏回归和环境漂移要另外拦。
companies:
  - apple
tags:
  - Apple
  - Agent
  - Coding
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: SWE-Gym
    url: 'https://arxiv.org/abs/2412.21139'
    type: primary
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

SWE-Gym 用可执行仓库当任务环境：current policy 在里面 sampling，测试判成败，成功 trajectories 拿去做 SFT，成功和失败的 trajectories 一起训一个结果 verifier（outcome verifier），inference 时给多条候选 trajectories 打分。

它要解决的是 SWE 数据没法判对错的问题。没有能跑的测试，SWE 数据只能退回到「看 diff 像不像」。SWE-Gym 提供了 2438 个真实 Python 任务，每个都带可执行环境和单测。用它训练后，SWE-bench Verified 和 Lite 都涨了；再用成败 trajectories 训 verifier，resolve 率又涨了一截。

整个流程按顺序走。先把任务池和 evaluation gate 切开，Gym 的训练任务 $\ne$ SWE-bench 的 test。然后 current policy 对每个任务 sampling $k$ 条 trajectories，用 hidden tests 打标签。成功且过程可重放的 trajectories 进 SFT，失败 trajectories 可以拿去训 RM、做偏好或训 verifier。policy update 后，再重新扫一遍任务 difficulty band（见 `dt-math-passk-band`）。

环境本身也是数据资产。Docker、依赖和测试的哈希都要写进数据血缘。环境一变，昨天通过的 trajectories 今天可能就跑不起来，接着引发数据连锁问题（cascade，见 `dt-data-cascade`），这比网页过滤脆弱得多。

## 追问

**过了测试的 trajectories 能直接进 SFT 吗？**
过测只是必要条件。成功 trajectories 里仍可能有改测试、漏回归的情况，要单独拦，见 `dt-swe-success-noise`。

**verifier 为什么只看结果，不做逐步打分的 PRM？**
软件工程的步骤很难一步步判对错，跑最终测试相对便宜。不过 diff 还是要抽查，免得乱改代码、碰巧通过测试的 trajectories 被当成可靠过程。

**合成仓库行不行？**
当 seed 可以，但 grader 必须是真测试。LLM 写的假项目配假测试，是 HumanEval 式自嗨的放大版，我不会拿它当 evaluation gate。

**非 Python 怎么办？**
规则一样，按语言复制环境。没有可 executor，就不要称之为 SWE 数据。
