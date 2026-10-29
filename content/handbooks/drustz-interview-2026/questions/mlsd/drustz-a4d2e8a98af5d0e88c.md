---
id: drustz-a4d2e8a98af5d0e88c
section: mlsd
order: 113
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 10. Reward Hacking 的检测：从 trace 里看 ⭐⭐⭐
quick: >-
  作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 10. Reward Hacking 的检测：从 trace
  里看 ⭐⭐⭐
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
## 10. Reward Hacking 的检测：从 trace 里看 ⭐⭐⭐

**这一节讲的是我实际做过的事：手动读 trace，发现学习行为异常。** 这在面试里非常值钱，因为绝大多数候选人只会说「要防 reward hacking」，说不出「我是怎么看见它的」。

### 10.1 四种我实际观察到的模式

| 模式 | 症状（trace 里长什么样） | 自动检测信号 | 数据侧的修法 |
|---|---|---|---|
| **格式化推理** | 输出有推理的**外形**（"Let me verify…"、"Wait, reconsider…"），但中间步骤和最终答案**没有因果关系**——删掉推理答案不变 | ① **CoT ablation**：截断推理强制立即作答，准确率**不掉** → 推理没做功；② 组内 CoT 的 n-gram 重复率飙升；③ 长度涨但准确率平 | 检查是不是**题太简单**（答案能直接背出来，推理只是仪式）→ 提高难度带；检查 reward 里有没有变相奖励长度 |
| **失控推理** | 反复自我怀疑、循环重述、撞 `max_tokens` 被截断 | truncation 率按题族分组统计；长度分布出现 p99 贴顶的尖峰 | ① 定位诱发它的题族（常见是「讨论所有情况」「是否存在」这类开放题）；② **不要对截断样本一刀切给 0**——那是噪声惩罚，用 DAPO 式的软长度惩罚（缓冲区内线性衰减） |
| **错误推理侥幸答对** | 中间步骤明显错，最终答案却对 | ① 抽样让 judge **只判过程**、不看答案，与结果 reward 求不一致率；② 答案空间小的题（是/否、小整数）**天然高危** | 这是**过程奖励 vs 结果奖励**的经典场景；数据侧的修法是给小答案空间的题**降权或改造**（要求给出中间量），而不是全靠 reward 补救 |
| **答案泄漏 / verifier hack** | 输出里枚举多个候选答案；或直接复述题面里的数字；或代码题里 hard-code 测试用例 | ① §9.2 的严格位置匹配就能挡掉枚举；② §8.4 的 no-CoT 探针抓泄漏；③ 代码题：隐藏测试 vs 公开测试的准确率**落差** | 回到 §5.3 的 `no_answer_leak` gate 和 §6 的 verifier 设计 |

> ⭐ **过程 vs 结果奖励我有实测数据可引**（[decagon_finetune L5](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/levels/level5_process_reward/)，153 条轨迹的对照）：在一个多步流程任务里，**只看最终结果的 reward 对「合规」与「跳步骤」完全无法区分——两者都是 1.000**；而一旦给工具调用加上效率惩罚，**跳过校验步骤的轨迹反而严格胜出（0.800 vs 0.750）**，因为它少调了一次工具还拿到了同样的结果。这个数字很适合用来说明「结果 reward 的盲区不是理论担忧，是可以构造出来量出来的」。

### 10.2 读 trace 的可操作协议

「手动看 trace」不能是随机翻。我用的是**分层抽样 + 固定节奏**：

| 抽哪些 | 为了找什么 | 每轮条数 |
|---|---|---|
| **reward 最高的 N 条** | reward hacking（最高分往往是钻空子的） | 20 |
| **同一 prompt 组内 reward 方差最大的** | verifier 不稳定 / 题目歧义 | 20 |
| **pass rate 跨 checkpoint 从 ~0 跳到 ~1 的 prompt** | **verifier 假阳性被发现的瞬间**——这是最强的 hack 信号 | 全部（通常很少） |
| **长度 p99 的** | 失控推理 | 20 |
| **新数据源的随机样本** | pipeline bug（解析错误、格式错乱） | 20/源 |
| **下游 eval 上出现回归的题** | 训练数据引入的负面行为 | 全部 |

节奏：**每个训练 run 至少两次**（早期一次抓 pipeline bug，中后期一次抓 hacking），加上每次数据源变更后一次。

**一句高分句**：

> 读 trace 不是「有空看看」，它是这条 pipeline 唯一能发现**我没预料到的失败模式**的手段。所有自动指标都只能检测我已经想到的问题；trace 是唯一的 open-ended 通道。所以我把它做成有固定抽样规则和固定节奏的例行动作，而不是靠直觉抽查。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
