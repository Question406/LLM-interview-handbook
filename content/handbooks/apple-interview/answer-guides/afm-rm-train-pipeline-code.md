---
id: afm-rm-train-pipeline-code
kind: coding
situation: 每条 pair 包含同一个 prompt 下 A、B 的数值特征，以及偏好 A 的比例 q；训练与 validation 分开提供。
task: 用零初始化的共享线性 scorer 训练指定次数，并返回权重、训练统计和四项 validation 结果。
approach: 只用 a、b 拟合 standardization；以 A、B 的 reward difference 为 logit，对 q 计算 mean BCE，再做 full-batch SGD。
result: 用零步、一步更新和 soft-target 例子手算核对；替换 validation 不得改变 weight、mean、std，全 tie 时 strict_acc 为 None。
---

## 可以这样回答

这里不是训练一个 LLM，而是给已经提取好的回答特征训练一个线性 scorer。每行 a、b 是同一个 prompt 的两个候选，q 是人工偏好 A 的比例。例如 q=0.75 就直接作为 BCE 的 soft target，不能把它当作 sample weight，也不能先转成 A 获胜的 hard labels。

我会先合并训练回答，计算每个 feature 的 mean 和 population std，并冻结这组统计。A、B 共用一个零初始化、无 bias 的 scorer，两个 reward 的差就是 pairwise logit。然后用 full-batch SGD 恰好更新 epochs 次；validation 不参与任何参数或 preprocessing 的拟合。

验证时输出 A 的预测概率，以及 soft-label NLL、soft-target squared error 和 non-tie preference accuracy。vq=0.5 的样本仍参与前两个指标，只从 accuracy 中排除；如果全是这种样本，accuracy 返回 None。

我会先检查题面的手算例子：a=1、b=-1、q=1 时，零步预测是 0.5；learning rate 为 0.1，更新一步后 weight 应为 0.1，A 的概率约为 0.549834。再检查 soft targets、constant features，以及更换 validation 后训练结果是否完全一致。
