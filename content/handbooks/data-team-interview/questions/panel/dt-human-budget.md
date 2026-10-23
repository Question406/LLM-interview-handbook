---
id: dt-human-budget
section: panel
order: 19
level: A
title: Panel：人标预算只够标 1 万条，花在哪？
quick: "先买门禁，再买边界，最后才扩量。人工预算优先保证协议、金标和评测可靠，再标模型失败的边界任务；能执行验证的数学和代码由人写种子、教师扩充、执行器检查，工具轨迹先让模型预跑、人只纠错。均匀撒到所有任务，会把钱花在模型已有的能力上。"
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

1 万条人工预算我会先花在协议、参考标签和评测上，再花在模型不会的难例上，最后才考虑常规扩量。均匀分给所有任务，会把钱花在模型已经会的地方。

这题考的是 ROI。没有金标，后面 9000 条标注只是在放大噪声；能用执行器验证的数学和代码，拿人工当 oracle 是浪费。人的判断最值钱的地方，是机器验证不了、模型又做不对的那部分。

所以我第一笔钱会买几百条高质量、双标过的样本，用来校准标注员和 judge（`dt-annotator-protocol`）。第二笔买评测：locale 母语题、按能力切开的评测切片、对抗性拒答题。评测靠人工保证可靠，训练样本再靠合成扩充，AFM 每种语言几百条母语输入提示（prompt），就是这种花法。第三笔给模型处理不了的边界，比如采样全错的题、过程监督里需要人工回滚的决策点，以及标签比较一致、确实要人判断的主观偏好。

剩下的部分用人加机器扩量。能验证的数学和代码，人写种子和标准答案，扩写交给教师模型加执行器检查。质量分类器的种子也可以人标后再蒸馏，FineWeb-Edu 就是这么做的。工具轨迹让参考模型先跑、人来改错，人的时间花在决策点上；AFM 的工具标注平台就是这样，人修改参考模型预跑里的错误，用不着从零写每一跳。开放闲聊、教师已经会的短指令、和评测重叠的题，这些就不花钱了。

面试时可以现场给一版分法，数字只是示意：金标和评测 1500，协议迭代 500，工具过程监督 3000，偏好里 cohesion 高的 3000，各 locale 种子 2000。具体数字按缺口改，逻辑是门禁和边界优先。

## 追问

**再给 10 万条呢？**
先复盘这 1 万条的边际 $\Delta$。没有 $\Delta$，就不要线性加预算。

**专家贵、众包便宜，怎么选？**
专家用来定协议和金标，众包在协议定好之后扩量。

**用户 opt-in 的数据能替代人标吗？**
默认不能。可用的通道见 `dt-privacy-feedback`。

**数学和代码为什么基本不花人标的钱？**
它们能用执行器验证，人只需要写种子和标准答案，扩写交给教师模型、对错交给执行器检查。
