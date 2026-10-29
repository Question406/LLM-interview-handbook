# AFM Interview Answers

专业术语直接使用英文，个人经历和设计方案保持真实经历与拟议设计的区别。

## 主动采偏好：一万条标注预算该花在最大分歧还是最不确定的样本？


## 可以这样回答

我会先看当前模型的错误和已有数据覆盖。高风险失败、几个 RM 明显意见不同的例子，以及新任务里缺标签的部分，都可能值得优先标。

但我不会把预算全部花在分歧最大的地方。有些题本来就几乎一样，标了很多次也很难得到有用区分；几个模型也可能一起犯错。所以我会留一部分随机样本和已知困难 evaluation slices，用来检查没被主动选中的地方。先标一小批，看这些标签是否真的改善独立评价，再决定下一批怎么分。


## Best-of-N 越大越差：怎么画出 reward overoptimization 的证据？


## 可以这样回答

我会先暂停继续扩大 N，拿被 RM 选中的失败答案来看。比如 agent 根本没完成工具操作，却写了一段非常完整的成功说明，RM 反而给了高分。这种情况下，增加 sampling 次数可能只是在增加找到这种答案的机会。

不过我会先确认比较条件一样：是不是同一批任务、同一个生成模型、相同的执行环境。确认以后，再补这类高分错例，或者限制目前的 sampling 规模。改完还得用独立任务结果检查，不能因为新 RM 给自己的分数好看，就认为问题解决了。


## RM 基础：preference probability 80%，为什么不能说 chosen 的成功率是 80%？


## 可以这样回答

这里我会先问，这个模型训练时的标签是什么。如果标签是人更喜欢 A 还是 B，它学到的就是两条回答的相对偏好。A 打3分、B 打1分，我可以用分差去估计 A 胜过 B 的概率，但不能把 A 自己的分数变成任务成功率。

比如两条回答都答错了，人仍然可能更喜欢其中一条。要预测任务成功，我还需要实际成功/失败的标签。另外，同一问题下把所有分数一起加上一个常数，排序和 preference probability 都没变，这也说明绝对分数本身没有那么直接的解释。


## DPO 深挖：chosen 概率也下降，为什么 loss 仍然改善？


## 可以这样回答

因为它优化的不是单独把 chosen 概率推高。比如 chosen 的 logprob 从负10变成负12，rejected 从负11变成负18，两条都降了，但它们的差距反而从1变成6。reference 固定时，DPO 目标仍然可能改善。

所以只看 loss 下降或 chosen 概率变化都不够。我会检查两边的概率、reference 是不是固定、回答长度和实际生成质量。如果模型在旧 preference pairs 上越学越好，当前回答却变差，还要查数据是不是已经跟不上新策略。


## 有四个 RM，怎样更可靠、又更省计算地选出好回答？


## 可以这样回答

假设同一个问题有 A、B 两个候选回答，我要决定保留哪一个。RM 就是给“问题＋回答”打分的模型。我有四个 RM，想让它们帮我选得更准，但还得考虑打分需要多少计算。

如果预算允许，我会先试 score averaging：让四个 RM 都打分，再取平均。例如 A 得到 8、8、8、0，平均是 6；B 得到 5、5、5、5，平均是 5，所以这个规则会选 A。分数要先放到可比较的尺度，一个模型打 0–1 分、另一个打 0–100 分，不能直接平均。

但 A 的分数也说明，四个模型对它意见差得很大。如果我想谨慎一点，可以试 conservative reward：在平均分上减去一个与分歧大小有关的惩罚。还是这个例子，用 mean−std，A 大约是 2.54，B 还是 5，就会改选 B。这表示我们更偏好模型意见一致的回答，不代表 B 已经被证明更好。如果四个 RM 都被同一类错误骗过，分歧小也没用。

如果每条回答的预算只够跑一个 RM，前面两种方法就太贵了。这时可以尝试 WARM：假设四个 RM 来自共同的 pre-trained model，模型结构相同、参数能够一一对应，先把它们的 weights 平均，得到一个新的 RM，部署时只跑这个模型。注意，平均 weights 后的模型，不等于四个模型输出分数的平均，所以必须重新测它选出的回答好不好。

