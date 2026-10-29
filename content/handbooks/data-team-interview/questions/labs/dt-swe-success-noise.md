---
id: dt-swe-success-noise
section: labs
order: 25
level: S
title: SWE trajectories：测试过了就能整段进 SFT 吗？
quick: >-
  不能。hidden tests 通过只说明最终补丁对，过程里仍可能有改测试、重复执行但没有推进任务和反复失败的 tool calls，整段进 SFT
  会把这些一起教给模型。先丢掉改过测试文件的 trajectories，再按过程质量筛片段，loss 只算助手生成的编辑和推理。SWE-Prime 筛出的约
  10% 子集胜过全部已解决 trajectories，这个比例是论文 ablation study 结果，换了数据要重新定。
companies:
  - apple
tags:
  - SWE-bench
  - Agent
  - Trajectory
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'SWE-Prime: Fewer Trajectories, Better Performance'
    url: 'https://arxiv.org/abs/2608.27449'
    type: primary
  - title: From SWE-Zero to SWE-Hero
    url: 'https://arxiv.org/abs/2604.01496'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能整段进。测试通过只证明最终补丁对，证明不了过程值得模仿，通过的 trajectories 里照样有重复执行但没有推进任务、乱改测试、反复失败的 tool calls。我会按过程质量截取，只把值得模仿的部分放进 SFT。

模型学的是 trajectories 里每一步怎么做。比如一条成功 trajectories 里有十次空的 `str_replace`、几轮死循环，SFT 就会把这些也当示范学进去。更糟的是捷径：补丁只改测试，或者把期望输出硬编码进去，测试照样能过，这等于在教模型作弊。

筛的时候先看结果：hidden tests 是否通过，trajectories 有没有改过测试文件；只改测试或硬编码期望输出的补丁当负例，不当正例。再看过程，tool calls 成功率过低，或者出现空 `str_replace`、死循环、超步数的，降低整段 trajectories 或对应片段的训练权重。loss 只算助手生成的编辑和推理，输入的仓库文件和工具返回不算。仓库提交号、镜像和测试命令都要存下来，事后复现不了的 trajectories 不能用。

公开工作给了具体的筛法。SWE-Hero 把改了测试补丁里任何文件的 trajectories 直接丢掉，一步调用多个工具、或同一编辑器连错三次的，也丢掉。SWE-Prime 先按过程、结果和代表性筛 trajectories，再把连续步切成片段，loss 只开在选中的片段上；用筛过的约 10% 子集训练，SWE-Bench Pro / Verified 相对全部已解决集最高大约 +12.2% / +24.2%。trajectories 少一些、干净一些，效果更好。

## 追问

**失败 trajectories 全扔吗？**
不全扔。重复执行但没有推进任务的扔；中途改对了的失败尝试可以当恢复示范，见 `dt-traj-quality`。

**10% 要照搬吗？**
不用，那是 SWE-Prime 的 ablation study 结果。现场讲清按哪些过程标准截取，百分比只当论文里的参考数字。

**没有真实仓库怎么办？**
至少要有可重置的假仓库和冻结的测试。纯文本「假装修 bug」进不了基于 verifiable reward 的 RL（RLVR）。

**这和一般 tool-use trajectories 的筛法有什么不同？**
思路一样，这张卡补的是软件工程 trajectories 特有的脏法；通用 tool-use trajectories 哪一段进 SFT，见 `dt-traj-quality`。AFM 2025 报告处理 tool-use trajectories 也是这个思路，成功的主要执行路径要做状态核验，被放弃的尝试另作他用。
