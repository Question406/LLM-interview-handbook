---
id: baidu-code-agent-verifier
section: posttrain
order: 101
level: S
title: 百度文心一言：Code Agent 的 verifier 怎样设计？
quick: >-
  我会把 verifier 做成分层、可执行的判定器：先 sandbox、编译和单测，再做隐藏测试、属性测试、静态安全检查和
  resource limit，输出结构化 failure reason。既要低 false positive，也要挡住 reward hacking，而且训练和评测集必须严格隔离。
tags:
  - Baidu
  - Code Agent
  - Verifier
  - RLVR
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度文心一言面试（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/681c33aafac84af0a70b6fd5e663a04c
    type: candidate-first-hand
---

## 真题记录

- 公司：百度
- 团队 / 岗位：文心一言；岗位原帖未披露
- 届别 / 流程：原帖未披露；一面
- 面试时间：2026-07-02；帖子发布于 2026 年 7 月
- 来源类型与可信度：牛客候选人原帖，B（公司、轮次与面试日期明确，岗位和届别未披露）
- 原始措辞：**“Code Agent verifier 怎么设计”**

错法：「再训一个打分模型」或「让 LLM 当 judge」。第一职责是判定可执行事实：编译过不过、测试过不过、有没有越权、有没有超时。自然语言评语既不可复现，也极易被拍马，不能当唯一奖励。GRPO / RLVR 的优势完全建立在这张 $r$ 上，整组同奖励则 $\hat A=0$，见 `sys-rl-group-n`，所以 verifier 的洞会直接变成策略。训练用的 judge 和最终 holdout 必须隔离，否则模型学的是公开测试的漏洞，不是写对代码。

## 分层判定，输出结构化原因

把候选放进隔离 sandbox：断网、限文件系统、CPU、内存和 wall time，防止训练时打到评测机或读隐藏文件。按语言分层执行：编译 → 公开测试 → 隐藏测试 → 属性测试或 differential testing → 静态安全检查。输出结构化原因，例如 `compile_error`、`wrong_answer`、`timeout`、`security`，不要只给 $0/1$。Repository / Agent 任务还要验证 diff 范围、测试命令、依赖锁定和不可修改文件。失败原因可以回灌纠错 SFT，但不能把隐藏测试细节写进给模型看的反馈，否则策略学会读题面而不是写实现。

奖励可以做成分层标量：编译过给小正、单测过给中等、隐藏测试过给 1。过程奖容易变成刷模板（先打印「通过」再乱写），先用终局奖把正确率做起来，再决定要不要过程项。反向 KL 挡的是参考支撑外的胡话，挡不住「参考里就有的假通过」，见 `fund-kl-directions`。

## Reward hacking 与评测隔离

测试不可只覆盖题面样例。要随机生成边界、做 mutation、检查硬编码返回值和读取测试文件等投机路径，并定期人工审计「通过但不正确」的轨迹。verifier 本身要单独评估：precision、recall、逃逸率、平均执行成本和超时占比。训练 reward 用公开 judge，最终 holdout 用另一套用例和另一份隐藏种子，避免把 judge 漏洞学成策略。组内全过但 holdout 全挂，是泄漏的典型病历，应立刻停训查测试隔离，而不是加 $n$。异步大 batch 里过期轨迹的 $r$ 仍按旧测试算，策略比需要 CISPO 一类受控 IS，见 `pt-cispo`；权重再稳，奖错了也救不了。

## 追问

- **为什么不用 LLM judge？** 不可执行、不稳定、易拍马。可作辅助信号或解释层，不能当唯一 $r$。
- **False positive 和 false negative 哪个更致命？** 训练里 FP 会强化 hack；评测里 FN 会低估能力。两边都要单独报，不要用一个 F1 糊弄。
- **和 DAPO 动态采样怎么配合？** 全对 / 全错组仍是零方差，该滤；滤的是当前策略下的信息量，不是永久删题。
- **工具调用失败算不算负例？** 算。超时、权限错误、错误依赖必须进 $r$，否则 Agent 学会「假装成功」。
- **sandbox 被逃逸怎么办？** 当安全事故，不当时训练噪声。先修隔离，再谈算法；被逃逸的轨迹不能回灌。
