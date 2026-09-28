---
id: pdd-pick-relevant-chunks
section: agent
order: 163
level: A
title: 拼多多：检索返回很多相关内容时，如何选最相关的？
quick: >-
  先用类型过滤和 rerank，再按 token 预算做 MMR / 多样性去重，强制覆盖问题槽位。不要按相似度裸取
  top-k；冲突条款要都留下或升级澄清。
tags:
  - PDD
  - RAG
  - Rerank
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多日常实习 大模型算法一面分享
    url: https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377
    type: candidate-first-hand
  - title: The Use of MMR for Diversity-Based Reranking (Carbonell & Goldstein, SIGIR 1998)
    url: https://www.cs.cmu.edu/~jgc/publication/The_Use_MMP_Diversity_Based_Reranking_1998.pdf
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-15
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“如果检索返回了很多相关的内容，如何选择最相关的？”**

错法：按向量相似度裸取 top-$k$。「很多相关」往往是近重复和槽位不全：十条都在讲同一款颜色，运费和售后一块都没有。电商问答里，相关不等于可答。流程应是过滤 → rerank → 覆盖检查 → 多样性截断，冲突条款不能只留最高分。和切块、混合检索是同一条链路的后半段，见 `xiaohongshu-mmkg-chunk`。

## 过滤、rerank、槽位覆盖

先做权限 / 类目 / 时效过滤，过期活动和大盘政策不要和当前 SKU 条款混排。再用交叉编码器或业务 rerank，把「语义近但买不了」压下去。然后按问题实体做覆盖检查：价格、运费、售后、库存各至少一块；缺槽位就补召或改写 query，别把同分近重复填满窗口。token 预算内用 MMR 一类目标在相关与多样性之间折中：已选集合里太像的块让位给未覆盖槽位。不要把 MMR 背成唯一公式，核心是「相关且不重复且盖住问题」。

## 冲突必须显式，不能静默赢家

两个退货时效、两个价格，不能只留最高分。应并列展示来源或升级澄清 / 转人工。静默赢家会把幻觉伪装成检索成功，见 `xiaohongshu-rag-limits`。记录被丢块的原因（权限、过期、近重复、超预算），便于回调切块粒度和召回通道。引用必须能指回块 ID，生成后做引用完整性检查，和产物护栏同一思路。

## 和上下文预算一起截断

选块不是检索的终点。进模型前还要按预算截断：优先保留覆盖槽位的块，再留高 rerank 分的多样性块，工具 JSON 和重复政策全文最后进。超窗时的驱逐顺序见 `pdd-context-overflow`。评测不要只看 nDCG：看槽位覆盖率、冲突是否被抹掉、错误引用次数和最终任务成功。拼多多商品页、活动页、售后政策经常语义接近，向量分会挤在一起；这时「最相关」应定义成「能填完用户当前槽位的最小集合」，别取分最高的十条近重复。切块过碎会让覆盖检查永远缺半句，过宽又把冲突条款揉进同一块，选块问题和分块问题必须一起改，见 `xiaohongshu-mmkg-chunk`。记录丢块原因，下周调的是切块和通道，不是再把 $k$ 加大。

## 追问

- **为什么不用纯 top-$k$？** 近重复会占满窗口，关键槽位缺失；相似度高不等于可执行。
- **冲突为什么不能取最高分？** 条款冲突是业务风险，不是排序噪声。要并列或升级。
- **MMR 的 $\lambda$ 怎么定？** 在验证集上扫「重复率 vs 槽位覆盖」，按类目分档，不要写死一个数。
- **丢块要不要日志？** 要。否则无法判断是切块太碎、召回通道偏，还是 rerank 把售后打下去了。
