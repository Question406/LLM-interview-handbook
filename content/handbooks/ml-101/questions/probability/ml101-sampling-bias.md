---
id: ml101-sampling-bias
section: probability
order: 6
level: A
title: selection bias 和 survivorship bias 会怎样影响训练数据？
quick: >-
  selection bias 让进入样本的机制改变了数据分布，survivorship bias
  是只看留下来的对象而忽略退出者的一种情况。训练和验证若共用同一筛选机制，离线分数也可能一起乐观。先定义目标人群，再检查谁被采到、谁没有标签，最后才决定补采或加权。
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Andrew Gelman: Ethics and Statistics, survivorship selection example'
    url: >-
      https://sites.stat.columbia.edu/gelman/research/published/ChanceEthics8.pdf
    type: primary
---

这两类偏差都会让模型学到“被留下来的样本”的规律，未必是目标人群的规律。selection bias 来自样本进入数据集的机制；survivorship bias 特别指只保留持续存在或成功完成某个过程的对象。

用 S 表示是否被纳入样本，X 是特征，Y 是标签。训练数据来自 $P(X,Y\mid S=1)$，部署关心的却可能是 $P(X,Y)$。如果 S 与 X、Y 的关系没有处理，扩大同一种 sampling 方式只会更准确地估计被筛选的人群。Gelman 的[选择与 survivorship bias 案例](https://sites.stat.columbia.edu/gelman/research/published/ChanceEthics8.pdf)说明，按“仍被观察到”筛选，可以改变关联甚至误导因果解释。

比如做新用户留存预测，却只从“一个月后仍有登录”的日志中取训练集。已经流失的用户完全消失了，模型看不到最需要预测的失败情况；再随机切分这批幸存者做验证，也查不出这个缺口。这个例子说明要从注册时点定义完整队列，按统一的未来窗口补齐结果，再分别统计退出和缺失原因。

修正方法要看缺口能否识别。能补采时优先补覆盖；若已知入样概率且目标人群各区域都有非零入样机会，可以在相应假设下做逆概率加权。某一类人完全没入样时，权重不能凭空产生这类人的标签。只观察相关性也不能直接断言某个特征导致留存变化。

## 追问

**随机切训练集和测试集能消除 selection bias 吗？**
不能。随机切分保留了原样本的筛选机制，能评估的是同一筛选人群上的泛化。

**survivorship bias 一定让结果变好看吗？**
不一定。它改变的是观察到的分布，具体偏向哪个方向要看退出与结果如何关联，不能只凭名称判断符号。

**应该记录哪些数据帮助排查？**
记录候选总体、实际入样者、无标签者和退出者的数量及原因，并比较关键特征分布。未曝光样本没有点击标签时，也要区分“没看到”和“看到了但没点”。
