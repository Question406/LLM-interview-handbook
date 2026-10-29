---
id: afm-rm-train-pipeline-code
section: alignment
order: 132
level: S
title: 模拟 B 编程：从偏好特征训练一个 RM，并输出独立验证指标
quick: >-
  共享线性 scorer 对两条回答打分，差值进入 soft preference BCE；训练变换只拟合训练回答。验证返回 NLL、Brier
  和严格偏好准确率，软 tie 不强制当 A 或 B。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: 'PyTorch: Optimizing Model Parameters'
    url: >-
      https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
    type: primary
---

## 题目描述

你已经拿到回答的数值特征和人工 preference labels。请用 PyTorch 训练一个**线性 reward model（RM）**，并在独立 validation set 上计算预测概率和指标。你不需要读取文本、提取特征或训练 LLM。

本题是原创模拟练习，接口、训练规则与指标定义均为教学约定。建议用 25 分钟实现；完整的 45 分钟模拟见 `afm-mock-screen-b`。下面的题面已经包含独立完成本题所需的信息。

### 1. 一条样本表示什么？

每条样本包含**同一个 prompt 的两个候选回答 A、B**，以及人工更喜欢 A 的比例。

- `a[i]` 是第 i 条训练样本中回答 A 的 D 维特征；`b[i]` 是同一 prompt 下回答 B 的特征。特征可以描述证据支持度、回答长度等，本题只把它们当作已给定的数值。
- `q[i]` 是 A 的 soft preference target。例如 4 人中 3 人选 A，可以记为 `q[i]=0.75`；`1.0` 表示全部选 A，`0.0` 表示全部选 B。
- `q[i]=0.5` 表示人工偏好比例相等。这不一定证明两个回答质量相同；本题将它作为 soft target 参与训练，不将它改写成某一方获胜。
- **`q` 不是 sample weight。** 每条 pair 在 loss 中的权重相同。
- Validation 数据 `va[j]`、`vb[j]`、`vq[j]` 具有相同含义。它们来自独立 prompts，不能参与训练或拟合 preprocessing statistics。

### 2. 实现接口与输入

实现以下函数，参数顺序必须保持一致：

```text
fit_pairwise_rm(a, b, q, va, vb, vq, epochs=80, lr=0.1) -> dict
```

| 参数 | 类型与 shape | 含义 |
| --- | --- | --- |
| `a`, `b` | `torch.float32` CPU tensors，均为 `[N,D]` | N 条训练 pairs 的 A、B 特征 |
| `q` | `torch.float32` CPU tensor，`[N]` | 训练 pairs 中偏好 A 的比例 |
| `va`, `vb` | `torch.float32` CPU tensors，均为 `[M,D]` | M 条 validation pairs 的 A、B 特征 |
| `vq` | `torch.float32` CPU tensor，`[M]` | Validation pairs 中偏好 A 的比例 |
| `epochs` | 非负整数 | 完整训练集的 SGD update 次数；允许为 0 |
| `lr` | 正的 Python float | SGD learning rate |

保证 `N,M,D >= 1`，特征均为有限值，`q` 和 `vq` 的值均在 `[0,1]`。假设数值规模使本题 float32 运算保持有限，不要求实现非法输入检查。不得原地修改输入，也不得向输入 tensors 写入 gradients。

### 3. 必须实现的训练行为

为使不同实现的结果可以比较，本题规定以下训练流程，不自行选择模型、optimizer 或 stopping rule：

1. 将训练回答 `a`、`b` 沿第 0 维合并成 `[2N,D]`，按 feature dimension 计算 `mean` 和 population standard deviation。即标准差使用分母 `2N`，对应 `unbiased=False`；每一维的 `std` 最小设为 `1e-6`。
2. 所有回答使用同一组训练统计做 standardization：`z(x)=(x-mean)/std`。Validation 只能应用该变换，不能重新拟合统计。
3. 使用一个共享的 `torch.nn.Linear(D,1,bias=False)` 作为 scorer，所有 weight 初始化为 0。A、B 不能使用两个独立模型。
4. 一条 pair 的 logit 是两个 reward 的差：`logit=r(z(a))-r(z(b))`；模型预测 A 获胜的概率为 `sigmoid(logit)`。
5. Loss 是所有训练 pairs 的 **mean soft-label BCE**。对第 i 条，若预测概率为 $p_i$、target 为 $q_i$，其 loss 为：

$$-q_i\log p_i-(1-q_i)\log(1-p_i).$$

可直接使用 `binary_cross_entropy_with_logits`，以 logits 计算该 loss。每轮进行一次 full-batch SGD update，不使用 momentum、weight decay、mini-batch、early stopping 或 validation-based model selection。

训练前设置 `model.train()`；每次 update 按 `zero_grad → backward → step` 执行。恰好执行 `epochs` 次；`epochs=0` 时仍需拟合训练统计并返回零初始化模型的 validation 结果。最后使用 `model.eval()` 和 `torch.no_grad()` 做 validation。

