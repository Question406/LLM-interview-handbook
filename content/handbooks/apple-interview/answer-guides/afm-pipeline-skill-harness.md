---
id: afm-pipeline-skill-harness
kind: design
situation: agent 可能没找到或没用好现成 skill。
task: 决定应该补哪一类训练 trajectories。
approach: 先做 oracle skill 对照，再收选择和适配例子。
result: 未见任务有效，不能只提高加载率。
---

## 可以这样回答

我会先找一批已经能自动验收的任务，让 agent 带着现有 skill 跑一遍。比如让它整理一份有重复记录的 CSV，最后检查输出的统计有没有把重复数据算进去。这样我知道任务到底做对没有，也能回头看它用了哪条 skill。

接下来我想分清楚失败发生在哪。有时相关 skill 已经搜出来了，agent 却没打开；有时它打开了，但是文档里的列名和当前文件对不上。前一种情况，我会收集选择 skill 的例子；后一种情况，就收集把已有方法改到当前任务上，以及出错后怎么恢复的 trajectories。把这些混在一起，只说“多收一些成功数据”，很难知道模型学到了什么。

开始时我会先做一轮 SFT，用实际跑对、过程也合理的 trajectories 教这些行为。新一轮再看没见过的任务组合有没有变好。如果只在原来的 CSV 格式上提高，我会怀疑它记住了模板。等任务和检查方法比较稳定，再考虑在线 RL；这个阶段最重要的是先确认我收的数据确实对应那个失败原因。

## 被追问时再展开

**怎么知道是检索的问题，还是模型不会做？** 我会直接给它一条确认相关的 skill 再跑。如果这样能做对，先查检索和选择；如果仍然失败，就看 skill 内容和执行过程。这个对照比直接重训便宜。

**需要记录哪些东西？** 我最先要的是任务、当时能看到的信息、搜到和打开的 skill、tool calls，以及最后的检查结果。具体存储字段我会在实现时补齐，先保证能用一条记录解释一次失败。

## 英文口述参考

I would start with tasks that already have a reliable checker, and run the agent with the skills it currently has. What I want to understand is why the skill did not help. Did the agent fail to retrieve it, choose not to open it, or use it incorrectly?

Those cases need different data. If the skill was available but ignored, I would collect examples of when to load it. If the agent loaded it but could not adapt it, I would collect successful adaptations and recovery attempts. I would start with supervised training on verified traces, then check whether the improvement transfers to new tasks. Before collecting more data, I would also try giving the agent the right skill directly. That tells me whether retrieval is actually the bottleneck.
