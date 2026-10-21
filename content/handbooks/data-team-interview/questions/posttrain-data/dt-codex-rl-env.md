---
id: dt-codex-rl-env
section: posttrain-data
order: 30
level: S
title: Codex 公开写了怎样的 Agent RL 环境？
quick: "每个 agent 一个云容器，代码和依赖预先装好，轨迹开始后断网；agent 在里面读文件、改代码、反复跑测试直到通过。正确性靠测试判，风格放在测过之后另评。断网是为了防止 agent 搜到标准补丁污染奖励；没有 grader 的仓库，要先建好检查器才能做 RL。"
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

Codex 公开的做法是：每个 agent 一个云容器，代码和依赖预先装好，轨迹开始后断网，模型在里面读文件、改文件，根据测试结果反复迭代。正确性主要靠测试判，风格另外评。这就是「环境即数据」的产品形态，见 `dt-agent-env-is-data`。

公开出处是 2025-05 的 Codex 博客和 o3 system card 的 Codex 附录，里面写明 codex-1 是 o3 针对软件工程做强化学习（RL）得到的版本。

## 环境里有什么

容器里可以读文件、改文件、跑测试、linter 和类型检查。训练侧的公开说法是：在多样环境里的真实编程任务上做 RL，目标有三条，补丁像人写的、听从指令、迭代跑测试直到通过。后来的 GPT-5-Codex 把任务拉得更长：从零搭项目、加功能、大规模重构、code review，公开演示里有过数小时的独立迭代。回答时说它支持较长任务、靠测试反复迭代就够了，内部时长没有公开，不用去推测。

仓库里的 `AGENTS.md` 告诉 agent 怎么跑测试、仓库有什么惯例。它是环境的一部分，训练时缺这类仓库说明，模型上线后就可能选错命令、忽略惯例。

为什么要断网：训练时开着外网，agent 可能直接搜到标准补丁，奖励就被污染了。所以断网既是安全措施，也是数据质量措施。

## 奖励怎么给

通过测试是主信号，其次才对齐人的 code style 和 PR 偏好。风格相似度放在「测过了」之后再评，这和 Cosine 的门禁顺序一样，见 `dt-agent-rft-recipe`。system card 还写了，模型会引用终端日志和文件，让人能核查；声称成功时，要给出能核查的日志或文件依据。

安全训练用了扰动环境和合成环境，比如缺文件、容器状态和用户假设的仓库对不上。模型在这种情况下做了不一致的动作要罚，承认不确定要奖。这是 agent 数据集里常缺的一类负例：环境撒谎或已经过期时，模型应该停下来。

还要分清训练和评测。公开榜单是评测，Codex 写的是真实任务、多样环境、断网沙箱，训练池要和 Verified 那 500 条评测题分开，见 `dt-agent-verified-stale`。

## 追问

- **断网是为了安全还是数据质量？** 两者都有。外网一开，agent 能搜到金标准补丁，奖励就被污染，所以我会断网。
- **风格奖励会不会压掉功能等价但写法不同的解？** 会，SWE-RL 用 patch 相似度做奖励就是前车之鉴。我会把风格放在测试通过之后。
- **没有测试的仓库怎么办？** 先合成或冻结一套检查器，再做 RL。没有 grader 的环境只能做监督微调（SFT）。
