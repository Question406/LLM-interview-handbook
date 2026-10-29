---
id: dt-repro-lineage
kind: concept
situation: 一周后可能需要解释增益或撤回来源。
task: 复现同一数据版本和处理过程。
approach: 保存来源、teacher、过滤器及 mix 的版本依赖。
result: 同配置可重建，指定来源能准确移除。
---

## 可以这样回答

一周后可能需要解释增益或撤回来源。

能不能复现，看每条样本能不能追到来源和版本：来源 URL、许可集或研究协议，加上抽取器、过滤器、teacher、verifier 和 dataset_version。这样每次增益都能对应固定评测和具体 mix，opt-out 也能按精确记录撤回。只有文件目录、没有来源和版本，说明不了数据可复现。
