---
id: byte-function-call-rule-reward-vs-rm
section: data
order: 101
level: S
title: 字节 AI 数据技术：Function Call 有标准答案，为什么还要 Reward Model？
quick: >-
  schema、执行结果、业务判定规则能准确检查的部分，用规则奖励做 mandatory checks，成本低、可审计，噪声也少。Reward Model
  只补规则覆盖不到的歧义、软约束和偏好，比如多条正确序列里哪条更高效。两类信号分项组合，RM 不替代已经能直接验证的正确性。
tags:
  - ByteDance
  - Function Calling
  - RLVR
  - Reward Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 4.28 字节 AI数据技术一面（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/8e812a2e2b824779bea596a90d7603e0?sourceSSR=enterprise
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 团队 / 岗位：AI 数据技术
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-28
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Function Call 这类偏封闭式的任务，入参/格式都有标准答案，为什么不直接用 rule-based 奖励信号做 RL，而要训一个 Reward Model？”**

能被规则准确检查的部分照样用规则奖励，RM 补的是规则管不到的那一层。题目问「为什么还要 RM」，问的是 reward model（RM）补哪一层；用 RM 去替代本来就能验证的正确性，是这题最大的设计错误。

tool 名、schema、类型、权限、可执行性和确定性的业务结果，都优先用确定性验证器（verifier）。它让 RLVR 的核心正确性可以复现，出现钻奖励规则的空子也更容易定位。可标准答案管不到所有东西。比如用户说「查一下明天的天气，下雨就提醒我带伞」，先查天气再建提醒能完成任务，中间多查一次城市编码也能完成，两条轨迹规则都给满分；哪条更简洁、提醒的措辞合不合用户的意思，规则就分不出来了。

## 规则做 mandatory checks，RM 打软质量

mandatory checks 是不合法就直接失败：JSON 能解析、字段类型、枚举、权限、执行是否成功、oracle 是否匹配。规则奖励还可以给部分分，比如少一次多余调用。RM / judge 只打规则没有唯一答案的那层：多条正确工具序列的效率、意图与参数的语义匹配、对用户软约束的轻微违反、解释是否忠实。总分写成：

$$
R= \mathbf{1}[\mathrm{hard\ pass}]\cdot\bigl(R_{\mathrm{rule}}+\alpha R_{\mathrm{RM}}\bigr).
$$

$\alpha$ 要小，$R_{\mathrm{RM}}$ 要先 calibration（见 `data-reward-calibration`）。每一项单独上报：规则分涨没涨、RM 分涨没涨、人评动没动。RM 和人工在 edge cases 上不一致时，回去查 rubric、数据和 oracle，别把 RM 当真相。

## 用 ablation 说话

光说「两个都要」不够，我会对照四组：只用规则；规则加未 calibration 的 RM；规则加 calibration 过的 RM；只用 RM。预期是只用 RM 会在 schema 错误上给高分，也就是被 hack；只用规则分不开「都对但啰嗦」的回答；组合之后 holdout 人评最好。另外报 hacking 率，也就是规则判失败、RM 却打高分的比例。Function Call 里封闭的那部分，没有理由交给神经网络打分。

## 追问

**有标准答案为什么还要 RM？**
标准答案管得住格式和执行，管不住效率、措辞和软约束。RM 是补丁，替代不了规则。

**RM 和规则打架怎么办？**
mandatory checks 优先。打架的样本拉回去改 rubric 或者重标，别调 $\alpha$ 把它抹平。

**怎么验收？**
看分项报表、人评和 hacking 率。RM 的 acc 再高，也不能因此撤掉 verifier。
