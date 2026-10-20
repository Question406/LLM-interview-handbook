---
id: dt-agent-tmax-synth
section: posttrain-data
order: 27
level: S
title: 没有现成 GitHub issue 池，怎么合成一批能拿来做 Agent RL 的环境？
quick: "没有现成 issue 池，可以按技能、复杂度、资源等维度生成任务，每题配 Docker 和程序验证器。用教师 pass@$k$ 检查难度，检查领域覆盖，再与 Terminal-Bench 做去污。镜像能构建不保证题和评分器可靠，还要抽查；不要只生成全对的简单任务。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Synthetic
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "TMax: A simple recipe for terminal agents"
    url: https://arxiv.org/abs/2606.23321
    type: primary
  - title: "Lambert: TMax, an open RL recipe for terminal agents"
    url: https://natolambert.substack.com/p/tmax-an-open-rl-recipe-for-terminal
    type: secondary
  - title: TMax GitHub
    url: https://github.com/hamishivi/tmax
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

可以按任务维度组合出题，为每题生成 Docker 环境和程序检查器。GitHub issue 能滤成 SWE 强化学习（RL） 池，见 `dt-agent-rl-filter`；终端 / 通用 agent 很多任务根本没有 PR：装环境、写新仓库、安全演练。公开配方是 Ai2 的 TMax（Ivison、Lambert 等）；Lambert 博文把它叫目前最好用的公开终端 RL 数据，用来在 Terminal-Bench 上爬坡。

常见误区是：只合成「ls 一下」那种全对题，或先逼教师解一遍才留题。任务池如果太简单，增加采样也无法产生足够的中等难度任务。

## 怎么造

按轴采样，再让教师实例化成 Dockerfile、源文件、说明、程序 验证器（verifier）。他们写了九个结构化轴：域和技能、人设、任务复杂度（几条命令到几十步）、命令复杂度（纯 bash 到 bash+代码+系统服务）、fixture（图、音、二进制、compose）、verifier 种类。轴一乘，题面不会全挤在「改一个 Python 文件」。

Verifier 不要只会字符串相等。TMax 加了阈值（准确率 $\ge 0.95$）、对抗语料（干净过、恶意拒）、fuzz 对 oracle、多协议探活。连续奖励能反映部分完成程度，便于调整任务难度；只有全对或全错的二元分数，可能让任务都落在过易或过难两端。

他们故意跳过「先让教师解一遍才留题」。理由：RL 训练时 pass 率 0 的组本来就会被丢掉，见 `dt-agent-passk-zero`。生成侧只保证镜像能 build。代价是检查器可能弱，抽查 rubric 仍要做。

## 怎么判断这批合成环境好不好

TMax 用同一教师（文中 Gemini-3-Flash）在各公开终端集上跑 pass@$1/4/8$。Endless Terminals 一类数据的 pass@$1$ 达到九成，对这个教师而言可能太简单。他们自己的集 pass@$1$ 约四成，pass@$8$ 仍只有一半出头，说明加采样也挖不完。再看域是否均匀：SWE-Smith 一类几乎全是软件工程，终端产品用法盖不住。最后和 Terminal-Bench 做 13-gram 去污，见 `dt-ngram-contam-code`。

对照实验：同一 9B 骨干，换 RL 数据集再上 Terminal-Bench，Tmax-15k 高于 Endless Terminals / TermiGen / SWE-Smith。SWE-Smith 解出率太高，他们只跑了很短，说明「全是能修的 bug」不一定是好的终端 RL 燃料。

苹果：合成环境、许可仓库，不要用户终端日志。教师用参考模型。镜像和检查器进 lineage。门禁用私有 holdout，不要用合成题面洗公开 Terminal-Bench。

## 追问

- **轴采样会不会出不可做的题？** 会。我会靠 RL 软过滤掉全零组。若全零率高，先把复杂度轴往下调，别先换算法。
- **监督微调（SFT） 还要不要？** 要。TMax 另外生成约 2k 环境，每题让教师采 8 条轨迹，过滤无法解析的工具调用，用成功轨迹做 SFT 热身。和 FireAct 的冷启动同一位置，见 `dt-agent-fireact`。
- **和 SWE-rebench 滤 2 万条？** 一条是网上收来再剪，一条是轴上长出来。判断标准共用：检查器稳、难度中间带、和门禁切开。