### 4. 返回什么？

返回包含以下 7 个字段的字典。返回的 tensors 均为 CPU float32 tensors，且不保留 autograd graph。

| 字段 | 类型与 shape | 定义 |
| --- | --- | --- |
| `weight` | tensor `[D]` | **Standardized feature space** 中的最终 scorer weight，不转换回原始特征空间 |
| `mean` | tensor `[D]` | 从训练回答拟合的逐维 mean |
| `std` | tensor `[D]` | 从训练回答拟合、并应用 `1e-6` 下限后的逐维 std |
| `prob` | tensor `[M]` | 每条 validation pair 中 A 获胜的预测概率 |
| `nll` | Python float | Validation 上的 mean soft-label BCE，使用自然对数 |
| `brier` | Python float | Validation 上 `mean((prob-vq)**2)` |
| `strict_acc` | Python float 或 `None` | 仅在 `vq != 0.5` 的 validation pairs 上计算 binary preference accuracy；若没有这些 pairs，返回 `None` |

`strict_acc` 的具体规则：预测 `prob > 0.5` 时选 A，否则选 B；target `vq > 0.5` 时选 A，否则选 B。**当预测恰好为 `0.5` 时，本题约定选 B**，并不表示模型对 B 有更高 confidence。`vq=0.5` 的 pairs 仍计入 `nll` 和 `brier`，只从 `strict_acc` 中排除。

这里的 `brier` 是预测概率与已给定 soft target 的均方差，不是逐个 annotator 的 binary Brier score，也不能单独证明模型已经 calibrated。

### 5. 输入输出示例：不训练与训练一步

以下方括号表示 tensors 的数值；调用前将它们转换成上述 dtype 和 shape：

```text
a  = [[ 1.0]]     b  = [[-1.0]]     q  = [1.0]
va = [[ 1.0]]     vb = [[-1.0]]     vq = [1.0]
```

这里 `N=M=D=1`，训练与 validation 使用相同数值只是为了手算；真实数据仍需按 prompt 隔离。

**调用 A：** `fit_pairwise_rm(a,b,q,va,vb,vq,epochs=0,lr=0.1)` 应返回：

```text
{
  weight: tensor([0.0]),
  mean: tensor([0.0]),
  std: tensor([1.0]),
  prob: tensor([0.5]),
  nll: 0.69314718,       # log(2)
  brier: 0.25,
  strict_acc: 0.0        # target 选 A；prob=0.5 按约定选 B
}
```

**调用 B：** 对相同输入设置 `epochs=1, lr=0.1`，应得到近似结果：

```text
{
  weight: tensor([0.1]),
  mean: tensor([0.0]),
  std: tensor([1.0]),
  prob: tensor([0.549834]),
  nll: 0.598139,
  brier: 0.202649,
  strict_acc: 1.0
}
```

浮点结果允许 `atol=1e-6, rtol=1e-6` 的误差，不要求打印格式一致。

### 6. 必须覆盖的特殊情况

- **Constant feature：** 如果某维训练特征全部相同，返回该维 `std=1e-6`，不得产生 `NaN`。
- **Soft target：** `q=0.75` 必须直接作为 BCE target，不能先转成 `1.0`；`q=0.5` 也不能从 training loss 中删除。
- **全部 validation targets 为 `0.5`：** 仍返回有效的 `prob`、`nll`、`brier`，但 `strict_acc=None`。
- **Validation isolation：** 训练输入与 hyperparameters 不变时，替换全部 validation features 或 labels，不应改变返回的 `weight`、`mean`、`std`。

## 解题思路与参考答案

先冻结训练变换，差特征可等价实现共享线性 RM。bias 在奖励差中抵消，所以去掉 bias；均值也抵消，但仍返回训练变换方便检查契约。此 small model 检验训练工程，不代表 transformer RM 的能力或可识别尺度已经解决。

```python
import torch
import torch.nn.functional as F


def fit_pairwise_rm(a, b, q, va, vb, vq, epochs=80, lr=0.1):
    train = torch.cat([a, b], dim=0).detach()
    mean = train.mean(0)
    std = train.std(0, unbiased=False).clamp_min(1e-6)
    delta = ((a - mean) / std - (b - mean) / std).detach()
    with torch.random.fork_rng(devices=[]):
        model = torch.nn.Linear(a.shape[1], 1, bias=False)
    torch.nn.init.zeros_(model.weight)
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    model.train()
    for _ in range(epochs):
        opt.zero_grad(set_to_none=True)
        loss = F.binary_cross_entropy_with_logits(model(delta).squeeze(-1), q.detach())
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        logits = model((va - mean) / std - (vb - mean) / std).squeeze(-1)
        prob = logits.sigmoid()
        strict = vq != 0.5
        accuracy = (
            ((prob[strict] > 0.5) == (vq[strict] > 0.5)).float().mean().item()
            if strict.any()
            else None
        )
        return dict(
            weight=model.weight.detach().squeeze(0).clone(),
            mean=mean.clone(),
            std=std.clone(),
            prob=prob.clone(),
            nll=F.binary_cross_entropy_with_logits(logits, vq).item(),
            brier=((prob - vq) ** 2).mean().item(),
            strict_acc=accuracy,
        )
```

