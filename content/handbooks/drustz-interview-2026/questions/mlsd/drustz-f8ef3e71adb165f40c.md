---
id: drustz-f8ef3e71adb165f40c
section: mlsd
order: 177
level: A
title: 19 · Case：设计 agent 能力 benchmark · 15. 常见追问 + 应答要点
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 15. 常见追问 + 应答要点
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 15. 常见追问 + 应答要点

1. **"为什么不能只看最终成功率？就业务而言不就是看结果吗？"**
   业务确实只看结果，但 benchmark 是**预测器**不是记录仪。终态指标对"绕过约束达成目标"完全失明——退款跳过身份验证和正确退款在数据库里长得一样。而且现实中没有纯结果指标，只要叠一个效率项，违规就严格胜出（举 0.800 vs 0.750 那组数）。业务看结果，benchmark 必须多看一层，否则它预测不了下一次会不会出事故。

2. **"过程分会不会惩罚比人聪明的解法？"**
   会——如果写成脚本匹配。所以断言写成**约束**（`verify_identity` 必须在 `issue_refund` 之前完成）而不是**顺序脚本**（第一步必须是 X）。允许 agent 用一次批量查询代替三次单查。判断标准：这条断言删掉之后，是否存在一条既安全又更优的路径被误判——有的话说明断言写得太紧。

3. **"多少题够？"**
   反问要检测多大效应量。$p\approx0.5$、未配对、每题跑一次时 SE $=\sqrt{2p(1-p)/n}$；要分辨 5pt 需要 $n\approx1500$，配对设计能降到 500 上下。再叠 run-to-run 方差还要恶化。**所以我先测 test-retest 噪声，再反推题量**，不先拍一个数字。

4. **" $\mathrm{pass}^k$  的 $k$ 怎么选？"**
   由产品的重试预算决定。有廉价 verifier 且可重试 → pass@k；一次性有副作用 →  $\mathrm{pass}^k$ ，$k$ 取用户一天遇到这类任务的次数量级（3–10）。另外 $k$ 还要够大到能估 per-task $p$——$k=3$ 时 $\hat p$ 只有 4 个取值，算不出有意义的 flaky rate。

5. **"user simulator 用什么模型？会不会有同源偏差？"**
   会。同 family 的 simulator 和 agent 会共享同样的误解并互相配合。做法：simulator 用不同 family、固定版本与 seed、给剧本约束（persona + 已知信息 + **不能主动透露的信息**）、**绝不持有判分权**。并且做一次换 simulator 模型的排名稳定性检验——排名翻了说明测的是 simulator 不是 agent。

6. **"怎么防止 agent 在环境里作弊？"**
   分两层。**环境卫生**：strip `.git`、测试文件延后挂载、网络 deny、verifier 代码只读、答案不出现在任何 fixture 里。**行为检测**：为已知捷径写显式断言（直构 URL、改测试文件、读评分脚本一律判 violation），并且抽样人工读轨迹——**新的作弊方式只能靠读轨迹发现**。我在工作里手动检查 trace 时抓到过格式化推理、失控推理、错误推理、reward hacking 四类异常，这类东西聚合指标上是看不见的。

7. **"任务本身没有可程序化终态怎么办（写报告、做设计）？"**
   三步降级：先看能不能把任务改写成可验证形式（要求输出结构化结论、可核对的数值、明确的引用）——我做过这种 QA 转换；改不动的用 L3 约束断言拆成多个可判定的子条件（是否引用了这三份材料、是否覆盖了这四个必答点）；仍然不行的才上 rubric judge，且必须先用人工标注算 AUROC 和分层检出率来证明这个 judge 有用——我做过一次这样的验证，被验的自动指标 AUROC 只有 0.569，等于掷硬币。

8. **"离线 benchmark 的分数能外推到线上吗？"**
   默认不能，必须实测相关性：拿已上线的若干版本，算离线分与线上指标的秩相关。相关性低时优先怀疑任务分布（初始状态是手写的还是从真实系统 dump 的）。**诚实边界**：大规模在线实验的指标设计、延迟指标 join 和 cohort 分析我在 Meta 做推荐时做过，这套方法论我是熟的；但 LLM/agent 产品的线上 serving 和 oncall 我没做过，所以这一段我给的是设计，会找有线上经验的同事calibration口径。

9. **"benchmark 饱和了怎么办？"**
   饱和是设计里就该预留的。frontier 层从第一天就要有（占 25%），并且按季度用新时间窗任务换掉 30%，换题时保留重叠期做新旧calibration，否则换题前后的分数不可比。另外饱和常常是假的——把总分拆到写操作、长步数、多轮澄清这些分层上，通常还有大量空间。

10. **"你怎么证明你的 benchmark 比现有的好？"**
    不比"好"，比**互补**和**可用**。给三个数：(a) 与现有 benchmark 的排名相关性（如果完全一致，那我没提供新信息）；(b) test-retest 噪声比现有的小多少；(c) 与线上指标的秩相关比现有的高多少。再加一条定性的：现有 benchmark 测不到的那类失败，我能测到（比如绕过约束达成目标）。

11. **"LLM judge 到底能不能用？"**
    能用，但不能当主 gate，也不能只报一个平均分。用法是：先用人工标注做calibration并**分层**报一致率——我遇到过同一条 rubric 在不同题型上判得松紧不一致的情况，全局 agreement 会把这掩盖掉；judge 换 family、固定版本、temperature=0、多次投票并报一致率；分歧样本进人工。更根本的是尽量把任务往可验证阶梯上推，减少对 judge 的依赖。参见 [08 §5](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436)。

12. **"我们的模型在你的 benchmark 上涨了 5 个点，你信吗？"**
    先看四件事：这 5 点是否超过 test-retest 噪声带宽；是配对比较还是各跑各的；harness / 依赖 / prompt 模板有没有同时变（变了就是混杂）；涨的是哪几层——如果只涨在 core 层而 frontier 和 adversarial 层没动，可能是对已知题型的适配而不是能力提升。都过了我才信，而且我会要求在私有 held-out 集上复现一次。

13. **"评测预算只有现在的十分之一怎么办？"**
    按序砍：先砍 frontier 层的 $k$（那层反正 $p$ 低，$k=1$ 就够）→ 用固定的分层子样代替全集（子样必须固定且分层，否则跨版本不可比）→ 开 prefix cache 和不可恢复态剪枝 → 最后才砍 core 层的 $k$，因为砍它等于放弃 flaky rate，而那是可部署性的唯一直接指标。**绝不砍的是 sanity 层和 verifier CI**——它们最便宜，且是防止整批结果无效的保险。

14. **"如果我只给你两周，你先做什么？"**
    第一周：50 题的最小可用集（覆盖三个任务类型），全部 L0/L1 判分，配 gold + known-bad 轨迹，把 harness 和 run manifest 打通。第二周：测 test-retest 噪声，用两个已知强弱差异的系统验区分度。**在噪声和区分度这两个数出来之前，我不会用它做任何决策**——一个没测过噪声的 benchmark 比没有 benchmark 更危险，因为它会给出有信心的错误结论。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
