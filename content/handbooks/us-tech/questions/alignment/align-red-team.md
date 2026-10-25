---
id: align-red-team
section: alignment
order: 6
level: A
title: 对齐：红队和自动化攻击，覆盖率和过拟合评测模型
quick: "我会让人红队先找新失败模式，再用自动化攻击扩成回归集，最后用未参与训练的攻击家族验收。覆盖率按多轮、语言、工具和攻击方式分开看；ASR 很低时，还要检查攻击集、裁判和生成器是否被过拟合。"
tags:
  - Anthropic
  - OpenAI
  - Red Teaming
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Red Teaming Language Models to Reduce Harms
    url: https://arxiv.org/abs/2209.07858
    type: primary
  - title: Red Teaming Language Models with Language Models
    url: https://arxiv.org/abs/2202.03286
    type: primary
  - title: Universal and Transferable Adversarial Attacks on Aligned Language Models
    url: https://arxiv.org/abs/2307.15043
    type: primary
---

红队覆盖率要按失败模式衡量，验收则要保留没参与训练的攻击家族。比如一万条「ignore previous instructions」的改写，虽然数量很多，仍可能完全漏掉多轮诱导和工具参数注入。Anthropic 的 HH / CAI 工作把人红队纳入流程，关键就是发现这种自动化集没想到的问题。

## 人和自动化各干什么

人红队主要用来发现新的失败模式。Ganguli 等人让红队员对 HH 模型找有害完成；价值在于分类：诱导、角色扮演、多轮升级、虚构借口、工具调用、编码绕过。一条新模式进入 taxonomy，再写自动化回归。人红队规模小、贵，不适合把它直接用作每周 CI 的常规量化指标。

模型红队（Perez et al.）用 LM 生成攻击，吞吐高，但容易集中在模型熟悉的模板上。我会让它扩展已有类别，再让人继续找新类别。

白盒 / 优化攻击（GCG 一类）在 token 层面优化可迁移的攻击后缀，专门打对齐后的拒答。它测的是：拒答边界对对抗扰动脆不脆。不要把 GCG 成功率当成产品安全的全部。用户不会贴乱码后缀，但能说明边界靠关键词和浅层模式。PAIR、多轮、many-shot 更接近真实：用语言说服模型逐步越界。

实际流程是人发现模式后先归入分类，再自动化生成变体做回归，最后用 held-out 家族做门禁。

## 检查覆盖和评测隔离

我会按下面的维度交叉检查 taxonomy，找出还没覆盖的组合：

- 单轮 vs 多轮 vs 长上下文 many-shot
- 自然语言诱导 vs 编码 / 翻译 / Base64 vs 工具参数
- 明确犯罪 vs 双重用途 vs 虚构包装
- 英文 vs 其他语言 vs 代码注释
- 无工具聊天 vs function call / computer use

先补空白组合，已有类别不必急着扩到 10 万条。报告 ASR 2% 时，也要写清工具参数注入、低资源语言等未覆盖部分。

人红队的工时应该花在空格子上。已经自动化覆盖的家族，人再去打是浪费，除非你怀疑自动化过拟合了生成器自己的风格。

低 ASR 可能来自三种过拟合，需要分别排查：

1. **过拟合攻击集。** 把公开 jailbreak 放进训练或迭代过滤，再在同一套上报 ASR。数字会到 0，换一类攻击就可能绕过防护。正确做法：训练可见一套，门禁用从未微调过的家族，定期更新攻击变体。
2. **过拟合 judge。** 用同一个 LLM judge 既当 强化学习（RL） 奖励又当安全验收。策略学会 judge 的口味：更长的拒答、更像某家族的说教，真实有害完成不一定降。验收 judge 必须隔离，最好换家族，并抽样用人工标注校准。
3. **过拟合攻击生成器。** 自动化红队和被测模型同家族，生成的攻击分布窄。换一个攻击模型，ASR 跳起来。攻击生成器要多样化，并保留人写的种子。

GCG 还可以过拟合到某个 输入提示（prompt） 模板：后缀只打 `You are a helpful assistant` 这条系统提示。换系统提示或加一层转述，攻击失效，不代表通用鲁棒。要报迁移：跨 prompt、跨模型尺寸、跨解码温度。

同类攻击中，训练变体 ASR 低、改写或新家族 ASR 高，就是过拟合的信号。我会先隔离评测、换题，避免继续针对旧集训练到 0，也不把验收集写进监督微调（SFT）拒答示范。

相关：`align-over-refuse`、`align-eval-contam`。

## 追问

**ASR 为 0 为什么不能交差？**
可能过拟合了攻击集或 judge。问 held-out 家族和人抽查。
**GCG 和人红队哪个优先？**
都要。GCG 测试模型对对抗扰动的脆弱程度；人红队测你没想到的分类。只跑 GCG 会漏多轮诱导。
**能对评测模型做对抗训练吗？**
可以对 **训练用** 攻击分布做，但门禁必须换分布。对着验收集对抗训练就是过拟合评测。
**和过度拒答怎么一起看？**
把攻击打没的同时误拒飙升，是把模型推到「全部拒答」的状态，不是对齐成功。
