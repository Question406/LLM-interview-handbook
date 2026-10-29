---
id: drustz-1e0ce2124ab6b5a6b2
section: openai
order: 146
level: A
title: ML Debugging with Transformer Model
quick: original-structured-preparation-guide · ML Debugging with Transformer Model
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
      https://www.1point3acres.com/interview/problems/da45a11e-5cc2-404c-8a37-f13f235bb9bb
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# ML 调试：Transformer 能运行，但学不会

> 内容定位：本地题库确认 Transformer bug hunt 是高频题族，本地还有一份可运行的 MiniGPT 同族练习。当前 UUID 的原始 400 行代码并未取得，因此下面讲的是基于本地练习的原创调试流程，不是对会员 starter code 的逐行还原。

## 题目要做什么

给定一份语法正确、forward 也能跑通的 decoder-only Transformer，训练 loss 却几乎不下降，生成结果也异常。要求在有限时间内定位根因、写最小修复，并用测试证明修复不是“碰巧让 loss 降了”。

## 数据或需求

本地练习使用形状为 `(B,T)` 的 token/target，embedding 维度 `C`，多头数 `H`，attention 张量为 `(B,H,T,T)`。代表性故障包括：位置向量没有加入、causal mask 用乘零而非 softmax 前填 `-inf`、训练循环漏掉 `backward()`、权重绑定输出头漏转置但因 `V == C` 恰好不报错。

## 例子

错误写法 `scores = scores * lower_triangle` 会把未来位置变成 0；如果合法位置的 score 是负数，softmax 反而会给未来 token 正概率。正确做法是：

```python
scores = scores.masked_fill(mask == 0, float("-inf"))
probs = scores.softmax(dim=-1)
```



## 解法

先建立症状基线：初始cross entropy应接近 `log(V)`，记录若干步后的 loss、梯度是否存在和参数是否变化。然后从最便宜的检查开始：

1. 写出每层 shape ledger，尤其是 `q,k,v` 的 reshape/transpose；
2. 改变最后一个 token，断言之前位置的 logits 完全不变，验证因果性；
3. `loss.backward()` 后检查每个应训练参数的 `grad is not None`；
4. 保存 step 前后的参数，确认 optimizer 确实更新；
5. 用 PyTorch SDPA 对比一个小 attention 输入；
6. 用极小 batch overfitting，区分实现 bug 与数据/容量问题。

修复时一次只改一个点并添加回归测试。不要先重写整份模型，否则难以证明哪个变化解决了问题。

## 复杂度

全 attention 的时间为 `O(BT²C)`，attention 权重空间为 `O(BHT²)`；MLP 时间约 `O(BTC²)`。调试测试使用很小的 `B,T`，成本远低于完整训练。

## 边界与验证

- `V == C` 会掩盖输出头转置错误，测试必须让二者不等；
- mask 需同时检查设备、dtype 和 `T=1`；
- dropout 测因果性时要切到 `eval()`；
- loss 下降不代表没有未来泄漏；
- 真实题若指定四个不同 bug，应保留方法论，替换具体答案。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/da45a11e-5cc2-404c-8a37-f13f235bb9bb)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
