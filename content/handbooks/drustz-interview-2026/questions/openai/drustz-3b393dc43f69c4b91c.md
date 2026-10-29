---
id: drustz-3b393dc43f69c4b91c
section: openai
order: 35
level: A
title: Autograd Hillis Steele Scan
quick: locally-saved-research-summary · Autograd Hillis Steele Scan
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-research-summary
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
      https://www.1point3acres.com/interview/problems/company/openai/autograd-hillis-steele-scan
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## PracHub 2026-04-03 MLE tech screen：Debug MiniGPT + 手推 matmul 反向 + KV cache 实现

两 part，共约 1 小时（MLE technical screen，上报 2026-04-03）。Part A：decoder-only transformer 代码语法正确但autoregressivedecoding输出错误文本，要求 debug 并加 KV cache。考点：各阶段 tensor shape、causal mask 机制、attention 计算、位置编码、loss 对齐（next-token shift）、train/eval 模式、greedy/sampling。期望交付：找出并修复 bug（mask 错误/softmax 轴/√ $d_h$  缩放/位置编码/target shift/模式类 bug）、prefill 与 decode 干净分离、O(T) decode vs O( $T^{2}$ ) 重算、内存讨论（MQA/GQA/量化）。Part B：自定义 C=A@B 的 forward+backward：从  $C_{ij}$ = $Σ_r$   $A_{ir}$   $B_{rj}$  逐 index 推导 dA=dC@Bᵀ、dB=Aᵀ@dC，支持 batch/broadcast，用 torch.autograd.Function + save_for_backward，gradcheck 验证。追加 follow-up：Hillis-Steele prefix scan 的 O(n log n) work / O(log n) depth，及 scan vs reduction 何时划算；Blelloch scan 对比。

### 解题与准备提示

来源已给完整解法框架（见 detail）。补充：dA/dB 的 broadcast 情形要对被广播的轴求和还原形状；KV cache 只改 attention 的 K/V 拼接与 mask 的增量部分，Q 只算新 token。

---

## Autograd / 矩阵乘 forward+backward / Hillis-Steele scan——RS/RE 75min ML coding

官方题库：autograd-hillis-steele-scan，coding，medium，6 帖，75min，roles RS/RE，tech screen+onsite，tags: ml-knowledge/autograd/pytorch/parallel-algorithm，last_asked 2026-05-31。佐证：thread-1171922（2026-04-07《OpenAI onsite coding 新题 + 求 75min ML coding》）楼主明言 75min ML coding 与 'linear algebra or autograd' 相关；thread-1173645 回复区问 'AI coding I (autograd) 是 60min 还是 75min'——autograd 是 research 轨 AI coding 题池固定成员。OJ 镜像：'Implement Matrix Multiplication Forward and Backward (Autograd-Style) in PyTorch'。

### 解题与准备提示

（我的推断）实现 Tensor 类 + 计算图：matmul forward 存 (A,B)，backward dA=dC·Bᵀ, dB=Aᵀ·dC；拓扑序backpropagation；Hillis-Steele 部分=O(log n) 步并行前缀和（每步 stride 翻倍），考并行思维与 work-efficiency 对比 Blelloch scan；用 numpy/pytorch 张量原语表达'并行'。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/autograd-hillis-steele-scan)
- [相关来源](https://www.1point3acres.com/bbs/thread-1171922-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
