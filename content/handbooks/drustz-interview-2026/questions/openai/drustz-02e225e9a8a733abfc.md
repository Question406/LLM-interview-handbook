---
id: drustz-02e225e9a8a733abfc
section: openai
order: 63
level: A
title: Debug A/B Test Python Code (Metric Computation and Statistical Testing)
quick: >-
  original-structured-preparation-guide · Debug A/B Test Python Code (Metric
  Computation and Statistical Testing)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/fbde06cd-0253-4b64-a01a-9ea551c06435
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Debug A/B Test Python Code

> 公开 OJ 描述已与当前 UUID 精确对应，但原始待调试 Python 代码没有公开。输入是用户级 DataFrame，包含 `user_id / variant / exposure / metric`；要求找出至少三个 bug 或统计陷阱，修正过滤、缺失值、检验、SRM 与confidence interval。

## 先确认实验单位

最常见的根因不是公式，而是统计单位错误：随机分流按 user、session 还是 event？同一用户的多行记录不能被当成独立样本。先验证一个 unit 是否只属于一个 variant，并检查 Sample Ratio Mismatch。

SRM 必须在按 `exposure` 过滤前、基于随机分配人数检查。若 estimand 是 intention-to-treat，不应按实验后的 exposure 条件筛选；若明确分析 exposed population，则需说明selection bias风险。

## 指标计算

对 ratio metric：

```text
conversion_rate = converted_users / eligible_users
revenue_per_user = total_revenue / assigned_users
```



分母必须来自实验分配且符合 eligibility，而不是只统计“产生过事件”的用户。处理重复事件、缺失值、实验前数据、时区边界和 late-arriving events。

```python
assigned = df.drop_duplicates("user_id")
assert assigned.groupby("user_id")["variant"].nunique().max() == 1

metric = user_level.groupby("variant")["converted"].agg(["mean", "count", "var"])
```



## 统计检验

- 二元转化率：two-proportion z-test 或在 user-level bootstrap；
- 连续均值：Welch t-test，方差不齐时不要使用 pooled variance；
- ratio metric：delta method 或按随机化单位 bootstrap；
- 重尾 revenue：报告confidence interval，并考虑 winsorization，但规则必须在看结果前确定。

同时报告 effect size 与confidence interval，不要只返回 p-value。多指标或多次查看结果需要控制 multiple testing / sequential peeking。

原代码中 `pandas.mean()` 会跳过 NaN，而某些统计函数默认传播 NaN；清洗口径必须一致。Mann–Whitney 检验比较的是分布/秩，不是“均值提升”的通用替代。A 组均值为 0 时相对 lift 未定义。

## 调试测试

用小型合成数据覆盖：A/B 完全相同应不显著；人为给 B 增加固定 lift 应能检出；重复行不应改变 user-level 指标；交换 variant 标签结果应对称；固定 seed 的 bootstrap 可复现。

## 复杂度

groupby 聚合通常平均 `O(n)`；排序去重可能为 `O(n log n)`；`B` 次 bootstrap 为 `O(Bn)`，可使用向量化或充分统计量优化。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/fbde06cd-0253-4b64-a01a-9ea551c06435)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