最后，我会固定一批问题和候选回答，用独立的人工评价，或代码测试这类正确性检查，比较各方案实际选中了什么，同时测 latency 和成本。预算够时可以比较多模型打分；预算只够一个模型时，就比较单 RM 与 WARM。不会因为方法名字叫 ensemble，就默认它一定更可靠。



## 同家族 self-preference：换一个 judge 就足以消除 teacher 文风优势吗？


## 可以这样回答

我会先把它当成一个待验证的结果。student 可能真的变好了，也可能只是学到了 teacher 的写法，而同家族 judge 正好喜欢这种写法。

我会保留同一批候选，用其他 judge 和独立 human evaluation 再看，最好把事实正确、信息完整和文风分开。还可以隐藏模型名、交换顺序，看看偏好是否稳定。如果换一个 judge 结论就反过来，我会先查评审标准。仅仅换成不同家族，也不保证所有偏差就消失了。


## length bias：把奖励除以 token 数，为什么可能惩罚正确推理？


## 可以这样回答

我会先看长答案为什么赢。有些题确实需要更长的解释；直接把分数除以长度，可能把必要的信息也惩罚掉。

我会挑一批题做内容对照。比如同一个正确答案，一版保留必要步骤，另一版只是多加客套和重复；再补一些“短但漏关键信息”的例子。这样才能看出 RM 是在认有用内容，还是单纯认长度。训练以后我会同时看正确性、完整性和长度，避免把偏长改成了偏短。


## multimodal RM：会写漂亮说明，却看不到图中的错误，怎么揭穿？


## 可以这样回答

我会先确认评审器拿到了什么。有时叫 multimodal 评价，实际只把 OCR 文本或 caption 交给 judge，那它可能根本看不到小数点、位置关系或图里的矛盾。

然后我会做很小的图像变化，比如把票据总额从18.50改成1850，其他内容尽量保持一样。两条候选回答的正确性应该随证据改变；如果 RM 仍然只喜欢更详细的那条，就说明值得进一步查视觉证据的使用。最终我会用字段真值或实际状态核验，而不是再让同一个模型写一段解释证明自己看对了。


## 群体偏好冲突：英语 annotator 共识很高，是否代表所有用户？


## 可以这样回答

我会先看大家为什么不同意。有时是翻译不自然，有时是标注规则没说清，也可能确实有人喜欢直接、有人喜欢详细。这些问题不能都靠多数票解决。

如果是合理偏好差异，我会保留分组和投票信息，明确产品到底服务谁。可以比较一个统一模型、按任务或 locale 调整，以及输出多个评价维度的办法。最后要看各组表现；总体涨了，但某一组持续变差，我会把这个结果摆出来，而不是只报一个平均数。


## position bias：AB 和 BA 都选第一个，如何计分和分配人审？


## 可以这样回答

这两次其实选了不同的回答。AB 时第一个是 A，BA 时第一个是 B，所以我会记成顺序不一致，而不是说两条内容一样好。

如果要算交换顺序后的平均得分，A 可以拿0.5分，但我会同时报告不一致比例。否则，一个永远选第一个的 judge，看起来也能给出很“平衡”的总分。对于重要或不一致的题，我会再交给人看；两次都选同一条，也还需要检查它是不是选对了。


## PRM vs outcome RM：最终答案对了，过程错了，怎么标、怎么聚合？


## 可以这样回答

我会把最终结果和过程分开。数学题可能中间算错了，最后碰巧得到正确答案；工具任务也可能先改错文件，再把结果补回来。它们都不适合简单地把每一步标成好。

如果收过程标签，我会先定义 annotator 到底判断什么：这一步是否正确，是否推动任务，还是出错以后能不能恢复。然后比较这些标签带来的收益和成本。有些任务有很可靠的最终执行结果，先用 outcome reward 就足够；没有必要因为 PRM 更细，就假定它一定更好。


## 同预算选 RM：绝对打分、成对偏好，还是多属性回归？


## 可以这样回答

我会先看需要什么信息。只是选出两条回答里更好的一条，成对比较比较直接；但如果我还想知道它为什么好，是事实正确、信息更全，还是表达更清楚，分项评分会更有用。

