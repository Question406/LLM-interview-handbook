---
id: dt-contamination
section: panel
order: 7
level: S
title: Panel：怎么查评测被训练数据看见了，查到了怎么办？
quick: "把冻结的评测题和训练数据从便宜到贵逐层比对，依次比 URL、n-gram、embedding 近邻，再拿训练截止后才出现的新题作对照，旧题好、新题差就是泄漏的警报。确认泄漏后，正式评测换新题，旧题降为开发集，命中的训练文档隔离出下一轮 mix，对外同时报新旧两套结果。"
companies:
  - apple
tags:
  - Apple
  - Contamination
  - Evaluation
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "LiveCodeBench: Holistic and Contamination Free Evaluation"
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

把评测题和训练数据从便宜到贵逐层比对，再拿训练截止之后的新题作对照；查到泄漏就换门禁，旧题降成开发集，命中的训练文档隔离掉。

最容易漏的是改过的题。一道 GSM8K 题被人转载时把数字换了一换，题目字符串的精确匹配就对不上了，可模型其实见过这道题。评测一旦被训练数据看见，分数就不再代表能力，门禁也就失效了，而这类重叠不会自己暴露出来，所以要单独对着冻结评测去查。

## 怎么查

我会先比来源。评测题如果来自网页或 GitHub，直接拿它的 URL 或文档 id 和训练抓取表比对，这一步最便宜。

再比 n-gram，出现 13-gram 一类的命中，就把整道题放进 quarantine。改写数字、换变量名之后 n-gram 可能对不上，所以还要再找嵌入近邻：用题面 embedding 找出高相似的训练样本，人工抽查是转载还是正常的同类题，阈值按领域定。

最后做时间切分。LiveCodeBench 的做法是只用训练截止之后出现的题当门禁。旧题表现好、新题明显下降，就先怀疑泄漏，排除了再算作能力提升。

## 查到之后

正式评测换成新题，或者按时间切分后的题。旧题可以留作开发调优集，报告里新旧结果分开列。训练侧命中评测的文档放进 quarantine，不进下一轮 mix；模型已经见过这些题，再拿它们 SFT 一遍只会把旧分数刷得更满。合成那边也要堵住入口，生成器的输入提示（prompt）里禁止带评测题，把评测题改写后当合成种子，等于故意污染。对外同时报旧门禁和新门禁的结果，只报旧的，别人没法判断涨分里有多少来自泄漏。

## 追问

**训练集已经去过重了，为什么还要单独查？**
训练集内部去重只保证训练数据之间不重复，不会去对照评测集。精确去重和 MinHash 先在训练侧做完（`dt-exact-dedup-code`、`dt-minhash-code`），污染检查另外对着冻结评测做。

**合成数据会不会也带来污染？**
会。训练数据和评测题出自同一个教师模型，也是一种污染（`dt-self-improve`），训练和评测两边都要查。AFM 的多语门禁用母语者写的题、不用翻译题，也是在防这种情况：题看起来是新的，其实只是英语题的影子。

**多少 n-gram 重叠算脏？**
没有普适阈值。报命中率和抽查出来的假阳性，代码题要比自然语言更严。

**人写的内部题会不会脏？**
会，如果标注员能搜到 GSM8K。协议里要禁止搜索，事后也要查重叠。

**泄漏 2%，分数涨了 5 个点，算不算真涨？**
把命中的题拿掉再报。拿掉之后还涨，才算真涨。

相关：`dt-benchmark-gap`（能力缺口的整体诊断顺序）
