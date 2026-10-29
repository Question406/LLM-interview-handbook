---
id: drustz-f2b96aa47c77ff1063
section: openai
order: 163
level: A
title: Transformer Model Debugging
quick: original-structured-preparation-guide · Transformer Model Debugging
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
      https://www.1point3acres.com/interview/problems/73bacbfd-0f76-432a-a927-484ad38107a4
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Transformer 模型调试：用不变量缩小故障范围

> 内容定位：标题与本地高频 Transformer 调试题族一致；本地可运行练习能佐证一套具体测试方法，但不能证明当前 UUID 使用相同代码或同样四个 bug。本指南侧重“怎样调试”，所有示例均为原创同族练习。

## 题目要做什么

面对一个输出不正确或训练不稳定的 Transformer，不靠盲读数百行源码，而是把模型拆成 embedding、attention、residual/normalization、MLP、LM head 和训练循环，逐层建立可自动验证的不变量，定位第一个出错边界。

## 数据或需求

假设输入 `idx.shape=(B,T)`，隐藏状态 `(B,T,C)`，每头维度 `D=C/H`。需要检查三类正确性：shape 正确、数值有限、语义正确。shape 通过仍可能存在未来信息泄漏、softmax 轴错误、梯度断开或训练/评估模式混用。

## 例子

因果性测试无需知道正确 logits。复制输入，只改变位置 `j` 的 token；则所有 `t < j` 的输出必须保持不变：

```text
y1 = model(x).logits
x2 = x; x2[j] = another_token
y2 = model(x2).logits
assert_close(y1[:j], y2[:j])
```



如果断言失败，优先查 mask 的方向、应用时机和广播维度，而不是先调学习率。

## 解法

建立一张模块检查表。Embedding：位置索引从 0 到 `T-1`，token 与 position embedding 都进入计算图。Attention：除以 `sqrt(D)`，mask 在 softmax 前把非法位置设为负无穷，softmax 在 key 轴。Residual：输入输出 shape 一致，LayerNorm 作用在最后一维。MLP：`C -> 4C -> C`。输出头：若与 embedding 权重绑定，应计算 `x @ E.T`。训练循环必须满足 `zero_grad -> forward -> backward -> step`。

测试顺序按信息量排列：先检查 NaN/Inf 和 shape；再让 attention 与 `scaled_dot_product_attention(..., is_causal=True)` 对拍；接着验证梯度可达、参数更新；最后在几十个 token 上overfitting并看生成。每修一个 bug 就保留一个“修复前必失败、修复后通过”的测试，这比只展示最终 loss 更有说服力。

## 复杂度

单层 self-attention 时间 `O(BT²C)`、权重内存 `O(BHT²)`；逐层 hook 会额外保存 `O(LBTC)` 激活，调试时应缩小批量和序列。参考实现对拍的量级与一次 forward 相同。

## 边界与验证

- 全相同 token 也必须产生有限输出；
- `T=1` 时 mask 退化为 `1×1`；
- mixed precision 下 `-inf`、大负数和 NaN 行为要单测；
- 只检查平均 loss 会漏掉单头或单层失效；
- 使用随机测试时固定 seed，并说明容差与 dtype。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/73bacbfd-0f76-432a-a927-484ad38107a4)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
