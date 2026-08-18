---
id: agent-tool-routing
section: agent
order: 4
level: S
title: 有 1000 个 Tools，如何做 Tool Routing？
quick: >-
  多阶段路由：cheap lexical/embedding/classifier 先 1000→几十，再用小模型/reranker 选
  top-k，最后主模型基于 task state 决定调用；最终指标必须看 downstream success 而非只看 retrieval
  recall。
tags:
  - Tool Routing
  - Retrieval
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>多阶段路由：cheap lexical/embedding/classifier 先 1000→几十，再用小模型/reranker 选 top-k，最后主模型基于 task state 决定调用；最终指标必须看 downstream success 而非只看 retrieval recall。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>一个常见层级：</p><ol><li><b>Namespace/category routing：</b>先判断 calendar / code / finance / web / files 等大类。</li><li><b>Cheap retrieval：</b>BM25/embedding 从 1000 个 tool descriptions 取 top-30。</li><li><b>Rerank/router：</b>小模型看 task、state 与 schema，取 top-3~5。</li><li><b>Main policy：</b>决定是否调用、哪个 tool、参数是什么。</li></ol><p>训练 router 时 random negative 太简单，最好加入 semantic hard negatives：名字相似但 capability 边界不同的工具；还要加入 <b>do-not-call</b> / ask-user / no-tool 选项，否则 router 会有“工具总要选一个”的偏差。</p><p>Eval 除 Recall@K，还要测 wrong-tool cost、downstream task success、token savings、latency，以及 selected candidate set 对主模型的干扰。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么 Recall@K 高还可能性能差？</summary><div class="follow-answer"><p>Top-k 里混入多个语义相近但危险/干扰工具会提高主模型误选率；candidate quality 不是简单 recall。</p></div></details><details class="followup"><summary>Router 应不应该是 1B/2B 小模型？</summary><div class="follow-answer"><p>如果调用频繁、工具多、主模型 token 成本高，小模型 router 很有价值；但要用 end-to-end success 检验，避免 routing error 抵消节省。</p></div></details></div>
