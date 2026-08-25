---
id: align-red-team
section: alignment
order: 6
level: A
title: 对齐：红队和自动化攻击，覆盖率和过拟合评测模型
quick: >-
  人红队找新失败模式，自动化攻击（GCG、PAIR、多轮越狱）测已知家族的回归。覆盖率看攻击分类有没有洞，不看
  条数。最常见的假安全是过拟合评测模型或公开 jailbreak 集：训练集上 ASR 为 0，换家族就穿。
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

Anthropic 把人红队写进 HH / CAI 的论文；OpenAI 安全岗会问「你怎么知道没过拟合 eval」。别答「我们跑了多少条 jailbreak」。评委听的是：攻击分类覆盖了什么、哪一块是 held-out、自动化攻击有没有被拿去梯度攻击同一个评测模型。误拒切片见 `align-over-refuse`，污染见 `align-eval-contam`。

## 人和自动化各干什么

**人红队** 的产出是新的失败模式，不是分数。Ganguli 等人让红队员对 HH 模型找有害完成；价值在于分类：诱导、角色扮演、多轮升级、虚构借口、工具调用、编码绕过。一条新模式进入 taxonomy，再写自动化回归。人红队规模小、贵，不要拿它当每周 CI 的分子。

**模型红队**（Perez et al.）用 LM 生成攻击，吞吐高，容易扎堆在模型已经会写的模板上。它能扩覆盖，不能替代人去发现「你没想到的分类」。

**白盒 / 优化攻击**（GCG 一类）在 token 上优化可迁移后缀，专门打对齐后的拒答。它测的是：拒答边界对对抗扰动脆不脆。不要把 GCG 成功率当成产品安全的全部。用户不会贴乱码后缀，但能说明边界靠关键词和浅层模式。PAIR、多轮、many-shot 更接近真实：用语言说服模型逐步越界。

面试我会把流水线说成：人发现模式 → 写进分类 → 自动化生成变体做回归 → held-out 家族做门禁。缺任何一段都是洞。

## 覆盖率：分类，不是条数

一万条同一句「ignore previous instructions」的改写，覆盖率几乎为零。覆盖率看 taxonomy 的格子有没有空：

- 单轮 vs 多轮 vs 长上下文 many-shot
- 自然语言诱导 vs 编码 / 翻译 / Base64 vs 工具参数
- 明确犯罪 vs 双重用途 vs 虚构包装
- 英文 vs 其他语言 vs 代码注释
- 无工具聊天 vs function call / computer use

空格子优先补，而不是把已满的格子刷到 10 万条。报告要写「未覆盖：工具参数注入、低资源语言」，比写「ASR 2%」更像做过评测。

人红队的工时应该花在空格子上。已经自动化覆盖的家族，人再去打是浪费，除非你怀疑自动化过拟合了生成器自己的风格。

## 过拟合评测模型，这才是假安全

三种假：

1. **过拟合攻击集。** 把公开 jailbreak 放进训练或迭代过滤，再在同一套上报 ASR。数字会到 0，换一个家族就穿。正确做法：训练可见一套，门禁用从未微调过的家族，定期换皮。
2. **过拟合 judge。** 用同一个 LLM judge 既当 RL 奖励又当安全验收。策略学会 judge 的口味：更长的拒答、更像某家族的说教，真实有害完成不一定降。验收 judge 必须隔离，最好换家族，并抽人标校准。
3. **过拟合攻击生成器。** 自动化红队和被测模型同家族，生成的攻击分布窄。换一个攻击模型，ASR 跳起来。攻击生成器要多样化，并保留人写的种子。

GCG 还可以过拟合到某个 prompt 模板：后缀只打 `You are a helpful assistant` 这条系统提示。换系统提示或加一层转述，攻击失效，不代表通用鲁棒。要报迁移：跨 prompt、跨模型尺寸、跨解码温度。

发现过拟合：同一分类里训练变体 ASR 低、改写或新家族 ASR 高。处理是隔离评测、换题、而不是继续在旧集上训练到 0。不要把评测集写进 SFT 拒答示范，那是污染，见 `align-eval-contam`。

## 追问

- **ASR 为 0 为什么不能交差？** 可能过拟合了攻击集或 judge。问 held-out 家族和人抽查。
- **GCG 和人红队哪个优先？** 都要。GCG 测对抗脆；人红队测你没想到的分类。只跑 GCG 会漏多轮诱导。
- **能对评测模型做对抗训练吗？** 可以对 **训练用** 攻击分布做，但门禁必须换分布。对着验收集对抗训练就是过拟合评测。
- **和过度拒答怎么一起看？** 把攻击打没的同时误拒飙升，是把模型推到「全拒」角，不是对齐成功。
