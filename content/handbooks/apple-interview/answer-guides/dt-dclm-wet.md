---
id: dt-dclm-wet
kind: concept
situation: 下游过滤无法恢复抽取时丢掉的信息。
task: 判断瓶颈在正文抽取还是质量分。
approach: 固定过滤，只比较预抽文本与原 HTML 重抽。
result: 受控下游收益支持上游改进，非纯格式变化。
---

## 可以这样回答

下游过滤无法恢复抽取时丢掉的信息。

因为瓶颈常在正文抽取。WET 是 Common Crawl 预先抽好的纯文本，抽错漏掉的内容后面的质量分类器补不回来。DCLM 固定同一套过滤、只把 WET 换成从 WARC 原始 HTML 重新抽取，Core 就高了至少 2.5 点，所以先定抽取，再调分类器和阈值。
