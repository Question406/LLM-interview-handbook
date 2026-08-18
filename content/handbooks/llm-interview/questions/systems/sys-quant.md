---
id: sys-quant
section: systems
order: 12
level: A
title: GPTQ、AWQ、SmoothQuant、QAT 大概怎么区分？
quick: >-
  GPTQ 是典型 post-training weight-only 二阶近似量化；AWQ activation-aware
  地保护/缩放重要权重通道；SmoothQuant 把 activation outlier difficulty 平滑转移到 weights，常用于
  W8A8；QAT 在训练中显式模拟量化误差。
tags:
  - Quantization
  - Inference
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>GPTQ 是典型 post-training weight-only 二阶近似量化；AWQ activation-aware 地保护/缩放重要权重通道；SmoothQuant 把 activation outlier difficulty 平滑转移到 weights，常用于 W8A8；QAT 在训练中显式模拟量化误差。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>方法</th><th>典型类别</th><th>核心</th></tr></thead><tbody><tr><td>GPTQ</td><td>PTQ weight-only</td><td>基于近似 Hessian/逐层重构最小化量化误差</td></tr><tr><td>AWQ</td><td>PTQ weight-only</td><td>用 activation 统计识别重要权重/通道并缩放</td></tr><tr><td>SmoothQuant</td><td>PTQ W8A8</td><td>把 activation outliers 平滑迁移到 weight scale</td></tr><tr><td>QAT</td><td>训练中量化</td><td>forward 模拟 quantization，让权重适应误差</td></tr></tbody></table></div><p>量化不一定提升吞吐：如果硬件 kernel 不支持、dequant overhead 大、模型原本不是 memory-bound、batch/shape 不友好，bit-width 降了也可能不快。</p></div>
