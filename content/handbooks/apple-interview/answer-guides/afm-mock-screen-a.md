---
{
  "id": "afm-mock-screen-a",
  "kind": "coding",
  "situation": "输入已划分的数值特征 x/vx 与 binary labels y/vy；只需训练指定的线性二分类器。",
  "task": "返回 standardized-space 参数、训练统计、validation probabilities、NLL、accuracy 和 update 次数。",
  "approach": "训练数据拟合 mean/std，零初始化 Linear，以固定顺序执行 mini-batch SGD；validation 只做 eval/no_grad。",
  "result": "单 epoch 的手算例子得到 weight=0.05、bias=0、steps=1；更换 validation 不得改变训练结果。"
}
---

## 可以这样回答

这道题的输入已经是数值 features 和 0/1 labels，不需要下载数据或选择复杂模型。我会先只在 x 上拟合 mean 和 population std，再把同一变换应用到 training 和 validation。

模型固定为零初始化的 Linear，带 bias。每个 epoch 按输入顺序做 mini-batch SGD，最后不足一批也单独更新，loss 按该批样本数平均。Epochs 为零时不更新参数，但仍返回 preprocessing statistics 和 validation 指标。

我会检查题面的手算场景：x 为 -1、1，标签为 0、1；一个 full-batch update、lr=0.1 后，weight 应为 0.05、bias 为 0、steps 为 1。然后检查 constant features、末批以及 validation isolation，最后再讨论十亿行数据如何分片和恢复。
