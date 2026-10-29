---
id: coding-spec-accept
kind: coding
situation: 草稿分布与目标分布并不相同。
task: 接受草稿时仍保持目标 sampling distribution。
approach: 逐步接受，首拒绝处用残差分布 resampling。
result: 检查全接受、首拒绝和总体 sampling 频率。
---

## 可以这样回答

草稿分布与目标分布并不相同。

草稿 token 从左到右按 $\min(1,p/q)$ 接受，第一次在第 $i$ 步拒绝时，就在同一步从 normalization 残差 $\max(0,p-q)$ resampling，并丢掉后续草稿。全部接受则从 $p$ 多抽一个 token。接受与残差两条路径的概率相加等于目标分布，因此保持 sampling distribution 不变。

测试时，我会检查全接受、首拒绝和总体 sampling 频率。
