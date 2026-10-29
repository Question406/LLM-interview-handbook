---
id: drustz-d0d3fa4bbb08ded57e
section: openai
order: 145
level: A
title: ML Coding with NP and NN Layers
quick: original-structured-preparation-guide · ML Coding with NP and NN Layers
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/59c77c9a-49d0-4955-be64-91473bb8ab7f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# NumPy ML Coding：实现可组合的神经网络层

> 内容定位：公开标题只说明 “NP and NN Layers”，本地资料能确认 NumPy、1-NN 和 `Wx+b` 层题族，但没有当前 UUID 的完整接口。因此本指南提供最贴近已知考点的独立练习，不声称是会员原题。

## 建议还原的任务

只用 NumPy 实现最小的 `Linear`、`ReLU`、`Softmax` 与 `Sequential` 前向接口，严格标注 batch-first shape；再用固定 Linear 权重表达 L2 1-NN 的 exemplar scores。重点不是调用深度学习框架，而是广播、轴、参数方向和数值稳定。

```python
class Linear:
    def __init__(self, W, b):  # W: (in_dim, out_dim), b: (out_dim,)
        self.W, self.b = W, b

    def __call__(self, x):  # x: (..., in_dim)
        return x @ self.W + self.b


class ReLU:
    def __call__(self, x):
        return np.maximum(x, 0)


def softmax(x, axis=-1):
    z = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=axis, keepdims=True)
```



`Sequential` 只需按注册顺序把输出传给下一层；但应校验最后一维与 `W.shape[0]` 匹配。不要把权重约定写成一半 `W@x`、一半 `x@W`，否则样例中维度恰好相等时 bug 会被掩盖。

## 与 1-NN 的连接

给 prototypes `P:(n,d)`，构造 `Linear(W=2P.T, b=-sum(P²,axis=1))`。查询 `Q:(m,d)` 得到 `(m,n)` scores，最大的 exemplar 就是 L2 最近邻；softmax 可把它变成normalization分数，但最终 hard 预测仍取 exemplar argmax 后索引标签。例：P 有 3 行、d=2，则 W 必须是 `(2,3)`，而不是 `(3,2)`。

若追问训练，可为 Linear 增加缓存输入和 backward：`dW=x.T@dout`、`db=sum(dout,axis=0)`、`dx=dout@W.T`；ReLU backward 用 `x>0` mask。先明确 loss 是 sum 还是 mean，因为这会改变梯度缩放。当前标题没有证明一定要求backpropagation，所以应在面试时先确认，不把 follow-up 当成主题硬写。

有限差分可检查 backward：对某个参数加减很小的 ε，比较 `(L(θ+ε)-L(θ-ε))/(2ε)` 与解析梯度。随机输入不要正好落在 ReLU 的 0 点；误差判断用相对容差。参数更新则放在独立 optimizer 中，避免 layer 的 forward 同时修改权重而难以复用。

## 复杂度与验证

Linear 从 `(B,I)` 到 `(B,O)` 的时间 `O(BIO)`、输出空间 `O(BO)`；1-NN scorer 为 `O(mnd)`、score 空间 `O(mn)`。测试要使用 `I!=O`，覆盖任意前导 batch 维、极大 logits 的稳定 softmax、每行概率和为 1、空 batch、dtype 转换和有限差分梯度。对固定 1-NN 权重，还要与显式平方距离的 `argmin` 对拍。若原题随后提供不同 layer API，可保留这些 shape/数值不变量，再替换外层签名。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/59c77c9a-49d0-4955-be64-91473bb8ab7f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
