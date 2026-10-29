---
id: afm-pipeline-code-verifier
section: projects
order: 9
level: S
title: Pipeline 2：从正确解、错误解与困难测试，构造代码 post-training 数据
quick: 我最担心的是测试没发现错误，结果把错解当成好数据反复训练。所以我会先检查测试，再用它筛解答和提供奖励。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Data Pipeline 实例
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: HarnessLLM
    url: 'https://arxiv.org/html/2511.01104v1'
    type: primary
  - title: HARDTESTGEN — ICLR 2026
    url: >-
      https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf
    type: primary
  - title: EvalPlus
    url: 'https://arxiv.org/abs/2305.01210'
    type: primary
---

## 面试官可能这样问

怎么给 coding 模型做一条 synthetic datapipeline？你觉得最容易出问题的是哪一步？

## 可以这样回答

我最担心的是我们生成了很多代码，测试也都通过了，但里面其实有错解。如果这些代码拿去做 SFT，或者测试结果拿来做 RL 奖励，模型反而会越来越擅长通过不完整的测试。

所以我会先从一批题意和正确解比较可信的题开始。每道题生成几个候选解，然后针对常见错误补测试。比如树上的题，随机生成的树可能都比较平衡，一个低效算法看起来也能跑完；换成很长的链，它的问题才会暴露。这时我需要补的是这种输入，而不只是继续生成更多随机树。

不过，测试更严格也不一定更好。我还要拿确认正确的程序跑一遍，看看有没有错误 assertion、非法输入，或者机器太慢造成的误判。等这两边都检查过，再用测试筛 SFT 数据，或者给当前模型的代码打奖励。

最后我会固定训练题和训练预算，只换测试这一个因素，看模型在另一批题上是否更好。训练时的通过率涨了，只能说明它更会过这套测试；我还想知道代码能力有没有真的提高。

## 被追问时再展开

**错误程序从哪来？** 优先用模型实际写错的程序，因为它们更接近训练时会遇到的错误。也可以人为改出 edge-case bugs，但要先确认改出来的程序确实错了。

**两个程序都通过，preference labels 怎么给？** 我不会仅凭哪个解释更长来选。功能上还分不出好坏，就先保留这种不确定；如果要比较效率，需要额外的、可靠的性能测量。

## 英文口述参考

The part I would be most careful about is the verifier. If the tests let a wrong solution pass, that solution can become SFT data or receive a positive RL reward.

I would start with problems and reference solutions I trust, generate candidate programs, and add tests for the mistakes those programs make. A simple example is a tree problem where random balanced trees fail to expose an algorithm that becomes too slow on a long chain. I would also run known-correct programs through the tests, because a bad assertion or an unrealistic timeout can reject good code.

Once the tests look reliable, I would use them for data selection or rewards. To measure the benefit, I would keep the training problems and compute fixed, change the verifier, and evaluate on separate problems.

## 技术备查

