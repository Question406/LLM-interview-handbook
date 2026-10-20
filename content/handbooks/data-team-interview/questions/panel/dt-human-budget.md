---
id: dt-human-budget
section: panel
order: 19
level: A
title: Panel：人标预算只够标 1 万条，花在哪？
quick: "人工预算优先保证协议、参考标签和评测可靠，再标注模型失败的边界任务。可执行验证的数学和代码由人写种子、教师扩充、执行器检查；工具轨迹先由模型预跑，人纠错。预算分配要看实际缺口，不均匀撒到所有任务。"
companies:
  - apple
tags:
  - Apple
  - Annotation
  - Budget
  - Human-in-the-loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
---

如果只有 1 万条人工标注预算，先投入协议、参考标签和评测，再处理模型不会的难例，最后才考虑常规扩量。均匀分给所有任务，会把预算花在已有能力上。

不这么选的理由：Director 和 Panel 都可能问 ROI。没有金标，后面 9000 条在放大噪声。能执行验证的数学 / 代码，用人换 oracle 是浪费。AFM 工具平台是人改模型预跑，人不是从零写每一跳。

## 人的预算先买门和边界

协议和金标先买。几百条高质量、双标过的，用来校准人和 judge。没有这个，后面 9000 条在放大噪声，见 `dt-annotator-protocol`。

评测也先买。locale 母语题、产品切片、对抗拒答。先用人工保证评测可靠，再让训练样本通过合成扩充。AFM 各语言几百条母语 输入提示（prompt） 就是这种买法。

剩余预算用于模型无法处理的边界：采样全错的题、过程监督中需要人工回滚的决策点，以及标签较一致、确实需要人判断的主观偏好。

能验证的数学 / 代码，人写种子和标准答案，扩写交给教师 + 执行。质量分类器的种子也可以人标，再蒸馏，FineWeb-Edu 那条。工具用参考模型先跑、人改错。AFM 的平台让人修改参考模型预跑中的错误，把时间花在决策上，无需从零写每一步。

不要买：开放闲聊、教师已经会的短指令、和评测重叠的题。

1 万条我可以口播一版分法，不是教条：金标和评测 1500；协议迭代 500；工具过程监督 3000；偏好里 cohesion 高的 3000；各 locale 种子 2000。数字现场按缺口改。逻辑是门禁和边界优先。

## 追问

- **再给 10 万呢？** 先复盘 1 万的边际 $\Delta$。没有 $\Delta$ 就不要线性加。
- **专家贵、众包便宜？** 专家买协议和金标；众包买已定协议的扩量。
- **用户 opt-in 能替代人标吗？** 不能默认。通道见 `dt-privacy-feedback`。
