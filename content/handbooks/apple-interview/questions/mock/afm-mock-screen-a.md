---
id: afm-mock-screen-a
section: mock
order: 10
level: S
title: 45 分钟模拟 A：从零完成 PyTorch 分类训练并口述 data pipeline
quick: >-
  在 45 分钟内跑通 training set standardization、mini-batch
  SGD、验证与错误分析；同时解释来源、deduplication、分片和版本。先保证可复现且无验证 leakage，再谈模型复杂度。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: 'PyTorch: Optimizing Model Parameters'
    url: >-
      https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
    type: primary
---

## 题目描述

给定已经划分好的数值训练数据和 validation 数据，用 PyTorch 完成二分类训练与评估。你需要自己实现 preprocessing、mini-batch training 和指标计算，不需要提取文本特征、下载数据或选择网络结构。

本题是原创模拟 A，所有接口和训练规则均为练习约定。建议 0–5 分钟澄清任务，5–28 分钟实现，28–36 分钟测试，36–42 分钟讨论规模化，最后总结。

### 接口与数据含义

实现 `fit_classifier(x,y,vx,vy,epochs=30,batch_size=4,lr=0.1)`：

| 参数 | 类型与 shape | 含义 |
| --- | --- | --- |
| `x` | CPU float32 tensor `[N,D]` | 每行是一条训练样本，列为已给定的数值 features |
| `y` | CPU float32 tensor `[N]` | 对应训练样本的 binary label，0 为负类、1 为正类 |
| `vx`、`vy` | CPU float32 tensors `[M,D]`、`[M]` | 独立 validation 样本及其 0/1 labels |
| `epochs` | 非负整数 | 按固定顺序遍历完整 training set 的次数 |
| `batch_size` | 正整数 | 每次 SGD update 使用的训练样本数上限 |
| `lr` | 正的 Python float | SGD learning rate |

`N,M,D>=1`，数值规模正常且有限。数据已经按实体或时间隔离，不能合并后重新划分。输入保证合法；不得修改输入或向输入写入 gradients。

### 必须实现的训练规则

1. 仅用 x 按列拟合 mean 和 population std（`unbiased=False`），std 最小为 `1e-6`。训练与 validation 共用这组 statistics。
2. 模型固定为 `Linear(D,1,bias=True)`，weight 和 bias 全零初始化。令 standardized features 为 z，logit 为 `z@weight+bias`，正类概率为 sigmoid(logit)。
3. 使用普通 SGD，无 momentum、weight decay、shuffle 或 early stopping。每个 epoch 按输入顺序分批，末批不足 batch_size 时也训练。
4. 每批 loss 为该批 binary cross-entropy 的算术平均，可用 `binary_cross_entropy_with_logits`。每批各执行一次 `zero_grad → backward → step`；不要把末批乘以额外比例。
5. 训练使用 `model.train()`，validation 使用 `model.eval()` 和 `torch.no_grad()`；validation 不能影响参数或 statistics。epochs=0 时也返回初始化模型的评估。

### 输出字典

返回以下 8 个字段，所有 tensor 均为 CPU float32 且不保留 autograd graph：

| 字段 | 类型 / shape | 定义 |
| --- | --- | --- |
| `weight` | tensor `[D]` | Standardized feature space 中的最终 weight |
| `bias` | tensor `[1]` | 最终 bias |
| `mean`、`std` | tensors `[D]` | 仅在 x 上拟合并应用 std 下限后的统计 |
| `prob` | tensor `[M]` | Validation 正类概率 |
| `nll` | Python float | 全部 validation 样本的 mean binary cross-entropy，使用自然对数 |
| `accuracy` | Python float | `prob>=0.5` 预测为 1，否则为 0，与 vy 比较后的比例 |
| `steps` | Python int | 实际 optimizer updates，等于 `epochs*ceil(N/batch_size)` |

表格一行列出 mean、std 两个字段，因此总计 8 个字段。

### 完整输入输出示例

```text
x=[[-1.0],[1.0]], y=[0.0,1.0]
vx=[[-1.0],[1.0]], vy=[0.0,1.0]
```

此处训练与 validation 的数值相同只用于手算，不表示真实数据可以跨 split 复制。

```text
epochs=0, batch_size=2, lr=0.1
返回：weight=[0.0], bias=[0.0], mean=[0.0], std=[1.0],
      prob=[0.5,0.5], nll=0.69314718, accuracy=0.5, steps=0

epochs=1, batch_size=2, lr=0.1
返回：weight=[0.05], bias=[0.0], mean=[0.0], std=[1.0],
      prob≈[0.48750260,0.51249740], nll≈0.66845965,
      accuracy=1.0, steps=1
```

允许 `atol=1e-6,rtol=1e-6` 的浮点误差。必须覆盖 constant feature、epochs=0、末批不足一批，以及改变 validation 后训练结果不变。

### 训练之后的口述任务

