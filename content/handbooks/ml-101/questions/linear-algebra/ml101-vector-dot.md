---
id: ml101-vector-dot
section: linear-algebra
order: 1
level: A
title: "向量点积、夹角和余弦相似度有什么关系？"
quick: "点积同时受长度和方向影响；两个非零向量的点积除以各自 L2 范数，就得到夹角余弦。若只想比较方向，可以用余弦相似度；若长度也携带有用信息，直接点积会保留这部分差异，零向量要单独处理。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "NumPy: numpy.dot"
    url: https://numpy.org/doc/stable/reference/generated/numpy.dot.html
    type: primary
  - title: "SciPy: scipy.spatial.distance.cosine"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cosine.html
    type: primary
---

点积把长度和方向合在一个数里，余弦相似度则把长度除掉，只比较方向。例如 $(1,0)$ 和 $(10,0)$ 同方向，余弦都是 1，但它们与 $(1,0)$ 的点积分别是 1 和 10。

对两个实向量 $u,v\in\mathbb R^d$，点积与夹角的关系是

$$
u^\top v=\sum_{i=1}^{d}u_iv_i
=\|u\|_2\|v\|_2\cos\theta.
$$

这里 $d$ 是维数，$u_i,v_i$ 是第 $i$ 维坐标，$\theta$ 是两个非零向量的夹角，$\|\cdot\|_2$ 表示向量长度。因此余弦相似度为

$$
\operatorname{sim}_{\cos}(u,v)
=\frac{u^\top v}{\|u\|_2\|v\|_2}.
$$

它在 $[-1,1]$ 内：1 表示同向，0 表示正交，-1 表示反向。若向量只含非负坐标，就不会出现负余弦。实向量点积的计算约定见 [NumPy dot 文档](https://numpy.org/doc/stable/reference/generated/numpy.dot.html)。

选择时先问长度有没有业务含义。比如检索已经明确采用单位长度向量，就可以用点积完成余弦排序；如果向量长度本来代表强度，归一化会丢掉它。零向量没有方向，不能直接除以零，要在输入检查中约定报错、跳过或给默认结果。

## 追问

**归一化后，欧氏距离和余弦排序还一样吗？**
一样。对单位向量，有 $\|u-v\|_2^2=2-2u^\top v=2-2\operatorname{sim}_{\cos}(u,v)$，所以距离越小，余弦越大。这个等价关系要求两边都已归一化。

**库里叫 cosine 的函数返回的就是相似度吗？**
要看接口。SciPy 的 `scipy.spatial.distance.cosine` 返回 $1-\operatorname{sim}_{\cos}(u,v)$，是余弦距离，值小更相近，见 [官方定义](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cosine.html)。排序方向不能用反。
