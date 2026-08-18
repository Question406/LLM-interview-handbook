---
id: ali-arch-hotspots
section: alibaba
order: 33
level: S
title: 通义/云智能方向：架构与系统高频题该怎么刷？
quick: >-
  白板优先：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 α、ZeRO
  显存手算、TP 切分。每题练到能画图讲 trade-off。
tags:
  - Alibaba
  - Architecture
  - Systems
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里系 2025-26 算法高频整理
    url: 'https://www.nowcoder.com/discuss/848942791164981248'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>白板优先：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 α、ZeRO 显存手算、TP 切分。每题练到能画图讲 trade-off。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>据阿里系公开面经统计，高频簇是：</p>
<ul>
<li>位置编码 RoPE（含长上下文外推）；</li>
<li>GQA/MQA 与推理带宽；</li>
<li>LoRA/QLoRA；</li>
<li>ZeRO 1/2/3 与显存构成；</li>
<li>推理：PagedAttention、量化、投机解码。</li>
</ul>
<p>这些题在手册 Architecture / Systems 章已有深卡；本卡作阿里定向刷题清单。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/848942791164981248" target="_blank" rel="noopener noreferrer">↗ 阿里系 2025-26 算法高频整理</a></div>
