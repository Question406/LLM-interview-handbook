---
id: afm-pipeline-code-verifier
kind: design
situation: 错解可能通过不完整测试进入训练。
task: 先获得可靠的代码反馈。
approach: 补定向困难输入，并用正确程序检查 false rejection。
result: 固定训练条件换 verifier，独立题验证收益。
---

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