我不会拿两批完全不同的数据来比较两种方法。可以先抽同一批问题和回答，同时收评分和偏好，记录标注时间，再用差不多的预算训练。最后看哪种反馈更能帮模型选出好答案，而不是只比较哪个 loss 更低。


## RM 榜单高分但 RL 变差：RewardBench 到底测到了什么？


## 可以这样回答

我会先固定一批当前模型的候选回答，让两个 RM 都来选，然后实际检查被选中的答案。这样比较的是它们在同一批选择上的表现。

一种可能是，分数高的 RM 很擅长明显的好坏对，却特别容易给少数错误答案打极高分。做 best-of-N 时，这些错误就容易被选出来。还有一种可能是，当前模型的回答风格和它训练时见过的不一样。

所以我会看当前候选上的选择质量和高分错例，再决定要不要补 preference data。公共 benchmark 仍有参考价值，但我不会用它的总分代替这个任务里的结果。


## RM 实现排错：取了最后一个 padding token，为什么训练准确率仍很高？


## 可以这样回答

我会先把一个 batch 打印出来，看看 token、mask、截断位置和实际取来打分的位置。比如右侧补了 padding，却直接取最后一个位置，那读到的可能已经不是回答结束的位置。

训练准确率高并不能排除这种错误。假如好回答普遍更长，模型可能只学了长度或模板特征。我会先用同一条回答换不同 padding 长度，看分数会不会变；再查两条回答是不是截断以后已经一样，却仍然带相反标签。实现和数据先对上，再讨论模型容量。


## 安全与帮助性：拒绝所有请求的 RM 为什么可能拿高分？


## 可以这样回答

我会把两类错误分开报：危险请求没有拒绝，以及正常请求被错误拒绝。如果总是拒绝，第一项可能很好看，但产品已经没法正常帮助用户。

数据上我会补一些很接近的对照，比如真正有害的请求、讨论风险的教育内容，以及只需要澄清就能回答的问题，让模型学会区别。评价也用这几类独立任务。对于不可接受的风险，我会单独设限制，再看帮助性；不能让更多正常题的收益把严重违规平均掉。


## 偏好分歧：6 比 4 的投票，soft labels、confidence weight 和 tie 是同一件事吗？


## 可以这样回答

我会先把十张票保留下来，而不是只存一个“A 赢了”。6比4和10比0表达的信息不同，尤其是在两条回答都合理的时候。

如果标注目标清楚、这些人也代表目标用户，我可以把0.6作为偏好 A 的 soft labels。但它和“这条数据有多可信”是两回事：十个人的6比4，和一个人的一次选择，证据量不同。遇到平票，我还会区分“都很好”“都很差”和“我看不懂”，因为这三种情况不能都变成同一个训练信号。


## sycophancy：用户满意度上涨，模型却开始赞同错误前提怎么办？


## 可以这样回答

我会先看点赞在这个场景里代表什么。用户可能喜欢被认同，但这和回答正确不是一回事。比如用户坚持悉尼是澳大利亚首都，模型附和后得到点赞，我不会把它当成事实任务的好回答。

我会构造只改变用户立场的问题，看模型的事实判断会不会跟着翻转。然后让 annotator 分别看事实和态度，补“礼貌地纠正”这样的例子。目标也不是训练一个总反驳用户的模型，而是让它有依据地回答，同时保持尊重。


## Pipeline 2：从正确解、错误解与困难测试，构造代码 post-training 数据


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


## Pipeline 3：从票据截图到表格操作，合成 multimodal Tool-Use 数据


## 可以这样回答

我会选一个比较容易检查结果的任务，比如给 agent 一张票据截图，让它把日期、币种和总额填进表格，再导出文件。这样既要读图，也要实际操作软件，最后还有一个可以检查的结果。

最开始我会用合成票据。先确定日期和金额，再把它们渲染成不同样式的图片，所以我知道正确答案是什么。让 agent 在固定的软件环境里操作，记录它每一步看到的截图和接下来的动作。结束以后，我直接检查导出的表格，不能因为 agent 说“已经完成”就算成功。

如果金额填错了，我会先看它是把图读错了，还是知道金额却填错了格子。比如小计是115，总额是128.50，它填了115，这更像是字段理解的问题；如果它正确说出了128.50，却输入到日期那一格，问题就更接近界面操作。这两种错误，我会补不同的数据。

