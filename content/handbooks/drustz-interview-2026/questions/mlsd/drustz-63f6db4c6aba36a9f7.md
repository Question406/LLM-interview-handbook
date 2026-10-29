---
id: drustz-63f6db4c6aba36a9f7
section: mlsd
order: 112
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 9. Reward 的来源与验证 ⭐⭐⭐
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 9. Reward 的来源与验证 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 9. Reward 的来源与验证 ⭐⭐⭐

通用的 reward 结构、provenance 表和防 hacking 清单在 [03 §6–§7](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2)，**这里只讲 RL 数据 pipeline 特有的部分**。

### 9.1 三类来源在 RL 数据侧的分工

| 来源 | 覆盖的题型 | 假阳性来源 | 我的做法 |
|---|---|---|---|
| **规则 / 符号等价** | 数值、表达式、集合 | normalization过松（`包含 "5"` 就算对）、sympy 误判 | 按答案类型分派比较器；**禁止「任意位置出现即算对」的匹配** |
| **单元测试** | 代码、可执行任务 | 测试不完备、模型 hard-code | 隐藏测试集 + 对抗用例；参考解交叉验证 |
| **LRM-as-judge** | 前两者覆盖不到的 | 风格偏好、位置偏好、跨题标准漂移（§9.3） | **尽量降级成「抽答案 + 规则比较」**，把 judge 的作用域压到最小 |

### 9.2 一个具体的规则设计原则

> **匹配要严格，等价要宽松。** 「严格」指答案必须出现在约定位置（`\boxed{}` 里、最后一行），不接受在推理过程中任意位置扫描；「宽松」指一旦抽出来，`1/2`、`0.5`、`\frac{1}{2}` 要互认。
>
> 把这两件事搞反是最常见的 verifier bug：宽松匹配 + 严格等价 = 模型学会**枚举一串候选答案**（「可能是 3，也可能是 5，或者 7」），只要正确答案在里面就通过。这是我见过的最经典的 verifier hack，而且它在 pass rate 曲线上看起来完全正常。

### 9.3 LRM-as-judge 的一致性问题（我的真实经历）

**我遇到的具体问题**：同一套评判标准，judge 在不同题目上判得不一致——同样是「解法有一步跳跃」，在 A 题上判过、在 B 题上判不过。

**为什么会这样**（可以讲的分析）：judge 被要求同时做三件事——理解题目、复核解法、按 rubric 打分。当题目本身的难度变化时，judge 用于「理解题目」的能力预算变化，剩给「按标准打分」的部分就不稳定。**这不是 prompt 写得不够清楚的问题，是任务负载的问题。**

**怎么量化不一致**（面试官很可能追问）：

| 检验 | 做法 | 健康线 |
|---|---|---|
| **test–retest** | 同一个 (prompt, response) 在 T>0 下判 N 次 | 自一致率；<90% 说明 judge 本身就是噪声源 |
| **顺序/位置交换** | pairwise 判定时交换两个回答的位置 | 翻转率应 <10% |
| **锚定集漂移** | 一组人工标注的固定样本，每次 pipeline 运行都重判 | 跨批次一致率；换 judge 版本时必查 |
| **跨域calibration** | 分域统计 judge 通过率 vs 人工抽检通过率 | 差值 >5pp 说明该域系统性宽/严 |

**修法的优先级**（这个排序本身是观点）：

1. **缩小作用域**（最有效）：能抽答案就别让 judge 读全文。judge 只做「这两个表达式等价吗」比「这个解法对吗」一致得多。
2. **拆成 claim 级 yes/no**（§6.2 路径 D，有 0.569 → 0.844 的实测支撑）。
3. 给 few-shot 锚例，且锚例要**跨难度**覆盖。
4. 多 judge 投票——**最后才用**，因为它成本翻倍且掩盖问题而不是解决问题；共享盲区不会被投票消除。

### 9.4 ⭐⭐⭐ 两类 verifier 错误的代价严重不对称

| | **假阳性**（错的判成对） | **假阴性**（对的判成错） |
|---|---|---|
| 对梯度的影响 | **强化了错误行为** | 只是噪声 |
| 会不会被放大 | **会**——策略会主动搜索 FP 区域，这是一个对抗过程，危害随训练时间**增长** | **不会**——策略没有动机去撞它 |
| 对难度估计的影响 | p̂ 虚高 → 好题被当简单题丢 | p̂ 偏低 → 简单题被当好题留（相对无害） |
| 表现 | pass rate 上翘但下游 eval 不动 | 训练慢、天花板低 |
| 设计取向 | **「判对」这一侧必须高 precision** | 可以容忍一定比例 |

**一句可以直接说的话**：

> verifier 的两类错误在 RL 里代价不对称好几个数量级。假阴性只是给梯度加噪声，策略没有动机去利用它；假阳性是被策略**主动搜索**的——RL 的整个机制就是找到能拿高 reward 的路径，而假阳性区域正是免费高 reward 的所在。所以我在设计 verifier 时是 **precision-first on the positive label**：宁可漏判一些正确答案，也不要放过一个错误答案。这也是为什么我不愿意用「宽松匹配」——它换来的召回率提升，代价是打开了一个 hack 通道。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
