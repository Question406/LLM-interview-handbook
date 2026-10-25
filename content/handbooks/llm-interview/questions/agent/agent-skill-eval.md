---
id: agent-skill-eval
section: agent
order: 9
level: S
title: 怎么评估一个 Agent Skill 写得好不好？
quick: "评 Skill 要做只改 Skill 的对照实验：固定模型、工具和预算，比较不加载、只加载描述、加载全文及新版本。成功率之外还要测 token、工具调用、延迟、抗干扰和误触发对其他任务的伤害，并排除把答案写进 Skill 的情况。"
tags:
  - Skill
  - Eval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Equipping agents for the real world with Agent Skills
    url: 'https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills'
    type: primary
---

判断一个 Skill 好不好，我会做一组只改 Skill 的对照实验，看它在固定模型、工具和预算下有没有带来净收益。读着合理只说明文档写得清楚，它也可能泄漏了评测答案、只对某一个模型有效，或者误触发后拖累相邻任务。开卷改完 Skill 就宣布「Agent 更强了」，是最常见的误区。Anthropic 把 Skill 定位成可加载的程序性说明书，它的价值应该落在让 Agent 少走弯路上，把题解写进文档不算。

举个例子，一个 Skill 让目标任务成功率涨了 10%，可它在相邻任务上被误触发，那边掉了 20%，合起来净效益是负的，这就不是好 Skill。这种负迁移只有把相邻任务也放进评测才看得到。

实验条件我会这样排。先跑不加载 Skill 的基线；再只加载名字和触发描述，因为这两样本身就有提示效应，不拆出来会把检索带来的增益算到 Skill 正文头上；然后加载全文，看真实增益；再在全文之外混进干扰 Skill，测抗干扰和误触发；最后新旧版本对比，查回归。每种条件都比成功率、token 用量、工具调用次数和延迟。流程型 Skill 常常能减少无效探索，这部分省下的成本也是收益，所以效率按 success per token、per tool-call、per latency 来报。只报成功不报成本，最后选出来的往往是更啰嗦的说明书。

接着查泄漏。Skill 里该写的是 procedure，比如先查再改、失败了怎么停、什么时候问用户，benchmark 的标准答案和隐藏数字不该出现。验证办法是用 held-out 实例、参数化任务、藏起答案、换域变体去跑；拿掉数字答案后成功率崩了，说明它在作弊。评测集要和 Skill 作者隔离，作者边看失败 case 边改 Skill 的时候，评测一定得是 held-out 的，否则增益只是把答案写进了说明书。

还要承认 Skill 和模型是绑定的。同一篇自然语言 Skill，不同模型的理解差别很大，我会把它当成效果依赖具体模型的文档：要么分模型出变体，要么写成更结构化、可执行的步骤，减少「会不会读长文」带来的差异。

最后是发布门禁：相对 no-skill 有成功增益，token 不涨或者涨幅说得清，干扰条件下误触发低于阈值，held-out 变体不崩。过不了的就当参考文档，不默认加载。Skill 仓库也要有版本和回归集，像代码一样审，合并的条件是对照实验有增益且没有负迁移，写得清楚不够。

## 追问

**怎么判断 Skill 只是把答案泄漏进去了？**
用 held-out 实例、参数化任务、隐藏数字答案和跨域变体去测。Skill 应该描述 procedure，拿掉题面特解就崩，就是在作弊。

**同一个 Skill 在不同模型上效果不一样怎么办？**
把它当 model-conditioned artifact。分模型出变体，或者写成更结构化的可执行清单，别假设一份文字说明适合所有模型。

**Skill 的增益和 harness 的增益怎么分开？**
评 Skill 时冻结模型、工具和预算；反过来声称模型变强时冻结 Skill，见 `arl-model-harness-ablation`。两边同时改，就说不清各自带来了多少改善。

**只看成功率够吗？**
不够。还要看 token、调用次数、延迟和干扰条件下的误触发。啰嗦的说明书能把成功率抬一点，成本和负迁移也跟着抬上去了。
