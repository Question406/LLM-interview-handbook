---
id: dt-agent-tmax-synth
section: posttrain-data
order: 27
level: S
title: 没有现成 GitHub issue 池，怎么合成一批能拿来做 Agent RL 的环境？
quick: >-
  没有现成 issue 池，就按技能、复杂度、资源这些维度组合出题，每题配 Docker 环境和程序 verifier，这是 Ai2 TMax
  的做法。生成时只保证镜像能 build，全零题留给 RL 训练时剪掉。质量看 teacher pass@$k$ 和领域覆盖，再和
  Terminal-Bench decontamination；checker 还要抽查，全对的简单题也要控制比例。
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Synthetic
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'TMax: A simple recipe for terminal agents'
    url: 'https://arxiv.org/abs/2606.23321'
    type: primary
  - title: 'Lambert: TMax, an open RL recipe for terminal agents'
    url: 'https://natolambert.substack.com/p/tmax-an-open-rl-recipe-for-terminal'
    type: secondary
  - title: TMax GitHub
    url: 'https://github.com/hamishivi/tmax'
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 可以这样回答

可以按任务维度组合出题，给每道题生成 Docker 环境和程序 checker。GitHub issue 能滤成 SWE RL 的任务池（见 `dt-agent-rl-filter`），可终端和通用 agent 的很多任务根本没有对应的 PR，比如装环境、从零写一个仓库、安全演练。公开配方是 Ai2 的 TMax（Ivison、Lambert 等），Lambert 在博文里称它是目前最好用的公开终端 RL 数据，用来在 Terminal-Bench 上爬坡。

Verifier 要比字符串相等检查更强。TMax 加了阈值判定（准确率 $\ge 0.95$）、对抗 corpus（干净输入要通过，恶意输入要拒绝）、对 oracle 做 fuzz、多协议探活。连续奖励能反映部分完成的程度，方便调难度；只有全对或全错的二元分数，任务容易全落在过易或过难两头。

## 技术备查

可以按任务维度组合出题，给每道题生成 Docker 环境和程序 checker。GitHub issue 能滤成 SWE RL 的任务池（见 `dt-agent-rl-filter`），可终端和通用 agent 的很多任务根本没有对应的 PR，比如装环境、从零写一个仓库、安全演练。公开配方是 Ai2 的 TMax（Ivison、Lambert 等），Lambert 在博文里称它是目前最好用的公开终端 RL 数据，用来在 Terminal-Bench 上爬坡。

造法是先按轴 sampling，再让 teacher 把采到的组合实例化成 Dockerfile、源文件、任务说明和程序 verifier（verifier）。他们定义了九个结构化轴，包括域和技能、人设、任务复杂度（几条命令到几十步）、命令复杂度（纯 bash 到 bash 加代码加系统服务）、fixture（图片、音频、二进制、compose）、verifier 种类等。几个轴相乘，题面就不会全挤在「改一个 Python 文件」上。

Verifier 要比字符串相等检查更强。TMax 加了阈值判定（准确率 $\ge 0.95$）、对抗 corpus（干净输入要通过，恶意输入要拒绝）、对 oracle 做 fuzz、多协议探活。连续奖励能反映部分完成的程度，方便调难度；只有全对或全错的二元分数，任务容易全落在过易或过难两头。

常见做法是先逼 teacher 解出来才留题，TMax 故意跳过了这一步。理由是 RL 训练时 pass 率为 0 的组本来就会被丢掉（见 `dt-agent-passk-zero`），生成侧只要保证镜像能 build。代价是 checker 可能偏弱，所以 rubric 抽查还是要做。另一头，「ls 一下」那种全对的题也要控制比例，任务池太简单，sampling 再多也凑不出足够的中等难度任务。

判断这批环境好不好，他们看了难度、覆盖和 contamination。难度上，用同一个 teacher（文中是 Gemini-3-Flash）在各个公开终端数据集上跑 pass@$1/4/8$：Endless Terminals 一类数据 pass@$1$ 到了九成，对这个 teacher 来说可能太简单；他们自己的数据集 pass@$1$ 约四成，pass@$8$ 也只有一半出头，说明加 sampling 也挖不完。覆盖上看域是否均匀，SWE-Smith 一类几乎全是软件工程，覆盖不了终端产品的真实用法。最后和 Terminal-Bench 做 13-gram decontamination（见 `dt-ngram-contam-code`），镜像和 checker 都进 lineage。

最有说服力的是下游对照。同一个 9B 骨干，只换 RL 数据集再测 Terminal-Bench，Tmax-15k 高于 Endless Terminals、TermiGen 和 SWE-Smith。SWE-Smith 解出率太高，他们只跑了很短，可见「全是能修的 bug」不一定是好的终端 RL 燃料。

## 追问

**轴 sampling 会不会出不可做的题？**
会。RL 阶段的软过滤会把全零组剪掉。如果全零率很高，先把复杂度轴往下调，别急着换算法。

**和 SWE-rebench 滤 2 万条比呢？**
一个是从网上收来再剪，一个是沿着轴长出来。判断标准是共用的：checker 要稳，难度在中间带，和 held-out evaluation set 分开。

**SFT 冷启动还要吗？**
要。TMax 另外生成约 2k 个环境，每题让 teacher 采 8 条 trajectories，过滤掉无法解析的 tool calls，用成功 trajectories 做 SFT 热身。这和 FireAct 的冷启动处在同一个位置，见 `dt-agent-fireact`。

**合成题能拿来刷公开的 Terminal-Bench 吗？**
别这么用。自己的 evaluation gate 用私有 holdout，拿合成题面去刷公开的 Terminal-Bench 只会得到虚高的分数。
