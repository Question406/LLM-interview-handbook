---
id: pt-dapo
section: posttrain
order: 19
level: S
title: DAPO 四个关键修改分别解决什么？
quick: >-
  Clip-Higher 增强正向 exploration；Dynamic Sampling 过滤全对/全错无效 groups；Token-level PG
  改变长短 response 的权重；Overlong Reward Shaping 缓解硬截断带来的不连续噪声。
tags:
  - DAPO
  - GRPO
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ DAPO
    url: 'https://arxiv.org/abs/2503.14476'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Clip-Higher 增强正向 exploration；Dynamic Sampling 过滤全对/全错无效 groups；Token-level PG 改变长短 response 的权重；Overlong Reward Shaping 缓解硬截断带来的不连续噪声。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>1. Clip-Higher：</b>使用 asymmetric clip，让极低概率但高 advantage 的 token 有更大的上升空间，避免 rare good exploration 刚出现就被上界限制。</p><p><b>2. Dynamic Sampling：</b>生成后过滤 accuracy=0 或 1 的 group，减少 zero-variance batch 对 compute 的浪费。注意这是 current-policy dependent 的动态过滤，不是永久删除 prompt。</p><p><b>3. Token-level Policy Gradient：</b>把 loss reduction 更靠近“每 token 等权”，避免每条 response 固定总权重导致长序列单 token 权重变小。</p><p><b>4. Overlong Reward Shaping：</b>如果长度稍超 max 就把 reward 从 1 突然置 0，会制造巨大不连续。用更平滑的 overlong handling 可以减少 truncation noise。</p><p>DAPO 的启示是：long-CoT RL 的性能不仅取决于“主算法名字”，还由 clipping、data filtering、loss reduction、length handling 这些训练细节共同决定。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Dynamic Sampling 会不会导致 curriculum 偏差？</summary><div class="follow-answer"><p>会有风险。如果长期只保留当前可解题，可能忽略新 domain 或超难题。因此要配合 coverage quota，并周期性重新探测 0% bucket。</p></div></details><details class="followup"><summary>Clip-Higher 为什么和 entropy collapse 有关？</summary><div class="follow-answer"><p>如果 rare token 的正向概率提升很快被裁掉，policy 更容易锁定已有高概率模式；放宽正向上界能延长对新行为的放大空间。</p></div></details><details class="followup"><summary>Token-level loss 一定比 response-level 好吗？</summary><div class="follow-answer"><p>不一定，取决于目标。如果你关心每个 sequence 等权，response-level 也有合理性；关键是明确 length weighting。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2503.14476" target="_blank" rel="noopener noreferrer">↗ DAPO</a></div>
