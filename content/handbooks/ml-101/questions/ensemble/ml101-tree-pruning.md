---
id: ml101-tree-pruning
section: ensemble
order: 2
level: S
title: 决策树为什么容易 overfitting？怎么剪枝？
quick: >-
  树不断分裂会形成只覆盖少量样本的小区域，把噪声也当成规律。可以提前限制深度、最小叶子样本数或分裂收益，也可以先长树再用成本复杂度剪枝；控制强度要按独立验证表现选择。
tags:
  - Machine Learning
  - ensemble
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Decision Trees'
    url: 'https://scikit-learn.org/stable/modules/tree.html'
    type: primary
---

深树能为很少几个样本单独制定规则，所以对标签噪声和样本扰动很敏感。例如一个误标记录可能被深树用多次切分隔出来，训练分数因此提高，但新数据不会遵守这个偶然规则。

预剪枝在生长时设限制，比如最大深度、每片叶子至少多少样本，以及分裂要带来多少收益。后剪枝则先训练较大的树，再比较删掉子树后，拟合误差和复杂度如何变化。

成本复杂度剪枝把目标写成：

$$R_\alpha(T)=R(T)+\alpha|T|.$$

$T$ 是一棵树，$R(T)$ 是叶子上的加权训练不纯度或损失，$|T|$ 是叶子数，$\alpha$ 表示每多一片叶子的成本。提高 $\alpha$ 会更偏向小树。实际根据剪枝路径得到候选值，再用验证或交叉验证选取。

训练分数降低是预期现象，关键看独立验证是否改善，也要检查重要小群体是否被过粗的叶子混在一起。

## 面试追问

**最大深度和最小叶子样本数有什么区别？**
深度限制一条判断路径最多问多少次；最小叶子样本数限制每个局部区域至少包含多少训练样本。相同深度下，后者仍可避免极小叶子。

**特征缩放能防止树 overfitting 吗？**
对常规精确阈值树，单调缩放通常保持样本顺序和候选分组，无法有效控制复杂度。应直接调整树结构约束、sampling 或正则参数。
