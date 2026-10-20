---
id: us-research-vs-applied
section: overview
order: 6
level: B
title: Research Engineer、Research Scientist、Applied MLE，准备重点怎么分？
quick: >-
  Scientist 深挖假设、消融和「结果反了信谁」；RE 要能把论文想法写进可维护的训练/推理栈；Applied
  要在延迟、权限、评测和产品指标上做权衡。三类岗位都可能问 attention，但后续追问的方向不同。
tags:
  - 岗位
  - 备考
  - Research
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide (Exponent)
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: Google research vs software engineering interview tracks (Hello Interview)
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

JD 经常写混。我面试前会问 recruiter 这一轮的 interviewer 是 research 还是 product eng，然后按下面三条线准备，而不是只看 title。

## Research Scientist

预期你能讲清：问题为什么存在、基线为什么不够、你的方法改了哪一个假设、哪张表能证伪你。GQA 这题在 Scientist 嘴里会变成「KV 共享在什么数据分布上掉点」。论文岗见 Google / FAIR / DeepMind 更多。

## Research Engineer

OpenAI RE、Anthropic、xAI 很多轮是工程科研混合。你要能实现、能 debug、能把 checkpoint / 数据格式 / 评测脚本讲成可交接的系统。信息论轮、KV cache、noisy all_gather 都偏这一侧。见 `openai-allgather-noise`。

## Applied MLE / Product

Apple Siri、Amazon Bedrock、Microsoft Copilot、部分 Meta 应用团队：模型是部件，约束是语音预算、p95、引用、权限、上线门禁。答成「换更大的模型」几乎一定被追问。见 `apple-siri-grounded`、`amazon-bedrock-rag`。

## 交叉地带

NVIDIA 的解决方案岗位更像 RE + 系统：并行策略、kernel、精度。Tesla 更像 Applied + 数据引擎。别用一套「大模型八股」打所有 JD。

## 追问

- **简历只有论文没有生产经验？** RE 面把论文代码的训练细节、失败实验和评测漏洞讲透，比编造「我上过线」安全。
- **只有业务 MLE 经验？** 补上 debug 和系统题的准备，不要假装发过 Llama。产品约束是你的优势，主动用它。
