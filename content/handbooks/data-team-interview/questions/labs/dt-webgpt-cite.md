---
id: dt-webgpt-cite
section: labs
order: 32
level: A
title: WebGPT：为什么没有引用，事实偏好几乎标不动？
quick: >-
  因为没有引用，annotator 只能凭记忆或文笔判断真假，事实 preference labels 噪声很大。WebGPT 把数据拆成两部分：浏览
  trajectories 教模型怎么搜，带引用的答案让 annotator
  逐句核对出处。「引用是否支持」和「来源是否可信」要分开评，评测时再去掉引用比一次，防止引用格式本身让答案显得可信。
companies:
  - apple
tags:
  - OpenAI
  - Factuality
  - Search
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'WebGPT: Browser-assisted question-answering with human feedback'
    url: 'https://arxiv.org/abs/2112.09332'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

因为没有引用，annotator 手里没有材料可核对，只能凭记忆或文笔判断哪个回答更真实，事实 preference labels 自然噪声很大，见 `dt-annotator-protocol`。引用让每句话都能指回支持它的材料，annotator 才有东西可比。

比如两个回答对同一件事给出不同的说法，annotator 自己也记不清，最后只能挑写得更笃定、更流畅的那个。这样标出来的偏好，奖励的是文笔。

WebGPT 用文本浏览器，人先演示检索，再比较带引用的回答，数据也就分成两部分。浏览 trajectories 记下查询、点击链接和滚动，用 SFT 教模型怎么搜；工具返回的 observation 不计入损失，浏览 trajectories 和答案也不要不加区分地算进同一份 cross-entropy 损失（CE）。带引用的答案每句话指回材料，annotator 按材料比较事实是否得到支持，之后还可以让 reward model（RM）做 rejection sampling，挑带引用的答案。公开实验里效果最好的组合是行为克隆加 rejection sampling。

评测时去掉引用再比一次，防止引用格式本身让答案显得更可信。必须搜索的题，要检查是否真的调用了搜索工具，见 `dt-when-to-search`、`dt-agent-state-path`。

## 追问

**WebGPT 的效果怎么样？**
在 ELI5 上，模型相对人工演示的偏好胜率为 56%，相对 Reddit 高票回答为 69%；他们也在去掉引用后做了比较。Reddit 高票本身也不是 gold labels，他们换过不熟悉细则的 annotator 做对照。

**引用支持了答案，答案就可信吗？**
不一定，来源本身也可能不可靠。「是否支持」和「来源是否可信」要分开评，混成一个「更好」，强硬的语气和引用格式就会掩盖问题。

**Llama 3 也是这个思路吗？**
是。Llama 3 post-training 用 Brave Search 补训练截止之后的事件，工具章节说明人工按调用步骤标注、不修改工具返回内容。搜索负责获取材料，事实标签检查材料能否支持回答。

**模型不搜、直接答对了呢？**
产品上可以快，但训练标签要求该搜的题必须出现搜索调用。
