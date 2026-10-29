---
id: drustz-e0174f950fcfeff32a
section: mlsd
order: 94
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 10. 成本：人工评不起，怎么sampling ⭐⭐⭐
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 10. 成本：人工评不起，怎么sampling ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md
    type: primary
---
## 10. 成本：人工评不起，怎么sampling ⭐⭐⭐

### 10.1 两个池子绝对不能混

这是很多候选人会栽的地方：

| 池子 | sampling方式 | 用途 | 混用的后果 |
|---|---|---|---|
| **无偏审计池** | 按生产分布**纯随机**（或已知概率的分层随机） | 估计总体质量、算 judge 一致率、对外报数 | 一旦掺入"挑难的"，所有总体估计都偏低 |
| **调试 / 高信息池** | 不确定性sampling、judge 分歧、低分尾部、新切片 | 找 bug、补 rubric、生成训练数据 | 用它算总体 = 系统性低估质量 |

**必背句**：不确定性sampling是**分配标注预算**的方法，不是**估计总体**的方法。要用它做估计，必须带已知的sampling概率做重要性加权（IPS），否则就分开报。

### 10.2 sampling策略对比

| 策略 | 用在哪 | 收益 | 陷阱 |
|---|---|---|---|
| **分层配额** | 保证每个切片有最小 n | 切片可报、CI 可算 | 结果要按真实流量重加权才是产品分 |
| **随机审计集** | 无偏总体估计、judge calibration | 唯一无偏 | 绝大多数样本平淡无聊，信息密度低 |
| **不确定性 / 分歧sampling** | 分配人工预算 | 每美元信息量最高：优先标 judge 双向不一致、多 judge 分歧、分差 <0.5 的样本 | 有偏，不能直接算均值 |
| **两阶段 / 序贯** | 模型差距悬殊时提前停 | 可省 50%+ | 序贯检验要做 alpha spending，否则假阳性膨胀 |
| **PPI / 控制变量** | judge 全量 + 人工小样本 | 无偏且更窄的 CI，等效人力 ×2–4 | 需要 judge 与人评相关性够高，ρ<0.5 时收益很小 |
| **IRT / 区分度筛题** | 压缩 benchmark | tinyBenchmarks 类工作：约 100 条精选题即可把全量 benchmark 估到 ±2pp 量级 | 区分度随模型代际变化，要定期重calibration |

### 10.3 PPI：这一节的技术亮点

**问题**：judge 便宜但有偏，人工无偏但贵。能不能两者结合，拿到"无偏 + 窄 CI"？

能。设 $f(x)$ 是 judge 对样本 $x$ 的打分，$y$ 是人工标签，全量 $N$ 条里随机抽 $n$ 条做人工：

$$\hat\theta_{\text{PPI}} = \underbrace{\frac{1}{N}\sum_{i=1}^{N} f(x_i)}_{\text{judge 全量}} + \underbrace{\frac{1}{n}\sum_{j\in \text{labeled}} \big(y_j - f(x_j)\big)}_{\text{人工修正项}}$$

- **只要人工子集是随机抽的，这个估计量就是无偏的**——judge 有多大偏差都不影响无偏性，偏差被第二项完整减掉。
- 方差大致按 $(1-\rho^2)$ 缩小，$\rho$ 是 judge 与人评的相关性。$\rho=0.8$ → 等效人工样本量约 **2.8 倍**。
- 面试里的一句话总结：**judge 提供variance reduction，人工提供无偏性；judge 变差只会让 CI 变宽，不会让结论变错。**这比"我们用 judge 代替人工"稳健得多。

### 10.4 我做过的两阶段sampling，直接搬过来

我在 Reflection 做 RL 数据筛选时的做法：**正式 rollout 前先用 16 条小批量探测可解率，全对或全错的直接丢弃（没有梯度信号），保留下来的再跑 128 条**。这套筛选大约消耗 **12% 的算力**，思想和 DAPO 的 dynamic sampling 一致。

**同一套逻辑在评测里的三处应用**：

1. **题目筛选（item discrimination）**：所有被测模型都对、或都错的题**没有区分度**，占着预算却不影响结论。用一次小批量探测把它们移出主 gate 集（但要留在 canary 集里防退化）。
2. **两阶段样本量**：先用 16–32 条粗判两个模型是否明显有差距；差距悬殊就早停，接近才追加到 128+。这在扫描 144 个切片时能省一大半。
3. **算力预算的心理锚**：**把总算力的百分之十几花在"筛选/评测"上是正常且值得的**——面试官问"评测该占多少预算"时，这是一个有来源的答案。

### 10.5 评测流水线的工程现实（差异化素材）

大多数候选人不谈这一层，但它决定评测能不能真的每天跑。

**评测本身就是一个大规模batch inference作业**：几万条 prompt × 多个模型 × 多次sampling × judge 调用。我在 Reflection 自建过batch inference框架，共享 GPU 池被其他团队抢占是常态，所以做了：

- **pause / resume**：作业能被抢占后从断点恢复，动态申领和让出资源。
- **TCP 式自适应并发**：成功就加并发，窗口内出现失败就退避——对付 API 限流和不稳定的推理后端同样有效。
- **结果按样本粒度幂等持久化**：每条样本的结果单独落盘并带idempotency key，重跑不会重复计费也不会丢。

**为什么这在评测里是必需的**：一次发布 gate 要跑 6 小时，在第 5 小时被抢占就全白跑，团队就会开始"跳过评测直接发"。**评测的可靠性直接决定它会不会被绕过**——这是社会技术问题，不只是工程问题。

### 10.6 其他降本杠杆

| 杠杆 | 说明 |
|---|---|
| **级联** | 先用便宜 judge 扫全量，只把"接近/分歧"的送贵 judge，再把贵 judge 的分歧送人工。三级漏斗 |
| **prefix cache** | judge 的 system prompt + rubric 是固定长前缀，命中率极高 |
| **能门禁化就别用 judge** | 可验证的部分（格式、约束、schema）用代码，一次判决省一次 LLM 调用（§4.3） |
| **judge distillation** | 用大 judge 的判决训一个小 judge，只用于**筛查和训练中信号**，发布 gate 仍用大 judge + 人工。小 judge 要单独跑一遍 §5.3 的验证 |
| **复用** | 同一批 prompt 的旧模型输出缓存下来，新旧对比时只需要跑新模型 |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
