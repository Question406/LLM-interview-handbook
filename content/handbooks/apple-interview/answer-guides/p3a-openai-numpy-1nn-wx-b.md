---
id: p3a-openai-numpy-1nn-wx-b
kind: coding
situation: 逐点计算最 nearest neighbors 成本高且难向 quantization。
task: 把平方欧氏1-NN 写成线性得分。
approach: 展开距离，去掉对候选相同的查询范数。
result: 随机小样本对照暴力距离，保留平票契约。
---

## 可以这样回答

逐点计算最 nearest neighbors 成本高且难向 quantization。

展开平方欧氏距离后，查询自身范数对所有候选都相同，可以去掉，剩下比较 2q·x - ||x||²。把训练点的两倍作权重、负平方范数作偏置，一次 Wx + b 再 argmax 就得到 1-NN。L1 没有同样的点积展开，要另算广播距离，并注意中间内存。

测试还要满足这个条件：随机小样本对照暴力距离，保留平票契约。
