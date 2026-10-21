---
id: dt-contamination
section: panel
order: 7
level: S
title: Panel：怎么查评测被训练数据看见了，查到了怎么办？
quick: "把冻结的评测题和训练数据逐层比对：URL、n-gram、embedding 近邻，再用训练截止后才出现的新题作对照。旧题好、新题差是泄漏的警报。确认泄漏后，正式评测换成新题，旧题降为开发集，命中的训练文档隔离出下一轮 mix，对外同时报新旧两套结果。"
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

我会把评测题和训练数据从便宜到贵逐层比对，再用训练截止之后的新题作对照。只看题目字符串的精确匹配，会漏掉改过数字的题。查到泄漏就换门禁，旧题降成开发集，命中的训练文档隔离掉。

## 为什么要专门查

评测一旦被训练数据看见，分数就不再代表能力，门禁也就失效了。这类重叠不会自己暴露：训练集内部去重只保证训练数据之间不重复，不会去对照评测集。所以污染检查要单独对着**冻结评测**做。精确去重和 MinHash 先在训练侧做完，见 `dt-exact-dedup-code`、`dt-minhash-code`。

## 怎么查：从便宜到贵

第一层比来源。评测题如果来自网页或 GitHub，直接拿它的 URL 或文档 id 和训练抓取表比对，这是最便宜的一步。

第二层比 n-gram。比如出现 13-gram 一类的命中，就把整道题放进 quarantine。改写数字、换变量名之后 n-gram 可能对不上，所以还需要下一层。

第三层找嵌入近邻。用题面 embedding 找出高相似的训练样本，人工抽查是转载还是正常的同类题。阈值按领域定。

最后做时间切分。LiveCodeBench 的做法是只用训练截止之后出现的题当门禁。旧题表现好、新题明显下降时，先怀疑泄漏，排除之后再算作能力提升。

还有一种污染来自合成：训练数据和评测题出自同一个教师模型，见 `dt-self-improve`。训练和评测两边都要查。AFM 的多语门禁用母语者写的题，不用翻译题，也是在防这种情况：题看起来是新的，其实只是英语题的影子。

## 查到了怎么办

1. **换门禁。** 正式评测换成新题，或按时间切分后的题。旧题可以留作开发调优集，但报告里要分别列出新旧结果。
2. **隔离训练文档。** 训练侧命中评测的文档放进 quarantine，不进下一轮 mix。模型已经看见过这些题，再拿它们 SFT 一遍只会把旧分数刷得更满。
3. **堵住合成入口。** 合成生成器的输入提示（prompt）里禁止带评测题。把评测题改写后当合成种子，等于故意污染。
4. **对外报两套数。** 同时报旧门禁和新门禁的结果。只报旧的，别人没法判断涨分里有多少来自泄漏。

## 追问

- **多少 n-gram 重叠算脏？** 没有普适阈值。报命中率和抽查出来的假阳性。代码题要比自然语言更严。
- **人写的内部题会不会脏？** 会，如果标注员能搜到 GSM8K。协议里要禁止搜索，事后也要查重叠。
- **泄漏 2%，分数涨了 5 个点，算不算真涨？** 把命中的题拿掉再报。拿掉之后还涨，才算真涨。

相关：能力缺口的整体诊断顺序见 `dt-benchmark-gap`。