## 公开参考与设计假设
[HarnessLLM](https://arxiv.org/html/2511.01104v1) 研究可执行 harness 生成；[HARDTESTGEN](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf) 强调代码测试对 post-training 反馈的影响。[EvalPlus](https://arxiv.org/abs/2305.01210) 可作为扩充测试的参照。以下具体任务与流水线是建议设计，不声称你已实现全部环节。这里 harness 指代码测试器。

## 1. 任务：树上所有节点到根的距离和
输入合法的根树，边权均为1，输出所有节点到根距离的总和。路径型树、星形树、平衡树、不同节点编号构成测试家族。根树契约、N 范围、I/O 协议和资源约束先写清。

链状树有 N 个节点时答案为 $N(N-1)/2$。一个逐节点回溯祖先的算法在平衡树上可能不显得慢，但在长链上是二次工作量。因此“随机测过了”未必验证复杂度。例子用于教学，不是声称论文指定了本接口。

## 2. Pipeline 与 data quality checks
`许可题目/可信实现 → 按题目家族切分 → 多策略生成候选解 → 产生定向错误程序 → 合成harness和困难输入 → 验证输入/答案/资源 → 双向审计verifier → 构造训练视图 → 独立代码评测`

| 阶段 | 输入与输出 | 关键检查 |
| --- | --- | --- |
| 题目规范化 | 题意、约束、I/O、可信实现、许可 → 版本化任务 | 相同题翻译/改写/代码近克隆同 split；不能将评价题扩写进训练 |
| 候选解 | 不同模型/温度/算法 → 正确、逻辑错、复杂度错程序 | 保留生成策略版本；独立核实正解，不能靠投票称其可信 |
| 错误解 | 真实失败与定向变异，如漏根、off-by-one、慢算法 | 变异应符合语法；未证实错误的标 unknown，不能默认负例 |
| 测试生成 | 题目契约＋错误模式 → 输入生成器与 assertion | 树必须连通无环且编号合法；禁止非法输入制造“抓错” |
| oracle | 小规模穷举/独立实现/可证明结构 → 正确结果 | 大链可用解析式；普通大输入参考实现仍要审计 |
| verifier 审计 | 正确/错误/unknown 程序与测试 → 双向混淆表 | 分清 false acceptance 错误、false rejection 正确、测试自身错误、非确定超时 |
| 下游训练 | 合格解/trajectories/偏好/任务环境 → 版本化 manifest | 训练与隐藏验收测试分开，策略无权修改 validator |

超时由固定硬件、编译器与资源预算判定；不稳定接近阈值的案例先复跑或隔离。若环境失效，则标环境错误而非程序错误；不能靠更短 timeout 假装 verifier 更强。

## 3. 数据样本与 hard examples
```json
{
  "task_id": "root-distance-001",
  "task_family": "tree-distance",
  "split": "train",
  "candidate_id": "ancestor-walk",
  "program_hash": "example:slow-v1",
  "generator_checkpoint": "example-coder-v0",
  "test_family": "long-chain",
  "input_valid": true,
  "oracle": "closed_form_unit_chain",
  "observed": { "small_correct": true, "large_case": "timeout" },
  "label": "complexity_failure_under_fixed_budget",
  "label_source": "sandbox-plus-audited-oracle"
}
```

[示意 JSONL](/apple-prep/pipelines/code_verifier.jsonl)展示正确解、复杂度错与 unknown 三类。这里没有附实际程序和运行产物，不能当作可直接训练的标签。

## 4. 训练的三种视图
**SFT**：先从许可 seed 题 sampling 多解，用经过审计的测试筛选；对通过且过程可接受的解做 rejection sampling fine-tuning。训练数据保留来源/题目/算法家族和负例审计统计，避免只选简单树导致单一课程。若训练的是 test generator，示范应是有效生成器与可信核验逻辑，而非只给标准答案。

**Preference / RM / DPO**：同题同约束下，选择有效且通过独立测试的解优于被证实逻辑或复杂度失败的解。两个都通过时不凭长度强造标签；可以按可靠测量的资源与可维护性分维度，但不得混淆功能正确和风格。可另建 verifier 偏好：合法、低 false rejection、能抓困难错解的 harness 优于非法输入或错误 assertion。

**Online RL**：sampling 当前 coder 并执行奖励；测试生成器的目标还需约束对正确程序的 acceptance rate 与输入合法性，不能只奖励 kill 错误程序数量。coder、test generator、checker 三者权限和版本独立；若共同迭代，保留不参与它们适配的审计池，防止共同钻漏洞。

## 5. 怎样证明不是“测试更难，所以看起来更好”
先固定候选代码，比较 verifier 的 false accept/false reject 和每秒有效判定；再固定题目、初始模型、训练 token 与算力，只替换 verifier，评独立新题代码成功率。不要只在新测试上报告通过率，或用训练奖励选完 checkpoint 再把该奖励当验收。

代码生成和测试生成器要对不同模型产生的错误迁移；样本按错误算法/模板和题目家族隔离。对真正新题的结论需说明语言、时间窗、checker 版本与限制。

## 6. 下一轮数据怎么补
若随机树全过而长链失败，补复杂度敏感结构及相同算法在其他题型的负例；若正确程序被 false rejection，先修 oracle/资源契约；若新 coder 钻过固定测试，更新开发侧测试并保留新隐藏家族。rule-based reward 也会有分布偏差，执行可重复不代表覆盖完整。

## 90秒英文参考
> I would build the code pipeline around a problem, trusted solutions, realistic wrong solutions, and tests that distinguish them. For example, random trees may fail to expose a quadratic algorithm that breaks on a long chain. Before using tests to select SFT data or reward RL, I would check input validity, oracle correctness, false acceptance, and false rejection. I would then hold the training problems and compute fixed, change only the verifier, and evaluate on independent problems. The important data product is reliable feedback, not simply a larger number of tests.

## 追问
**两个解都过了就一样好吗？** 功能证据相同，不足以凭文风定真偏好；更强测试或资源/维护目标需独立定义。
**奖励稀疏怎么办？** 用课程、可靠 SFT 和更可学任务调整，不将未知正确性当正奖励。
**你的真实经历怎么说？** 可以从参与的公开 verifier 研究谈出发点，再把本方案称作后续设计。

