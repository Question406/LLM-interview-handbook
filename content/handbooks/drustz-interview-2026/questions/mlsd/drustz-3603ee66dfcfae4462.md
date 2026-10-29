---
id: drustz-3603ee66dfcfae4462
section: mlsd
order: 216
level: A
title: ml_sys_prep · ML System Design 冲刺（唯一入口）
quick: 作者完整文档 · ml_sys_prep · ML System Design 冲刺（唯一入口）
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/README.md
    type: primary
---
# ml_sys_prep · ML System Design 冲刺（唯一入口）

⏱ 本文件 3 分钟读完 ｜ 面向 2026-07 的 Exa / OpenAI pretraining / Mirendil / Bridgewater / Decagon 等面试

## 🔴 入口：[`NOW.md`](?book=drustz-interview-2026&section=mlsd&question=drustz-2cedb992b9aecc82c2)

只有一屏：**下一场是谁、几点、今天只做什么**。每场面试后立刻更新。
（原来写在这里的「当前最紧」和 `00_study_plan.md` 的两天日历都过期过 ——
静态日历注定过期，所以换成按面试驱动的一屏。）

**评分门槛**：`python mock.py status` —— 40 分 rubric 现在是**机器判的**，
连续两次「≥32/40 且无单项<3 且三个追问都稳」才算 ready。

## 怎么用（只有一条规则）

**打开 [00_study_plan.md](?book=drustz-interview-2026&section=mlsd&question=drustz-34e3ea7e7d01abfa56)，看当天那一节，照做。** 其余 14 个文件已全部编排进日程，不需要自己另外浏览。

本目录 9600+ 行。**通读是错误用法**——日程已经按 ⭐⭐⭐ 挑好了每篇要读的节。

## 这套材料解决什么

不是「记住某个模型」，而是面对陌生题时能稳定做出一组可解释的工程判断：**任务到底是什么、数据从哪里来、标签是否可信、数据不够怎么办、为什么选这个模型、如何评估、怎样以合理成本上线并持续学习。**

> 默认答题主线：**Problem → Metrics → Data → Model/Objectives → Evaluation → Serving → Feedback loop**

**2026-07-29 新增 §15–19 五个 frontier-lab 题型的 case study**（共 3588 行）。
这五题和传统的推荐/搜索 MLSD 不同，是 OpenAI / Anthropic / Reflection 这类实验室的常考题型，
而且**全部命中你在 Reflection 的真实经历**（RL 数据、合成数据、batch inference基础设施），
写作时已把你的经历直接编进对位素材一节。

针对性说明：你现有的 [`../online_resource/question-bank/theory-and-mlsd.md`](?book=drustz-interview-2026&section=collections&question=drustz-10114ff26622b3e07c) 已经覆盖 **架构轴**（serving / RAG / KV cache / 成本架构）。本目录补的是正交的 **数据轴**——也正是你两场面试被问倒的地方（code review 用什么数据+什么 reward；OCR signature 怎么收各种场景数据）。

## 先看 [`INDEX.md`](?book=drustz-interview-2026&section=mlsd&question=drustz-a553df5e0438d81347)

12,000 行里，**16 个核心概念各自散落在 5–18 个文件**。
`INDEX.md` 给每个概念指定唯一的「正本」—— 想学一个概念只读正本，
其他文件出现它只是在自己的语境里用一下。

它同时标出了一个已知问题：**04/05/06/07 四篇 = 全库 32%，
但一手数字密度只有 0.15 条/百行**（21/22/23 是 6.3/4.0/8.7）。
那四篇是早期的散文版，待重写。

## 怎么用这些文件：分两类，别混

| 类别 | 是什么 | 怎么用 |
|---|---|---|
| **必须内化**（能闭卷讲出） | 判断、坑、反直觉结论 | **`python drill.py`** —— 36 道题覆盖 7 个 topic。**不要重读** |
| **查阅**（用到再翻） | 一手数字、公司情报、完整推导、代码 | 需要引用时打开，或面试前扫速记那一节 |

大文件（04–07、14–19、21–22 共约 10000 行）**全部属于「查阅」**。
它们第一次读是为了建立概念；之后每次复习都该是 drill。
**通读第二遍是这套材料里性价比最低的动作。**

## 文件地图

