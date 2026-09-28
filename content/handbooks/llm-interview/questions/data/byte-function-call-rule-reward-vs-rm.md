---
id: byte-function-call-rule-reward-vs-rm
section: data
order: 101
level: S
title: 字节 AI 数据技术：Function Call 有标准答案，为什么还要 Reward Model？
quick: >-
  schema、执行结果或 business oracle 能精确验证的部分，我优先用 rule-based reward：便宜、可审计、噪声低。Reward Model 只补规则盖不住的歧义、多目标质量和偏好。两者分项组合，不能用 RM 替代本可验证的正确性。
tags:
  - ByteDance
  - Function Calling
  - RLVR
  - Reward Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 4.28 字节 AI数据技术一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/8e812a2e2b824779bea596a90d7603e0?sourceSSR=enterprise
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 团队 / 岗位：AI 数据技术
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-28
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Function Call这类偏封闭式的任务，入参/格式都有标准答案，为什么不直接用rule-based奖励信号做RL，而要训一个Reward Model？”**

对 tool 名、schema、类型、权限、可执行性和确定性业务结果，应优先用 deterministic verifier。它让 RLVR 的核心正确性可复现，也更容易定位 reward hacking。题干问「为什么还要 RM」，不是否定规则，而是问 RM 补哪一层。用 RM 替代本可验证的正确性，是这题最大的设计错误。

## 规则做硬门，RM 只打软质量

硬门（不合法直接失败）：JSON 可解析、字段类型、枚举、权限、执行是否成功、oracle 是否匹配。规则奖励可再给部分分（少一次多余调用）。RM / judge 只打规则没有唯一答案的层：多条正确工具序列的效率、意图与参数的语义匹配、对用户软约束的轻微违反、解释是否忠实。总分：

$$
R= \mathbf{1}[\mathrm{hard\ pass}]\cdot\bigl(R_{\mathrm{rule}}+\alpha R_{\mathrm{RM}}\bigr).
$$

$\alpha$ 要小，且 $R_{\mathrm{RM}}$ 经校准（见 `data-reward-calibration`）。每项独立上报：规则分涨、RM 分涨、人评是否动。若 RM 与人工在边界 case 上不一致，回 rubric / 数据 / oracle，不把 RM 当真相。

## 实验：消融 RM，别只说「都要」

对照四条：仅规则；规则+未校准 RM；规则+校准 RM；仅 RM。预期：仅 RM 会在 schema 错误上给高分（hacking）；仅规则在「都对但啰嗦」上分不开；组合后 holdout 人评最好。报告 hacking 率（对规则失败却高 RM 分的比例）。Function Call 的封闭部分没有理由交给神经网络打分。

## 追问

- **有标准答案为何还要 RM？** 标准答案盖住格式与执行，盖不住效率、措辞和软约束。RM 是补丁，不是替代。
- **RM 和规则打架怎么办？** 硬门优先。打架样本拉回去改 rubric 或重标，不要调 $\alpha$ 抹平。
- **如何验收？** 分项报表 + 人评 + hacking 率。RM acc 高不能取消 verifier。
