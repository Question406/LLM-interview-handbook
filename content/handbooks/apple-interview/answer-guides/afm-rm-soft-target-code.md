---
{
  "id": "afm-rm-soft-target-code",
  "kind": "coding",
  "situation": "每个 prompt 有 A/B 两个 reward scores；q 是偏好 A 的比例，w 是独立 confidence weight。",
  "task": "返回 weighted mean soft-label BCE，并只对 a、b 保留 gradients。",
  "approach": "以 a-b 为 logit，逐 pair 计算稳定 BCE，再按 w 加权；q、w 先 detach。",
  "result": "单条 q=0.6 时 reward gradients 为 -0.1/+0.1；全零 w 时 loss 与 reward gradients 为零。"
}
---

## 可以这样回答

我会先分清四个输入：a、b 已经是两个回答的 reward scores，不是 features；q 表示偏好 A 的比例，w 才决定一条 pair 对 batch 的贡献。

以 a-b 为 logit，按 q 计算逐条 BCE，再用 w 加权除以总权重。q、w 都作为固定数据，不能收到 gradients。总权重为零时也要返回可以 backward 的零，不能除零或直接返回 Python 数字。

我会用题面的一条样本验证：a=b=0、q=0.6 时，loss 是 log(2)，对 a 的 gradient 为 -0.1，对 b 为 +0.1。因为按总权重 normalization，只有一条样本时 w=0.2 不会再把 gradient 缩小五倍。
