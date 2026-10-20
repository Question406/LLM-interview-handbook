---
id: dt-rlef-split
section: labs
order: 29
level: A
title: RLEF：执行反馈进对话，奖励却看私有测试，数据怎么切？
quick: "公开测试的结果可以反馈给模型，最终奖励只由未展示的私有测试决定。两套测试分别记录哈希，stderr 不计入交叉熵训练目标。即使公开测试全部通过，只要私有测试失败，奖励仍为 0。"
companies:
  - apple
tags:
  - Meta
  - Coding
  - RLVR
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning"
    url: https://arxiv.org/abs/2410.02089
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

每题准备两套测试，分别记录哈希。公开测试结果可以作为 observation 返回给模型；私有测试只交给评分程序，不写进 prompt。公开测试偏重样例，私有测试覆盖边界条件。训练 loss 只计算助手生成的下一版代码，不计算编译器报错，见 `dt-packed-sft-code`。改测试本身过门的轨迹丢掉，见 `dt-code-exec-synth`。中途公开测全绿但私有挂，奖励是 0，否则学的是「骗过样例」。达到轮次上限仍未提交有效代码，奖励也为 0。

不这么选的理由：公开、私有同一套测，或把 stderr 当 监督微调（SFT） 正文一起 交叉熵损失（CE）。两套测混用，模型会背公开测、改测迎合。和 `dt-rlvr-data` 的差别：基于可验证奖励的强化学习（RLVR） 常是一题一轮、终局对错；RLEF 把中间失败变成合法 observation。

接到苹果：AFM 工具树同构：环境返回给人看、给人改，奖励仍看状态核验，不看「模型说我改好了」。没有私有测至少留人写的一小撮冻结测当门禁，别用对话里出现过的断言。公开测会泄漏私有测，如果是同一生成器切的，题面演化、断言要分源。许可题或验证合成，用户代码会话不进基础模型。

公开锚点：Gehring 等人（Meta，CodeContests）先交一版，公开测试失败就把用例结果和报错拼回对话再改；公开测试全过或到轮次上限，才拿私有测试打 0/1，用 PPO 更新。他们要的是「会读反馈」，不是多采几次碰对。

## 追问

- **公开测会不会泄漏私有测？** 会，如果是同一生成器切的。题面演化、断言要分源。
- **轮次上限交白卷怎么奖？** 0。中途公开测全绿但私有挂，也是 0，否则学的是「骗过样例」。
- **没有私有测？** 至少留人写的一小撮冻结测当门禁，别用对话里出现过的断言。
