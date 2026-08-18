---
id: ali-rag-eval
section: alibaba
order: 14
level: S
title: RAG 如何提升生成质量？怎样评估一个 RAG 是否 work？
quick: 用检索证据约束生成，降低过时与幻觉。评估要拆开：检索（召回/精确/nDCG）、生成（忠实度/引用正确率）、端到端任务成功率，并做失败归因。
tags:
  - Alibaba
  - RAG
  - Eval
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>用检索证据约束生成，降低过时与幻觉。评估要拆开：检索（召回/精确/nDCG）、生成（忠实度/引用正确率）、端到端任务成功率，并做失败归因。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>相对“裸生成”，RAG 把外部知识以证据形式注入上下文；与传统检索+模板不同，生成器需在证据上做综合与拒答。</p>
<p>评估分层：</p>
<ol>
<li>检索：Recall@k、Hit、nDCG、路由正确率；</li>
<li>生成： faithfulness、引用可追溯、拒答率；</li>
<li>业务：任务成功、人工满意度、延迟与成本。</li>
</ol>
<p>淘天追问常落到：切分策略、混合检索、rerank、以及“检索错还是生成幻觉”的归因。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