训练时先用实际完成、过程也合理的 trajectories。评价时换一批票据布局，而不只是换金额。如果换个排版就不会了，说明它可能记住了位置，没有真正学会找总额。这条 pipeline 是我会设计的扩展；和我参与的 VisualSkill 工作可以连接起来讲，但不能把这套票据实验说成已经做过。

## 被追问时再展开

**为什么不用 OCR 加脚本？** 我会把它作为 baseline。如果固定票据模板用 OCR 就能很好解决，那没有必要强行做复杂 agent。这个例子更适合需要理解变化的页面、再跨软件完成操作的场景。

**数据怎么扩大？** 我会根据真实失败补变化，比如小计和总额很接近、日期格式不同、表格需要滚动。先确认是哪一种变化带来错误，再生成对应的新样本，而不是只把同一个模板复制很多遍。

## 英文口述参考

I would use a task with an outcome I can check, such as reading a receipt image, entering the date and total into a spreadsheet, and exporting the file.

I would begin with synthetic receipts, so I know the correct fields before rendering the image. During collection, I would record the screenshot the agent saw before each action. Afterwards, I would inspect the exported spreadsheet. The agent saying it succeeded would not be enough.

If it failed, I would separate reading errors from action errors. Entering the subtotal instead of the total suggests a different data problem from reading the amount correctly but typing it into the wrong cell. I would collect examples for the failure I actually observed, and test on new receipt layouts to see whether the model learned more than a fixed screen position.


## Pipeline 1：从 Skill 检索与执行失败，造出可训练的适配 trajectories


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


## 个人 Reference 4：Joint Agent–Speculator RL，预测正确是否就是好奖励？


## 可以这样回答

一个具体例子是我们做的下一次 tool calls 预测。agent 运行以后，会留下“在这段历史之后，它实际调用了什么工具”的记录。这些记录可以拿来训练预测器，而且比一个完全不同的模型生成的 trajectories，更接近当前 agent 的行为。

但我会特别注意，预测正确和任务正确不是一回事。假如 agent 本来就要调用一个错误工具，预测器猜中了，也不代表用户的任务完成得更好。所以我会同时看调用预测和最后的任务结果。

另一个问题是策略会变。训练了几轮以后，它的调用方式可能已经不同了，旧 trajectories 就没那么合适。我会保留 trajectories 对应的模型版本，并检查新策略上的表现。至于是否真的节省时间，还得算上预测开销和白做的调用，不能只拿命中率来推断。

## 被追问时再展开

**可以提前执行所有预测的工具吗？** 不能一概而论。只读查询和会创建订单、改文件的调用风险不同；写操作需要单独的执行条件和权限判断。


## 个人 Reference 1：DeepAmbigQA，如何把“漏答”变成 synthetic data 问题？


## 可以这样回答

我会讲 DeepAmbigQA。这项工作里有一个很直观的问题：有些问题里的名字对应不止一个实体，模型可能只选了其中一个，然后给出一个完全正确、但不完整的答案。只检查它说出来的内容，很容易漏掉这种失败。

我们在这篇工作里研究了这类歧义和多跳问题。对这个岗位来说，我觉得有价值的是把“答案不够全”变成可以检查的数据问题：有哪些解释、每个解释需要找什么证据、最后应该包含哪些答案。这样比只让一个 judge 给整体印象分，更容易看清缺口。

如果继续往训练上做，我会先检查模型是没发现另一种解释，还是发现了却没找到证据。前者补消歧和分支探索的例子，后者补检索或证据整合。这个训练扩展是我的方案；论文里的 benchmark 工作，以及我本人负责的部分，需要分别讲清楚。

## 被追问时再展开

**面试官问你具体做了什么？** 回到你实际负责的数据生成、质量检查或实验模块，选一个真实决定讲清原因。公开作者名单无法替你补这一段。


## 个人 Reference 3：Skill Usage，如何从评测失败构造 self-improvement feedback loop？


## 可以这样回答

我会用 skill 的例子。给 agent 一条写得很好的 skill，它做得更好了，这还不能说明真实使用时也会更好，因为真实情况下它首先得找到这条 skill，还得判断什么时候用。

