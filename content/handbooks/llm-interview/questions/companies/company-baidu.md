---
id: company-baidu
section: companies
order: 4
level: A
title: 百度 AIDU：大模型与 Agent 岗该怎么定向准备？
quick: >-
  Post-training 重点准备 SFT/RLHF、DPO dynamics、GRPO/SimPO、Reasoning、MoE/Latent
  Attention、speculative decoding 与分布式训练；Agent 岗额外覆盖
  Tool/API、Memory、RAG+Agent、Multi-Agent 与 Eval。
tags:
  - Baidu
  - AIDU
  - 真题导航
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 百度 2027 AIDU 招聘
    url: 'https://talent.baidu.com/jobs/list?projectType=3&amp;recruitType=GRADUATE'
    type: legacy-reference
  - title: ↗ 腾讯/百度/MiniMax 公开面经汇总
    url: 'https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Post-training 重点准备 SFT/RLHF、DPO dynamics、GRPO/SimPO、Reasoning、MoE/Latent Attention、speculative decoding 与分布式训练；Agent 岗额外覆盖 Tool/API、Memory、RAG+Agent、Multi-Agent 与 Eval。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>百度相关公开面经有一个很好的深度样例：不是只问“DPO 是什么”，而会追 chosen probability 是否一定上升、length issue、SimPO、Base Model 如何增强 reasoning。</p><p>所以准备方式应以“追问树”为单位。例如 DPO：推导 → beta → chosen/rejected likelihood → length bias → hard negatives → SimPO/KTO → offline vs online RL。</p></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://talent.baidu.com/jobs/list?projectType=3&amp;recruitType=GRADUATE" target="_blank" rel="noopener noreferrer">↗ 百度 2027 AIDU 招聘</a><a href="https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279" target="_blank" rel="noopener noreferrer">↗ 腾讯/百度/MiniMax 公开面经汇总</a></div>
