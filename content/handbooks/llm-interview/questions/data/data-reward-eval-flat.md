---
id: data-reward-eval-flat
section: data
order: 5
level: S
title: RL reward 涨但真正 Eval 不涨，怎么 Debug？
quick: "先检查奖励是否真正衡量目标、模型是否利用奖励漏洞、训练与评测分布是否一致，再检查策略偏移、优化统计和评测可靠性。明确问题来源后再调整学习率，避免只优化了代理奖励，却没有提高实际成功率。"
tags:
  - Debug
  - Reward
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先检查奖励是否真正衡量目标、模型是否利用奖励漏洞、训练与评测分布是否一致，再检查策略偏移、优化统计和评测可靠性。明确问题来源后再调整学习率，避免只优化了代理奖励，却没有提高实际成功率。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><ol><li><b>Reward validity：</b>人工检查高奖励和低奖励轨迹，确认代理指标确实在衡量目标。</li><li><b>Reward hacking：</b>检查回答长度、格式、重复内容、迎合 judge 的措辞，以及验证器（verifier）的可利用漏洞。</li><li><b>Distribution：</b>训练提示、采样轨迹（rollout）的生成配置与评测领域是否一致？</li><li><b>Policy drift：</b>看 KL、SFT/general capability regression、language/style drift。</li><li><b>Optimization：</b>entropy、clip fraction、importance ratio、grad norm、advantage、zero-variance group rate、response length。</li><li><b>Eval reliability：</b>sample size、judge noise、temperature、max tokens、输入提示（prompt） template、benchmark contamination。</li></ol><p>实用做法：将奖励分数（reward）与外部成功指标画成散点图或做分组统计，找出奖励高但外部评测低的样本簇，再检查共同特征。如果训练 reward 持续上涨，但与外部成功指标的相关性不断下降，往往说明代理奖励被过度优化。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>怎么区分 reward overfit 与 catastrophic forgetting？</summary><div class="follow-answer"><p>前者通常在目标 reward 上优化过头，还能讲出 shortcut。后者会在跟 reward 无关的通用能力上也明显退化。需要用多个基准检查通用能力是否保留。</p></div></details><details class="followup"><summary>如果 train/eval distribution 一样仍不涨？</summary><div class="follow-answer"><p>检查 reward metric 是不是和 eval 一回事、逐 token 生成（decode）的配置是否一致、reward normalization 和 length bias，以及训练数据有没有 leakage 把 reward 抬假了。</p></div></details></div>