我们在相关研究里看了更接近这种使用方式的设置。对数据迭代来说，我会把任务失败和 skill 使用过程放在一起看。相关 skill 没找到，就先查检索；找到了却没用，要看选择；用了还是失败，再看它缺什么步骤，或者是不是没有适配当前任务。

下一轮我会围绕那个具体问题补数据，再换一批任务验证。这里也要分清两件事：把 skill 文件改得更好，是运行时改进；让模型本身学会选择和适配，需要另外的训练实验。我不会把前者的收益直接算成后者的证据。

## 被追问时再展开

**什么时候值得训进模型？** 当同一种行为在很多任务里反复有用，而且外部 skill 已经很清楚、模型仍然不会用时，我会考虑训练。经常变化的知识则可能更适合继续放在 skill 里。


## 个人 Reference 6：Unlearning，如何把 forget/retain 研究接到数据治理？


## 可以这样回答

我觉得最直接的联系是，数据要撤回以后，我们怎么知道模型的行为真的改变了。在 unlearning 研究里，一个很容易产生误解的结果是：原来的问题答不出来了，但换一种问法，信息又出来了。

所以我会同时看忘记和保留两边。目标信息是否还能通过改写或间接问题取出来，其他正常能力有没有受到影响。只看原问题的准确率下降，我觉得证据还不够。

如果接到实际数据流程，我还会先检查数据来源和版本。模型这次做了 unlearning，但下一轮训练又把同一来源加回来，问题仍然存在。我的研究可以支持我讨论这些评价和权衡；它不能自动证明我处理过用户私有数据，也不能保证一种方法删除了所有可能提取的信息。

## 被追问时再展开

**那 unlearning 能替代数据许可吗？** 不能。允许不允许收集和训练，应当在前面决定。unlearning 是已经训练之后可能采用的一种补救办法，还需要验证。


## 个人 Reference 2：HarnessLLM／HardTestGen，奖励错了比模型弱更危险？


## 可以这样回答

我比较直接的连接是代码验证。在我参与的测试生成研究里，我们关心的是：一个程序看起来能通过测试，它到底是不是真的正确？因为测试一旦漏掉某类错误，这些错误程序就可能被选进 training set，或者在 RL 里拿到正奖励。

我觉得这和 learned RM 有一个共同点：模型得到的是评审器的判断，而这个判断可能和我们真正想要的质量有差距。代码里可能是漏了长链这种 edge-case inputs，preference model 里可能是把回答长、语气自信当成质量好。

所以我会先看评审器在哪些样本上容易错，再决定补什么标签。然后用另一套独立检查验证模型有没有变好。我没有负责过生产级 preference model 的话，会直接说明这一点；我能深入讲的是验证反馈怎么影响数据选择和优化。

## 被追问时再展开

**那两种奖励能直接互换吗？** 不能。代码测试对应一个明确的功能要求；preference labels 还涉及谁来评、按什么标准评，以及分歧怎么处理。共同的问题是反馈可靠性，具体标签和验证办法仍然不同。


## 个人 Reference 5：VisualSkill，怎么讲真实 multimodal 数据与评审偏差？


## 可以这样回答

我会用参与的 VisualSkill 工作来讲。界面操作里，有些东西用文字解释很费劲，一张图可能更直接，比如按钮在对话框的哪个位置。但图片也会占上下文，过期的截图甚至可能误导模型，所以我关心的是它在哪些任务上有实际帮助。

如果做对照，我会尽量让文字版和图文版来自同一份材料，用相同的 agent 和工具跑。否则图文版多知道了几个操作步骤，最后分数更高，也很难说是视觉信息带来的。

评价这里也有一个我觉得值得讨论的点：看截图给分，和检查文件、应用状态，测到的东西可能不同。一个表格外观很整齐，数字仍然可能填错。我会把这些结果分开看，再抽查它们不一致的任务。具体我本人负责了哪部分，面试时仍然按实际贡献来讲。

## 被追问时再展开

**这等于训练过 multimodal 模型吗？** 不一定。这是 multimodalagent、技能内容和评价的研究。有没有更新视觉模型权重，需要按实际实验回答。


## 表达方式参考

- [Interview Query](https://www.interviewquery.com/p/data-science-project-interview)
- [Hello Interview](https://www.hellointerview.com/learn/ml-system-design/in-a-hurry/delivery)