| 文件 | 行数 | 解决的问题 |
|---|---|---|
| [00_study_plan.md](?book=drustz-interview-2026&section=mlsd&question=drustz-34e3ea7e7d01abfa56) | 主线 | **两天冲刺日历**、4 小时急救版、面试前 30 分钟 |
| [01_answer_framework.md](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) | 188 | 45–60 分钟通用答题框架与白板顺序（**唯一建议逐字读完的文件**） |
| [02_data_and_labels.md](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) | 199 | 数据来源、标签合同、泄漏、长尾与数据短缺阶梯 |
| [03_model_training_reward.md](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) | 188 | baseline ladder、模型选择、loss、SFT/preference/RL、reward 设计与防 hacking |
| [04_case_code_review_llm.md](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45) | 955 | 如何训练并上线 code-review LLM |
| [05_case_ocr_signature.md](?book=drustz-interview-2026&section=mlsd&question=drustz-6f0414d424a39e12e5) | 784 | OCR、签名检测/识别/验真及场景数据收集 |
| [06_search_post_training.md](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) | 906 | Exa 类搜索：retriever / reranker / answerer / search agent 的 post-training |
| [07_pretraining_data.md](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) | 1207 | pre-training 数据获取、过滤、去重、配比、污染与治理 |
| [08_evaluation_production.md](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) | 209 | offline→online eval、阈值、成本、部署、监控与反馈闭环 |
| [09_question_bank.md](?book=drustz-interview-2026&section=mlsd&question=drustz-354984fdc7bc9d31a9) | 300+ | 60+ 题库与追问锚点，**§I 是 1p3a 真题实录**（带来源与日期） |
| [10_cheatsheet.md](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde) | 105 | 面试前一页速查 |
| [11_mock_interviews.md](?book=drustz-interview-2026&section=mlsd&question=drustz-9a8db33390986aace4) | 117 | 三套 mock 流程、评分 rubric 和复盘模板 |
| [12_personal_bridge.md](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) | 119 | 把 HCI / wearable / 文本输入 / agentic LLM 经验诚实迁移到 MLSD |
| [13_company_cards.md](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9) | — | 五家公司速记卡（面试前 5 分钟看） |
| [14_case_customer_service_agent.md](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca) | 300+ | AI 客服 agent 的**数据轴**：resolution 标签、多租户冷启动、AOP、reward hacking |
| [15_case_eval_pipeline.md](?book=drustz-interview-2026&section=mlsd&question=drustz-07520390a6b2c475a2) | 740 | **ChatGPT 级评测流水线**：judge 偏差与验证、benchmark 污染、分层报告、PPI sampling |
| [16_case_rl_data_pipeline.md](?book=drustz-interview-2026&section=mlsd&question=drustz-8df61c36cf3291cc69) | 828 | **RL post-training 数据流水线** ⭐ 最对口你的经历：难度筛选、可验证性、reward hacking 检测 |
| [17_case_synthetic_data.md](?book=drustz-interview-2026&section=mlsd&question=drustz-296c269c87350db28f) | 684 | **合成数据生成**：质量闸门、多样性、模型坍塌、什么时候不该合成 |
| [18_case_distributed_inference.md](?book=drustz-interview-2026&section=mlsd&question=drustz-ed4eb9e01c767c533b) | 646 | **分布式推理**：在线 serving vs 离线批量的分叉、抢占恢复、成本模型 |
| [19_case_agent_benchmark.md](?book=drustz-interview-2026&section=mlsd&question=drustz-f2abdd7ba423c258b9) | 690 | **Agent benchmark**：过程 vs 结果、 $\mathrm{pass}^k$ 、环境可复现、污染与漂移 |
| **[20_case_exa_agentic_search.md](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)** | 500+ | 🔴 **Exa 第二轮（systems design）专用**：Exa 全栈一手事实卡、snippet generation / reranking / model alignment 三套完整设计、延迟与算力算术 |
| **[21_swe_agent_data.md](?book=drustz-interview-2026&section=mlsd&question=drustz-2f6e575475ae73e26e)** | 600+ | 🆕 **SWE agent 训练数据**：从 GitHub 爬 → 选仓库 → 挖 PR → 搭环境 → **F2P/P2P 执行验证** → 合成 bug → 去重去污染 → 造 pair。配 [labs/swe_data/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/swe_data/) 可跑代码 |
| **[22_code_review_agent_data.md](?book=drustz-interview-2026&section=mlsd&question=drustz-3b050f56a2ca44e09d)** | 400+ | 🆕 **Code review agent 训练数据**：**没有 oracle** 怎么办 → 从历史制造可验证性（采纳信号 + SZZ）→ 质量把关与**信号calibration** → 正负样本（含「未评论行」陷阱）→ **不对称 reward**。配 [labs/cr_data/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/cr_data/) 可跑代码 |
| **[23_agent_rollout_inference.md](?book=drustz-interview-2026&section=mlsd&question=drustz-d24b05ca7a310a9ccc)** | 速查卡 | 🆕 **Agent rollout 的推理配置与 KV cache**：prefill 是 O( $T^{2}$ )、什么会静默打掉 prefix cache、prompt 布局、cache-aware 路由、按 repo 分组调度。配 `labs/swe_data/rollout_cost.py` |
| [labs/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/) | — | 五个可跑 lab（去重与质量分类 / reward 设计 / 检索负例 / **swe_data** / **cr_data**）+ **[exa_drills/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/exa_drills/) Exa 技术轮冷写题包（5 题，含实考的流式分位数）** |

## 与你现有材料的边界

- **架构轴**（serving、RAG、KV cache、成本）→ [`../online_resource/question-bank/theory-and-mlsd.md`](?book=drustz-interview-2026&section=collections&question=drustz-10114ff26622b3e07c)
- **agent runtime**（tool protocol、durable execution、多智能体）→ [`../agentic_prep/agentic2/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/README.md)
- **ML 理论与手写题**（attention、GRPO、sampling、KV cache 手写）→ [`../online_resource/core-ml.md`](?book=drustz-interview-2026&section=collections&question=drustz-9c5e41490dec58d4d2) 与 [`../online_resource/drills/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/drills/)
- **pretraining data 的实操场** → [`../../cs336/assignment4-data/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/cs336/assignment4-data/)（handout PDF 里就是 07 描述的那条 funnel：Common Crawl → 质量分类器 → dedup → 毒性过滤 → leaderboard。Day 2 若时间充裕，跑一遍比读十遍强）
- **post-training 实操场** → [`../../cs336/assignment5-alignment/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/cs336/assignment5-alignment/)

若题目是 RAG/search：先在这里回答 retrieval / training / eval，再用 agentic2 补权限、工具调用与状态恢复。

## 诚实性约束（重要）

这里的案例是**面试设计方案**，不是伪装成做过的项目。没有亲自做过时，用「我会先…」「我会用实验验证…」，不要说成已经取得过的结果。可用的迁移句式见 [12_personal_bridge.md](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) §3。

## 每次练习必须交付的 8 行

```text
1. User/action: 谁基于预测做什么决定？
2. Unit/label: 一个样本是什么，标签何时可得？
3. Success: 一个主指标 + 两个 guardrail。
4. Data: 来源、split、最大 bias/leakage。
5. Baseline: 最便宜的可行系统。
6. Model/objective: 为什么匹配输出结构与数据规模？
7. Production: p95/QPS/cost budget 与降级路径。
8. Loop: 如何观测错误、获得新标签、决定是否重训？
```



如果这 8 行说不清，继续堆模型名通常不会让答案变好。

## 外部资源 Top 10（只在错题暴露弱点时打开）

各案例文件末尾另有本主题的延伸阅读；下表是跨主题的。

