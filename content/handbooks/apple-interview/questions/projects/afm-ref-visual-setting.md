---
id: afm-ref-visual-setting
section: projects
order: 5
level: S
title: 个人 Reference 5：VisualSkill，怎么讲真实 multimodal 数据与评审偏差？
quick: 我会用 VisualSkill 讲图像信息什么时候真的有帮助，并检查收益是不是来自多给了信息、或者换了一种评分方式。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Jiabao Ji
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: VisualSkill — v1
    url: 'https://arxiv.org/html/2606.18448v1'
    type: primary
  - title: OSWorld — original benchmark paper
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
---

## 面试官可能这样问

你有什么 multimodal 相关的例子可以展开？

## 可以这样回答

我会用参与的 VisualSkill 工作来讲。界面操作里，有些东西用文字解释很费劲，一张图可能更直接，比如按钮在对话框的哪个位置。但图片也会占上下文，过期的截图甚至可能误导模型，所以我关心的是它在哪些任务上有实际帮助。

如果做对照，我会尽量让文字版和图文版来自同一份材料，用相同的 agent 和工具跑。否则图文版多知道了几个操作步骤，最后分数更高，也很难说是视觉信息带来的。

评价这里也有一个我觉得值得讨论的点：看截图给分，和检查文件、应用状态，测到的东西可能不同。一个表格外观很整齐，数字仍然可能填错。我会把这些结果分开看，再抽查它们不一致的任务。具体我本人负责了哪部分，面试时仍然按实际贡献来讲。

## 被追问时再展开

**这等于训练过 multimodal 模型吗？** 不一定。这是 multimodalagent、技能内容和评价的研究。有没有更新视觉模型权重，需要按实际实验回答。

## 技术备查

## 已核对的相关研究
[VisualSkill](https://arxiv.org/html/2606.18448v1) 从文档和 UI 探索构造图文技能，使用 CUA-World、OSExpert-Eval，并有 OSWorld 跨模型补充。你是公开共同作者；具体主导内容需自行补充。multimodal 对照和任务评价细节优先读论文§2、§3及附录 F。

[OSWorld 原始论文](https://arxiv.org/abs/2404.07972) 提供真实计算机任务与执行评价背景，但不同任务集、应用版本、观察/动作接口和 verifier 要分别固定，不能合并当一张排行榜。

## 可深入的 setting（建议实验）
选一个许可软件环境的“修改表格并导出 PDF”任务。技能样本含 topic、文字说明、截图 crop、动作前后状态和出处。将文档版、探索增强版分别做图文/文字配对，再加 no-skillbaseline。控制信息来源、agent、动作接口和总 context/时间预算；文字版需要描述同样的内容，不能人为删掉关键信息。

用正确截图、无关截图、过期 UI 截图作诊断，不把所有性能差都 attribution 视觉能力。分开查按钮定位、任务规划、工具 schema 和 context 压力。反馈环节只用训练任务的错误定位探索区域，再在新任务/新 UI 上验收，避免照着测试答案补文档。

本论文中 CUA-World 使用 VLM checklist 给部分分，OSExpert-Eval 为状态型成功检查。它们 normalization 到0–1后仍测量不同，平均分不等于相同成功概率。建议 sampling 人工核验，增加状态/文件内容检查，并报告视觉 judge 对漂亮但错误输出的偏好。可解释地并列报告两个基准，而非只看合并总分。

## 英文60秒参考
> My multimodal discussion would start from VisualSkill, where I am a coauthor. The broader question is whether visual reference material contributes grounded information beyond a text-only artifact. I would use matched-source controls, hold the agent interface fixed, and evaluate on tasks not used to patch the skills. I would also separate state-based success from visual-judge scores: putting both on a zero-to-one scale does not make them equivalent. Additional images can help, but they can also introduce stale information or context overhead.

## 高频追问与回答方向
**是不是 vision token 越多越好？** 不，按任务定位信息价值，测不相关/过期内容和预算开销。
**这算 multimodal 训练经验吗？** 是 multimodalagent 与数据 artifact 研究；是否训练了视觉模型权重按实际经历回答。
**怎样接合成训练？** 可提出将成功与恢复 trajectories 转为 SFT、用独立状态构造偏好；尚未做的训练结果明确标 proposal。

继续练 `afm-rm-multimodal-evidence`、`dt-mm-shortcut-audit`、`dt-multimodal-data`。

