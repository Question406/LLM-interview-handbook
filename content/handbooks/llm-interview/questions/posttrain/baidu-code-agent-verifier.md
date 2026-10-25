---
id: baidu-code-agent-verifier
section: posttrain
order: 101
level: S
title: 百度文心一言：Code Agent 的 verifier 怎样设计？
quick: "Code Agent 的验证器先判可执行事实：把代码放进限资源的 sandbox，编译、跑单测，再跑隐藏测试、属性测试和静态安全检查，每次返回结构化失败原因。verifier 本身的误判和投机通过要单独测，训练与评测用例严格隔离，因为它的洞会直接变成策略。"
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

Code Agent 的验证器（verifier）首先要判定可执行的事实：编译过不过、测试过不过、有没有越权、有没有超时。我会把它做成分层的执行检查，每一层返回结构化的失败原因，再把训练用的 judge 和最终 holdout 严格隔开。再训一个打分模型、或者让 LLM 当 judge，给不出可复现的结论，自然语言评语还极易被拍马屁，当不了唯一的奖励。

为什么这么较真？GRPO / 基于可验证奖励的强化学习（RLVR）的优势完全建立在这个 $r$ 上，整组同奖励时 $\hat A=0$，见 `sys-rl-group-n`，所以 verifier 有洞，洞就会直接变成策略。比如测试只覆盖题面样例，模型就可能学会针对样例硬编码返回值，训练奖励一路涨，换一组用例就全挂，学到的是公开测试的漏洞，代码并没写对。

具体做法按执行顺序讲。先把候选放进隔离的 sandbox：断网，限制文件系统、CPU、内存和 wall time，防止训练时打到评测机或者读到隐藏文件。然后按语言分层执行：编译 → 公开测试 → 隐藏测试 → 属性测试或 differential testing → 静态安全检查。输出结构化原因，比如 `compile_error`、`wrong_answer`、`timeout`、`security`，别只给 $0/1$。Repository 或 Agent 任务还要验证 diff 范围、测试命令、依赖锁定和不可修改的文件。失败原因可以回灌做纠错监督微调（SFT），但给模型看的反馈里不能写隐藏测试的细节，否则策略学会的是读题面，实现照样写不对。

奖励可以做成分层标量：编译过给小的正分，单测过给中等，隐藏测试过给 1。过程奖励容易变成刷模板，比如先打印「通过」再乱写，所以先用终局奖励把正确率做起来，再决定要不要加过程项。反向 KL 挡的是参考支撑以外的胡话，挡不住「参考里本来就有的假通过」，见 `fund-kl-directions`。

防 reward hacking 要主动做。测试要覆盖题面样例以外的情况：随机生成边界、做 mutation、检查硬编码返回值和读取测试文件这类投机路径，并定期人工审计「通过了但其实不对」的轨迹。verifier 本身也要单独评估：precision、recall、逃逸率、平均执行成本和超时占比。训练 reward 用公开 judge，最终 holdout 用另一套用例和另一份隐藏种子，免得把 judge 的漏洞学成策略。组内全过、holdout 全挂，是泄漏的典型病历，这时应该立刻停训查测试隔离，加 $n$ 没用。异步大 batch 里，过期轨迹的 $r$ 仍按旧测试算，策略比要用 CISPO 这类受控 IS，见 `pt-cispo`；不过权重再稳，奖励算错了也救不回来。

## 追问

**为什么不用 LLM judge？**
它不可执行、不稳定，还容易被拍马屁。可以当辅助信号或解释层，不能当唯一的 $r$。

**false positive 和 false negative 哪个更要命？**
训练里 FP 会强化 hack，评测里 FN 会低估能力。两边要分开报，别用一个 F1 糊过去。

**和 DAPO 的动态采样怎么配合？**
全对、全错的组仍是零方差，该滤就滤；滤的是当前策略下没信息量的组，题并没有被永久删掉。

**工具调用失败算负例吗？**
算。超时、权限错误、错误依赖都要进 $r$，不然 Agent 会学会「假装成功」。

**sandbox 被逃逸了怎么办？**
当安全事故处理，别当训练噪声。先修隔离，再谈算法；被逃逸的轨迹不能回灌。
