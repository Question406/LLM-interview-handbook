---
id: xai-screen-15min
section: xai
order: 0
level: S
title: "xAI: 15-minute video screen, clock and cut reasons"
quick: "我会按 15 分钟准备：2–3 分钟从近期工作讲起，5–8 分钟展开一个技术决策，1–2 分钟说明想去的具体团队。公开材料称多数被报告的拒绝发生在这里；若面试官迟到 10 分钟就改用 90 秒项目介绍，并提前和 coordinator 确认本轮是否包含 coding，准备可选 CS 问答或 BankAccount race。"
tags:
  - xAI
  - 15-minute screen
  - Interview process
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-29
sources:
  - title: The xAI 15-Minute Phone Screen (Complete Guide)
    url: https://aceoffer.app/interviews/xai_phone_screen_guide
    type: secondary
  - title: xAI Interview Question Bank (1Point3Acres)
    url: https://www.1point3acres.com/interview/problems/company/xai
    type: secondary
  - title: xAI Exceptional Engineer (SWE) Interview Guide
    url: https://www.tryexponent.com/guides/xai-exceptional-engineer-swe-interview
    type: secondary
  - title: Member of Technical Staff, Coding Agents / Post Training (job loop)
    url: https://simplify.jobs/p/1bfe5ce2-5b08-407c-8528-525c646ffee4/Member-of-Technical-Staff
    type: secondary
---

这轮要把时间留给一个你真正负责过的技术决策：近期经历简短开场，项目讲到接口、kernel 或训练约定的粒度，再说一个具体团队方向。公开准备材料称，多数被报告的拒绝发生在这里，面试风格直接、取决于面试官，常用 Google Meet。回答「为什么 xAI」的产品背景见 `xai-spacexai-now`，内存 KV 和 race 细节见 `xai-kv-txn`。

## 15 分钟怎么分配

| 时间段 | 对方想听什么 | 公开准备材料提醒的失误 |
| --- | --- | --- |
| 自我介绍，2–3 分钟 | 先讲当前角色；可能被打断要求「focus on recent」 | 从本科按年份复述简历 |
| 一个项目，5–8 分钟 | 瓶颈、为什么选这个方法、放弃了哪个方案，能落到 API、kernel、训练约定 | 只讲「我们协调了各方」等项目管理经过 |
| 为什么 xAI、想做什么，1–2 分钟 | 明确方向：Grok inference、training infra、agentic RL、video gen、supercompute；LLM PhD 也可选 Grok Build、post-training、search、compaction、Grok Bot | 只说「我喜欢 Grok」 |
| 可选基础问答或编码 | 进程和线程、共享内存、GIL、async 和 threading；也可能现场修 BankAccount race | 卡住后恢复太慢，剩余时间不够展开 |
| 反问 | 能接住对方团队正在做的问题 | 只问 onsite 是否考 LRU、要刷多少 LC medium |

公开 MTS 招聘流程中，通过后常见的是 CV 和 exceptional-work statement、这轮 screen，再接 coding、两轮 post-training 和一个短报告。Researcher、PhD 的 screen 也可能围绕论文，不能据此认定每个岗位流程相同。

面试官如果迟到 10 分钟，只剩 5 分钟，也可能还希望听完核心内容。这时直接用 90 秒讲项目，再用 45 秒点明团队方向，然后停下来等追问。项目介绍涵盖问题、约束、你负责的决策、一个失败方案，以及能证伪方案的指标。

coordinator 的说明写着「...as well as a coding question」，就准备 `xai-kv-txn` 和下面的 live-debug 变体；如果明确是 papers-only，就把深挖时间留给论文。我会为同一个项目准备两种讲法：一种沿训练、奖励约定展开，一种沿 serving、KV 和进程约定展开，由对方第一个追问决定用哪种。对方明显偏 search-eval 或 coding-verifier 时，再准备第二篇论文。

澄清题意时先提问，等回答后复述约定，再开始解。直接说「我假设 deposit 是共享 `balance` 的 lost update」然后马上改代码，即使修法正确，也可能没回应对方要求。口头 CS 题的停顿在这轮尤其明显；如果不熟 GIL，可以一句话说明，再给出自己能解释清楚的 OS 层回答。

## 90 秒项目介绍怎么讲

先用一句话说明卡在哪里，例如 wall-clock 主要花在 tool I/O、搜索集合不完整，或者 verifier 无法执行；再说明什么约束让直接方案失效。接着讲自己做出的算法、loss、隔离或 API 决策，为什么放弃另一个方案，以及上线后什么结果会证明自己错了。例如 Hit@1 上升但 wall-clock 没变，或压缩率提高、任务成功率却下降，都要能解释。

实际回答只用自己真实参与过的项目。roadmap、团队规模和「我们发布了 v2」这类信息，除非能解释关键决策，否则不占这 90 秒。

可选的 BankAccount 题通常给一段 `deposit`：读余额、`sleep`、写回。共享状态是 `balance`，临界区覆盖整个读改写，sleep 只是放大竞态窗口。两个线程都读到 100、都写回 110，就丢了一次存款。可以用 mutex 包住整个 RMW，或用 CAS 循环；不允许改原类时就在外层 wrap，并明确说出锁覆盖哪几行。细节见 `xai-kv-txn`。

还有一种 live-debug 变体，预约 15 分钟，实际可能跑 30–45 分钟：在 CoderPad 上修失败单测，常用 Python，有时还是 BankAccount，难度通常不高。时间到时仍漏了异常路径也会失败。我会先复述约定、跑最小失败用例、修复，再检查剩余的 `except`、`None` 和空列表边界，然后才说完成。

## 追问

**PhD 和 SWE 的 screen 有什么差别？**
时间相同，技术深挖的粒度不同：前者可能围绕 GRPO、reward、eval protocol，后者围绕锁粒度。Coding Agents 的公开岗位仍可能安排后续 coding assessment。

**这一章的 Tesla 卡片可以当 xAI 背景讲吗？**
只用作对照。不要把 occupancy nets 当成自己的 xAI 研究方向。

**怎么回答伦理或使命相关的问题？**
用空搜索时是否诚实、引用是否有证据这样的具体约定来讲，见 `xai-search-agent`。不要说因为没有 ethics round 才申请。
