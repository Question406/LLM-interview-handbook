---
id: dt-webgpt-cite
kind: concept
situation: 没有可查证据，human evaluation 容易按文风打分。
task: 让事实偏好可逐项核对。
approach: 分别记录搜索 trajectories、引用支持与来源可信度。
result: 去掉格式优势后内容仍正确，事实判断独立。
---

## 可以这样回答

没有可查证据，human evaluation 容易按文风打分。

因为没有引用，annotator 只能凭记忆或文笔判断真假，事实 preference labels 噪声很大。WebGPT 把数据拆成两部分：浏览 trajectories 教模型怎么搜，带引用的答案让 annotator 逐句核对出处。「引用是否支持」和「来源是否可信」要分开评，评测时再去掉引用比一次，防止引用格式本身让答案显得可信。
