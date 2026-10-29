---
id: dt-data-replay-incident
section: panel
order: 35
level: S
title: Panel 情景：数据任务重跑后样本翻倍，怎么恢复并防止训练重复？
quick: 假设数据作业失败后重跑，训练样本数翻倍。先暂停发布这个版本，确认重复来自输入、重试还是提交过程，不要直接让训练继续消耗它。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

原创系统设计情景题。离线数据任务处理十亿文档，失败后部分重跑。数据仓库统计条数只增加 2%，但某些语言的数据在最终训练 sampling 中翻倍。训练已运行一天，有人建议继续训练、下轮再清理。

请给出事故排查、恢复决策和重跑协议。说明样本 ID、过滤器版本、分片发布、训练 checkpoint 和监控分别记录什么，不要求编写分布式系统代码。

## 回答思路

> **问题与场景：** 假设数据作业失败后重跑，训练样本数翻倍。
>
> **做法与原因：** 我会给源记录和处理版本定义稳定身份，让同一次逻辑产出可重复执行而不重复写入。
>
> **检查与取舍：** 验证既看总数和唯一记录，也检查分布、缺失和下游引用。

## 可以这样回答

假设数据作业失败后重跑，训练样本数翻倍。先暂停发布这个版本，确认重复来自输入、重试还是提交过程，不要直接让训练继续消耗它。

我会给源记录和处理版本定义稳定身份，让同一次逻辑产出可重复执行而不重复写入。恢复时按完整性记录重建数据，不能盲目删掉所有相似文本，因为合法重复与重复提交不是一回事。

验证既看总数和唯一记录，也检查分布、缺失和下游引用。最后用故障注入测试“写完但没收到确认”等过程。

## 技术备查

## 解题思路与参考答案

先冻结当前数据 manifest 和受影响分片的发布，保存训练 checkpoint 与 sampling 日志。条数增加少不代表影响小：小语种可能被 temperature sampling 放大，重复的少量源也可能集中在某个高权重域。检查真正被消费的 token 和样本身份，不能只看仓库全量行数。

### 身份和发布协议

源记录有稳定 source ID，规范化内容有内容指纹，变换输出还包含过滤器、tokenizer 与增强配置版本。运行尝试 ID 只用于追踪执行，不能当作样本逻辑身份。重复交付同一变换结果应被覆盖或拒绝；不同合法增强可以保留不同 variant ID，但其 source groups 要能聚合分析。

每次任务写到独立的临时或不可变分片，完成后记录计数、checksum、token 数和分布统计。只有全部分片验证通过才发布完整 manifest；可以通过单一原子引用切换或事务提交，不让训练边读目录边发现半成品。相同任务重跑不能把旧分片与新分片同时加入 manifest。

### 已训练一天怎么办

从训练记录重建受影响的消费量，比较目标语言和基础 capability slices，再决定回滚到 contamination 前 checkpoint、用修复数据重跑，或在影响可接受且有证据时保留本轮。直接少采一点不能从已有权重中精确删除重复训练的影响，不能声称“反向抵消”。

checkpoint 除模型与 optimizer 外，应关联 manifest、sampling 器状态、分片/样本位置、随机数状态及分词版本。只记录 epoch 不足以恢复动态混合流。恢复后检查分域 token 占比、source groups 重复频率和过滤器版本分布。

## 面试追问

**内容哈希就足够吗？** 不足。相同文本可能是合法重复或不同授权来源；不同文本也可能属于同一增强家族。身份、内容、来源和许可都应分别记录。

**必须实现 exactly-once 吗？** 重点是最终发布的数据与消费语义可验证。执行可以重试多次，通过幂等产物和 deduplication 的 manifest 达到一次逻辑交付；不能只喊消息队列的术语。

**这与普通 deduplication 题有什么区别？** 普通 deduplication 讨论内容相似性，本题还涉及任务重试、版本一致性和已发生的训练更新，不能只对最终文本做 set deduplication。