| # | 资料 | 分钟 | 对口 |
|---|---|---|---|
| 1 | [Hello Interview · ML System Design in a Hurry](https://www.hellointerview.com/learn/ml-system-design/in-a-hurry/delivery) | 60 | 2026 最新交付框架，免费部分够用 |
| 2 | [alirezadir · Machine-Learning-Interviews（9-step MLSD）](https://github.com/alirezadir/Machine-Learning-Interviews) | 40 | 数据采集/标注章节最全 |
| 3 | **本地** [`cs336/assignment4-data`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/cs336/assignment4-data/) handout | 90 | pretraining data 最快上手路径 |
| 4 | [FineWeb 技术报告](https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1) | 60 | 07 那条 funnel 的「标准答案」，含全局 vs 分片去重的反直觉结论 |
| 5 | [DCLM / DataComp-LM](https://arxiv.org/abs/2406.11794) | 40 | model-based filtering 是最大杠杆 |
| 6 | [SWE-RL](https://arxiv.org/abs/2502.18449) | 25 | 从 PR 历史挖可验证信号，直接对口 04 |
| 7 | [Rubrics as Rewards](https://openreview.net/forum?id=c1bTcrDmt4) | 20 | 主观任务怎么做成可 RL 的 reward，对口 04 §7 |
| 8 | [Search-R1](https://arxiv.org/abs/2503.09516) | 20 | 多轮 search+reason RL，retrieved-token masking |
| 9 | [DeepRetrieval](https://arxiv.org/abs/2503.00223) | 20 | 用检索指标直接当 reward 训 query rewriter |
| 10 | [Exa 官方研究博客](https://exa.ai/research) | 40 | Exa 面试前必读，见 [13 · 公司卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9) |

## drill.py

```python
"""闭卷 drill：**把「读过」换成「讲得出」**。

    python drill.py --topic timeseries -n 8      # 抽 8 题，闭卷答
    python drill.py --topic all -n 12 --hard     # 只抽你最近答错的
    python drill.py --list                       # 有哪些 topic
    python drill.py --weak                       # 我最弱的是什么

为什么要这个：现在的瓶颈**不是材料不够，是闭卷提取不出来**。
22 个 md 文件一万多行，通读一遍要一整天，读完还是讲不出。
这个 drill 把每个文件的**必须能脱口而出的判断**抽成题，
答完自评（0=想不起来 / 1=方向对细节忘 / 2=能完整讲出），只重练答不好的。

**每题都有一个「必须提到的锚点」列表** —— 自评时对着它勾，
勾不满就是 0 或 1，不许自己放水。
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

STATE = Path(__file__).parent / ".drill_state.json"


def Q(topic, q, anchors, src, tier=1):
    return {"topic": topic, "q": q, "anchors": anchors, "src": src, "tier": tier}


BANK = [
    # ───────────────────────────────── 时序 / demand forecasting（P0 Bridgewater）
    Q(
        "timeseries",
        "时序数据上随机切分为什么是泄漏？危害有多大？",
        [
            "相邻样本特征几乎相同",
            "**危害 = f(近重复率 × 模型容量)，不是常数**",
            "线性+无重复约 0.05 点；kNN k=1 + 40% 重复 5.6 点",
            "所以不能只喊口号，要说清模型是什么、重复率多少",
        ],
        "07_timeseries_crashcourse / ts_lab demo1",
        3,
    ),
    Q(
        "timeseries",
        "有没有什么统计检验能自动发现 `shift(-1)` 方向写反了？",
        [
            "**没有**",
            "shift(1) 和 shift(-1) 与目标的相关性完全相同（自相关对称）",
            "只能逐个特征问「预测那一刻这个值算得出来吗」",
            "这恰好也是 AI 做不到的 —— 它不知道预测时刻是什么时候",
        ],
        "ts_lab demo6",
        3,
    ),
    Q(
        "timeseries",
        "MAPE 有哪几个坑？需求预测该用什么？",
        [
            "y=0 除零，inf 常被 dropna 静默丢掉",
            "过预测惩罚无上界、欠预测最多 100% → 偏爱猜小",
            "**WAPE**：Σ|y−ŷ|/Σy，零值安全、业务可解释",
            "还要报**两个聚合口径**：按 SKU 等权 vs 按销量加权，可能选出不同冠军",
        ],
        "03_demand_forecasting / ts_lab demo4",
        3,
    ),
    Q(
        "timeseries",
        "为什么 seasonal naive 是必须报的 baseline？",
        [
            "零售周季节性强，y[t-7] 极难打败",
            "M5（Walmart）冠军是 LightGBM + lag 特征，不是深度学习",
            "大量参赛模型打不过 snaive",
            "repo 里没有 baseline = blocker 级 finding",
        ],
        "07_timeseries_crashcourse §2.4",
        3,
    ),
    Q(
        "timeseries",
        "`groupby('sku').shift(1)` 什么时候是错的？怎么一行验证？",
        [
            "DataFrame 没按时间排序时，shift 按**行序**移位不是按时间",
            "不报错、列里有值 —— 静默",
            "`df.groupby('sku').date.is_monotonic_increasing.all()`",
            "rolling / diff / cumsum 同理",
        ],
        "ts_lab demo7",
        3,
    ),
    Q(
        "timeseries",
        "残差自相关对置信区间有什么影响？",
        [
            "样本不 iid → 有效样本量远小于 n",
            "AR(1)：n_eff = n(1−ρ)/(1+ρ)",
            "ρ=0.62、n=800 → n_eff≈185，标准误要乘约 2",
            "按 iid 算的显著性不可信",
        ],
        "ts_lab demo2",
        2,
    ),
    Q(
        "timeseries",
        "多步预测 direct vs recursive 的区别？它和特征可得性什么关系？",
        [
            "recursive：1 步模型迭代，**误差累积**",
            "direct：每个视界 h 一个模型",
            "**视界 h 决定哪些 lag 可用** —— 预测 14 天后拿不到 t−1 的实际值",
            "所以 README 说 14 天视界但特征里有 lag_1 = 矛盾",
        ],
        "ts_lab demo5",
        2,
    ),
    Q(
        "timeseries",
        "间歇性需求（大量 0）怎么处理？评估要注意什么？",
        [
            "常规回归预测出无意义的小数",
            "Croston：分别建模需求间隔和非零需求量",
            "**恒为 0 的 WAPE = 100%**，这是天花板参照",
            "业务真正要的是分位数（服务水平）不是均值",
        ],
        "ts_lab demo8",
        2,
    ),
    # ───────────────────────────────── code review（P0）
    Q(
        "review",
        "官方评分三元组是什么？哪一条最少人准备？",
        [
            "directing machines / evaluating their output / **knowing when to go deeper**",
            "第三条：考的不是深度，是**深度的分配**",
            "正确示范 = 主动说「这条我不深入，因为我量过影响是 0」",
        ],
        "bridgewater 02_code_review §零",
        3,
    ),
    Q(
        "review",
        "「AI 找到的东西」在面试里算不算分？分界线在哪？",
        [
            "**AI 找到不减分；未经验证地复述才减分**",
            "零分：「AI 说这里有泄漏」",
            "满分：「AI 说有泄漏，我改成按时间切重跑，WAPE 掉 X 点，排第一」",
            "验证并排序 AI 的发现本身就是得分项",
        ],
        "bridgewater 05_practice §① / 02 §六",
        3,
    ),
    Q(
        "review",
        "拿到陌生 repo 的头三件事？为什么第一件最少人做？",
        [
            "① **先跑一遍**（README 的数字复现得出来吗）",
            "② git log 看演化",
            "③ pytest 看测试绿不绿、**断言的是什么**",
            "跑一遍能抓到独立 blocker，而大多数人直接开始读代码",
        ],
        "bridgewater README",
        3,
    ),
    Q(
        "review",
        "「测试全绿」为什么可能比没有测试更危险？",
        [
            "测试可能把 bug 锁成契约（注释里写着「包含未来三天」）",
            "改对了反而会红 → 下一个人会把修改改回去",
            "AI 看到有测试就打勾，不会问断言在断言什么",
        ],
        "bridgewater ANSWER_KEY S5",
        2,
    ),
    Q(
        "review",
        "AI 通常漏掉的类别有哪些？举三个。",
        [
            "领域正确性（不知道这是时序）",
            "静默失败（不抛异常只是悄悄错）",
            "**缺失的东西**（AI 只评论看得见的代码）",
            "README 与代码的偏离（跨文件核对）",
            "同一逻辑多处实现且不一致",
        ],
        "bridgewater 02 §一",
        2,
    ),
    # ───────────────────────────────── SWE agent 数据
    Q(
        "swe_data",
        "SWE-bench 的三步验证是什么？为什么 P2P 不能省？",
        [
            "① parent 上全过（环境对）② 打 test_patch 新测试必须 FAIL（bug 真存在）"
            "③ 再打 solution_patch 必须全过",
            "F2P = ②失败③通过；P2P = ②通过③通过",
            "**只用 F2P，模型可以把不相关代码删光**；P2P 是防回归约束",
        ],
        "21_swe_agent_data §5",
        3,
    ),
    Q(
        "swe_data",
        "四条造 SWE 训练数据的路线，各自的验证方式和规模？",
        [
            "A 挖 PR：执行 F2P/P2P，~200/仓库（SWE-bench 12 仓库 2294 条）",
            "B 合成 bug（**环境优先**）：用已有测试，~381/仓库（SWE-smith 128 仓库 5 万条 $1,360）",
            "C commit 回译：自动生成测试（R2E-Gym）",
            "D 不执行：patch 相似度当 reward（SWE-RL 1100 万 PR）",
            "实践：B 训练 + A 评测",
        ],
        "21 §1",
        3,
    ),
    Q(
        "swe_data",
        "SWE 数据 pipeline 的产出率大概是多少？损耗在哪？",
        [
            "SWE-rebench V2：58 万候选 → 3.2 万可执行，**约 5.5%**",
            "几乎所有损耗在**环境搭建和执行**两步",
            "别用 math 的直觉估算",
        ],
        "21 §9",
        2,
    ),
    Q(
        "swe_data",
        "选仓库那一刀为什么性价比最高？给个数。",
        [
            "任务产出极度长尾",
            "SWE-rebench V2：**20% 的仓库覆盖 80% 的任务**",
            "需要搭环境的仓库数降到 1/5",
            "先给 yield_score 高的搭环境",
        ],
        "21 §2",
        2,
    ),
    Q(
        "swe_data",
        "gold patch 里混进测试文件会怎样？「是不是测试文件」这个判断有什么坑？",
        [
            "**答案泄漏** —— 模型训练时直接看到断言",
            "论文用无锚定子串 `(?i)(test(?:ing|s)?|e2e)` → `contest.py` 被误判",
            "后果：那些改动进 test_patch，solution patch 变空，**实例被静默丢弃**",
            "加路径段边界",
        ],
        "21 §3 / labs/swe_data",
        2,
    ),
    # ───────────────────────────────── code review 数据
    Q(
        "cr_data",
        "code review 数据最核心的难点是什么？业界的答案？",
        [
            "**没有 oracle** —— 「这条评论有用吗」无法执行验证",
            "答案：从历史**制造可验证性**",
            "ByteDance（Outdated Rate）和 Atlassian（CRR）**独立收敛到同一个信号**：评论指向的代码后来被改了吗",
            "人类基线 35–46%；两家做到 26.7% / 40–45%",
        ],
        "22 §0–1",
        3,
    ),
    Q(
        "cr_data",
        "采纳信号有什么偏？最危险的是哪一类？",
        [
            "实测 precision 约 70%，**30% 假阳性**",
            "机制：评论恰好落在因**别的原因**被改的行上",
            "**最危险：事实错误的评论被盖章成「有用」** → 教模型编造听起来专业的错误结论",
            "假阴性：说得对但当时没被采纳的（后来变成真 bug）",
        ],
        "22 §4",
        3,
    ),
    Q(
        "cr_data",
        "为什么「没有评论的代码行」不能当负样本？",
        [
            "没人评论只说明**没人看**",
            "数量上会淹没正例（真实仓库几千比一）",
            "**里面有真问题** —— lab 里那行三周后被 fix 了，它本该是正样本",
            "这是 positive-unlabeled，不是二分类",
        ],
        "22 §5",
        3,
    ),
    Q(
        "cr_data",
        "code review 的 reward 和 math/SWE 有什么根本不同？",
        [
            "math/SWE 的 reward **对称**（找不到只是没得分）",
            "CR **不对称**：误报主动消耗 reviewer 信任",
            "只有 30% 的 review 会被立刻看；机器人说废话会被整体屏蔽",
            "→ 精度优先，硬闸门在前，误报单独重罚",
        ],
        "22 §6",
        3,
    ),
    Q(
        "cr_data",
        "为什么不能按 F1 调 review filter 的阈值？",
        [
            "**F1 不知道一次误报值多少钱**",
            "实测：F1 最优阈值恒为 0.675，产品最优随误报代价从 0.075 移到 0.825",
            "该问的是「一条误报让用户少看了多少条」，从线上量",
            "量出来之后阈值是**算出来的**不是调出来的",
        ],
        "22 §6 / reward.py",
        3,
    ),
    Q(
        "cr_data",
        "BitsAI-CR 关于 judge 输出格式的反直觉发现？",
        [
            "Conclusion-First（先结论后理由）**77.09% / 1.7s**",
            "Reasoning-First（先推理后结论）65.80% / **31.0s**",
            "先给结论精度高 11 点、快 18 倍",
            "解释：先推理会让模型被自己的推理链带跑，为不成立的结论找补",
        ],
        "22 §6",
        2,
    ),
    Q(
        "cr_data",
        "SZZ 是什么？它的边界在哪？",
        [
            "bug-fix commit → git blame 被修的行 → 找到引入 bug 的 commit",
            "产出**唯一一类真正可验证的正样本**（由后来的修复证明）",
            "ghost commit 17.47%、跨文件 7.20%、**>40% 光靠 blame 解决不了**",
            "高精度低召回 —— 是种子不是全集",
        ],
        "22 §3",
        2,
    ),
    # ───────────────────────────────── 通用方法论（跨场景高频）
    Q(
        "method",
        "任何「数据改进」的收益，你怎么确认它是真的？",
        [
            "必须有**样本数/预算对齐的对照组**",
            "我自己的例子：hard negative 报 +0.109，加对照组后三分之二只是样本翻倍，净增益 2 胜 2 负 → **划掉**",
            "配对比较 + bootstrap CI，不看两个均值各自的 CI",
            "跨折/跨切片的一致性，不只看均值",
        ],
        "decagon L7 / 15",
        3,
    ),
    Q(
        "method",
        "「评测器和被评物同源」是什么问题？举个你自己的例子。",
        [
            "用 BM25 造标签又用 BM25 评测 → 检索改进被系统性抹掉",
            "词汇重叠说 46.2%（≈随机），换语义相似度是 **62.5%（p=0.014）**",
            "尺子选错了，信号一直在",
            "另一个例子：ROUGE 预测医生 unsafe 标注 AUROC **0.569**（掷硬币）vs grader 0.844",
        ],
        "decagon L3 / anthropic take-home",
        3,
    ),
    Q(
        "method",
        "什么时候该上 RL？什么时候不该？",
        [
            "verifier 可靠 **且基线成功率 > 0**",
            "基线为 0 时 vanilla RL 完全没信号（RMSD 那篇原话）→ 先 SFT / 自蒸馏",
            "开训前扔掉 pass@k ∈ {0,1} 的 prompt —— GRPO 组内优势全 0，白烧算力",
            "reward 噪声会被 RL 放大，verifier 本身是难题时先 rejection sampling",
        ],
        "21 §8 / 16",
        3,
    ),
    Q(
        "method",
        "LLM judge 怎么才算可信？",
        [
            "**必须拿人工标注校准**，报 AUROC/κ + bootstrap CI",
            "阈值在校准集选、验证集报",
            "分类别看一致率 —— 均值会盖住「只在某一类上打架」",
            "在标注员自己分歧的子集上单独报（那里上限本来就不是 100%）",
        ],
        "15 / onsite projectA",
        3,
    ),
    Q(
        "method",
        "自动指标涨了但质量没涨，怎么发现？",
        [
            "**优化目标之外必须有一个不参与优化的口径**",
            "我的实测：grader 涨 +0.214 但人工口径 CI 跨 0；涨最少的 +0.128 才真改善 +0.192",
            "hack 是删条目 —— grader 结构上看不见（线上没有 gold）",
            "**校准错误权重救不了特征空间之外的作弊**，只能靠硬约束",
        ],
        "onsite projectA",
        3,
    ),
    # ───────────────────────────────── agent rollout 的推理配置
    Q(
        "inference",
        "为什么 agent rollout 的 prefill 是 O(T²)？完美缓存能省多少？",
        [
            "每一轮都要**重发整段历史**",
            "Σ_t (base + t·per_turn) = O(T²)；缓存后只算新增 = O(T)",
            "40 轮的 SWE 任务实测差 **23 倍**",
            "5000 任务 × 8 样本：1353 GPU-小时 → 59 GPU-小时",
        ],
        "23_agent_rollout_inference §1",
        3,
    ),
    Q(
        "inference",
        "哪些操作会静默打掉 prefix cache？按隐蔽程度排。",
        [
            "**system prompt 里的时间戳/随机 ID** —— 每轮全失效，等于没开缓存",
            "工具 schema 序列化顺序不稳定",
            "**context compaction 重写了前缀**",
            "检索内容插在前面而不是后面",
            "**多副本没有 cache-aware 路由**（命中率掉到 1/N）",
            "纪律：**agent loop 必须 append-only**，前缀只增不改",
        ],
        "23 §2",
        3,
    ),
    Q(
        "inference",
        "「开了 prefix caching」和「用上了 prefix caching」差在哪？给个数。",
        [
            "前缀匹配是**逐 token 的前缀**，不是子串",
            "8 副本 round-robin 时命中率 ≈ 1/8 → 实测仍是 20.7× 成本",
            "SGLang RadixAttention + sticky：命中率 **18% → 71%**",
            "llm-d 实测 cache-aware 路由 **TTFT 快 57×、吞吐 2×**",
        ],
        "23 §1/§4",
        3,
    ),
    Q(
        "inference",
        "prompt 该怎么排布？原则是什么？",
        [
            "**从稳定到易变，严格排序**",
            "system + 工具 schema（固定顺序）→ 仓库上下文 → 任务描述 → 对话历史（只追加）→ 易变内容",
            "时间戳、剩余预算这类**一律放最后**",
            "Anthropic 最多 4 个 cache_control 断点，打在这几个边界上",
        ],
        "23 §3/§5",
        3,
    ),
    Q(
        "inference",
        "离线 rollout 生成和在线 serving 的推理配置有什么不同？",
        [
            "目标：p99 延迟 → **吞吐/$**",
            "并发拉满，让 KV cache 占满显存",
            "大 batch + chunked prefill",
            "抢占可接受（有缓存重算便宜）",
            "投机解码通常**关掉**（吞吐场景收益小还吃显存）",
        ],
        "23 §4",
        2,
    ),
    Q(
        "inference",
        "三条能直接省钱的调度决策？哪条最被忽略？",
        [
            "**① 按仓库分组调度** ← 最被忽略。同 repo 40 个任务共享 6k 上下文："
            "打散 240k vs 分组 6k",
            "② n 样本用引擎的 `n` 参数 —— **但只值 15%**，样本第一轮就分叉了",
            "③ compaction 尽量晚尽量少（40 轮里 compact 三次 = 2.7× 成本）；"
            "替代方案是只截断工具返回，别重写整段历史",
        ],
        "23 §6",
        3,
    ),
    Q(
        "inference",
        "Anthropic prompt caching 的关键参数？TTL 对 rollout 有什么含义？",
        [
            "显式 `cache_control: ephemeral`，最多 **4 个断点**",
            "写 **1.25×**（5min）/ 2.0×（1h），读 **0.10×**（省 90%）",
            "**TTL 默认 5 分钟**（2026 年从 60 分钟改的），**命中会重置 TTL**",
            "→ 同一个 repo 的任务**必须连着发**，间隔超过 5 分钟仓库上下文缓存就没了",
        ],
        "23 §5",
        2,
    ),
    # ───────────────────────────────── 非 ML 系统设计（Bridgewater 第 2 轮）
    Q(
        "sysdesign",
        "greenfield 系统设计的前 10 分钟该干什么？",
        [
            "**只问不画**",
            "官方 prep 第一条就是 ask clarifying questions",
            "问：谁用、量级、读写比、一致性要求、失败了会怎样、预算",
            "把需求澄清算进考核 —— 「from requirements discussion」是原话",
        ],
        "bridgewater 06_rounds_2_3",
        3,
    ),
    Q(
        "sysdesign",
        "被问「为什么不用 X」时的标准答法？",
        [
            "「X 在 ___ 情况下更好；我选 Y 是因为 ___ 这个约束",
            "如果 ___ 变了，我会换成 X」",
            "**给出切换条件**，而不是辩护",
        ],
        "bridgewater 06",
        3,
    ),
    Q(
        "sysdesign",
        "一个写多读少、要求强一致的系统，先在哪里坏掉？",
        [
            "单点写入的吞吐上限",
            "跨分片事务",
            "热点 key",
            "重试导致的重复写（幂等键）",
            "扩容时的再平衡",
        ],
        "自答",
        1,
    ),
    # —— Michael Rickert 那轮（2026-08-03）专项 ——
    Q(
        "sysdesign",
        "valid time 和 transaction time 分别是什么？「as of 2024-03-15」问的是哪一个？",
        [
            "**valid time** = 这件事在现实中何时为真（财报说的是 Q1 的业绩）",
            "**transaction time** = 我们何时知道它（5/15 发布、5/15 摄入）",
            "⭐ **as-of 问的是 transaction time**",
            "一份 3/1 发生、3/20 才发布的数据，在 3/15 的视角里**必须不可见**",
            "用 valid time 过滤 = foreknowledge bias，这就是那个 bug",
        ],
        "bridgewater 08 题1 / asof_store.py demo3",
        3,
    ),
    Q(
        "sysdesign",
        "as-of 存储的查询接口，最重要的一个设计决策是什么？",
        [
            "**as_of 是必填参数，没有默认值**，也不提供「查最新」的便捷重载",
            "只要存在无 as_of 的重载，就一定有人在回测里调它",
            "而且**不报错** —— 只让离线指标偷偷变好",
            "想查最新就显式传 now()，那一行在 code review 里是可见的",
            "（Scala 的说法：让非法状态无法表示）",
        ],
        "bridgewater 08 题1",
        3,
    ),
    Q(
        "sysdesign",
        "存储层的 as-of 语义做对了，系统还可能从哪里泄漏未来？",
        [
            "**缓存键漏了 as_of**（最常见，asof_store demo4 有可跑复现）",
            "外部搜索 API 不支持 as-of 过滤，返回的是今天的索引",
            "实体解析/映射表本身没有 tx 时间（「公司改名了」）",
            "网页被就地更新 —— 要存内容快照不是 URL",
            "模型权重的训练截止日晚于 as_of ← **无法根除，只能测量**",
            "⭐ 所以论文里是「检测 foreknowledge bias 的 pipeline」不是「防止」",
        ],
        "bridgewater 08 题1 / asof_store.py demo4",
        3,
    ),
    Q(
        "sysdesign",
        "怎么**检测**（而不是防止）信息泄漏？",
        [
            "三个对照：全知上界 / 被测系统 / 无信息基线。被测应显著低于上界",
            "⭐ **安慰剂测试**：把 as_of 往前推，准确率应该单调下降",
            "不降 = 要么检索没起作用（在靠先验），要么泄漏到 as_of 形同虚设",
            "漂亮之处：**不需要找出泄漏在哪**，只测总量",
            "结论：审计不完的不变量就持续测量它 —— 进 CI，不是一次性验证",
        ],
        "bridgewater 08 / asof_store.py demo6",
        3,
    ),
    Q(
        "sysdesign",
        "M/M/1：利用率 0.8 / 0.9 / 0.95 时排队时间各是服务时间的几倍？",
        [
            "W_q = S × ρ/(1−ρ)",
            "ρ=0.5 → 1×",
            "**ρ=0.8 → 4×**",
            "**ρ=0.9 → 9×**",
            "**ρ=0.95 → 19×**",
            "论据：0.8→0.95 只多榨 19% 容量，延迟涨 4 倍 → 不规划到 80% 以上",
            "降排队的三招（不是加机器）：缩短 S、分离快慢队列、限流降载",
        ],
        "bridgewater design_calc.py ②",
        3,
    ),
    Q(
        "sysdesign",
        "fan-out 到 N 路，每路 p99=1%，至少一路慢的概率？三个对策？",
        [
            "1 − (1−p)^N。N=10 → **10%**；N=20 → 18%；N=100 → **63%**",
            "⭐ fan-out 够宽时，尾延迟不是概率问题是**必然事件**",
            "① deadline + 部分结果，**并把实际参与数 M_actual 写进输出**",
            "② hedged request（等到 p95 再发一份取先到），尾部多 ~5% 负载",
            "③ 先问：M 是怎么定的？做过消融吗？宽度本身可能就是浪费",
        ],
        "bridgewater design_calc.py ④ / 08 题2",
        3,
    ),
    Q(
        "sysdesign",
        "编排 M 个跑几分钟、会失败的 agent，为什么必须持久化「一次运行」？",
        [
            "任务跑几分钟、要花钱 —— 进程挂了重跑全部不可接受",
            "Run / Task[M] / SupervisorTask 三级实体，Task 独立重试独立超时",
            "记下全部 tool_calls → 可回放「为什么这个 agent 给了这个答案」",
            "幂等键 = hash(run_id, agent_idx, attempt) 带给外部 API，重试不重复扣费",
            "重试要分错误类型：429/503 退避重试；4xx 立刻失败；OOM 别原样重试",
        ],
        "bridgewater 08 题2",
        2,
    ),
    Q(
        "sysdesign",
        "「为什么不用 Kafka / Temporal？」怎么答？",
        [
            "默认**用现成的**；自己写的门槛是「现成的表达不了我要的语义」",
            "Kafka 对：多消费者、要重放、上百 MB/s。这里单写者、每天几十万条",
            "→ Postgres `SELECT … FOR UPDATE SKIP LOCKED` 当队列，两百行、零新运维面",
            "⭐ **给切换条件**：出现第三个独立消费者、或超过单库写入能力时换",
            "如果自己写：只写调度不写存储，状态机落 Postgres",
        ],
        "bridgewater 08 题2 §要不要自己写",
        3,
    ),
    Q(
        "sysdesign",
        "什么样的设计决策应该慎重，什么样的应该快？",
        [
            "**不可逆的慎重，可逆的快**",
            "快照密度、缓存层、索引 —— 派生数据，随时可重建 → 可逆 → 先不做",
            "数据模型、时间语义、API 契约 → 不可逆 → 前期想清楚",
            "推论：**复杂度应该是被证据要求的，不是预先设计的**",
            "「我先上最小版本，等 ___ 指标超过 ___ 再加回来」",
        ],
        "bridgewater 08 / asof_store.py demo5",
        3,
    ),
    # ───────────────────────────────── 检索 / Exa
    Q(
        "search",
        "给 agent 用的 reranker 和给人用的有什么不同？",
        [
            "agent 把 5–10 条**全部**读进 context → 位置折扣基本不适用",
            "应优化 **set-level 覆盖 + 去冗余**，不是 pointwise nDCG",
            "失败代价是 agent 多搜一轮（延迟×N 成本×N）",
            "没有 click；query 分布是 agent 生成的",
        ],
        "20 §4.1",
        2,
    ),
    Q(
        "search",
        "`FLOPs ≈ 2 × 参数量 × token 数` —— 用它算一个 reranker 能重排多少候选。",
        [
            "100M 参数 × 512 token × N，预算 30ms，H100 有效 300 TFLOP/s",
            "→ **N ≈ 90**",
            "候选数是算出来的不是拍的；1B cross-encoder 直接出局",
            "QPS 500 × 30ms = 15 GPU-秒/秒 → 25–30 张卡",
        ],
        "20 §4.3",
        3,
    ),
    Q(
        "search",
        "hard negative mining 最大的坑？",
        [
            "top-k 里混着**未标注的相关文档**，当负例会伤召回",
            "和 Exa 拒绝 MS MARCO 的第一条理由（稀疏标注造假负例）是同一个问题",
            "解法：多正例 / soft label / 只把语义相似度低于阈值的当负例",
            "**而且要有样本数对齐的对照组**",
        ],
        "06 §六 / decagon L7",
        3,
    ),
]

TOPICS = sorted({q["topic"] for q in BANK})


def _load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def _save(d):
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2))


def pick(topic, n, hard, rng):
    st = _load()
    pool = [q for q in BANK if topic in ("all", q["topic"])]
    if hard:
        pool = [q for q in pool if st.get(q["q"], {}).get("last", 0) < 2] or pool

    # 优先级：没练过的 > 上次分低的 > tier 高的
    def key(q):
        r = st.get(q["q"], {})
        return (r.get("n", 0), r.get("last", -1), -q["tier"], rng.random())

    return sorted(pool, key=key)[:n]


def run(a):
    rng = random.Random(a.seed)
    qs = pick(a.topic, a.n, a.hard, rng)
    if not qs:
        sys.exit(f"没有题。可选 topic：{', '.join(TOPICS)}")
    st = _load()
    print(f"\n闭卷 {len(qs)} 题 · topic={a.topic} · **先出声答完再回车看锚点**\n")
    scores = []
    for i, q in enumerate(qs, 1):
        print(f"── {i}/{len(qs)} [{q['topic']}] {'⭐' * q['tier']}")
        print(f"   {q['q']}")
        input("   （出声答完按回车）")
        print("   必须提到的锚点：")
        for an in q["anchors"]:
            print(f"     · {an}")
        print(f"   出处：{q['src']}")
        while True:
            s = input("   自评 [0=想不起来 1=方向对细节忘 2=完整讲出] = ").strip()
            if s in "012" and s:
                break
        s = int(s)
        scores.append(s)
        r = st.setdefault(q["q"], {"n": 0, "hist": []})
        r["n"] += 1
        r["last"] = s
        r["hist"].append(s)
        r["topic"] = q["topic"]
        print()
    st["_meta"] = {"last_run": datetime.now().isoformat(timespec="seconds")}
    _save(st)
    avg = sum(scores) / len(scores)
    print(f"── 本轮 {sum(scores)}/{2 * len(scores)}（均分 {avg:.2f}/2）")
    n0 = scores.count(0)
    if n0:
        print(
            f"   有 {n0} 题完全想不起来 —— **这些明天再练一遍**："
            f"  python drill.py --topic {a.topic} --hard"
        )
    elif avg >= 1.7:
        print("   这个 topic 基本稳了。换一个。")


def weak(a):
    st = _load()
    by = defaultdict(list)
    for k, v in st.items():
        if k.startswith("_"):
            continue
        by[v.get("topic", "?")].append(v.get("last", 0))
    if not by:
        sys.exit("还没练过。先跑：python drill.py --topic timeseries -n 6")
    print("\n各 topic 掌握度（最近一次自评均分，满分 2）：")
    rows = sorted(
        ((t, sum(v) / len(v), len(v)) for t, v in by.items()), key=lambda x: x[1]
    )
    for t, avg, n in rows:
        bar = "█" * int(avg * 10) + "░" * (20 - int(avg * 10))
        print(f"  {t:<12} {bar} {avg:.2f}  ({n} 题练过)")
    covered = sum(len(v) for v in by.values())
    print(f"\n  覆盖 {covered}/{len(BANK)} 题")
    print(f"  最该练：**{rows[0][0]}** → python drill.py --topic {rows[0][0]} --hard")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    ap.add_argument("-n", type=int, default=8)
    ap.add_argument("--hard", action="store_true", help="只抽上次没答满分的")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--weak", action="store_true")
    a = ap.parse_args()
    if a.list:
        c = Counter(q["topic"] for q in BANK)
        print(f"共 {len(BANK)} 题：")
        for t in TOPICS:
            n3 = sum(1 for q in BANK if q["topic"] == t and q["tier"] == 3)
            print(f"  {t:<12} {c[t]:>2} 题（⭐⭐⭐ {n3} 题）")
        return
    if a.weak:
        return weak(a)
    run(a)


if __name__ == "__main__":
    main()
```




## mock.py

```python
"""Mock 评分器：把 40 分 rubric 变成**机器判的门槛**，不是散文。

    python mock.py score --kind review      # 跑一次评分，存历史
    python mock.py status                   # 我现在 ready 了吗
    python mock.py followups --kind review   # 随机抽 3 个追问（答完再评分）
    python mock.py log                       # 历史记录

为什么要这个：`11_mock_interviews.md` 里那张 40 分表一直是散文，
所以从来没成为**门槛** —— 自己判会放水，而且没有历史可比。

过关判据（四条同时满足，且**连续两次**）：
    ① 总分 ≥ 32/40
    ② 无单项 < 3
    ③ 三个随机追问都没卡住
    ④ 在时限内讲完
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(__file__).parent / ".mock_log.jsonl"

# ── 8 个维度 × 5 分 = 40（沿用 11_mock_interviews 的口径）
DIMS = {
    "framing": "先问清楚：澄清问题、定义成功、说明假设",
    "metrics": "指标选得对，且说清为什么不是别的",
    "data": "数据来源 / 标签可信度 / 泄漏 / split",
    "baseline": "有 baseline 阶梯，最蠢的那级也报了",
    "depth": "至少一处挖到「什么时候会咬人」+ 怎么验证",
    "priority": "分级清楚；**主动降级过一条**（含说明理由）",
    "honesty": "主动说边界；不确定处标明；不把设计说成经历",
    "delivery": "结论先行、控时、被打断能接回来",
}

KINDS = {
    "review": "陌生 repo code review（25 min）",
    "design": "ML system design（45 min）",
    "sysdesign": "非 ML 系统设计（45 min）",
    "deepdive": "项目深挖（20 min）",
    "presentation": "work trial presentation（40 min 讲 + 20 min Q&A）",
}

FOLLOWUPS = {
    "review": [
        "你说这里有泄漏 —— **影响有多大？**给个数。",
        "这条你标成 blocker，为什么不是 should fix？",
        "AI 报了这条你没采纳，为什么？",
        "如果只能改一处，你改哪个？",
        "你怎么验证你的判断是对的？现在就能验证吗？",
        "这段代码我们是故意这么写的，你怎么看？",
        "假设作者说没时间重构，你的建议会变吗？",
        "你漏了 X（面试官现场指出）—— 为什么没看到？",
    ],
    "design": [
        "为什么不用更简单的方案？",
        "数据从哪来？标签什么时候可得？",
        "这个指标被 game 了会怎样？",
        "规模乘以 100 会先在哪里坏掉？",
        "offline 提升多少你才敢上线？",
        "如果这个假设不成立，你的设计要改多少？",
        "谁会因为这个系统的错误而受损？",
    ],
    "sysdesign": [
        "写请求量再大 10 倍呢？",
        "这里为什么要强一致？最终一致行不行？",
        "某个下游挂了会怎样？",
        "怎么做灰度和回滚？",
        "为什么不用 X（一个更简单/更复杂的方案）？",
        "这个设计最贵的部分是哪里？",
    ],
    "deepdive": [
        "当时有什么替代方案？为什么否掉？",
        "你怎么知道它真的有效？对照是什么？",
        "重来一次你会怎么做？",
        "这个项目里你最大的判断失误是什么？",
        "和同事意见不一致时你怎么处理的？",
        "哪部分是你做的，哪部分是别人做的？",
    ],
    "presentation": [
        "这个数字是怎么算出来的？现在能重跑吗？",
        "你为什么先做这个而不是那个？",
        "哪里没成功？",
        "再给你两周你会做什么？",
        "这个结论在什么条件下不成立？",
    ],
}


def _load():
    if not LOG.exists():
        return []
    return [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()]


def _passed(rec) -> bool:
    return (
        rec["total"] >= 32
        and min(rec["scores"].values()) >= 3
        and rec["followups_ok"] >= 3
        and rec["in_time"]
    )


def cmd_followups(a):
    pool = FOLLOWUPS[a.kind]
    rng = random.Random(a.seed) if a.seed else random
    print(f"【{KINDS[a.kind]}】随机追问 —— 答完再去 score：\n")
    for i, q in enumerate(rng.sample(pool, min(3, len(pool))), 1):
        print(f"  {i}. {q}")
    print("\n⚠️ 卡住 / 答不出 / 开始绕 = 这一条不算过。")


def cmd_score(a):
    print(f"【{KINDS[a.kind]}】逐项打分（0–5，回车默认 3）\n")
    scores = {}
    for k, desc in DIMS.items():
        while True:
            raw = input(f"  {k:<10} {desc}\n    分数 [0-5] = ").strip()
            if raw == "":
                scores[k] = 3
                break
            if raw.isdigit() and 0 <= int(raw) <= 5:
                scores[k] = int(raw)
                break
            print("    请输入 0–5")
    fu = input("\n  三个随机追问，答稳了几个？[0-3] = ").strip()
    it = input("  在时限内讲完了吗？[y/n] = ").strip().lower()
    note = input("  一句话记：这次最差的是什么？= ").strip()

    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "kind": a.kind,
        "scores": scores,
        "total": sum(scores.values()),
        "followups_ok": int(fu or 0),
        "in_time": it.startswith("y"),
        "note": note,
    }
    rec["passed"] = _passed(rec)
    with LOG.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(
        f"\n  总分 {rec['total']}/40   最低单项 {min(scores.values())}"
        f"   追问 {rec['followups_ok']}/3   {'✅ 本次通过' if rec['passed'] else '❌ 本次不过'}"
    )
    if not rec["passed"]:
        why = []
        if rec["total"] < 32:
            why.append(f"总分 {rec['total']} < 32")
        if min(scores.values()) < 3:
            why.append("单项 <3：" + "、".join(k for k, v in scores.items() if v < 3))
        if rec["followups_ok"] < 3:
            why.append(f"追问只稳了 {rec['followups_ok']}/3")
        if not rec["in_time"]:
            why.append("超时")
        print("  差在：" + "；".join(why))
    cmd_status(argparse.Namespace(kind=a.kind))


def cmd_status(a):
    recs = [r for r in _load() if not a.kind or r["kind"] == a.kind]
    print("\n─── ready 状态 ───")
    for kind in [a.kind] if a.kind else KINDS:
        ks = [r for r in _load() if r["kind"] == kind]
        if not ks:
            print(f"  {kind:<14} 未练过")
            continue
        last2 = ks[-2:]
        ready = len(last2) == 2 and all(r["passed"] for r in last2)
        marks = " ".join("✅" if r["passed"] else "❌" for r in ks[-5:])
        print(
            f"  {kind:<14} {marks:<16} "
            f"{'🟢 READY（连续两次通过）' if ready else '🔴 未 ready'}"
        )
    if recs:
        worst = {}
        for r in recs:
            for k, v in r["scores"].items():
                worst.setdefault(k, []).append(v)
        avg = sorted(
            ((k, sum(v) / len(v)) for k, v in worst.items()), key=lambda x: x[1]
        )
        print("\n  最弱的三个维度（历史均分）：")
        for k, v in avg[:3]:
            print(f"    {k:<10} {v:.1f}/5   {DIMS[k]}")


def cmd_log(a):
    for r in _load():
        print(
            f"{r['ts']}  {r['kind']:<13} {r['total']:>2}/40  "
            f"追问{r['followups_ok']}/3  {'✅' if r['passed'] else '❌'}  {r['note']}"
        )


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (
        ("score", cmd_score),
        ("status", cmd_status),
        ("followups", cmd_followups),
        ("log", cmd_log),
    ):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name in ("score", "followups", "status"):
            p.add_argument(
                "--kind",
                choices=list(KINDS),
                default=None if name == "status" else "review",
            )
        if name == "followups":
            p.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
