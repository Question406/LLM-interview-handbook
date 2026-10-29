---
id: company-source-index
section: companies
order: 20
level: A
title: 真实面经与核心原论文：建议怎么用这些链接复习？
quick: "先看真实面经确认会怎么问，再读原论文补机制和公式，最后自己做 3 到 5 层追问树。别拿二手总结去倒推，把整篇论文背下来。"
tags:
  - Sources
  - Study Guide
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ Transformer
    url: 'https://arxiv.org/abs/1706.03762'
    type: legacy-reference
  - title: ↗ PPO
    url: 'https://arxiv.org/abs/1707.06347'
    type: legacy-reference
  - title: ↗ GAE
    url: 'https://arxiv.org/abs/1506.02438'
    type: legacy-reference
  - title: ↗ DPO
    url: 'https://arxiv.org/abs/2305.18290'
    type: legacy-reference
  - title: ↗ DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
  - title: ↗ DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: legacy-reference
  - title: ↗ DAPO
    url: 'https://arxiv.org/abs/2503.14476'
    type: legacy-reference
  - title: ↗ Dr.GRPO
    url: 'https://arxiv.org/abs/2503.20783'
    type: legacy-reference
  - title: ↗ GSPO
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
  - title: ↗ DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: legacy-reference
  - title: ↗ LoRA
    url: 'https://arxiv.org/abs/2106.09685'
    type: legacy-reference
  - title: ↗ QLoRA
    url: 'https://arxiv.org/abs/2305.14314'
    type: legacy-reference
  - title: ↗ ZeRO
    url: 'https://arxiv.org/abs/1910.02054'
    type: legacy-reference
  - title: ↗ FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
  - title: ↗ vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: legacy-reference
  - title: ↗ Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: legacy-reference
  - title: ↗ MCP
    url: 'https://modelcontextprotocol.io/'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先看真实面经确认会怎么问，再读原论文补机制和公式，最后自己做 3 到 5 层追问树。别拿二手总结去倒推，把整篇论文背下来。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>我会按这个顺序复习：<b>真题原帖 → 找到不会的节点 → 读论文对应 section → 关掉资料白板讲 → 自己生成追问 → 用实现或小实验验证。</b>下面这张表按类别列了推荐的原始材料，卡在哪一类，就去读那一类。</p><div class="table-wrap"><table><thead><tr><th>类别</th><th>推荐原始材料</th></tr></thead><tbody><tr><td>PPO / GAE</td><td>PPO 1707.06347；GAE 1506.02438</td></tr><tr><td>Preference</td><td>DPO 2305.18290；SimPO 2405.14734；KTO 2402.01306</td></tr><tr><td>Reasoning RL</td><td>DeepSeekMath 2402.03300；R1 2501.12948；DAPO 2503.14476；Dr.GRPO 2503.20783；GSPO 2507.18071</td></tr><tr><td>Architecture</td><td>Transformer；RoPE；GQA；DeepSeek-V3；LoRA/QLoRA</td></tr><tr><td>Systems</td><td>ZeRO；FlashAttention；vLLM</td></tr><tr><td>Agent</td><td>Anthropic Building Effective Agents / Skills / Context / Evals；MCP 官方规范</td></tr></tbody></table></div></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/1706.03762" target="_blank" rel="noopener noreferrer">↗ Transformer</a><a href="https://arxiv.org/abs/1707.06347" target="_blank" rel="noopener noreferrer">↗ PPO</a><a href="https://arxiv.org/abs/1506.02438" target="_blank" rel="noopener noreferrer">↗ GAE</a><a href="https://arxiv.org/abs/2305.18290" target="_blank" rel="noopener noreferrer">↗ DPO</a><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noopener noreferrer">↗ DeepSeekMath</a><a href="https://arxiv.org/abs/2501.12948" target="_blank" rel="noopener noreferrer">↗ DeepSeek-R1</a><a href="https://arxiv.org/abs/2503.14476" target="_blank" rel="noopener noreferrer">↗ DAPO</a><a href="https://arxiv.org/abs/2503.20783" target="_blank" rel="noopener noreferrer">↗ Dr.GRPO</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ GSPO</a><a href="https://arxiv.org/abs/2412.19437" target="_blank" rel="noopener noreferrer">↗ DeepSeek-V3</a><a href="https://arxiv.org/abs/2106.09685" target="_blank" rel="noopener noreferrer">↗ LoRA</a><a href="https://arxiv.org/abs/2305.14314" target="_blank" rel="noopener noreferrer">↗ QLoRA</a><a href="https://arxiv.org/abs/1910.02054" target="_blank" rel="noopener noreferrer">↗ ZeRO</a><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noopener noreferrer">↗ FlashAttention</a><a href="https://arxiv.org/abs/2309.06180" target="_blank" rel="noopener noreferrer">↗ vLLM</a><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a><a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer">↗ MCP</a></div>
