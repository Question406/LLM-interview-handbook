---
id: dt-inspect-corpus
kind: concept
situation: 不了解原始分布就无法合理设过滤规则。
task: 先弄清 corpus 包含什么和缺什么。
approach: 全库统计配合按语言、长度、来源 sampling。
result: 发现的异常能回到样本与来源，而非只看均值。
---

## 可以这样回答

不了解原始分布就无法合理设过滤规则。

先对全库做计数和检索，再 sampling 看。统计语言、长度、重复率、评测重叠、PII、密钥和抽取错误，才知道该滤什么。WIMBD 就是这样检查大规模 corpus 的；Datasheets 把来源、用途、偏差和处理版本记下来，方便以后复盘。