## 简单测试怎么写

将实现和下面测试按顺序放入 solution.py，用安装了 PyTorch 的 Python 执行。先检查可手算的例子，再验证 gradient、输入保持和独立 validation split；不以一次随机精度作为唯一正确性证据。

```python
import math

# Independent one-step check: delta=2, dloss/dweight=(0.5-1)*2=-1.
one = torch.tensor([[1.0]])
minus_one = -one
hard = torch.tensor([1.0])
step = fit_pairwise_rm(one, minus_one, hard, one, minus_one, hard, epochs=1, lr=0.1)
assert torch.allclose(step["weight"], torch.tensor([0.1]), atol=1e-6)
expected_p = 1.0 / (1.0 + math.exp(-0.2))
assert math.isclose(step["prob"].item(), expected_p, abs_tol=1e-6)
assert math.isclose(step["nll"], math.log1p(math.exp(-0.2)), abs_tol=1e-6)
assert math.isclose(step["brier"], (expected_p - 1.0) ** 2, abs_tol=1e-6)
assert step["strict_acc"] == 1.0

# q=0.75 must remain a soft target: gradient=-0.5, weight=0.05.
soft = torch.tensor([0.75])
soft_step = fit_pairwise_rm(
    one, minus_one, soft, one, minus_one, soft, epochs=1, lr=0.1
)
assert torch.allclose(soft_step["weight"], torch.tensor([0.05]), atol=1e-6)
soft_p = 1.0 / (1.0 + math.exp(-0.1))
soft_nll = 0.75 * math.log1p(math.exp(-0.1)) + 0.25 * math.log1p(math.exp(0.1))
assert math.isclose(soft_step["prob"].item(), soft_p, abs_tol=1e-6)
assert math.isclose(soft_step["nll"], soft_nll, abs_tol=1e-6)
assert math.isclose(soft_step["brier"], (soft_p - 0.75) ** 2, abs_tol=1e-6)

# Equal preference retains zero weights from zero initialization.
half = torch.tensor([0.5])
tied = fit_pairwise_rm(one, minus_one, half, one, minus_one, half, epochs=1)
assert torch.equal(tied["weight"], torch.zeros(1))
assert tied["strict_acc"] is None and tied["brier"] == 0.0

# Input features may require gradients, but this interface must not fill them.
feature = one.clone().requires_grad_()
label = hard.clone().requires_grad_()
checked = fit_pairwise_rm(
    feature, minus_one, label, feature, minus_one, label, epochs=1
)
assert feature.grad is None and label.grad is None
assert set(checked) == {"weight", "mean", "std", "prob", "nll", "brier", "strict_acc"}
for key in ("weight", "mean", "std", "prob"):
    assert not checked[key].requires_grad

x = torch.tensor([[1.0], [2.0], [3.0]])
y = -x
q = torch.ones(3)
saved = x.clone()
z = fit_pairwise_rm(x, y, q, x, y, q, epochs=0)
assert torch.equal(z["weight"], torch.zeros(1)) and torch.equal(
    z["prob"], torch.full((3,), 0.5)
)
assert math.isclose(z["nll"], math.log(2), rel_tol=1e-6) and z["brier"] == 0.25
assert z["strict_acc"] == 0.0
r = fit_pairwise_rm(x, y, q, x, y, q)
assert r["strict_acc"] == 1 and r["nll"] < z["nll"] and r["weight"].item() > 0
assert torch.equal(x, saved) and not r["prob"].requires_grad
shift = fit_pairwise_rm(x, y, q, x + 1000, y + 1000, torch.zeros(3))
assert torch.equal(r["weight"], shift["weight"]) and torch.equal(
    r["mean"], shift["mean"]
)
assert torch.equal(r["std"], shift["std"])
tie = fit_pairwise_rm(x, x, torch.full((3,), 0.5), x, x, torch.full((3,), 0.5))
assert tie["strict_acc"] is None and torch.isfinite(tie["std"]).all()
constant = fit_pairwise_rm(
    torch.ones(1, 2),
    torch.ones(1, 2),
    torch.ones(1),
    torch.ones(1, 2),
    torch.ones(1, 2),
    torch.ones(1),
    epochs=1,
)
assert torch.all(constant["std"] == 1e-6) and constant["prob"].item() == 0.5
```

## 面试追问

说明如何把当前内存内实现扩到数据流、哪些统计只在 training set 拟合、怎样版本化标签与输入。不要把 CPU 小样本的收益当成 large model 结论。
