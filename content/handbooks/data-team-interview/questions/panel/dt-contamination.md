---
id: dt-contamination
section: panel
order: 7
level: S
title: Panel：怎么查评测被训练数据看见了，查到了怎么办？
quick: 假设模型能背出评测答案，但逐字匹配没有发现重复。我会怀疑翻译、改写或同一题的变体，先保留证据并隔离可疑数据，避免继续混入训练。
companies:
  - apple
tags:
  - Apple
  - Contamination
  - Evaluation
  - Dedup
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: 'LiveCodeBench: Holistic and Contamination Free Evaluation'
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 回答思路

> **问题与场景：** 假设模型能背出评测答案，但逐字匹配没有发现重复。
>
> **做法与原因：** 检查不能只靠一种 n-gram：还要看来源与生成记录、语义近邻和人工复核。
>
> **检查与取舍：** 已经训练过的模型不会因为删除文件就忘掉内容。

## 可以这样回答

假设模型能背出评测答案，但逐字匹配没有发现重复。我会怀疑翻译、改写或同一题的变体，先保留证据并隔离可疑数据，避免继续混入训练。

检查不能只靠一种 n-gram：还要看来源与生成记录、语义近邻和人工复核。找到一条后，要追踪同源样本、它进入的训练版本和受影响的评测。

已经训练过的模型不会因为删除文件就忘掉内容。需要明确哪些结果不再能证明泛化，并使用真正独立的评估；后续训练再修复数据流程。

## 技术备查

把评测题和训练数据从便宜到贵逐层比对，再拿训练截止之后的新题作对照；查到 leakage 就换 evaluation gate，旧题降成 development set，命中的训练文档隔离掉。

最容易漏的是改过的题。一道 GSM8K 题被人转载时把数字换了一换，题目字符串的精确匹配就对不上了，可模型其实见过这道题。评测一旦被训练数据看见，分数就不再代表能力，evaluation gate 也就失效了，而这类重叠不会自己暴露出来，所以要单独对着冻结评测去查。

## 怎么查

我会先比来源。评测题如果来自网页或 GitHub，直接拿它的 URL 或文档 id 和训练抓取表比对，这一步最便宜。

再比 n-gram，出现 13-gram 一类的命中，就把整道题放进 quarantine。改写数字、换变量名之后 n-gram 可能对不上，所以还要再找 embedding nearest neighbors：用题面 embedding 找出高相似的训练样本，人工抽查是转载还是正常的同类题，阈值按领域定。

最后做时间切分。LiveCodeBench 的做法是只用训练截止之后出现的题当 evaluation gate。旧题表现好、新题明显下降，就先怀疑 leakage，排除了再算作能力提升。

## 查到之后

正式评测换成新题，或者按时间切分后的题。旧题可以留作开发调优集，报告里新旧结果分开列。训练侧命中评测的文档放进 quarantine，不进下一轮 mix；模型已经见过这些题，再拿它们 SFT 一遍只会把旧分数刷得更满。合成那边也要堵住入口，生成器的 prompt 里禁止带评测题，把评测题改写后当合成 seed，等于故意 contamination。对外同时报旧 evaluation gate 和新 evaluation gate 的结果，只报旧的，别人没法判断涨分里有多少来自 leakage。

## 追问

**training set 已经去过重了，为什么还要单独查？**
training set 内部 deduplication 只保证训练数据之间不重复，不会去对照 evaluation set。exact deduplication 和 MinHash 先在训练侧做完（`dt-exact-dedup-code`、`dt-minhash-code`），contamination 检查另外对着冻结评测做。

**synthetic data 会不会也带来 contamination？**
会。训练数据和评测题出自同一个 teacher model，也是一种 contamination（`dt-self-improve`），训练和评测两边都要查。AFM 的 multilingual evaluation gate 用母语者写的题、不用翻译题，也是在防这种情况：题看起来是新的，其实只是英语题的影子。

**多少 n-gram 重叠算脏？**
没有普适阈值。报命中率和抽查出来的假阳性，代码题要比自然语言更严。

**人写的内部题会不会脏？**
会，如果 annotator 能搜到 GSM8K。协议里要禁止搜索，事后也要查重叠。

**leakage 2%，分数涨了 5 个点，算不算真涨？**
把命中的题拿掉再报。拿掉之后还涨，才算真涨。

相关：`dt-benchmark-gap`（能力缺口的整体诊断顺序）
