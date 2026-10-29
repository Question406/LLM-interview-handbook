---
id: drustz-34e3ea7e7d01abfa56
section: mlsd
order: 1
level: A
title: 00 · 两天冲刺日历（唯一主线）
quick: 作者完整文档 · 00 · 两天冲刺日历（唯一主线）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/00_study_plan.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

# 00 · 两天冲刺日历（唯一主线）

⏱ 本文件 4 分钟读完 ｜ **每天只看当天那一节**，跟着走 = 自动覆盖本目录全部材料，不需要另外浏览任何文件

> ⚠️ **这份两天日历已经过期**（它只编排到 14，而目录已经扩到 22；
> 而且 Day 1/Day 2 标着「约 7 小时」，实际是 **545 / 502 分钟**，超 20–30%）。
> **入口请用 [`NOW.md`](?book=drustz-interview-2026&section=mlsd&question=drustz-2cedb992b9aecc82c2)** —— 只有一屏，按面试驱动。
> 下面这份仍可当「某个主题该读哪几节」的索引用，但**不要照着排时间**。

本目录 12000+ 行。**不要通读。** 下面的日程已经把每篇按 ⭐⭐⭐ 节挑好了，通读反而记不住。

规则：
- 每天格式固定：**主任务 ⭐⭐⭐** → **次任务 ⭐** → **砍时规则**
- 时间不够先砍 ⭐，绝不砍闭卷限时作答
- **顺序铁律**：先自己闭卷讲，再读材料。直接读材料 = 读完就忘
- 每天睡前 5 分钟做一遍[复盘五问](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/00_study_plan.md#复盘五问每天睡前-5-分钟)

---

## Day 1 · 数据轴地基 + 两道复盘题（约 7 小时）

你上周被问倒的 code review reward、这周被问倒的 OCR 场景数据，今天全部收掉。

| 时段 | 做什么 |
|---|---|
| 晨 ⭐⭐⭐（60 min） | [01 · 答题框架](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b)**全文**（188 行，是全目录的骨架，唯一必须逐字读完的文件）+ [10 · 一页速查](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde)，**闭卷默写开场 90 秒和结尾 60 秒各一遍** |
| 上午 ⭐⭐⭐（100 min） | [02 · 数据与标签](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3)全文 + [03 · 模型/训练/reward](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2)全文。这两篇正面回答你说的三个薄弱点：数据从哪来（02 §1）、数据短缺（02 §5 升级阶梯）、reward 怎么设计（03 §6 provenance 表 + §7 防 hacking） |
| 下午 ⭐⭐⭐（150 min） | **先闭卷限时 40 min 重答** "训练一个 code review LLM，用什么数据、什么 reward"（就是你被问倒那题，计时、白板、出声讲）→ 再读 [04 · code review](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45) 的 §0/§2/§3/§4/§7/§8/§15 → 用 §17 闭卷检查单查缺 |
| 傍晚 ⭐⭐⭐（90 min） | **先闭卷限时 30 min 重答** "OCR signature，怎么收各种场景的数据 + 怎么做到 production cost efficient" → 再读 [05 · OCR/signature](?book=drustz-interview-2026&section=mlsd&question=drustz-6f0414d424a39e12e5) 的 §0/§2/§3/§7/§10/§11 |
| 晚 ⭐（45 min） | [labs/lab02](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab02_reward_design/)：亲手写 code review 的 reward 打分器，跑 reward hacking 用例。手写过一遍，面试里讲 reward 才有细节 |
| 砍时 | 04 只读 §0 + §7 + §8 + §15；05 只读 §0 + §2 + §10；lab02 只读 `solution.py` 和测试输出 |

> **换题规则**：如果这两天要面的是 **AI 客服 agent 公司**（Decagon / Sierra / Intercom Fin / Ada 类），把傍晚的 OCR 那块换成 [14 · 客服 agent](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca)（先闭卷 30 min 答「设计一个企业 AI 客服 agent，怎么衡量它好不好」，再读 §0/§3/§4/§7/§12），并在 Day 2 晚补 [09 §H](?book=drustz-interview-2026&section=mlsd&question=drustz-354984fdc7bc9d31a9) 的 7 道客服题。OCR 那篇顺延到面试后再补。

**Day 1 结束时你应该能不看材料回答**：一个 code review 训练样本长什么样、历史 comment 为什么不是 gold label、reward 的四层结构（hard constraint / outcome / quality / cost）、三种 reward hacking 及其防御、签名题的五种任务区分、场景采集矩阵怎么画。

---

## Day 2 · 两块知识补全（约 7 小时）

Day 2 全部对口你已排期的面试：上午 = OpenAI pretraining，下午 = Exa。

| 时段 | 做什么 |
|---|---|
| 晨 ⭐⭐⭐（150 min） | **OpenAI pretraining 对口**。[07 · pretraining data](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 的 §一/§六/§七/§八/§九/§十/§十三 + **§十八 的 24 问自测（遮住答案）** + §二十 一页速记默写 funnel。这篇 1207 行是全目录最长的，但你没做过 pretraining，它是唯一的知识来源 |
| 上午 ⭐（40 min） | [labs/lab01](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab01_dedup_quality/)：手写 MinHash+LSH 去重和质量分类器。`Q5: MinHash 怎么工作` 是 07 里点名的高频题，手写过就不会卡 |
| 下午 ⭐⭐⭐（150 min） | **Exa 对口**。[06 · search post-training](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) 的 §一/§四/§五/§六/§七/§八/§九 + §十五 一页速记。重点是 §五（为什么 click ≠ positive）和 §六（hard negative 的坑），这两节是 Exa 面试最可能深挖的 |
| 下午 ⭐（40 min） | [labs/lab03](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab03_retrieval_negatives/)：InfoNCE + hard negative mining + false negative 陷阱 + 级联成本模型 |
| 晚 ⭐⭐⭐（70 min） | [13 · 公司卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)全过（Exa / OpenAI pretraining / Mirendil / Bridgewater / Decagon）+ [09 · 题库](?book=drustz-interview-2026&section=mlsd&question=drustz-354984fdc7bc9d31a9) **§I 真题实录**（1p3a 实录，不是模拟题）+ 从 A–H 随机抽 10 题每题 2 分钟口答 |
| 收尾 ⭐⭐⭐（50 min） | [08 · eval/production](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) 全文（209 行，成本和上线阶梯部分是每道题的收尾）+ [10 · 一页速查](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde)**闭卷默写** |
| 砍时 | 07 只读 §一 + §六 + §七 + §九 + §二十；06 只读 §一 + §五 + §六 + §十五；两个 lab 都只读 solution |

**Day 2 结束时你应该能不看材料回答**：pretraining 数据 funnel 十一步、为什么去重能提升模型且过度去重有害、quality classifier 的正样本从哪来、mixture 权重怎么定且怎么验证、benchmark 污染为什么不能只做 exact match、retriever/reranker/answerer 三层各自的监督信号和指标、click 的四种偏差、hard negative 的 false negative 陷阱。

---

## 只有 4 小时的急救版

面试明天就到、Day1/Day2 都来不及时：

| 时间 | 做什么 |
|---|---|
| 0–30 min | [01 · 答题框架](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) 全文，默写 8 步主线 |
| 30–50 min | [10 · 一页速查](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde)，背开场段和结尾段 |
| 50–80 min | [02 · 数据与标签](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) §1 来源表 + §4 split + §5 短缺阶梯 |
| 80–100 min | [03 · reward](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) §6 provenance 表 + §7 防 hacking |
| 100–160 min | 对口那家的案例文件，只读「90 秒开场 + 面试前一页速记 + 白板模板」三节 |
| 160–220 min | 闭卷讲一遍该案例，计时 40 min，用 [11 · mock](?book=drustz-interview-2026&section=mlsd&question=drustz-9a8db33390986aace4) 的 rubric 自评 |
| 220–240 min | [13 · 公司卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)对应那一张 |

## 面试前 30 分钟

1. [13 · 公司卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)对应那家（5 min）
2. [10 · 一页速查](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde)全文（10 min）
3. 白纸默写：`Problem → Metrics → Data → Baseline/Model → Objective → Eval → Serving → Loop`，以及该题的 data contract 字段（10 min）
4. 想好一个「我没做过这个 vertical」的诚实迁移句式，见 [12 · 个人切入](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) §3（5 min）

---

## 复盘五问（每天睡前 5 分钟）

1. 我今天讲的题里，prediction unit 和 label 何时可得，说清楚了吗？
2. 我说「数据不够就合成」的时候，有没有讲清楚合成能覆盖什么、不能代表什么？
3. 我的 split 能挡住 entity / time / 近重复三种泄漏吗？
4. 我给的每个 reward，说清楚它是观测事实还是 proxy 了吗？
5. 我的收尾有没有给出 launch gate、rollback 和获取新标签的方法？

## 之后的维护方式

错题表，错因只用五类：`framing`、`data`、`objective`、`evaluation`、`production`。

| 日期 | 题目 | 卡住的位置 | 漏掉的关键问题 | 下次固定动作 |
|---|---|---|---|---|
| YYYY-MM-DD | 例：签名验真 | split | 同一 writer 泄漏 | 先写 entity/time/device split |

连续两次同类错误，回读对应章节；不要从头重看全部材料。

---

## 附：七天慢速版（面试不急时用）

Day 1 [01](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) 框架 + 两道题各讲 10 分钟 ｜ Day 2 [02](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) 数据标签，写一份 code review 的 data contract 和签名题的 split policy ｜ Day 3 [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) 模型与 reward，对一个任务给出 rule/small/foundation 三版 ｜ Day 4 [04](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45) code review 闭卷 ｜ Day 5 [05](?book=drustz-interview-2026&section=mlsd&question=drustz-6f0414d424a39e12e5) OCR/signature 闭卷 ｜ Day 6 [06](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) + [07](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) ｜ Day 7 [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) + [11](?book=drustz-interview-2026&section=mlsd&question=drustz-9a8db33390986aace4) 一套完整 mock

## 覆盖核对表（本目录所有文件 ↔ 日程）

| 文件 | 被安排在 |
|---|---|
| [01](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) / [10](?book=drustz-interview-2026&section=mlsd&question=drustz-d194131afeba00ecde) | Day1 晨；Day2 收尾默写；每次面试前 30 min |
| [02](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) / [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) | Day1 上午 |
| [04](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45) | Day1 下午（先闭卷后对照） |
| [05](?book=drustz-interview-2026&section=mlsd&question=drustz-6f0414d424a39e12e5) | Day1 傍晚（先闭卷后对照） |
| [06](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) | Day2 下午（Exa 对口） |
| [07](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) | Day2 晨（OpenAI pretraining 对口） |
| [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) | Day2 收尾 |
| [09](?book=drustz-interview-2026&section=mlsd&question=drustz-354984fdc7bc9d31a9) | Day2 晚（§I 真题优先；面客服公司加做 §H） |
| [11](?book=drustz-interview-2026&section=mlsd&question=drustz-9a8db33390986aace4) | 急救版自评；七天版 Day 7 |
| [12](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) | 面试前 30 min 第 4 步 |
| [13](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9) | Day2 晚；每次面试前 5 min |
| [14](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca) | 仅面客服 agent 公司时，按换题规则替换 Day1 傍晚的 05 |
| [labs/](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/) | lab02→Day1 晚；lab01→Day2 上午；lab03→Day2 下午 |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/00_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/00_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