假设输入扩展到十亿行，说明如何保留 train/validation isolation、分配 worker、避免恢复后重复消费，以及处理坏记录。本部分讨论设计，不要求在本函数中实现分布式训练。

## 解题思路与参考答案

零初始化便于手算第一步，并避免随机数差异掩盖 data leakage。验证输入变化不得影响训练权重，这是测试训练/验证隔离的关键。最后一批按自身样本均值更新，若面试要求按全 epoch 权重累积，需要另行约定。

评分共20分：训练/验证隔离4，训练状态与 gradient4，edge cases 与可手算测试4，规模和质量口述4，沟通及时间管理4。每项0–4：0未做，1明显错误，2基本可用但需提示，3独立完成，4能验证并解释取舍。14分且无验证 leakage 是练习通过线，不是 Apple 标准。

```python
import torch
import torch.nn.functional as F


def fit_classifier(x, y, vx, vy, epochs=30, batch_size=4, lr=0.1):
    mean = x.detach().mean(0)
    std = x.detach().std(0, unbiased=False).clamp_min(1e-6)
    tx = ((x - mean) / std).detach()
    with torch.random.fork_rng(devices=[]):
        model = torch.nn.Linear(x.shape[1], 1)
    torch.nn.init.zeros_(model.weight)
    torch.nn.init.zeros_(model.bias)
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    steps = 0
    model.train()
    for _ in range(epochs):
        for start in range(0, len(x), batch_size):
            opt.zero_grad(set_to_none=True)
            logits = model(tx[start : start + batch_size]).squeeze(-1)
            loss = F.binary_cross_entropy_with_logits(
                logits, y[start : start + batch_size].detach()
            )
            loss.backward()
            opt.step()
            steps += 1
    model.eval()
    with torch.no_grad():
        logits = model((vx - mean) / std).squeeze(-1)
        prob = logits.sigmoid()
        return dict(
            weight=model.weight.detach().squeeze(0).clone(),
            bias=model.bias.detach().clone(),
            mean=mean.clone(),
            std=std.clone(),
            prob=prob.clone(),
            nll=F.binary_cross_entropy_with_logits(logits, vy).item(),
            accuracy=((prob >= 0.5) == vy.bool()).float().mean().item(),
            steps=steps,
        )
```

## 简单测试怎么写

将实现和下面测试按顺序放入 solution.py，用安装了 PyTorch 的 Python 执行。先检查可手算的例子，再验证 gradient、输入保持和独立 validation split；不以一次随机精度作为唯一正确性证据。

```python
import math

small_x = torch.tensor([[-1.0], [1.0]])
small_y = torch.tensor([0.0, 1.0])
small = fit_classifier(
    small_x, small_y, small_x, small_y, epochs=1, batch_size=2, lr=0.1
)
assert torch.allclose(small["weight"], torch.tensor([0.05]), atol=1e-6)
assert torch.equal(small["bias"], torch.zeros(1))
assert torch.equal(small["mean"], torch.zeros(1))
assert torch.equal(small["std"], torch.ones(1))
expected_prob = torch.tensor([1 / (1 + math.exp(0.05)), 1 / (1 + math.exp(-0.05))])
assert torch.allclose(small["prob"], expected_prob, atol=1e-6)
assert math.isclose(small["nll"], math.log1p(math.exp(-0.05)), abs_tol=1e-6)
assert small["accuracy"] == 1.0 and small["steps"] == 1
assert set(small) == {
    "weight",
    "bias",
    "mean",
    "std",
    "prob",
    "nll",
    "accuracy",
    "steps",
}
x = torch.tensor(
    [[-3.0, 2.0], [-2.0, 2.0], [-1.0, 2.0], [1.0, 2.0], [2.0, 2.0], [3.0, 2.0]]
)
y = torch.tensor([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
saved = x.clone()
z = fit_classifier(x, y, x, y, epochs=0)
assert (
    z["steps"] == 0
    and z["accuracy"] == 0.5
    and math.isclose(z["nll"], math.log(2), rel_tol=1e-6)
)
r = fit_classifier(x, y, x, y, epochs=30, batch_size=4)
assert r["steps"] == 60 and r["accuracy"] == 1 and r["nll"] < z["nll"]
assert r["std"][1] == 1e-6 and torch.equal(x, saved) and not r["prob"].requires_grad
s = fit_classifier(x, y, x + 1000, 1 - y, epochs=30, batch_size=4)
assert torch.equal(r["weight"], s["weight"]) and torch.equal(r["mean"], s["mean"])
one = fit_classifier(
    torch.ones(1, 2),
    torch.zeros(1),
    torch.ones(1, 2),
    torch.zeros(1),
    epochs=1,
    batch_size=8,
)
assert one["steps"] == 1 and torch.isfinite(one["prob"]).all()
```

## 面试追问

说明如何把当前内存内实现扩到数据流、哪些统计只在 training set 拟合、怎样版本化标签与输入。不要把 CPU 小样本的收益当成 large model 结论。
