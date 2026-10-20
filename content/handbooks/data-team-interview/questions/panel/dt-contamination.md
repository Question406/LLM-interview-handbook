---
id: dt-contamination
section: panel
order: 7
level: S
title: Panel：怎么查评测被训练数据看见了，查到了怎么办？
quick: "把固定评测题与训练数据做 URL、n-gram 和 embedding 相似度检查，再用训练截止后出现的新题作对照。旧题好、新题差是污染的警报，需要进一步核查。确认泄漏后，更换正式评测题，把旧题降为开发集，并隔离命中的训练文档。"
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

诊断模型能力缺口时，我会先检查评测污染，见 `dt-benchmark-gap`。只看题目字符串精确匹配，改写数字会漏。查到了就换门禁，旧题降成开发集。

不这么选的理由：把泄漏当数据增强，门禁就废了。「既然已经看见了就再 SFT 一遍刷满」，Director 会当成刷榜。

## 查：重叠加时间切

URL / 文档 id。评测若来自网页或 GitHub，训练抓取表直接比。最便宜。

n-gram。13-gram 一类命中就把整题打进 quarantine。改写数字、换变量名仍可能漏，所以还有下一层。

嵌入近邻。题面 embedding 的高相似对，抽查看是转载还是正当同类题。阈值按域定。

时间切。LiveCodeBench 的做法：只用训练截止之后出现的题当门禁。旧题表现好、新题明显下降时，应优先怀疑泄漏，而不能直接认定能力提升。

合成自污染是另一件事：训练和评测都来自同一教师，见 `dt-self-improve`。两边都要查。AFM 多语门禁用母语者题，不用翻译题，也是在防「看起来像新题、其实是英语题的影子」。

精确去重和 MinHash 先做，见 `dt-exact-dedup-code`、`dt-minhash-code`。污染检查是对着**冻结评测**做的，不是训练内部去重的副作用。

## 查到了怎么办

正式评测换成新题，或按时间切分后的题。旧题可以保留为开发调优集，但报告要分别列出新旧结果。

训练侧命中评测的文档进 quarantine，不进下一轮 mix。不要「既然已经看见了就再 SFT 一遍刷满」。

合成生成器的 输入提示里禁止带评测题。改写评测题当合成种子，是故意污染。

对外数字：同时报旧门禁和新门禁。只报旧的，Director 会当成刷榜。

## 追问

- **多少 n-gram 算脏？** 没有普适阈值。报命中率和抽查假阳性。代码题要比自然语言更严。
- **人写的内部题会不会脏？** 会，如果标注员能搜到 GSM8K。协议里要禁搜、要查重叠。
- **泄漏 2% 还涨了 5 个点，算不算真涨？** 把命中题拿掉再报。拿掉后还涨，才算。
