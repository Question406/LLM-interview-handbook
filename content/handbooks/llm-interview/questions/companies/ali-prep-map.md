---
id: ali-prep-map
section: companies
order: 1
level: S
title: 阿里 LLM 人才计划：应该按哪三条主线准备？
quick: "按三条主线准备：后训练从 DPO 到 GRPO、DAPO/GSPO；Agent 看 Tool、MCP、Memory、RAG；系统看 RoPE、GQA、ZeRO、KV Cache 和推理。"
tags:
  - Alibaba
  - 备考地图
  - Qwen
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
  - title: ↗ Qwen GSPO blog
    url: 'https://qwenlm.github.io/blog/gspo/'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>按三条主线准备：后训练从 DPO 到 GRPO、DAPO/GSPO；Agent 看 Tool、MCP、Memory、RAG；系统看 RoPE、GQA、ZeRO、KV Cache 和推理。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>阿里 LLM 人才相关岗位，通义、淘天、国际、闪购 Agent，公开面经高度一致，可以按三条主线准备：</p>
<div class="table-wrap"><table><thead><tr><th>主线</th><th>必会节点</th><th>典型追问</th></tr></thead><tbody>
<tr><td>Post-Training</td><td>监督微调（SFT） 数据与 mask → preference/DPO → on-policy GRPO → DAPO/GSPO</td><td>为何不用继续 SFT？Advantages / KL / credit 怎么做？</td></tr>
<tr><td>Agent</td><td>规划、工具调度、MCP/Skill、Memory、RAG、Eval、Guardrail</td><td>双十一流量、幻觉拦截、多模态扩展</td></tr>
<tr><td>系统</td><td>RoPE、GQA、LoRA、ZeRO、显存手算、推理优化</td><td>白板推导与工程 trade-off</td></tr>
</tbody></table></div>
<p>准备方式：每条线准备一棵追问树，从定义到原理、项目落点、失败模式、怎么验证。别只背名词。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a><a href="https://qwenlm.github.io/blog/gspo/" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO blog</a></div>
