---
id: ml101-schedules
section: optimization
order: 7
level: A
title: "学习率衰减、预热和早停各解决什么问题？"
quick: "预热在训练开始用较小步长逐渐升高，减轻初始更新不稳定；衰减在后期减小步长，帮助细化优化；早停根据验证表现决定何时结束，避免无收益计算或过拟合。三者可以组合，分别控制起步、后期更新与停止时机，参数应由验证实验确定。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Dive into Deep Learning: Learning Rate Scheduling"
    url: https://d2l.ai/chapter_optimization/lr-scheduler.html
    type: primary
  - title: "scikit-learn: Early stopping in Gradient Boosting"
    url: https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_early_stopping.html
    type: primary
---

学习率预热帮助模型稳定起步，衰减调整后期更新尺度，早停则根据验证表现决定训练到哪一轮。它们作用的时间和判断依据不同，可以同时使用。

预热（warmup）让学习率从较小值逐渐升到计划峰值，避免某些网络在初始阶段的大更新导致发散。后续衰减可以按阶梯、余弦或验证平台期降低学习率，减少在较好区域附近的大幅波动；预热长度与衰减形状都没有适合所有任务的固定答案。机制见 [D2L 学习率调度](https://d2l.ai/chapter_optimization/lr-scheduler.html)。

例如先逐渐升高步长，再按余弦下降；若验证损失一段时间没有有意义的改善，就结束训练，并恢复验证表现最好的 checkpoint。早停检查的是泛化信号，训练损失仍下降时也可能触发。实际要定义监控指标、最小改善幅度和等待轮数，避免一次噪声波动就停。[scikit-learn 早停示例](https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_early_stopping.html) 展示了验证驱动的停止。

## 追问

**验证集用于早停后，还能当最终测试吗？**
不能视为未参与选择的独立测试。停止轮数已经用到了它的表现，最终评估应留其他数据。

**训练一开始就不稳定，早停能替代预热吗？**
不能。早停只终止训练，不会修正不稳定的更新；要检查学习率、初始化和梯度，再决定是否预热。
