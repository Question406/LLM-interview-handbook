---
id: ali-auc-offline-online
section: alibaba
order: 32
level: A
title: AI Coding 压轴：离线 AUC 高、上线暴跌，如何从数据/标签/serving 归因？
quick: >-
  优先查 train-serving skew、样本分布偏移、特征泄露、标签口径/延迟、标注噪声、模型与 feature schema
  不一致、在线缺失填充与精度差异。
tags:
  - Alibaba
  - Eval
  - AI Coding
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>优先查 train-serving skew、样本分布偏移、特征泄露、标签口径/延迟、标注噪声、模型与 feature schema 不一致、在线缺失填充与精度差异。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>公开闪购面经给的排序思路（可作答模板）：</p>
<ol>
<li>Train-Serving 特征分布偏移；</li>
<li>线上样本分布与训练不一致；</li>
<li>特征泄露导致离线虚高；</li>
<li>标签定义口径不一致；</li>
<li>Label delay；</li>
<li>标注噪声放大；</li>
<li>版本与 schema 未对齐；</li>
<li>在线推理精度/缺失填充策略差异。</li>
</ol>
<p>回答时说明：用日志回放、特征监控、切片评估验证，而不是只猜。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a></div>
