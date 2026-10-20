---
id: dt-swe-success-noise
section: labs
order: 25
level: S
title: SWE 轨迹：测试过了就能整段进 SFT 吗？
quick: "测试通过后仍要筛选轨迹：修改了测试文件的不要；环境返回不计入训练 loss；空转和失败操作也不能都当示范。SWE-Prime 筛出的约 10% 子集效果优于全部已解决轨迹，但这是论文消融结果，不能当作苹果的固定配额。"
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
updatedAt: 2026-10-12
sources:
  - title: "SWE-Prime: Fewer Trajectories, Better Performance"
    url: https://arxiv.org/abs/2608.27449
    type: primary
  - title: "From SWE-Zero to SWE-Hero"
    url: https://arxiv.org/abs/2604.01496
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先检查隐藏测试是否通过，以及轨迹有没有修改测试文件。再检查过程质量：工具调用成功率过低，出现空 `str_replace`、死循环或超步数时，要降低整段轨迹或对应片段的训练权重。捷径：补丁只改测试、或硬编码期望输出，当负例，不当正例。训练 loss 只计算助手生成的编辑和推理，不计算输入的仓库文件和工具返回。轨迹要同时记录仓库提交号、镜像和测试命令；之后无法复现的轨迹不能使用。`dt-traj-quality` 写 AFM 日历树的成功轨迹的筛选条件，这张卡是软件工程轨迹特有的脏法。

不这么选的理由：SWE-bench 过了的 采样轨迹（rollout） 全留。过测的轨迹里仍有空转、乱改测试、反复失败的工具调用。把 10% 当苹果配额也不对，那是他们的消融。现场说「按过程质量截」。

接到苹果：没有公开 SWE-bench 配方。能对上的是 AFM 工具树：成功的主要执行路径要状态核验，被放弃的尝试另用。端侧 / PCC 的工具更短，同一套「成功仍可能脏」。许可仓库或合成环境，用户会话默认不进基础模型。没有真实仓库至少要可重置的假仓和冻结测试。纯文本「假装修 bug」进不了 基于可验证奖励的强化学习（RLVR）。失败轨迹：空转的扔，有改对过程的失败的尝试可以当恢复示范，见 `dt-traj-quality`。

公开锚点：SWE-Prime 先按过程、结果、代表性筛轨迹，再把连续步切成片段，损失（loss） 只开选中的片段；筛过的约 10% 子集训，SWE-Bench Pro / Verified 相对全量已解决集最高大约 +12.2% / +24.2%。SWE-Hero：改了测试补丁里任何文件的轨迹丢掉；一步调了多个工具、或同一编辑器连错三次，也丢掉。

## 追问

- **失败轨迹全扔？** 空转的扔。有改对过程的失败的尝试可以当恢复示范，见 `dt-traj-quality`。
- **10% 是不是教条？** 那是他们的消融。现场说「按过程质量截」，别背百分比当苹果配额。
- **没有真实仓库？** 至少要可重置的假仓和冻结测试。纯文本「假装修 bug」进不了 RLVR。
