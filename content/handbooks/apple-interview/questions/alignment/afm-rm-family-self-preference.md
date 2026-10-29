---
id: afm-rm-family-self-preference
section: alignment
order: 108
level: A
title: 同家族 self-preference：换一个 judge 就足以消除 teacher 文风优势吗？
quick: 我会先把它当作一个需要验证的结果：可能能力提高了，也可能只是文风更像 judge 喜欢的样子。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---

## 面试官可能这样问

teacher 和 judge 是同一家族，student 涨分了，能信吗？

## 可以这样回答

我会先把它当成一个待验证的结果。student 可能真的变好了，也可能只是学到了 teacher 的写法，而同家族 judge 正好喜欢这种写法。

我会保留同一批候选，用其他 judge 和独立 human evaluation 再看，最好把事实正确、信息完整和文风分开。还可以隐藏模型名、交换顺序，看看偏好是否稳定。如果换一个 judge 结论就反过来，我会先查评审标准。仅仅换成不同家族，也不保证所有偏差就消失了。

## 技术备查

## 场景与问题
teacher T 生成 synthetic data，student S distillation T，judge 也用 T；S 自动胜率涨 12 点，human evaluation 不变。请提出至少三个竞争假设。

## 参考答案
可能是任务真正变好、风格更接近 T、候选或 evaluation leakage，也可能是 human evaluation 样本不足。构造生成器×judge 的交叉 matrix，隐藏模型名、随机顺序，使用同一组候选与任务。人工分别核对事实、完整性、风格；内容等价改写可做辅助，但改写器本身也会改变质量。

公开 judge 研究讨论 self-enhancement 等偏差，这不是“所有同家族评审必然作弊”的结论。若某 judge 只在同家族候选上异常偏好而独立核验不支持，减少该通道权重、补异风格对或更换评审。不同家族也可能共享训练源与长度偏好，多样性不能替代独立质量证据。

## 追问
**匿名模型名已经够了吗？** 不够，内容风格仍可 leakage 身份。
**多个 judge 多数投票就是真值吗？** 不是，共同错误不会被投票消除。

