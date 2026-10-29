---
id: drustz-b4ef7f7e7e82f74325
section: openai
order: 183
level: A
title: Diagnosing and Fixing Transformer Model Training Performance Drop
quick: >-
  original-structured-preparation-guide · Diagnosing and Fixing Transformer
  Model Training Performance Drop
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
      https://www.1point3acres.com/interview/problems/b326bc75-155a-4590-88e2-a92fb8cd01a1
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 诊断 Transformer 训练性能突然下降

> 内容定位：本地资料确认“模型能跑但 loss 不正常”的 Transformer 调试题族，也提供了对应练习；不过标题里的 performance 可能指模型质量、throughput或两者，公开信息不足以确定。本指南先把二者分开诊断，不冒充会员原题。

## 题目要做什么

某次代码、数据或配置变更后，Transformer 的训练表现退化。要求用指标判断是 quality regression（loss、准确率、生成质量）还是 systems regression（tokens/s、显存、延迟），找到最小根因，并提出可回滚、可验证的修复。

## 数据或需求

至少保留 good run 与 bad run 的 commit、随机种子、数据版本、环境、超参数、逐步 loss、梯度范数、tokens/s 和峰值显存。若只有最终分数而没有这些证据，第一步应当补 instrumentation，而不是猜原因。

## 例子

本地练习中的训练循环调用了 `optimizer.step()`，却漏掉 `loss.backward()`：程序正常、throughput甚至略高，但所有参数不变，loss 接近 `log(V)`。另一个隐蔽例子是 `V == C` 时 `x @ embedding.weight` 没有 shape error；换成 `V != C` 才暴露应当转置。

## 解法

先复现，再二分。固定一个 tiny batch，在 good/bad commit 上保存每个模块的输出与梯度摘要，找出第一个分叉层：

```text
reproduce -> classify quality vs speed
compare config/data/env -> git bisect
module output diff -> gradient/update diff
micro-overfit -> full-run A/B
```



质量下降依次检查 target shift、数据/tokenizer 版本、位置编码、causal mask、softmax 维度、loss reduction、train/eval、梯度累计和 optimizer 顺序。速度下降则检查序列长度分布，因为 attention 随 `T²` 增长；再看是否关闭 fused kernel、触发 host-device 同步、DataLoader 饥饿、梯度 checkpoint 或编译缓存失效。修复后用同样 seed 跑短 A/B，并同时比较 loss trajectory 与throughput；若只恢复一项，说明仍有第二个问题。

## 复杂度

标准 attention 计算约 `O(BT²C)`，所以平均序列长度翻倍可能接近四倍 attention 工作量。逐层对拍若保存全部激活需 `O(LBTC)` 额外空间；可只保存均值、方差、范数和少量sampling位置。

## 边界与验证

- 首次运行含编译/缓存预热，不能直接与稳态throughput比较；
- dropout 使逐元素对拍失效，需固定 seed 或用 `eval()`；
- 数据变容易会让 loss 下降，却不代表模型更好；
- 混合精度 overflow 应同时看 scaler 与梯度；
- 修复必须加入回归测试、版本记录和回滚阈值。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b326bc75-155a-4590-88e2-a92fb8cd01a1)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
