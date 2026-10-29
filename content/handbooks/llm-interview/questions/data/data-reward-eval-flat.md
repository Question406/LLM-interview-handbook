---
id: data-reward-eval-flat
section: data
order: 5
level: S
title: RL reward 涨但真正 Eval 不涨，怎么 Debug？
quick: 假设 RL reward 持续上升，但独立任务分数不变。我会先确认两边评的是什么，不能立刻认定需要更多训练。
tags:
  - Debug
  - Reward
  - 口述改写 2026-10-28
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources: []
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 假设 RL reward 持续上升，但独立任务分数不变。</p>
<p><strong>做法与原因：</strong> 固定同一批 prompts 与候选，检查 RM 是否偏爱长度、风格或某些格式；再用独立人工判断或可执行测试验证。</p>
<p><strong>检查与取舍：</strong> 找到主要失败后，一次只改评价规则、数据或训练设置中的一项，做匹配预算的对照。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>假设 RL reward 持续上升，但独立任务分数不变。我会先确认两边评的是什么，不能立刻认定需要更多训练。</p>
<p>固定同一批 prompts 与候选，检查 RM 是否偏爱长度、风格或某些格式；再用独立人工判断或可执行测试验证。也要核对评测版本、sampling 预算和 train/test 是否混用。</p>
<p>找到主要失败后，一次只改评价规则、数据或训练设置中的一项，做匹配预算的对照。最终看真实质量是否变化，不能让训练 reward 自己证明训练成功。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>先确认奖励到底有没有在衡量目标，再看模型有没有钻奖励的漏洞、训练和评测分布是否一致，然后才查策略偏移、优化统计和评测本身可不可靠。最实用的一步是把 reward 和外部成功指标放在一起看，找出奖励高、评测低的样本 cluster。问题来源没定位之前，别急着调学习率。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>reward 涨、eval 不涨，我会按「奖励本身 → 模型怎么拿到奖励 → 分布 → 训练动态 → 评测」的顺序往下查，因为越靠前的原因越常见，修起来也越根本。明确问题来源之前先别调学习率，否则很可能只是把代理奖励优化得更狠，实际成功率还是没提高。</p><p>最实用的一步是把奖励分数（reward）和外部成功指标画成散点图，或者分组统计，找出奖励高但外部评测低的那一个 cluster 样本，再看它们有什么共同特征。比如那一个 cluster 回答都特别长，或者都用了某种迎合 judge 的措辞，问题基本就定位了。如果训练 reward 一路上涨，它和外部成功指标的相关性却在不断下降，往往说明代理奖励被过度优化了。</p><p>具体按这个顺序查。先看 reward validity：人工翻一翻高奖励和低奖励的轨迹，确认代理指标确实在衡量目标。再看 reward hacking：回答长度、格式、重复内容、迎合 judge 的措辞，以及验证器（verifier）有没有可利用的漏洞。然后看分布：训练提示、sampling 轨迹（rollout）的生成配置和评测领域是否一致。接着看 policy drift：KL、SFT 和通用能力有没有回退、语言和风格有没有漂移。再看优化统计：entropy、clip fraction、importance ratio、grad norm、advantage、zero-variance group rate、response length。最后怀疑评测本身的可靠性：sample size、judge noise、temperature、max tokens、prompttemplate、benchmark contamination。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>怎么区分 reward overfit 和 catastrophic forgetting？</summary><div class="follow-answer"><p>看退化的范围。reward overfit 通常是在目标 reward 上优化过头，你还能指出它走的是哪条 shortcut；catastrophic forgetting 则会在和 reward 无关的通用能力上也明显退化。所以要用多个基准检查通用能力是否保留。</p></div></details><details class="followup"><summary>train/eval 分布一样，还是不涨怎么办？</summary><div class="follow-answer"><p>那就查 reward metric 和 eval 是不是在测同一件事、逐 token 生成（decode）的配置是否一致、reward normalization 和 length bias，以及训练数据里有没有 leakage 把 reward 抬假了。</p></div></details></div>

</details>
