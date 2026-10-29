# Apple 面试 Question Book

本册共 **340 道题**：279 道引用现有源题，61 道本册题（包含导读）。

网页题库切换到 **Apple 面试题本**，或使用 `?book=apple-interview`。cumsum／矩阵／mask 位于第 02 章，无需再搜索日期标签。

范围：整本 Apple Foundation Models Data Team；仓库各手册所有 Apple 公司标签题；以及显式挑选的 tensor／scan／decoding 迁移练习。原帖题、二手面经、主题扩展与公开研究保留原标记，不按数量推断出题频率。

已有答案通过 question-refs.json 引用原始文件，网页可直接阅读与练习；源题更新后重新构建即可同步，原手册链接保留。掌握进度与练习草稿按手册分别保存。

## 推荐练习顺序

先做 3 道新题：[position IDs](questions/tensor/apple-mask-position-ids.md)、[文档起点与 mask](questions/tensor/apple-starts-doc-mask.md)、[压缩与还原](questions/tensor/apple-mask-pack-unpack.md)。再做 cu_seqlens、packed mask、ML 全流程与数据管线，最后进入合成、评测与偏好。

Decoding 单列第 03 章：[解码练习路线](questions/decoding/apple-decoding-guide.md)。新增 [batch token selection](questions/decoding/apple-batched-token-selection.md)、[完整 batch greedy/sampling](questions/decoding/apple-batched-generation.md) 与 [完整 batched beam search](questions/decoding/apple-batched-beam-search.md)，包含独立 EOS、left padding、position IDs 与 KV cache。原单序列、单步和进阶题仍保留，支持范围见导读表格。端侧部署取舍仍见端侧章节。

新增全流程材料见第 14 章：两套 45 分钟技术模拟、两份带 CSV/JSONL 的诊断、端到端闭环、自我迭代演示、个人材料模板、五场 Panel 与 30 分钟 Director 模拟。Reward/Preference 第 08 章新增 20 道研究衍生题，其中 3 道可运行编程题。来源审计见 content/sources/apple-reward-prep-2026-10-26/README.md；题面与训练约定由本手册编写。

个人研究 Reference：[Jiabao Ji × AFM 完整参考稿](AFM-PERSONAL-REFERENCE.md)。基于公开主页、CV与论文，整理六条研究线、相关benchmark、英文表达与建议实验；网页版从第 12 章的 afm-personal-reference 进入。

三条数据 Pipeline：[Skill/Harness、Code、Multimodal Tool Use](AFM-DATA-PIPELINE-EXAMPLES.md)。第 12 章从 afm-pipeline-overview 进入；含来源、样本字段、data quality checks、SFT/偏好/RL视图和JSONL示意，均为面试设计方案。

口述参考：[26 道可直接练习的回答](AFM-ORAL-ANSWERS.md)。参考 Interview Query、IGotAnOffer、Hello Interview 和 Exponent/Aced 的公开示范重写；先读主回答，字段、公式与实验清单在每题的技术备查中展开。

全题回答逻辑：[340 题完整口述稿与 callout](AFM-ANSWER-GUIDES.md)。每题的情境、任务、做法/原因和结果/验证在 answer-guides 中单独维护；网页完整答案顶部显示。编程题使用输入约束、算法和正确性逻辑，个人故事不补造结果。

网站参考题：[14 张卡的导读与来源](questions/guide/afm-web-reference-guide.md)。网页搜索「AFM 网站参考题」筛出本批；覆盖 coding、agent evaluation、data pipeline、reward/DPO、benchmark、judge bias、synthetic data、multimodal search 与项目追问。

术语约定：[English terminology](TERMINOLOGY.md)。专业名词直接使用英文，中文解释含义和选择；inference/reasoning、release gate/held-out evaluation set 按语境区分。

## 更新方法

`npm run apple:sync` 更新来源清单与本目录，然后 `npm run content:build`。新增 Apple 标签题自动进入下次同步；章节规则和补选迁移题在 scripts/sync-apple-question-book.mjs 中维护。

[一亩三分地原帖核对记录](../../sources/apple-forum-2026-10-26/README.md)。

## 01 · 总览与练习路线（3 题）

范围、来源边界、二面优先级与全轮次地图

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Apple 面试 Question Book：怎么选题、怎么练、怎样判断来源？](questions/guide/apple-book-guide.md) | S | 本册自拟/导读 | 技术二面先练 cumsum／matrix／mask、Python 与 ML Coding 和 data pipeline；Panel 再练合成、评测、偏好与 multimodal。原帖题、主题扩展、公开研究和跨公司迁移分别保留来源，不能用题本数量推算出题频率。 |
| [AFM 网站参考题：13 张练习卡、来源与筛选入口](questions/guide/afm-web-reference-guide.md) | A | 公开培训材料改编/导读 | 搜索「AFM 网站参考题」筛选本批 14 张卡：13 张练习与 1 张导读。逐题保留外部来源、AFM 改写范围、回答思路与完整回答。 |
| [Apple Foundation Models Data Team：整条 loop 按哪几轮准备？](../data-team-interview/questions/overview/dt-prep-map.md) | S | 练习/研究 · AFM Data Team 备考 | 按面试轮次准备：HM 30 分钟讲清一个数据项目；Technical Screen 45 分钟在 CoderPad 写 data pipeline，边写边讲规模和质量检查；Panel 是四轮技术加一轮 See Around Corners，之后可能还有 Director / VP。数据岗的重点是数据选择、合成和评测，模型架构只当背景。 |

## 02 · cumsum、Matrix Operations 与 Mask（24 题）

position IDs、文档编号、pack/unpack、attention、序列概率与matrix扫描

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [cumsum 入门：从 padding mask 生成 position IDs](questions/tensor/apple-mask-position-ids.md) | S | 本册自拟/导读 | 对每行有效位置做 cumsum 后减一，再把无效位置设为 -1。按位置是否有效计数，不根据 token ID 猜 padding；同一实现支持左 padding、右 padding 及中间空位。 |
| [cumsum 与 cummax：从文档起始标记构造 doc IDs、段内位置和 mask](questions/tensor/apple-starts-doc-mask.md) | S | 本册自拟/导读 | 对 starts 做 cumsum 得到文档编号，用 cummax 传播最近起点下标，再相减得到段内位置。可见性是同文档、key 不晚于 query、两端有效三个条件同时成立。 |
| [cumsum＋scatter/gather：按 mask 压缩 token 并还原](questions/tensor/apple-mask-pack-unpack.md) | S | 本册自拟/导读 | 将 valid 展平做 cumsum，得到每个真实 token 的全局紧凑下标；scatter 写入 packed，gather 按下标还原。用额外的零行处理无效位置，避免 -1 索引误读最后一个 token。 |
| [Self-Attention Coding：实现 batched causal attention，并处理全 padding 行](questions/tensor/afm-web-attention-code.md) | S | 公开培训材料改编/导读 | 计算 scaled dot-product scores，组合 causal 与 padding mask，在 softmax 前处理全不可见行，最后将无效 query 输出置零。 |
| [Apple / Siri MLE：手写 Multi-Head Attention，shape 和 mask 怎么收？](../us-tech/questions/apple/apple-mha-code.md) | A | 面经依据；细节见来源 · Apple 标签题 | 我会先把 $[B,T,d]$ 的输入投影并拆成 $[B,H,T,d_h]$ 的 Q/K/V，计算 $QK^\top/\sqrt{d_h}$，在 softmax 前加 causal 和 padding mask，再乘 V、合并 heads。比如带 cache decoding 时，新 query 的绝对位置从旧 cache 长度开始，完整序列与逐 token 结果应一致。 |
| [手写从 logits gather token logprob，并乘 response mask](../llm-interview/questions/rl-coding/code-logprob-gather.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 取 `logits[:, :-1]` 做 `log_softmax`，用 `token_ids[:, 1:]` 去 `gather`，再乘 shift 后的 response mask，prompt 和 pad 位都是 0。SFT、DPO、GRPO 都用这个原语，最容易错的是忘了 shift 和 prompt 没 mask 掉。 |
| [白板：LayerNorm vs 在 feature 维上的 standardization，eps 和仿射](../us-tech/questions/coding/coding-layernorm.md) | S | 练习/研究 · Apple 标签题 | 对 $[B,T,D]$ 的每个 token，沿 $D$ 减均值、除以 $\sqrt{\sigma^2+\varepsilon}$，再乘 $\gamma$ 加 $\beta$。统计量只来自这个 token 的特征，方差除以 $D$，训练和推理都不依赖 batch 统计。 |
| [CoderPad：packed SFT 的 loss mask 怎么写，哪些 token 不能进 gradient？](../data-team-interview/questions/tech-screen/dt-packed-sft-code.md) | A | 练习/研究 · AFM Data Team 备考 | SFT 学的是给定上下文时助手怎么回答，所以只对助手回复算 cross-entropy，prompt、padding 和工具返回都不进监督目标。packed 序列里不同样本之间还要切断 attention，不然后一个样本能看到前一个的答案。漏掉 mask，模型就会同时学着重建用户文本和工具返回。 |
| [白板：packed sequences 的 cu_seqlens 和 document boundaries mask](../us-tech/questions/coding/coding-packed-lm.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 先按真实长度拼接有效 token，用长度为 $B+1$ 的 `cu_seqlens` prefix sum 标出各段起止。同一行放多篇独立文档时，要用块对角 causal mask，或把每篇当 varlen 序列，防止跨文档 attention。 |
| [手写 causal linear attention：并行形式和 O(1) 状态递推要对上](../llm-interview/questions/coding/code-linear-attn.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 把 softmax 换成非负核 $\phi(q)^\top\phi(k)$，靠结合律把历史累加成 $S_t=\sum\phi(k)v^\top$ 和 $z_t=\sum\phi(k)$。decode 时只更新这两个量，输出 $\phi(q)^\top S_t/\phi(q)^\top z_t$，状态大小和序列长度无关；训练用的并行形式和这个递推要数值一致。 |
| [白板：sliding window 和 causal mask 合成，prefill 与 decode 的 shape](../us-tech/questions/coding/coding-swa-mask.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 把 causal 和窗口两个条件相与：位置 $i$ 只看满足 $i-W \lt j \le i$ 的 key，其他位置设成 $-\infty$。Prefill 偏置是 `[1, 1, T, S]`，decode 只有一个 query，偏置是 `[1, 1, 1, S]`，query 的绝对下标取 cache 长度。 |
| [CoderPad：把变长对话组成 SFT batch，截断后还能保住监督信号吗？](../data-team-interview/questions/tech-screen/dt-sft-collate-code.md) | S | 练习/研究 · AFM Data Team 备考 | 先按明确的截断规则裁剪，再按 token 位置构造 attention mask 和 labels；padding 与 prompt 不参与 loss。不能通过 token 是否等于 pad_id 判断 padding，因为真实 token 也可能使用相同 ID。 |
| [CoderPad：批量计算回答 log probability，EOS 和 padding 怎么对齐？](../data-team-interview/questions/tech-screen/dt-response-logprob-code.md) | S | 练习/研究 · AFM Data Team 备考 | 先用前一位置 logits 预测后一 token，再按目标位置的回答 mask 选取 log probability。序列概率取 token log probability 的和；长度平均是另一种评分，不能无说明替换标准 DPO 的序列求和。 |
| [CoderPad：实现带 reference policy 的 DPO loss，并验证 gradient 方向](../data-team-interview/questions/tech-screen/dt-dpo-batch-code.md) | S | 练习/研究 · AFM Data Team 备考 | DPO 比较策略与 reference policy 对 chosen/rejected 的序列 log probability 差，用稳定的负 log-sigmoid 求 loss。参考分数不应收到 gradient；当两组相对差相同时 loss 为 log(2)。 |
| [白板：causal、padding、document boundaries 合成一张 attention mask](../us-tech/questions/coding/coding-attn-mask.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 先把 causal $j\le i$、key 非 pad、query 与 key 同文档三个条件按位与，再生成 `[B, 1, T, S]` 的加性 bias。合法位填 $0$，非法位填 $-\infty$；比如 packing 后第二篇文档不能读第一篇，一行全屏蔽时还要由 softmax 端处理 NaN。 |
| [CoderPad：变长 microbatch gradient accumulation，为什么平均 loss 会训练错？](../data-team-interview/questions/tech-screen/dt-token-accum-code.md) | S | 练习/研究 · AFM Data Team 备考 | 当每个 microbatch 的有效 token 数不同，应把各批 token loss 总和除以整个累积窗口的有效 token 总数，再分别 backward；直接平均各批均值会把短批放大。一次窗口只清 gradient 和更新一次。 |
| [手写数值稳定 Softmax：减 max、全 mask 行、以及和 CE 的关系](../llm-interview/questions/coding/code-softmax-stable.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 沿计算轴先减最大值再 $\exp$ 和 normalization，分布不变，指数落在 $(0,1]$ 不会上溢。整行都被 mask 成 $-\infty$ 时会出 NaN，要把这一行的概率置 0。 |
| [CoderPad：实现带 confidence weight 的 pairwise reward loss，全零权重怎么 backpropagation？](../data-team-interview/questions/tech-screen/dt-rm-weighted-loss-code.md) | S | 练习/研究 · AFM Data Team 备考 | 对 chosen 与 rejected 奖励差使用 softplus，再按 confidence weight normalization。分母是权重总和，不是样本数；全零权重时返回仍连着计算图的零，使 backward 有定义但 gradient 为零。 |
| [手写 packed sequence 的 document boundaries mask：`cu_seqlens` 怎么变成 keep matrix](../llm-interview/questions/coding/code-packed-mask.md) | A | 练习/研究 · 跨公司/通用 tensor 迁移 | 用 prefix sum `cu_seqlens` 给每个位置算出所属的 doc id，keep 的条件是同一文档且 $j\le i$。跨文档的位置要设成 $-\infty$，否则后一条样本能看到前一条。 |
| [CoderPad：手写 temperature-scaled distillation KL，teacher、student 和 reduction 哪个方向？](../data-team-interview/questions/tech-screen/dt-distill-forward-kl-code.md) | S | 练习/研究 · AFM Data Team 备考 | 本题用 teacher 分布到 student 分布的 forward KL，在 vocabulary 维求和，再按有效 token 平均并乘温度平方。teacher 必须冻结，不能把 KL 的输入顺序或对 vocabulary 的平均与 token 平均混淆。 |
| [CoderPad：构造 packed causal attention mask，padding query 怎么处理？](../data-team-interview/questions/tech-screen/dt-packed-attention-code.md) | S | 练习/研究 · AFM Data Team 备考 | 真实 query 只能看到同文档、不晚于自己的真实 key。padding query 本题只允许看自身以避免全屏蔽行，且其输出与 loss 必须丢弃；注意不同 PyTorch attention 接口的 bool mask 语义可能相反。 |
| [Apple CV/ML 面经形式练习：读公式实现可训练的 gated residual layer](../data-team-interview/questions/tech-screen/dt-p3a-paper-gated-layer.md) | S | 练习/研究 · AFM Data Team 备考 | 先澄清 tensor 形状、matrix 乘法方向、广播与 parameter sharing，再从公式写 forward。用可手算的初始状态检查输出，用 gradient 和参数注册检查能否真正训练；本题公式自拟，原帖未公开论文或层名。 |
| [OpenAI：NumPy 1-NN 向 quantization 与神经网络形式](../us-tech/questions/openai/p3a-openai-numpy-1nn-wx-b.md) | S | 面经依据；细节见来源 · 跨公司/通用 tensor 迁移 | 展开平方欧氏距离后，查询自身范数对所有候选都相同，可以去掉，剩下比较 2q·x - \|\|x\|\|²。把训练点的两倍作权重、负平方范数作偏置，一次 Wx + b 再 argmax 就得到 1-NN。L1 没有同样的点积展开，要另算广播距离，并注意中间内存。 |
| [OpenAI：matrix prefix product：手写 backpropagation 与并行扫描](../us-tech/questions/openai/p3a-openai-autograd-hillis-steele-scan.md) | S | 面经依据；细节见来源 · 跨公司/通用 tensor 迁移 | 我会保存 forward prefix product，backward 从后往前累积每个输出传回的 gradient，再按 matrix 乘法的左右顺序求导。Hillis–Steele 每层读上一层副本，用结合律并行合并；比如左块与右块交换会算错，浮点结果则用容差比较。 |

## 03 · Decoding 解码算法（11 题）

batch greedy/sampling 与完整 beam search、独立 EOS、left padding、position IDs、KV cache，以及原单序列和进阶 decoding 练习

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Decoding 练习路线：greedy、beam search、sampling 与约束 decoding 怎么选？](questions/decoding/apple-decoding-guide.md) | S | 本册自拟/导读 | 先写 [B,V] 的批量 token selection，再接入带独立 EOS、left padding 和 KV cache 的 greedy/sampling 生成循环，最后做完整 batched beam search。原单序列、单步与进阶题仍保留，并明确各自支持范围。 |
| [Batch token selection：greedy、top-k/top-p 与 Gumbel-max](questions/decoding/apple-batched-token-selection.md) | S | 本册自拟/导读 | 输入 [B,V]，每行独立做 mask、temperature、top-k、top-p，再返回 [B] 的 token IDs。支持每条请求不同参数；随机测试检查频率与 seed replay。 |
| [完整 Batch generation：greedy / sampling、独立 EOS 与 KV cache](questions/decoding/apple-batched-generation.md) | S | 本册自拟/导读 | 对不同长度的 left-padded prompts 先 prefill，再用单 token decode 更新 KV。每条请求独立维护 EOS、长度和 position IDs；greedy、multinomial 与 Gumbel 共用完整循环。 |
| [完整 Batched Beam Search：EOS、parent gather、KV 重排与 length penalty](questions/decoding/apple-batched-beam-search.md) | S | 本册自拟/导读 | 为 B 条请求各自运行 K-beam 完整生成，先 prefill，再按 parent 同步重排前缀、mask 和 KV。支持重复 parent、独立 EOS、无效空位与最终 length penalty，并用完整前缀参考验证。 |
| [Apple 电面：温度、top-k、nucleus 顺序，on-device 为什么常 top-k？](../us-tech/questions/apple/apple-topk-sample.md) | A | 练习/研究 · Apple 标签题 | sampling 先屏蔽非法 token，再除温度、做 top-k、在 renormalization 后的分布上做 nucleus，最后 sampling。比如温度为 0 直接选合法 token 中的最大值，全 mask 则报错；on-device top-k 候选数固定，便于控制延迟和 ANE 静态 shape。 |
| [白板：温度 → top-k → nucleus 的顺序，实现细节](../us-tech/questions/coding/coding-topk-nucleus.md) | S | 练习/研究 · Apple 标签题 | sampling 先屏蔽非法 token，再除温度 $T$，做 top-k，随后在剩余质量重新 normalization 的分布上做 nucleus 并 sampling。温度会改变 top-p 的累计质量，所以这一步必须在温度化之后；$T=0$ 或 $p=0$ 直接走 greedy。 |
| [白板：beam search vs greedy vs sampling，length penalty](../us-tech/questions/coding/coding-beam-search.md) | A | 练习/研究 · 跨公司/通用 decoding 迁移 | Greedy 每步取 $\arg\max$，beam 保留 $k$ 条前缀按累计 log-prob 扩展，$k=1$ 就退化为 greedy，sampling 则按指定分布随机选 token。beam 要让 EOS 后停止扩展、按 parent 重排 KV，并用 length penalty 缓解短句分数偏高；最后重排与搜索中使用惩罚也要分清。 |
| [白板：Gumbel-max sampling，和 softmax 温度的关系](../us-tech/questions/coding/coding-gumbel-max.md) | A | 练习/研究 · 跨公司/通用 decoding 迁移 | 硬 sampling 先缩放 logits，再用 argmax(z/τ+g)，得到 temperature sampling。Gumbel-softmax 松弛用 softmax((z+g)/τ)，它的 τ 只改变连续输出和 gradient，在固定噪声下不改变选中的类别。 |
| [Microsoft：约束 decoding / JSON 文法，和自由生成的质量](../us-tech/questions/microsoft/msft-constrained-decode.md) | A | 练习/研究 · 跨公司/通用 decoding 迁移 | 约束 decoding 把 JSON Schema / 文法变成逐 token mask，保证机器接口的字段和语法合法。格式约束也会改变生成分布，multi-step reasoning 可先得出结果再填结构。验收分别看可解析率与答案正确率，副作用与权限仍由工具运行时检查。 |
| [白板：speculative decoding 接受规则，拒绝后从哪一步 resampling](../us-tech/questions/coding/coding-spec-accept.md) | S | 练习/研究 · 跨公司/通用 decoding 迁移 | 草稿 token 从左到右按 $\min(1,p/q)$ 接受，第一次在第 $i$ 步拒绝时，就在同一步从 normalization 残差 $\max(0,p-q)$ resampling，并丢掉后续草稿。全部接受则从 $p$ 多抽一个 token。接受与残差两条路径的概率相加等于目标分布，因此保持 sampling distribution 不变。 |
| [手写 Beam Search 一步：累计 logprob、flatten top-k、backpointer 父 beam](../llm-interview/questions/coding/code-beam-search.md) | A | 练习/研究 · 跨公司/通用 decoding 迁移 | 每步把 $K$ 条 beam 的累计 logprob 加到 $[B,K,V]$ 的 log-softmax 上，展平成 $[B,KV]$ 取 top-$K$。下标整除 $V$ 得到父 beam，模 $V$ 得到新 token，再用父 beam 去 gather prefix sum KV cache。 |

## 04 · Python 与 ML Coding（8 题）

完整训练流程、kNN/k-means、normalization、sampling、缓存与通用编程

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Apple coding：k-means / nearest neighbors，作为电面算法题怎么答到 ML 岗标准？](../us-tech/questions/apple/apple-kmeans.md) | A | 练习/研究 · Apple 标签题 | 我会用向 quantization 距离计算实现 Lloyd 迭代：每个点分到最近中心，再把中心更新为均值，empty cluster 按约定处理，结束后重新分配标签。时间是 $O(n k d I)$，距离可写成 $[n,k]$；广播实现还要检查中间 tensor 内存，再讨论 k-means++ 和 16 个中心 $\approx$ 4-bit 的码本。 |
| [Apple Siri MLE 原帖：判断两句话是否恰好相差一次编辑](../data-team-interview/questions/tech-screen/dt-p3a-sentence-one-edit.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先确认编辑单位以及要求恰好一次还是至多一次。恰好一次时，相同输入应返回 False；长度差不超过一，用双指针只允许一次替换或跳过较长串的一个字符，避免完整编辑距离 DP。 |
| [Apple Foundation Model 原帖扩展：小数时间预约的最大重叠数](../data-team-interview/questions/tech-screen/dt-p3a-decimal-calendar.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 小数端点不能直接沿用整数区间算法里 endpoint 加一减一的做法。先明确时间精度和半开区间语义；本练习从字符串解析 Decimal，在起点加一、终点减一，并按同一端点的净变化做扫描。 |
| [Apple CVML 面经：手写 kNN end-to-end，standardization 在哪里 fit？](../data-team-interview/questions/tech-screen/p3a-apple-cvml-knn-pipeline.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 只用 training set 拟合均值与标准差，再对查询应用同一变换，按距离稳定选邻居并投票。距离平票、投票平票和零方差都要提前定义；把 validation set 一起拟合预处理会 leakage 分布，调 k 也只能用 development set。 |
| [Apple Sr MLE 原帖扩展：TTL 缓存到底何时过期、何时删除？](../data-team-interview/questions/tech-screen/dt-p3a-ttl-cache-contract.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先定义过期语义，再实现数据结构：本练习在 now 达到写入时刻加 TTL 时过期，读取不续期，覆盖写入重置期限。逻辑上过期与物理删除分开，测试用注入时间，不依赖 sleep。 |
| [Apple MLE 原帖：拿到数据后现场完成预处理、训练、评测与可视化](../data-team-interview/questions/tech-screen/dt-p3a-tabular-full-pipeline.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先冻结 train/test split，只在 training set 拟合缺失值填补、standardization、模型和降维投影；test set 只做 transform 与最终指标计算。先跑通简单 baseline，再解释降维图和误差，不用复杂网络掩盖 data leakage。 |
| [Apple DS 原帖：手写 K-fold CV，余数与预处理 leakage 怎么处理？](../data-team-interview/questions/tech-screen/dt-p3a-kfold-indices.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先生成一次可复现排列，把余数分给前几折；每个样本恰好一次进入 validation set，训练索引为该折的补集。执行模型比较时，每折重新拟合预处理与模型，不能在全数据上先 standardization 再交叉验证。 |
| [Apple AIML 视频组原帖：手写 BatchNorm，并分清训练与推断状态](../data-team-interview/questions/tech-screen/dt-p3a-batchnorm-state.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | BatchNorm 按特征聚合 batch 统计量；训练输出使用当前批的有偏方差，同时更新运行统计，推断只读运行均值方差。gamma/beta 是可学习仿射参数，running statistics 是状态，不能混为一谈。 |

## 05 · Data Pipeline 与 Data Strategy（50 题）

抽取、过滤、deduplication、contamination scan、sampling、data mix、版本与质量实验

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Data Pipeline：怎样从杂乱语料构建可追溯、可扩展的训练数据？](questions/data/afm-web-data-pipeline.md) | S | 公开培训材料改编/导读 | 先建立可追溯的小规模流程，再以稳定 record ID 扩展处理。 能复现 data mix，并证明质量收益不是仅来自更多训练 tokens。 |
| [通识：什么叫好数据，怎样才算把数据做对？](../data-team-interview/questions/good-data/dt-good-data-map.md) | S | 练习/研究 · AFM Data Team 备考 | 这章回答两件事：什么数据值得留，怎样证明一批数据有用。好数据让固定评测里的目标任务变好、保住其他重要能力、能追溯来源和版本；证明它要靠可被推翻的假设、对照和 ablation study，质量分只是其中一个信号。这章准备 Panel / HM 的解释，实现题在 CoderPad 部分。 |
| [CoderPad：边写边讲，一条 pre-training / SFT data pipeline 怎么画？](../data-team-interview/questions/tech-screen/dt-pipeline-talk.md) | S | 练习/研究 · AFM Data Team 备考 | 先问清数据类型、这轮要实现哪一步、输出什么格式，再边写边讲每一步筛掉什么、为什么。整条流程是来源、抽取、过滤、deduplication、data mix、评测隔离；现场只实现被要求的那部分，其余口头补齐版本、失败处理和大规模扩展。 |
| [什么叫好数据？别用「高质量」三个字糊过去](../data-team-interview/questions/good-data/dt-good-data-def.md) | S | 练习/研究 · AFM Data Team 备考 | 假设模型会选对工具，却经常把日期参数写错。对这项改进来说，好的数据应该包含可验证的日期与时区调用，而不只是文字通顺的普通问答。 |
| [CoderPad：手写 MinHash + LSH，near-duplicate deduplication 怎么讲规模？](../data-team-interview/questions/tech-screen/dt-minhash-code.md) | A | 练习/研究 · AFM Data Team 备考 | 先把文档拆成 shingle 集合并生成 MinHash 签名，再用 LSH 分段找候选：签名某一维相等的概率等于 Jaccard，任一 band 完全相等就进候选。候选最后仍要用精确 Jaccard 复核。规模分析要估候选对数，因为总成本取决于候选数量。 |
| [堆更多数据，还是把现有的做干净？这题怎么站队？](../data-team-interview/questions/good-data/dt-more-vs-better.md) | S | 练习/研究 · AFM Data Team 备考 | 不站死一边，先看模型缺什么：缺知识覆盖就加没见过的 token；重复和噪声多就先过滤、deduplication；能力有了、只是回答方式不对，再投精细标注。Chinchilla、FineWeb、DataComp 和 LIMA 分别支持这些不同条件下的选择。 |
| [CoderPad：质量过滤怎么写，启发式和模型分怎么叠？](../data-team-interview/questions/tech-screen/dt-quality-filter-code.md) | A | 练习/研究 · AFM Data Team 备考 | 过滤分三步：先做便宜的语言、长度、PII 和重复字符检查，再用按语言做 calibration 的质量模型打分，最后按阈值和配额选。全局取 top-$k$ 容易把 low-resource 语言整个丢掉。AFM 2025 公开的经验是过强的启发式会误删有价值的数据，所以要查 false rejection，并按语言分别对 threshold 做 calibration。 |
| [Data Cascade：数据上的错，为什么会在很后面才爆？](../data-team-interview/questions/good-data/dt-data-cascade.md) | A | 练习/研究 · AFM Data Team 备考 | 因为训练 loss 看不出来：上游数据错了，模型只是更好地拟合了错误数据，loss 照样往下走。抽取错误、阈值不合适、teacher 版本变化、evaluation contamination 会沿处理流程一步步放大，最后才在下游任务里暴露，这就是 Data Cascade。每一步都留下处理原因和版本，出事时才能回溯。 |
| [CoderPad：exact deduplication 怎么写，Bloom 和哈希表怎么选？](../data-team-interview/questions/tech-screen/dt-exact-dedup-code.md) | A | 练习/研究 · AFM Data Team 备考 | 先规范化正文再生成指纹，内存够时用 set 判断见没见过。十亿级时用 Bloom 先筛出「可能见过」的文档，再查落盘的精确记录复核，免得误删。exact deduplication 只管规范化后相同的内容，near-duplicates 另用 MinHash；opt-out 撤回要用精确墓碑表，因为 Bloom 不支持删除。 |
| [还没过滤之前，怎么知道 corpus 里到底有什么？](../data-team-interview/questions/good-data/dt-inspect-corpus.md) | A | 练习/研究 · AFM Data Team 备考 | 先对全库做计数和检索，再 sampling 看。统计语言、长度、重复率、评测重叠、PII、密钥和抽取错误，才知道该滤什么。WIMBD 就是这样检查大规模 corpus 的；Datasheets 把来源、用途、偏差和处理版本记下来，方便以后复盘。 |
| [Panel：data mix 怎么定，怎么证明没有在背某一个源？](../data-team-interview/questions/panel/dt-data-mix-quota.md) | S | 练习/研究 · AFM Data Team 备考 | 按能力类别分配 token 预算，预算来自冻结评测上的缺口，初值用小规模 data mix 实验或 mixing law 来定。要证明没背某个源，每个来源都留去过污的独立 test set，做 leave-one-source-out，并报 near-duplicates contamination rate。只看总 loss，或凭经验定 1:1:1，都说明不了问题。 |
| [质量过滤会不会滤过头？FineWeb 和 AFM 的公开教训是什么？](../data-team-interview/questions/good-data/dt-filter-too-hard.md) | S | 练习/研究 · AFM Data Team 备考 | 会。过滤器偏好「像英语维基或教科书」的文本，就可能把代码、公式、论坛答疑和 low-resource 语言一起删掉。阈值要试几档，比较各语言通过率和下游指标变化。FineWeb 和 AFM 2025 都提到减弱过强的启发式，滤到多严要靠实验定。 |
| [LIMA 说 1000 条精标就够对齐，那 pre-training 为什么还要上 T token？](../data-team-interview/questions/good-data/dt-lima-vs-scale.md) | A | 练习/研究 · AFM Data Team 备考 | 两个阶段解决的问题不同。LIMA 的 1000 条精标示范，教的是已有能力的模型怎么回答；pre-training 让模型学到知识、覆盖更多任务。base model 本来不会的事，少量漂亮示范补不上，False Promise 也发现模仿 teacher 的风格不等于学到 teacher 的能力。 |
| [CoderPad：域配额加 temperature sampling 怎么写，low-resource 语言怎么避免 overfitting？](../data-team-interview/questions/tech-screen/dt-temp-mix-code.md) | A | 练习/研究 · AFM Data Team 备考 | sampling 分两层：先按能力需求给各分组分配 token 预算，再在组内用 $p_i\propto n_i^{\alpha}$ 平衡来源，$\alpha=1$ 是按体积抽，趋近 0 时更均匀。low-resource 数据重复太多会出现 overfitting，所以要配合课程和 English regression data。实际数据不足或某组为空时必须报告。 |
| [CoderPad：对着冻结评测建 13-gram 倒排，训练文档怎么 quarantine？](../data-team-interview/questions/tech-screen/dt-ngram-contam-code.md) | S | 练习/研究 · AFM Data Team 备考 | 把评测题面切成 13-gram 建倒排索引，训练文档逐个 gram 查表，命中数过阈值的训练文档进 quarantine，评测题留着不删。改写数字或翻译会让 n-gram false negative，所以还要配合 URL 检查和 embedding nearest neighbors，见 `dt-contamination`。 |
| [unique token 不够，把同一批数据再读几遍行不行？](../data-team-interview/questions/good-data/dt-repeat-epoch.md) | A | 练习/研究 · AFM Data Team 备考 | 可以，但先 deduplication，再有限地重复。Muennighoff 等的 datablations 发现，固定算力下重复到约 4 个 epoch，效果接近用新数据，再多收益就很小。near-duplicates 文档不能算新数据，也别为了凑 token 数放松必要的质量过滤。 |
| [监督数据「好」吗，怎么发现标签本身是错的？](../data-team-interview/questions/good-data/dt-label-noise.md) | A | 练习/研究 · AFM Data Team 备考 | 先查 annotation guidelines 和人际一致性 $\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 能估计 label noise，找出来的样本由人确认后再改，别让模型自动翻转全部标签。training set 和 evaluation set 都要查，错标多的时候，加样本只会放大问题。 |
| [Director：一周后这批数据还能复现吗，lineage 要记什么？](../data-team-interview/questions/senior/dt-repro-lineage.md) | A | 练习/研究 · AFM Data Team 备考 | 能不能复现，看每条样本能不能追到来源和版本：来源 URL、许可集或研究协议，加上抽取器、过滤器、teacher、verifier 和 dataset_version。这样每次增益都能对应固定评测和具体 mix，opt-out 也能按精确记录撤回。只有文件目录、没有来源和版本，说明不了数据可复现。 |
| [CoderPad：十亿文档装不进内存，按 token 配额怎么流式抽？](../data-team-interview/questions/tech-screen/dt-reservoir-code.md) | S | 练习/研究 · AFM Data Team 备考 | 用加权水库 sampling：每条文档生成随机键 $k_i = u_i^{1/w_i}$，流式保留键最大的 $k$ 条，权重可以取 token 数乘质量分。按域各维护一个水库，不用把全量装进内存。水库控制的是条数，要和 token 预算对上，超长文档要切块或限制权重；空域要报告。 |
| [怎样证明一批数据是好的？固定模型，只换数据](../data-team-interview/questions/good-data/dt-hold-model-vary-data.md) | S | 练习/研究 · AFM Data Team 备考 | 固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务和其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都是这个对照思路。small model 也能做，但选出的方案最后要在 large model 上确认一次。 |
| [CoderPad：SimHash 怎么写，什么时候不用 MinHash？](../data-team-interview/questions/tech-screen/dt-simhash-code.md) | A | 练习/研究 · AFM Data Team 备考 | SimHash 把每个特征哈希到 $f$ 维，按权重给每个 bit 投 +1 或 -1，最后取各维的符号当指纹，汉明距离小就是 near-duplicates。它适合短标题、URL 和 query，因为短文本的 shingle 集合太小，Jaccard 不稳；长网页 near-duplicates 仍用 `dt-minhash-code` 的 Jaccard。 |
| [CoderPad：PII 门怎么写，信用卡 Luhn 和代码假阳性怎么处理？](../data-team-interview/questions/tech-screen/dt-pii-luhn-code.md) | A | 练习/研究 · AFM Data Team 备考 | 先用正则找可能的 personally identifiable information (PII)，再做校验：信用卡号用 Luhn，邮箱和电话查格式。命中后记下文本位置，隔离还是脱敏交给单独的规则决定。代码里的示例卡号 `4111-1111-1111-1111` 和 ISBN 会 false positive，要按领域设白名单，命中都记录下来再处理。 |
| [数据选择能不能讲成一个效用函数？](../data-team-interview/questions/good-data/dt-utility-select.md) | A | 练习/研究 · AFM Data Team 备考 | 可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛、按桶分配额，还是按分数加权 sampling。Albalak 等 2024 年的综述就是这样拆成两步的。启发式、ppl、分类器、EL2N 和 RL sampling，区别主要在效用怎么估。 |
| [CoderPad：精确哈希之前，Unicode / 零宽字符怎么规范化？](../data-team-interview/questions/tech-screen/dt-unicode-canon-code.md) | A | 练习/研究 · AFM Data Team 备考 | 算精确哈希之前，先用 NFKC 统一兼容字符和全角形式，按场景去掉零宽和控制字符，再压缩空白。规范化过度会把本来不同的文本变成一样，所以规则按数据类型开；跨文字体系的形近字映射只用在需要复核的高价值数据上。 |
| [用 LLM 把网页改写成干净段落，这算做好数据吗？](../data-team-interview/questions/good-data/dt-wrap-rephrase.md) | A | 练习/研究 · AFM Data Team 备考 | 算一种有用的 data augmentation，前提是和原文一起用：清理后的原文和改写版本一起训，再验证样本效率有没有提高。WRAP 在 C4 上公开报告过约 3 倍样本效率，但改写不增加新事实，也解决不了许可、evaluation contamination 和 teacher 错误，所以要保留原文，记下 teacher 和来源。 |
| [C4 那种块名单过滤，质量上去了，谁被切掉了？](../data-team-interview/questions/good-data/dt-c4-side-effect.md) | A | 练习/研究 · AFM Data Team 备考 | 常被切掉的是正常的身份讨论、方言、非英语页面和对话。块名单按词匹配、不看上下文，清理有害内容时会把这些一起删掉。所以过滤后除了看平均分和 perplexity，还要按语言、主题统计通过率，抽查被丢弃的样本，看清哪些人和话题被排除了。 |
| [CoderPad：embedding nearest neighbors 去语义重复，什么子集才值得上？](../data-team-interview/questions/tech-screen/dt-semdedup-code.md) | A | 练习/研究 · AFM Data Team 备考 | MinHash 抓不到换了说法的重复，这一层用 embedding 来补：对已经过精确哈希和 MinHash 的高价值子集，用 ANN 取 top-$k$ nearest neighbors，余弦相似度超过阈值的归入同一个 cluster，保留质量最高的一条。适合许可书、SFT 和通过 verifier 的 synthetic data；成本高，十亿级网页不宜直接全量跑。 |
| [CoderPad：HTML 去导航条，文本密度怎么写，什么时候才上 LLM 抽取？](../data-team-interview/questions/tech-screen/dt-boilerplate-code.md) | A | 练习/研究 · AFM Data Team 备考 | 先用块级的文本密度和链接密度把导航、页脚这类模板块滤掉，这一步最便宜。按域统计抽取失败率，静态抽取失败的域再开 headless 渲染，仍失败才上 LLM 抽取。每页都调 large model 成本高，抽取带来的变化也难追踪；用了 LLM 要记模型版本，抽出的正文照样过质量检查和 evaluation contamination 检查。 |
| [许可、opt-out、PII 为什么也算数据质量问题？](../data-team-interview/questions/good-data/dt-license-is-quality.md) | S | 练习/研究 · AFM Data Team 备考 | 因为能不能合法用于训练，本身就是质量条件。许可不合格、opt-out 执行不了、或者带着不该用的 personally identifiable information (PII)，评测分再高也可能被迫撤回重训。所以要把这些约束放进数据选择流程，追踪来源、拒绝记录、teacher 和合成 seed。 |
| [怎样才算把数据做对：一次干预从假设跑到能不能上 mix？](../data-team-interview/questions/good-data/dt-data-intervention.md) | S | 练习/研究 · AFM Data Team 备考 | 先写一个能被推翻的假设，固定评测，一次只改一项数据因素，比如来源、过滤或 data mix。用同模型、同预算的对照看目标能力和其他能力，再查 contamination、隐私、许可和版本记录。通过了才进训练 mix，没通过就隔离，记下失败原因。 |
| [Panel：long context 数据怎么造，短了补长度、长了丢能力怎么避免？](../data-team-interview/questions/panel/dt-longctx-data.md) | A | 练习/研究 · AFM Data Team 备考 | 长度本身教不会模型跨段检索，要用真实长文（许可书籍、代码仓库），加上把可核验答案埋在不同位置的合成长文，同时混入上一阶段的短数据，防止短任务退步。单纯 padding 或重复拼接短文只增加长度，没有需要查找的信息。AFM 用这三类数据把序列扩展到 65K。 |
| [CoderPad：语言识别怎么写，文档级和段落级差在哪？](../data-team-interview/questions/tech-screen/dt-lid-code.md) | A | 练习/研究 · AFM Data Team 备考 | 现场写一个字符 3-gram 朴素贝叶斯来识别语言。先剥掉代码块，再按段落分别识别，否则英语页里的中文段会被一起标成英语。分数低于阈值时输出 `und`，表示判断不了，别硬猜。 |
| [CoderPad：LSH 候选对怎么并成 near-duplicates cluster，cluster 里留哪一条？](../data-team-interview/questions/tech-screen/dt-lsh-cluster-code.md) | A | 练习/研究 · AFM Data Team 备考 | 对 LSH 候选对先算精确 Jaccard，只给达到阈值的文档对连边，再用并查集求连通分量，得到 near-duplicates cluster。每个 cluster 保留质量最高的一条，缺质量分时才看长度。异常大的 cluster 多半是公共模板造成的误连，要剥掉模板、分域后重新聚类。 |
| [CoderPad：精确子串 deduplication 怎么写，滚动哈希怎么扫 evaluation leakage？](../data-team-interview/questions/tech-screen/dt-substr-dedup-code.md) | A | 练习/研究 · AFM Data Team 备考 | 把评测内容切成固定长度的字符或 token 窗口，用滚动哈希扫训练文档，命中后再比原文，排除哈希碰撞。它能发现整篇哈希漏掉的局部片段复制。窗口太短会 false rejection 常见代码，太长会漏掉变体，规范化按域选；训练内部的子串 deduplication 和评测隔离用不同的表和阈值。 |
| [CoderPad：KenLM / perplexity data quality checks 怎么写，阈值按语言怎么切？](../data-team-interview/questions/tech-screen/dt-ppl-filter-code.md) | A | 练习/研究 · AFM Data Team 备考 | 用小语言模型算文档的平均 cross-entropy 或 perplexity，可以当质量的间接信号，但它只说明文本像不像参考 corpus。阈值要按语言和数据域取分位数，代码、公式和论坛要各设阈值，维基的阈值套不上。synthetic data 要用独立 verifier，筛得好不好靠下游对照判断。 |
| [Panel：网页抽取失败有哪些，LLM 抽取什么时候才上？](../data-team-interview/questions/panel/dt-web-extract.md) | A | 练习/研究 · AFM Data Team 备考 | 假设网页抽取后看起来很干净，却把代码缩进和表格对应关系删掉了。清理广告之外，还必须保住训练需要的内容结构。 |
| [CoderPad：pre-training 怎么把文档拼进固定长度，是否在 document boundaries 切断 causal attention？](../data-team-interview/questions/tech-screen/dt-pretrain-pack-code.md) | A | 练习/研究 · AFM Data Team 备考 | 把文档贪心装进长度为 `seq_len` 的序列，文档之间插 BOS/EOS，在 document boundaries 切断 attention，padding 不算 loss。这样算力不浪费在 pad 上，模型也不会跨篇续写。pre-training 一般监督文档里的大部分 token，SFT 还要按角色限制监督范围，见 `dt-packed-sft-code`。 |
| [CoderPad：代码近克隆怎么指纹，Winnowing 窗口怎么写？](../data-team-interview/questions/tech-screen/dt-winnow-code.md) | A | 练习/研究 · AFM Data Team 备考 | 先规范化源码，切成 k-gram 算哈希，每个窗口只留最小的哈希当指纹，再用 Jaccard 比较指纹集合。许可证头和 import 块要先剥掉，否则大量无关的 Python 文件也会显得相似。 |
| [CoderPad：爬到的网页和仓库里，API 密钥怎么扫出来？](../data-team-interview/questions/tech-screen/dt-secret-scan-code.md) | A | 练习/研究 · AFM Data Team 备考 | 用提供商前缀加字符串熵来找凭证，命中后整个文件隔离，高价值来源再人工核对。示例密钥可以白名单；只做脱敏的文件仍可能教会模型密钥格式，来源和安全检查都要做。检测覆盖不了所有提供商，teacher model 的合成输出也要扫。 |
| [CoderPad：训练 / 开发 / evaluation gate 怎么稳定切开，怎样才不会 leakage？](../data-team-interview/questions/tech-screen/dt-hash-split-code.md) | A | 练习/研究 · AFM Data Team 备考 | 对稳定的 group_id 做哈希再取模，让同一仓库、书、线程或 near-duplicates cluster 整组落在训练或评测的同一侧。随机 shuffle 会把同一篇转载拆到两边，让记忆看起来像泛化。seed 和规范化版本要记录，重跑才稳定；时间 leakage 和生成 prompt 里混入评测题，哈希解决不了，要单独查。 |
| [CoderPad：URL 怎么规范化，opt-out / robots 怎么落到一条拒绝函数？](../data-team-interview/questions/tech-screen/dt-url-canon-code.md) | A | 练习/研究 · AFM Data Team 备考 | URL 先统一规范化，再拿去做 deduplication、许可拒绝表和评测匹配：scheme 和 host 转小写，去掉默认端口和 fragment，只删跟踪类 query，保留分页参数。host 后缀匹配要检查 domain matching rules。原 URL 和规范化后的 URL 都要记录，robots 和 opt-out 由上游另做检查。 |
| [CoderPad：按长度分层 sampling 怎么写，短模板淹没长文档怎么避免？](../data-team-interview/questions/tech-screen/dt-length-bucket-code.md) | A | 练习/研究 · AFM Data Team 备考 | 按 token 数把文档分进长度桶（2k / 8k / 32k），每桶单独设 token 配额，再从桶里按文档抽。文档是 sampling 单位，token 是预算单位。只按文档数随机打乱的话，海量短网页会占满名额，书和长文档被抽得太少。 |
| [CoderPad：十亿文档里找高频样板 n-gram，Count-Min 怎么写？](../data-team-interview/questions/tech-screen/dt-countmin-code.md) | A | 练习/研究 · AFM Data Team 备考 | 要找的是跨文档反复出现的片段，比如版权声明、导航和 cookie 提示。精确计数要一张十亿级哈希表，所以用 Count-Min sketch：$d$ 行 $w$ 列计数器，每个 n-gram 经 $d$ 个哈希各加一，查询取 $d$ 行最小值。碰撞只会让估计偏高，阈值留余量，超阈值的候选抽查复核后再剥除。 |
| [Panel 情景：数据任务重跑后样本翻倍，怎么恢复并防止训练重复？](../data-team-interview/questions/panel/dt-data-replay-incident.md) | S | 练习/研究 · AFM Data Team 备考 | 假设数据作业失败后重跑，训练样本数翻倍。先暂停发布这个版本，确认重复来自输入、重试还是提交过程，不要直接让训练继续消耗它。 |
| [CoderPad：按 padding 后 token 预算组 batch，遇到超长样本怎么办？](../data-team-interview/questions/tech-screen/dt-token-budget-batch-code.md) | S | 练习/研究 · AFM Data Team 备考 | 预算按 batch 内最大长度乘样本数计算，不能只累加真实长度。顺序扫描，加入下一条会超预算时先交付当前 batch；单条超长样本单独记录为拒收，其他样本不丢失、不重排。 |
| [CoderPad：IterableDataset 多进程读取，怎样避免每个 worker 都读一遍？](../data-team-interview/questions/tech-screen/dt-worker-shard-code.md) | S | 练习/研究 · AFM Data Team 备考 | 先把 rank 与 worker 映射成全局消费者编号，再按稳定分片编号取模分配。必须说明 worker 数固定的假设；重新洗牌、弹性扩容和 checkpoint 恢复不能靠这个映射自动解决。 |
| [CoderPad：无限数据流如何用固定缓冲区近似打乱？](../data-team-interview/questions/tech-screen/dt-buffer-shuffle-code.md) | S | 练习/研究 · AFM Data Team 备考 | 维护固定容量缓冲区，新元素到达时随机交付一个旧元素并替换它，结束时随机清空。这样每条数据恰好交付一次且内存有界，但小缓冲区无法产生全局均匀排列。 |
| [Panel 情景：数学和工具数据单独都有效，一起加入为什么掉点？](../data-team-interview/questions/panel/dt-mixture-factorial-budget.md) | A | 练习/研究 · AFM Data Team 备考 | 用固定总预算的四组实验估计单独效果与交互，排查替换基础数据、重复率、gradient 与格式冲突。单独收益不能简单相加，组合表现差也不能直接推出“这两种能力互斥”。 |
| [Panel 情景：换 tokenizer 后 loss 更低，为什么 multilingual 能力和 long context 都退化？](../data-team-interview/questions/panel/dt-tokenizer-migration-gap.md) | A | 练习/研究 · AFM Data Team 备考 | 假设换 tokenizer 后平均 token loss 更低，但同一段文本被切成了不同数量的 tokens。两个 loss 的单位已经变化，不能直接比较谁更好。 |
| [一亩三分地 Apple AIML Infra：从 JSON 字符串清洗文档记录并汇总拒收原因](../data-team-interview/questions/tech-screen/p3a-apple-json-clean-code.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先解析 JSON，再按明确顺序校验字段、应用阈值和按 ID 保留最佳记录。要区分数据无效、质量不足与重复三种计数，避免一条记录被多个拒收原因重复统计，也要说明布尔值不能当质量数字。 |

## 06 · Synthetic Data 与 Self-Improvement（23 题）

数学、代码、任务生成、verifier、难度与课程迭代

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Synthetic Data：只有几百条 seed，怎样生成并筛出有用的训练样本？](questions/synthetic/afm-web-synthetic-loop.md) | S | 公开培训材料改编/导读 | 先按任务家族隔离真实评估，再做 generation、verification、deduplication 和训练对照。 在独立真实任务上优于等预算 baseline，且 long-tail 不退化。 |
| [Synthetic Data Audit：合成数据为什么仍会泄露隐私或放大 bias？](questions/synthetic/afm-web-synthetic-privacy-bias.md) | S | 公开培训材料改编/导读 | 追踪源数据权限，测试 memorization 与任务分布，必要时采用明确的 privacy mechanism。 有证据支持限定用途的共享，并且 minority tasks 的质量没有被掩盖。 |
| [post-training 数据：数学、代码、工具、agent，各自的 acceptance criteria 是什么？](../data-team-interview/questions/posttrain-data/dt-posttrain-map.md) | S | 练习/研究 · AFM Data Team 备考 | post-training 的数据单位是题目、trajectories 和 grader，各类任务的 acceptance criteria 就是 grader 如何判断正确性：数学看标准答案、解释器或 Lean，代码看冻结的测试，工具看 schema 和环境状态，agent 还要看 trajectories 能否 replay、多跑几次是否稳定。四类检查各管一个域，要分开建；post-training 要准备的是题目、trajectories 和 grader，多加网页解决不了。 |
| [数学 SFT 题太简单或太难，数据侧怎么切 difficulty band？](../data-team-interview/questions/posttrain-data/dt-math-passk-band.md) | S | 练习/研究 · AFM Data Team 备考 | 按当前 student model 每题 sampling $k$ 次、做对几次来切，竞赛名称只能粗分。全对的太易少留；部分对的是中间带，成功 trajectories 做 SFT、错的做负样本；全错的先降难度或找 teacher / 解释器，RLVR 也需要模型有机会拿到非零奖励。换 student 要重切，还要防止中间带被 GSM8K 改写题填满。 |
| [Director：模型怎么给自己造训练数据，limitations 是什么？](../data-team-interview/questions/senior/dt-self-improve.md) | A | 练习/研究 · AFM Data Team 备考 | 可以，但 correctness checks 必须独立于生成模型：当前模型生成候选，独立的 verifier 筛出对的，再拿去训下一版，STaR、ReST 和 rejection sampling 都是这个思路。需要满足三项 requirements：同一个模型默认不同时出答案和定标签，synthetic-data reuse iterations 要有上限，还要留真实来源的数据做对照。 |
| [Panel：推理 synthetic data 怎么做，什么样的 pipeline 你能画出来？](../data-team-interview/questions/panel/dt-synth-reasoning.md) | S | 练习/研究 · AFM Data Team 备考 | 从带答案或测试的 seed 题出发，把难度调到当前模型 pass@k 的中间带，每题采多条回答，再用执行、符号等价或标准答案验证。答案对了还要查推理过程，并和评测去 contamination。长 CoT 验证过才能当 SFT 正例，验证强度决定数据能进哪个训练阶段。 |
| [数学 post-training：纯 CoT、PAL 程序、还是 ToRA 那种边想边跑代码？](../data-team-interview/questions/posttrain-data/dt-math-tir-data.md) | S | 练习/研究 · AFM Data Team 备考 | 按任务分，需要计算的步骤用 TIR 交给解释器，心算、不等式、证明思路仍用自然语言。PAL / PoT 把题意转成程序，ToRA / OpenMathInstruct 让推理和代码调用交替。代码必须在沙箱里真实执行，最终答案再对 gold labels；解释器输出作为输入，不计入 CE。 |
| [Panel：tool calls 和 multimodal 合成，你能画出哪条具体 pipeline？](../data-team-interview/questions/panel/dt-synth-tool-mm.md) | S | 练习/研究 · AFM Data Team 备考 | 工具和视觉是两条 pipeline，要分别讲生成和验证。工具数据在可重置的执行环境里生成，reference model 调用工具，人能回滚纠错，保存成功路径和被放弃的尝试，oracle 是环境状态，最后一句话说得对不算数。视觉数据要补详细描述、代码渲染的图表和可核验问答，还要教模型拒绝回答图中没有的信息。 |
| [Lean / 形式化证明能不能当数学 post-training 的 oracle？](../data-team-interview/questions/posttrain-data/dt-math-lean-prover.md) | A | 练习/研究 · AFM Data Team 备考 | 能，但只覆盖形式化证明。Lean 的 kernel 逐步检查证明，通过编译和证明检查才算正例，比只看最终 boxed 答案可靠；DeepSeek-Prover 先用成功证明和子目标冷启动，再用 Lean 反馈做 RL。自然语言计算题仍要靠 TIR 等方法验证，两类数据和 grader 分开记录、分开评测。 |
| [MetaMath 那种改写 GSM8K，什么时候是 data augmentation，什么时候是 leakage？](../data-team-interview/questions/posttrain-data/dt-math-rewrite-leak.md) | A | 练习/研究 · AFM Data Team 备考 | 三条都满足才算增强：seed 不来自冻结评测题、答案重新计算、评测用独立题目。训练和测试都围着 GSM8K 同一题族时，换数字、换问法也可能只是让模型记住题族，换到 SVAMP、GSM-Hard 就掉分。看到合成集自称 MATH 提高 15%，先查 seed 和重叠。 |
| [CoderPad：手写 rejection sampling，verifier 和 $k$ 怎么选？](../data-team-interview/questions/tech-screen/dt-rejection-sample-code.md) | A | 练习/研究 · AFM Data Team 备考 | 同一道题采 $k$ 条回答，用独立 oracle 判对错，只留对的；生成器和 verifier 要分开。代码要处理全错、全对和过程假三种情况。$k$ 由当前 pass@$1$ 决定；没有 oracle 就别写 `if judge(y): keep`。 |
| [代码指令数据：从开源片段造题（OSS-Instruct），比让 teacher 空手编好在哪？](../data-team-interview/questions/posttrain-data/dt-code-oss-instruct.md) | S | 练习/研究 · AFM Data Team 备考 | 从许可仓库抽真实代码片段，让 teacher 照着片段出题，题目会覆盖 API、并发、文件和错误处理这些实际问题，比 teacher 凭空反复出教材题更能保持多样性。片段许可证、执行测试和与 HumanEval 的重叠仍然要查。OSS-Instruct 管覆盖，Evol-Instruct 管难度，两者可以叠着用。 |
| [代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？](../data-team-interview/questions/posttrain-data/dt-code-hidden-tests.md) | S | 练习/研究 · AFM Data Team 备考 | 三套测试三种用途：公开测试给模型当改代码的反馈，hidden tests 决定能不能当正例和 RL 奖励，EvalPlus 或新竞赛题做独立评测。hidden tests 要固定哈希，改过测试的 trajectories 要隔离；只过了公开样例或只是编译成功，都不算正确解。 |
| [函数级 HumanEval 数据，和仓库级 SWE 数据，post-training 怎么分桶？](../data-team-interview/questions/posttrain-data/dt-code-repo-vs-fn.md) | A | 练习/研究 · AFM Data Team 备考 | 分成两个桶，分别 data mix、分别评测。函数级是短 prompt、单文件、单测；仓库级要读 issue、定位多个文件、在执行环境里跑 regression tests，混在一起训，模型会把写独立函数的做法搬到仓库任务上。仓库 trajectories 要保留检索和失败恢复的过程，只训最终补丁，模型学不会定位；SWE-Gym 这类可执行环境里的成功 trajectories 也要再筛，见 `dt-swe-success-noise`。 |
| [Panel：最强 teacher 生成的数据，为什么 student 不一定学得最好？](../data-team-interview/questions/panel/dt-teacher-bias.md) | A | 练习/研究 · AFM Data Team 备考 | teacher 回答正确，不代表 student 能学会。还要查过程是否过长、是否用了 student 没有的工具，以及 student 自己 sampling 时能不能找到类似的正确解。太难的示范可以压缩、拆成子任务，或改用 student 自己生成且验证通过的回答。 |
| [Panel：什么时候不要上 synthetic data？](../data-team-interview/questions/panel/dt-when-not-synth.md) | A | 练习/研究 · AFM Data Team 备考 | 假设每一轮都让当前模型生成下一轮训练数据，又没有独立检查。模型经常生成的模式会被反复保留，少见但重要的情况可能越来越少，错误也可能被继续学习。 |
| [数学、代码、工具、聊天 post-training 配在一起，怎么避免互相打掉？](../data-team-interview/questions/posttrain-data/dt-posttrain-mix.md) | S | 练习/研究 · AFM Data Team 备考 | 四类数据分别设 token 配额和 loss 范围再混，可验证任务用 rule-based reward，主观偏好用 human evaluation 或 RM，奖励尺度不同的任务不放进同一个 GRPO 分组，工具返回不计入损失。每加一类数据都回看其余能力，防止代码伤拒答、工具 JSON 伤自然语言。 |
| [CoderPad：数学合成怎么验， boxed 答案怎么抽，过程假怎么办？](../data-team-interview/questions/tech-screen/dt-math-verifier-code.md) | A | 练习/研究 · AFM Data Team 备考 | 从模型输出里抽最后一个 `\boxed{}` 或最终数字，规范化后和独立的标准答案比较，抽不到或对不上就扔。最终答案对、过程自相矛盾的样本，也别直接当 SFT 正例。没有独立 gold labels 时，不能让模型给自己判对。 |
| [OpenAI 的 Shunyu Yao 把 Agent RL 配方写成什么？数据岗听哪一句？](../data-team-interview/questions/posttrain-data/dt-shunyu-second-half.md) | S | 练习/研究 · AFM Data Team 备考 | Yao 的配方按重要性排是语言 pre-training 给的先验、可执行环境和能自动计算的 outcome reward，最后才是算法。数据岗该听的是「任务定义比算法难」，定义任务、构造环境、降低评分噪声都是数据岗的活。只把 PPO 换成 GRPO 变体，解决不了任务和奖励本身的问题。 |
| [Llama 4 博客里的 RL data mixture 是什么？](../data-team-interview/questions/posttrain-data/dt-llama4-rl-recipe.md) | S | 练习/研究 · AFM Data Team 备考 | Llama 4 走轻量 SFT → 在线 RL → 轻量 DPO，理由是 SFT 太多会限制后续在线探索。数据侧先砍掉过易样本，再按 current policy 的 pass@$k$ 动态筛题、丢弃零优势组，batch 里混合能力与提示模板。过滤随 policy update 反复做，每训一轮就用新策略重筛。 |
| [Anthropic 做电脑使用，训练环境为什么故意很少、还断网？](../data-team-interview/questions/posttrain-data/dt-anthropic-cu-recipe.md) | S | 练习/研究 · AFM Data Team 备考 | 少、简单、离线：Anthropic 公开说训练只用了计算器、文本编辑器这类少数可重置的软件，训练期断网。重点是让模型看屏幕像素、数准坐标，用点击和键入直接操作人用的软件，不给它特制的 click_ok API。效果有很大一部分来自模型原有的视觉和工具能力，别全归到 GUI trajectories 数量上。 |
| [Panel 情景：verifier 通过率 98%，合成推理数据为什么仍然伤模型？](../data-team-interview/questions/panel/dt-verifier-counterfactual.md) | S | 练习/研究 · AFM Data Team 备考 | 通过率取决于 verifier 测了什么，不能替代数据有效性。检查答案 leakage、测试覆盖、过程正确性和重复模板，并用 counterfactual 样本审计 verifier；再用等预算 ablation study 区分过滤质量与任务难度。 |
| [Panel 情景：昨天的高价值难题，今天都变简单了，如何更新合成课程？](../data-team-interview/questions/panel/dt-curriculum-moving-target.md) | A | 练习/研究 · AFM Data Team 备考 | 假设昨天只有两成回答做对的一批题，今天已经九成都对。继续用同一份难度标签分配生成预算，可能大多在重复模型已经学会的内容。 |

## 07 · Evaluation 与 Capability Debugging（25 题）

benchmark、evaluation slices、controlled substitution、统计、幻觉、RAG 与回归

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Agent Evaluation：客服 agent 上线前后怎样评估，并把失败转成训练信号？](questions/evaluation/afm-web-agent-evals.md) | S | 公开培训材料改编/导读 | 先验证真实终局，再按失败原因构造数据，避免把满意度直接当正确性。 独立任务成功率提高，重复投诉和越权操作不增加。 |
| [Benchmark Debugging：500 题提高 2 个点，真的变强了吗？](questions/evaluation/afm-web-benchmark-two-points.md) | S | 公开培训材料改编/导读 | 分析同题 paired outcomes、重复 sampling 与数据独立性，再做定向验证。 报告 effect size 和 uncertainty，不能只凭总分做发布决策。 |
| [Panel：评测失败怎么变成下一轮训练信号？](../data-team-interview/questions/panel/dt-data-flywheel.md) | S | 练习/研究 · AFM Data Team 备考 | 每一圈只盯一类失败：用固定评测找出失败，判断是覆盖不足、标签错误、leakage 还是奖励设计的问题，再采集或合成相关任务，data quality checks post-training，最后看同类失败有没有减少。新失败追加成 gold-standard examples，旧评测标签冻结，不拿当前模型的判断去改。线上日志原样当 SFT 正例，模型只会重复自己的错误。 |
| [Frontier 发模型时，主表还在报哪些数据集？](../data-team-interview/questions/frontier-release/dt-frontier-release-map.md) | S | 练习/研究 · AFM Data Team 备考 | 2026 年闭源模型的发布主表主要报科学推理、仓库修复、终端操作、浏览、桌面操作、long context 和 multimodal，MMLU、HumanEval 已经不是重点。比分数前先核对思考预算、工具、尝试次数、运行框架、子集和报分方。evaluation set 的名字也不能当成 training set 的名字。 |
| [GPQA、HLE、FrontierMath、AIME 怎么造，卡的是哪项能力？](../data-team-interview/questions/frontier-release/dt-frontier-science.md) | S | 练习/研究 · AFM Data Team 备考 | 这几套题都考推理，区别在学科和筛题方式：GPQA Diamond 是 198 道博士出题、复核过的四选题；HLE 是 2500 道专家题，收题时先筛掉当时模型能答对的；FrontierMath 是研究级数学；AIME 是每年的竞赛新题。报分要写明子集、年份和工具，允许搜索和无工具是两个实验。 |
| [SWE-bench、Terminal-Bench、LiveCodeBench 怎么造，各卡哪段代码能力？](../data-team-interview/questions/frontier-release/dt-frontier-code-sets.md) | S | 练习/研究 · AFM Data Team 备考 | 这三套测的是不同的代码能力：SWE-bench 修真实 GitHub issue，新测试要从失败变成通过，旧测试还得过；Terminal-Bench 在终端里做完工程任务，运行框架对分数影响很大；LiveCodeBench 按比赛日期切新题，测算法编程、减少背题。三种分数不能合成一个比。 |
| [Panel：benchmark 上有能力缺口，怎么诊断，数据干预怎么选？](../data-team-interview/questions/panel/dt-benchmark-gap.md) | S | 练习/研究 · AFM Data Team 备考 | 先诊断再干预。查评测有没有 contamination、自动指标和 human evaluation 是不是在说同一件事，再按任务、难度、语言和工具步骤 evaluation slices 定位失败；病因对上了才选数据措施，覆盖不足补可验证合成，标签不一致改协议，leakage 换评测，奖励 hack 换独立 oracle。看到低分就直接加 SFT 数据，往往补错了地方。 |
| [BrowseComp、OSWorld、τ² 怎么造，各卡 agent 的哪一段？](../data-team-interview/questions/frontier-release/dt-frontier-agent-sets.md) | S | 练习/研究 · AFM Data Team 备考 | 这几套测的是 agent 的不同环节：BrowseComp 用 1266 道人写的事实题测持续搜索；OSWorld 原集用 369 个真实桌面任务检查最终状态；τ-bench 看 agent 和模拟用户对话后能不能把数据库改对，而且多跑几次都稳；MCP Atlas 测多步工具流程。所以要分开报，合成一个「工具分数」会盖住各自卡住的地方。 |
| [MRCR、MMMU、multilingual 榜怎么造，发版里的 long context 和 multimodal 在测什么？](../data-team-interview/questions/frontier-release/dt-frontier-ctx-mm.md) | S | 练习/研究 · AFM Data Team 备考 | long context 要看模型能不能在长输入里找对信息，「支持 1M」只说明收得下。MRCR v2 在长文里放多个相似目标，要求按指令取 backpointer 定那段，同一模型在 128k 和 1M 下可能差很多。MMMU-Pro 尽量去掉不看图也能答对的题，multilingual 榜要先查题目是不是英语翻译来的。 |
| [哪家 lab、哪个模型、在哪次发布里报了哪项 benchmark？](../data-team-interview/questions/frontier-release/dt-frontier-who-reports.md) | S | 练习/研究 · AFM Data Team 备考 | 按每份官方发布材料分开记分数，写明日期和思考档。比如 Gemini 3.1 Pro 模型卡里的 Opus 分数是 Google 跑的对照，不能算作 Anthropic 自报。 |
| [Panel：怎么查评测被训练数据看见了，查到了怎么办？](../data-team-interview/questions/panel/dt-contamination.md) | S | 练习/研究 · AFM Data Team 备考 | 假设模型能背出评测答案，但逐字匹配没有发现重复。我会怀疑翻译、改写或同一题的变体，先保留证据并隔离可疑数据，避免继续混入训练。 |
| [Panel：加了一批数据，target evaluation slices 掉了，怎么查？](../data-team-interview/questions/panel/dt-worse-after-data.md) | S | 练习/研究 · AFM Data Team 备考 | 先复现只换数据的对照，排除步数、decoding 和奖励的变化；确认是数据造成的，再按 evaluation slices、新旧题、抽查、data mix、learnability 的顺序查 negative transfer、标签错误、data mix 失控、过难样本和 evaluation leakage。旧题降而新题不变，也可能只是去除了原本由 contamination 带来的优势。按查到的证据调整对应的数据，全部回滚会把有用的部分一起丢掉。 |
| [Panel：补一个能力，把另一个打掉了，如何用数据保住已有能力？](../data-team-interview/questions/panel/dt-neg-transfer.md) | A | 练习/研究 · AFM Data Team 备考 | 训练前先列出必须保住的旧能力（英语通用、安全、格式、已经做好的核心任务），固定评测和允许波动；data mix 里给这些域设最低 token 份额，新数据比例逐步提高。旧能力超出波动就先降新来源的比例。目标任务涨了就发版，旧能力可能已经悄悄掉了。 |
| [Panel：怎么用数据压 hallucination？](../data-team-interview/questions/panel/dt-grounding-data.md) | A | 练习/研究 · AFM Data Team 备考 | 造 (证据, 问题, 答案) 形式的训练数据，证据里没有的细节答案就承认看不到，证据里有的答案要能指回证据。两类题在同一份证据上成对出现，防止模型学成一律拒答。摘要、图片问答和工具状态都按这个形状造，单写「不要 hallucination」或用开放世界 QA 都替代不了。 |
| [Apple：on-device LLM 怎么评，延迟、耗电、隐私，为什么不能只报 BLEU？](../us-tech/questions/apple/apple-afm-eval.md) | A | 练习/研究 · Apple 标签题 | 我会分别评任务质量、证据支持、安全、系统性能和隐私，再决定 on-device 模型能否上线。BLEU 只看 n-gram 重叠，既看不出摘要漏限定词，也测不到热降频或邮件是否离开设备，所以只能当辅助回归指标。 |
| [Panel：multilingual 和 locale 数据怎么做，为什么翻译题不能当 evaluation gate？](../data-team-interview/questions/panel/dt-locale-data.md) | A | 练习/研究 · AFM Data Team 备考 | 训练和评测用不同来源。训练可以用验证过的机翻和爬取 corpus 补覆盖，用母语者示范和 human evaluation 改善自然度；正式评测让母语者直接出题，翻译题不自然，测到的只是英语题的影子。过滤阈值按语言做 calibration，配额逐步提高，桶内做 temperature sampling；AFM 公开把 multilingual 比例从 8% 提到 30%，human evaluation 不用翻译题。 |
| [CoderPad：两个人标同一批，Cohen's $\kappa$ 怎么算，低了改什么？](../data-team-interview/questions/tech-screen/dt-kappa-code.md) | A | 练习/研究 · AFM Data Team 备考 | 类别不平衡时偶然一致率本身就很高，所以要报 Cohen's $\kappa$：先建混淆 matrix，再算 $\kappa=(p_o-p_e)/(1-p_e)$，$p_o$ 是观测一致率，$p_e$ 是按边际分布算的偶然一致率。$\kappa$ 低时先改协议和例子，再考虑加人投票。 |
| [Panel：人标预算只够标 1 万条，花在哪？](../data-team-interview/questions/panel/dt-human-budget.md) | A | 练习/研究 · AFM Data Team 备考 | 先建立可靠的 evaluation set，再标注 challenging cases，最后扩大数据量。human-review budget 优先保证 annotation guidelines、gold labels 和评测可靠，再标模型失败的 challenging tasks；能执行验证的数学和代码由人写 seed、teacher 扩充、executor 检查，tool-use trajectories 先让模型预跑、人只纠错。均匀撒到所有任务，会把钱花在模型已有的能力上。 |
| [Panel 情景：隐私聚合看不到罕见失败，怎样为 long-tail 能力补数据？](../data-team-interview/questions/panel/dt-private-tail-budget.md) | S | 练习/研究 · AFM Data Team 备考 | 聚合趋势适合发现常见需求，未观察到稀有模式不代表它不存在。long-tail 能力应结合公开或获授权的 seed、专家设计和受控合成，用独立验证确认；不能为追求覆盖绕开隐私阈值。 |
| [Panel 情景：总成功率涨了 18 个点，为什么两个任务桶都在退化？](../data-team-interview/questions/panel/dt-simpson-release-metrics.md) | A | 练习/研究 · AFM Data Team 备考 | 先固定任务分布，再比较桶内成功率。流量结构变化可能抬高总分，即使每个桶都变差；报告同一权重下的新旧结果，并将模型变化与产品路由变化分开评估。 |
| [Panel 情景：异步 rollout throughput 翻倍，为什么训练奖励上涨但任务成功下降？](../data-team-interview/questions/panel/dt-stale-rollout-incident.md) | A | 练习/研究 · AFM Data Team 备考 | 假设生成服务还在用版本 10，而训练已经到了版本 15。这些回答来自旧策略，不能因为刚刚送到 trainer 就称它们是当前策略的 on-policy 数据。 |
| [CoderPad：按任务家族做配对 bootstrap，如何避免模板多的家族支配结论？](../data-team-interview/questions/tech-screen/dt-cluster-bootstrap-code.md) | S | 练习/研究 · AFM Data Team 备考 | 先计算同一任务上新旧模型的差，再在家族内取均值、对家族等权。bootstrap 时 resampling 家族而非单行，以保持组内相关结构；这种指标评价的是家族平均收益，不是流量平均收益。 |
| [Panel 情景：13-gram contamination scan 全绿，模型却能背出翻译后的评测答案？](../data-team-interview/questions/panel/dt-paraphrase-leakage-audit.md) | A | 练习/研究 · AFM Data Team 备考 | 假设模型能背出评测答案，但逐字匹配没有发现重复。我会怀疑翻译、改写或同一题的变体，先保留证据并隔离可疑数据，避免继续混入训练。 |
| [CoderPad：从 n 次生成估计 pass@k，为什么不能直接用成功率的幂？](../data-team-interview/questions/tech-screen/dt-passk-estimator-code.md) | S | 练习/研究 · AFM Data Team 备考 | 对同一任务的 n 个候选及 c 个成功，使用1减去抽 k 个全部失败的组合比例，再对任务等权平均。它估计至少一个候选成功，不代表模型能识别并选中那个正确候选。 |
| [Apple AFM 面经：RAG 项目如何减少 hallucination，如何做 evaluation？](../data-team-interview/questions/panel/p3a-apple-afm-rag-deepdive.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 先把检索没找到、上下文装不下、证据有但生成错分开诊断。用固定问题与文档版本测证据召回、答案正确性、引用支持和无答案时的行为，再用正确证据替换实验定位瓶颈；只报最终准确率或换一个更强模型，都解释不了 RAG 改动为什么有效。 |

## 08 · Reward、Preference 与 Alignment（33 题）

偏好采集、RM、DPO、RL、judge、奖励偏差和安全边界

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [RM 基础：preference probability 80%，为什么不能说 chosen 的成功率是 80%？](questions/alignment/afm-rm-bt-identifiability.md) | A | 本册自拟/导读 | 我会先分清它预测的是“更喜欢 A”，还是“A 做对了”。preference model 的分数通常不能直接当任务成功率。 |
| [偏好分歧：6 比 4 的投票，soft labels、confidence weight 和 tie 是同一件事吗？](questions/alignment/afm-rm-soft-target-ties.md) | A | 本册自拟/导读 | 我会保留6比4这个分歧，先查它是标注出了问题，还是两种回答各有合理之处，再决定怎么训练。 |
| [同预算选 RM：绝对打分、成对偏好，还是多属性回归？](questions/alignment/afm-rm-rating-versus-pairwise.md) | A | 本册自拟/导读 | 如果我关心两条回答哪条更好，会先考虑成对比较；如果要知道错在正确性还是表达上，分项评分会更有帮助。 |
| [RM 实现排错：取了最后一个 padding token，为什么训练准确率仍很高？](questions/alignment/afm-rm-rm-pooling-truncation.md) | A | 本册自拟/导读 | 我会先检查模型到底在给哪个位置打分，以及截断后两条回答是否还保留了真正的差别。 |
| [RM 榜单高分但 RL 变差：RewardBench 到底测到了什么？](questions/alignment/afm-rm-rewardbench-downstream.md) | A | 本册自拟/导读 | 我会拿当前模型生成的同一批候选，让两个 RM 分别选，再实际检查它们选出的答案。榜单上的排序能力未必覆盖当前模型的错误。 |
| [Best-of-N 越大越差：怎么画出 reward overoptimization 的证据？](questions/alignment/afm-rm-bestofn-overoptimization.md) | A | 本册自拟/导读 | 我会先暂停扩大 N，检查那些高分失败答案。模型可能找到了评审器喜欢、但对任务没有帮助的写法。 |
| [length bias：把奖励除以 token 数，为什么可能惩罚正确推理？](questions/alignment/afm-rm-length-causal-audit.md) | A | 本册自拟/导读 | 我会先查它喜欢的是必要信息，还是重复套话。直接除长度，可能把需要解释清楚的好答案也压下去。 |
| [position bias：AB 和 BA 都选第一个，如何计分和分配人审？](questions/alignment/afm-rm-position-swap.md) | A | 本册自拟/导读 | 这说明判断随顺序变了，不能直接叫 tie。我会先还原到底选了哪条回答，再单独统计不一致。 |
| [同家族 self-preference：换一个 judge 就足以消除 teacher 文风优势吗？](questions/alignment/afm-rm-family-self-preference.md) | A | 本册自拟/导读 | 我会先把它当作一个需要验证的结果：可能能力提高了，也可能只是文风更像 judge 喜欢的样子。 |
| [sycophancy：用户满意度上涨，模型却开始赞同错误前提怎么办？](questions/alignment/afm-rm-sycophancy-truth.md) | A | 本册自拟/导读 | 我会把点赞当作用户反应，而不是直接当事实正确的标签。需要另外判断它是在帮用户，还是在附和用户。 |
| [群体偏好冲突：英语 annotator 共识很高，是否代表所有用户？](questions/alignment/afm-rm-population-disagreement.md) | A | 本册自拟/导读 | 我会先弄清分歧来自理解错误，还是合理的偏好差异。多数票能定义一个总体目标，但不自动代表每组用户。 |
| [主动采偏好：一万条标注预算该花在最大分歧还是最不确定的样本？](questions/alignment/afm-rm-active-label-selection.md) | A | 本册自拟/导读 | 我会优先选有可能改变训练决策的例子，同时留一部分随机样本，防止只看模型最困惑的那一小类题。 |
| [有四个 RM，怎样更可靠、又更省计算地选出好回答？](questions/alignment/afm-rm-ensemble-warm.md) | A | 本册自拟/导读 | 四个 RM 都打分再平均，需要跑四个模型；WARM 先合并参数，之后只跑一个模型；保守奖励会给评分分歧大的回答扣分。最终都要检查选出的回答是否更好。 |
| [PRM vs outcome RM：最终答案对了，过程错了，怎么标、怎么聚合？](questions/alignment/afm-rm-prm-credit.md) | A | 本册自拟/导读 | 最终答对只能证明结果这一项，不能说明每一步都值得学。过程监督要先定义究竟在评价局部正确、进展，还是可恢复性。 |
| [DPO 深挖：chosen 概率也下降，为什么 loss 仍然改善？](questions/alignment/afm-rm-dpo-reference-shift.md) | A | 本册自拟/导读 | 因为 DPO 关心的是 chosen 相对 rejected、再相对 reference 的差距。两条概率都下降时，这个差距仍然可能变大。 |
| [multimodal RM：会写漂亮说明，却看不到图中的错误，怎么揭穿？](questions/alignment/afm-rm-multimodal-evidence.md) | A | 本册自拟/导读 | 我会先确认 judge 真的看到了图片，再检查它的选择会不会跟着图中的关键证据变化。 |
| [安全与帮助性：拒绝所有请求的 RM 为什么可能拿高分？](questions/alignment/afm-rm-safety-multiobjective.md) | A | 本册自拟/导读 | 我会把不该回答却回答，和应该回答却拒绝，分开看。一个安全总分很容易把后者藏起来。 |
| [编程：soft preference BCE，如何区分投票比例与样本权重？](questions/alignment/afm-rm-soft-target-code.md) | S | 本册自拟/导读 | 用奖励差作为 BCE logit，q 表示偏好 A 的概率，w 单独控制样本贡献。全零权重返回可 backpropagation 零，q=0.5 在 margin=0 处 gradient 为零。 |
| [编程：交换 AB／BA 后还原身份，计算 position bias 审计表](questions/alignment/afm-rm-bias-audit-code.md) | S | 本册自拟/导读 | 先把 first/second 映射回 A/B 身份，再分稳定胜负、tie 与不一致。交换平均分与顺序一致率是不同指标，不能把顺序不一致伪装成内容 tie。 |
| [模拟 B 编程：从偏好特征训练一个 RM，并输出独立验证指标](questions/alignment/afm-rm-train-pipeline-code.md) | S | 本册自拟/导读 | 共享线性 scorer 对两条回答打分，差值进入 soft preference BCE；训练变换只拟合训练回答。验证返回 NLL、Brier 和严格偏好准确率，软 tie 不强制当 A 或 B。 |
| [Reward Model：怎样训练，并识别高分却退化的 reward hacking？](questions/alignment/afm-web-reward-hacking.md) | S | 公开培训材料改编/导读 | 用同 prompt 的 preference 数据训练，再用独立评价检查 score 与行为是否一致。 真实质量提高，而非只提高被优化的 proxy。 |
| [DPO：β 控制什么，为什么不能只用“大或小”解释训练行为？](questions/alignment/afm-web-dpo-beta.md) | S | 公开培训材料改编/导读 | 先看相对 log-prob margin，再区分理论 regularization 与实际 gradient scale。 能给出检查 KL、preference 和任务质量的 tuning 实验。 |
| [Post-Training Design：从 base model 到可靠 assistant，数据怎样分工？](questions/alignment/afm-web-posttraining.md) | S | 公开培训材料改编/导读 | 先建立基线，区分 SFT、preference 与 verifiable reward 的作用，再逐步干预。 目标能力提高，同时保留通用能力并控制 over-refusal。 |
| [LLM-as-a-Judge：怎样发现 position、verbosity 和 self-preference bias？](questions/alignment/afm-web-judge-bias.md) | S | 公开培训材料改编/导读 | 用对照 pairs 分离内容、顺序和长度，结合 blind human labels calibration。 判断稳定且与独立正确性相符，保留 disagreement 和不确定样本。 |
| [Panel：reward model 和 preference learning 怎么选，坑在哪？](../data-team-interview/questions/panel/dt-reward-pref.md) | S | 练习/研究 · AFM Data Team 备考 | 先看任务能不能独立验证。代码测试、数学答案、工具状态用 rule-based reward，主观偏好才用人标，再选 DPO 或带 RM 的在线 RLHF；AFM 用 RLOO，文本和图像-文本走 RM，数学和视觉 STEM 走规则。坑在过优化，RM 分要和 human evaluation 核对，preference data 要查长度、礼貌和人与人分歧。 |
| [Panel：人标协议怎么写，一致率低怎么办？](../data-team-interview/questions/panel/dt-annotator-protocol.md) | A | 练习/研究 · AFM Data Team 备考 | 先写协议再开标，每个维度写清定义、正例、反例和不允许的判断捷径，再让两人独立标、算一致率。一致率低先查原因，是协议含糊、题本身不可比还是有长度捷径，查清了再决定要不要加人。AFM 报告里 20-30% 的 preference pairs 人与人之间不同意，他们用 cohesion 挑更容易达成一致的 prompt。 |
| [Panel：LLM-as-judge 会偏什么，什么时候能用？](../data-team-interview/questions/panel/dt-judge-bias.md) | A | 练习/研究 · AFM Data Team 备考 | LLM judge 适合 development set 的快速回归，和 human evaluation gold labels calibration 过才能拿它的赢率做参考，发布仍看 human evaluation。它会偏爱长答案、同家族文风、先出现的候选和礼貌套话，所以要按长度分层、交换候选顺序、保留独立 human evaluation。可执行任务用规则验证，judge 替代不了 oracle。 |
| [CoderPad：preference pairs 怎么滤，margin、长度、差不多的对谁扔掉？](../data-team-interview/questions/tech-screen/dt-pref-pair-code.md) | A | 练习/研究 · AFM Data Team 备考 | preference pairs 要先过滤再用：丢掉 $y_w\approx y_l$ 的对、长度差过大的对，以及 annotator 自己标了「难分」的对。能执行的任务用独立 verifier 的结果当 margin，不让生成模型给自己打分。Llama 3 公开的排序是 edited > chosen > rejected，弱档不进 DPO。 |
| [Panel：偏好和 RM 爱上长答案，数据侧怎么拆？](../data-team-interview/questions/panel/dt-length-hack-data.md) | A | 练习/研究 · AFM Data Team 备考 | 问题出在 preference data 里长回答总是赢，只调优化参数压不住。数据侧构造信息相同、长度不同的回答对，协议写明同等忠实且完整时选短的；human evaluation 和 RM 结果按长度分层分析，BoN 候选中保留简短的 SFT 回答。平均长度增加不代表能力提高。 |
| [Panel：安全 / 拒答数据怎么配，才不会变成一律拒绝？](../data-team-interview/questions/panel/dt-safety-refuse.md) | A | 练习/研究 · AFM Data Team 备考 | 应该拒绝和应该回答的题要成对出现，明确有害的请求配简短拒答，看起来敏感、实际无害的请求配正常回答。只喂有害请求和拒答示范，模型会把拒绝当成通用答案，连正常问题也不回答。评测分开报攻击成功率、over-refusal 和任务有用性。 |
| [Panel 情景：自动 judge 胜率涨了，human evaluation 却反转，先修模型还是修测量？](../data-team-interview/questions/panel/dt-judge-ranking-reversal.md) | S | 练习/研究 · AFM Data Team 备考 | 假设自动 judge 认为新模型更好，人工却更喜欢旧模型。我会先暂停扩大训练，检查两边是否比较相同任务、候选和评分标准。 |
| [Panel 情景：组内奖励几乎都一样，RL 数据怎样恢复学习信号？](../data-team-interview/questions/panel/dt-zero-advantage-groups.md) | A | 练习/研究 · AFM Data Team 备考 | 假设同一道题采了 8 个回答，全部奖励为零。减去组均值后仍全是零，没有哪个回答相对更好；全部奖励为一时也一样。 |
| [Panel 情景：英文 preference labels 很一致，换语言后“好答案”标准冲突怎么办？](../data-team-interview/questions/panel/dt-preference-multilingual-conflict.md) | A | 练习/研究 · AFM Data Team 备考 | 假设英文评审偏好直接简短的回答，另一语言的评审更重视礼貌和语境。先判断这是合理风格差异，还是翻译与事实判断出了问题。 |

## 09 · Multimodal：Vision、Audio 与 Video（16 题）

图文grounding、视觉编码、语音语义、生成图像与时序数据

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Multimodal Search：私人照片搜索的数据、评估和 model upgrade 怎么设计？](questions/multimodal/afm-web-photos-search.md) | S | 公开培训材料改编/导读 | 分开视觉语义与时间人物信息，使用获授权的数据验证，版本化 embedding。 搜索成功改善，同时不跨用户访问且升级期间结果可用。 |
| [Director：multimodal 数据举一个你能讲到底的例子](../data-team-interview/questions/senior/dt-multimodal-data.md) | A | 练习/研究 · AFM Data Team 备考 | 挑一个任务讲到底，比如从海报、文档截图里抽字段：图片从哪来、真数据缺什么、合成补哪一层、进哪个训练阶段、怎么评测。只报一个 LAION 的名字，听的人看不出你做过什么。AFM 2025 报告公开的 text-rich / OCR 数据可以当骨架，换成自己的模态时七项照填。 |
| [设计：multimodal 助手（图/屏/语音），模态延迟不齐](../us-tech/questions/design/design-multimodal-prod.md) | A | 练习/研究 · Apple 标签题 | 语音、图像、屏幕三路到达时间差一个数量级。契约是：没到的模态不当证据，先到的可以先应答或先问。on-device 保隐私和首包；云端跑重视觉。评测分别看答案是否有证据、是否正确、是否适合口头播报，以及各模态超时后的行为。 |
| [Apple：图文 / 屏幕理解 grounding，引用的是像素区域还是 OCR 文本？](../us-tech/questions/apple/apple-multimodal.md) | S | 练习/研究 · Apple 标签题 | 屏幕 grounding 要同时保留像素区域和 OCR 文本：点击、高亮依赖框或 mask，朗读、复制和填槽依赖文本 span。比如模型读出「下午三点」还要指向对应控件，两种输出必须共用能对齐的 id，避免说对内容却点错按钮。 |
| [Apple：on-device / server-side multimodal 训练，视觉塔冻结还是联合，分辨率怎么选？](../us-tech/questions/apple/apple-mm-train.md) | S | 练习/研究 · Apple 标签题 | 我会先定任务需要的分辨率和视觉 token 数，再决定是否解冻视觉塔。MM1 的公开 ablation study 中，低分辨率时冻结更好，高分辨率或偏离 pre-training 分辨率时解冻更好；on-device 还要按 ANE 静态档位训练和导出，server-side 切块方案不能直接搬过去。 |
| [Apple：on-device 视觉 token 预算和 ANE 静态 shape 怎么卡？](../us-tech/questions/apple/apple-vision-edge.md) | S | 练习/研究 · Apple 标签题 | 视觉 token 与文本、输出共享上下文和 KV，先按 $(H/P)\times(W/P)$ 算数量，再检查总数是否在 $S_{\max}$ 内。比如多张截图会挤占工具证据和生成空间；on-device 要预编译分辨率与切块档位，按任务选缩略图、ROI 或 PCC，并验证计算仍留在 ANE。 |
| [设计：multimodal 助手的引用区域与视觉 token 预算](../us-tech/questions/design/design-mm-assistant.md) | A | 练习/研究 · Apple 标签题 | 回答要能指回图上的框或屏幕区域，引用对不上就删句，尚未到达的模态不能当证据。视觉 token 按 patch 占上下文，高分辨率图先粗定位、再裁剪细看；模态延迟状态机见 `design-multimodal-prod`。 |
| [Apple：语音进 LLM，流式 ASR 文本还是音频 token？](../us-tech/questions/apple/apple-audio-llm.md) | S | 练习/研究 · Apple 标签题 | 我会让 ASR 文本负责工具参数和事实核对，写操作等最终识别稳定再执行。音频 token 能保留韵律、叠音等信息，但前缀更长、静态 shape 和证据对齐更难，适合在需要这些信息时补一条短窗口通道。 |
| [Apple：视觉 token 剪枝 / 合并，质量和延迟怎么折？](../us-tech/questions/apple/apple-token-prune.md) | S | 练习/研究 · Apple 标签题 | 视觉 token 可以按 attention 剪掉或按相似度合并，减少后续 prefill 和 KV 开销，但小字和定位通常先受损。on-device 要把剩余数量固定为 $K$ 并保留原图索引；分别测 OCR、grounding 和 VQA，再决定压缩比例。 |
| [CoderPad：image-text pairs CLIP 分怎么滤，合成 caption 要不要同一阈值？](../data-team-interview/questions/tech-screen/dt-clip-filter-code.md) | A | 练习/研究 · AFM Data Team 备考 | 图像和文本各自编码成向量，用余弦相似度当图文匹配分，再按语言和来源分桶，每桶取分位数当阈值。合成 caption 的 CLIP 分会向 teacher model 的分布靠拢而虚高，所以要和网页 alt-text 分开设阈值。重复和安全 CLIP 分管不到，要用各自的 checker，误删靠下游对照来验证。 |
| [Panel 情景：截图问答高分，换一套 UI 就失败，如何排查视觉捷径？](../data-team-interview/questions/panel/dt-mm-shortcut-audit.md) | S | 练习/研究 · AFM Data Team 备考 | 假设截图问答在旧 UI 上很好，换布局就失败。模型可能在读关键控件，也可能记住了按钮通常出现的位置。 |
| [Panel 情景：语音识别 WER 降了，语音助手却更容易做错操作？](../data-team-interview/questions/panel/dt-audio-semantic-regression.md) | A | 练习/研究 · AFM Data Team 备考 | 假设语音识别总体 WER 降低了，却把“不要打开暖气”漏成“打开暖气”。字数错误更少，执行结果仍可能更危险。 |
| [Panel 情景：视频问答能识物却分不清先后，如何造时序训练数据？](../data-team-interview/questions/panel/dt-video-temporal-shortcut.md) | A | 练习/研究 · AFM Data Team 备考 | 假设视频里先拿起杯子、再倒水，模型却把顺序说反。它可能认出了对象，但没有学会事件之间的时序关系。 |
| [Apple CVML 面经：手写二维 circular padding，怎样保留自动求导？](../data-team-interview/questions/tech-screen/p3a-apple-cvml-circular-padding.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 把输出行列映射到原图的模索引，再用 index_select 取值。这样能处理非对称及超过图像尺寸的补边，并保留 gradient；环形补边会改变 boundary conditions，不能不加分析地替换普通图像的零补边。 |
| [Apple CVML 面经：怎样评测生成式图像，而不只看好不好看？](../data-team-interview/questions/panel/p3a-apple-cvml-image-evaluation.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 把图像质量、文本遵循、组合关系、多样性与安全分开测。用成对提示控制颜色、数量、位置等因素，自动评分先与盲评 calibration；FID 不能证明某条提示被满足，单个相似度总分也会掩盖属性绑定错误。 |
| [Apple MLE 原帖：设计大型 video summary 系统，怎样保住证据与时序？](../data-team-interview/questions/panel/p3a-apple-video-summary-design.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 先明确输出是文字摘要还是视频片段，再把音频、视觉和时间证据对齐，分段提取后做带时间戳的全局汇总。评测覆盖事实性、关键事件与时序，不能只看与参考摘要的字面相似度。 |

## 10 · On-Device、Privacy 与 Inference（13 题）

ANE、quantization、KV、投机、on-device / server分工与隐私反馈

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Apple：on-device 权重 quantization / KV quantization，ANE 上 mask 的 -inf 还安全吗？](../us-tech/questions/apple/apple-ondevice-quant.md) | S | 练习/研究 · Apple 标签题 | 权重 palettization、激活和 KV quantization 要分别看：2024 公开方案混合 2/4-bit 权重、约 3.7 bpw，KV 用 8-bit，再用 LoRA 恢复质量。ANE 上 mask 应在反 quantization 后加 fp16 有限大负数，检查非法位置的 softmax 是否为零，避免 $-\infty$ 和 int8 截断导致错误。 |
| [Director：真实世界反馈怎么用，还不把用户数据喂进基础模型？](../data-team-interview/questions/senior/dt-privacy-feedback.md) | S | 练习/研究 · AFM Data Team 备考 | 先问这条反馈要改进什么：基础模型训练、当前请求的处理，还是 on-device 个性化。基础模型用许可、公开和 synthetic data；私人偏好留在设备上，用检索或 adapter 改善；要上传的聚合统计再设计 $\varepsilon$-DP。PCC、数据不落盘和训练许可是三个问题，点踩原文不能直接送进下一轮 SFT。 |
| [Apple：differential privacy 在个性化语言模型里怎么讲 ε，和「数据不出设备」的关系？](../us-tech/questions/apple/apple-diff-privacy.md) | S | 练习/研究 · Apple 标签题 | 数据不出设备说明这条路径没有发布数据，本身没有一个可报的 $\varepsilon$。DP 约束的是发布结果对单条记录的敏感度；个性化上下文优先留在 on-device，只有发布人群统计时再讨论噪声、每日条数和合成预算。 |
| [Apple：Siri 语音链路延迟预算，流式 TTS vs 等完整答案？](../us-tech/questions/apple/apple-siri-latency.md) | A | 练习/研究 · Apple 标签题 | 我会分段记录端点检测、流式 ASR、工具与 LLM 首句、TTS 首包，再决定哪些阶段可以重叠。改写和已确认的长摘要可流式播报，时间、金额、身份和工具事实要等证据齐全再读；公开 on-device 约 0.6 ms/prompt-token、30 token/s，不能直接当整条语音链路的延迟。 |
| [Director：这件事该改 base model 数据，还是只训 feature adapter？](../data-team-interview/questions/senior/dt-adapter-vs-base.md) | A | 练习/研究 · AFM Data Team 备考 | 看问题影响多少个功能。多个功能共有的缺口，比如工具 schema、multilingual 指令、有证据支持的拒答，补进 base model post-training；只属于一个功能的固定格式或口吻，训 feature adapter；用户私有偏好留在 on-device。全回 base model SFT 或全交给 LoRA，都说明范围没切清。 |
| [Apple：Neural Engine 约束（静态 shape、算子白名单）对 Transformer 设计的影响？](../us-tech/questions/apple/apple-ane.md) | S | 练习/研究 · Apple 标签题 | 我会按 ANE 能编译的静态图来设计 Transformer：固定 shape 和 KV 槽位，采用合适的布局、算子与 dtype，再验证整网是否驻留。某层回退到 CPU/GPU 会增加拷贝和耗电，quantization 之前先把这类问题定位清楚。 |
| [Director：on-device distillation 该蒸哪些数据，为什么不从头蒸 14T？](../data-team-interview/questions/senior/dt-ondevice-distill-data.md) | A | 练习/研究 · AFM Data Team 备考 | AFM 公开的 on-device 配方没有从头蒸：先用 1T 高质量数据把 dense on-device 模型 sparse-upcycle 成 MoE teacher，再只在 dense student 最后约 10% 的 token（约 1.4T）上加 distillation 损失，teacher 训练成本因此降了约 90%。蒸什么还要看 3B student 学不学得会、对不对得上产品任务，server 的长 RL trajectories 不宜原样蒸。 |
| [Apple：个性化不能上传全量私有上下文，adapter / 本地检索怎么选？](../us-tech/questions/apple/apple-personalize.md) | S | 练习/研究 · Apple 标签题 | 会变的事实用本地检索，稳定的任务格式用功能 LoRA：比如日程走工具，邮件摘要和通知摘要切换各自的 adapter。公开 adapter 常为 rank 16、16-bit、几十 MB，基础模型冻结 quantization；私有上下文默认留在设备，需要人群统计时再考虑 DP，见 `apple-diff-privacy`。 |
| [Director：guided generation / 约束 decoding 要什么样的 post-training 数据？](../data-team-interview/questions/senior/dt-guided-gen-data.md) | A | 练习/研究 · AFM Data Team 备考 | 训练样本要和框架真正给模型的输入一样：用户请求、框架注入的结构定义，加一个既符合定义、字段也填对的输出。约束 decoding 只保证格式合法，内容填对要靠数据教。只给几条「请输出 JSON」的示范，和框架的实际输入对不上。 |
| [Apple：Foundation Models 公开叙事怎么讲，on-device 和云各自干什么、capability limits 在哪？](../us-tech/questions/apple/apple-foundation-models.md) | S | 练习/研究 · Apple 标签题 | Apple 的公开方案是 on-device 与 PCC 上的 server 模型互补：约 3B 的 on-device 模型处理日常、低延迟和私有上下文任务，更难的推理交给 server-side。on-device 擅长摘要、抽取和短对话，设计时要按能力与隐私要求决定路由，并保留拒答或非生成 UI。 |
| [Apple：on-device KV 的显存和带宽怎么估，GQA 加 quantization cache 各省哪一刀？](../us-tech/questions/apple/apple-ondevice-kv.md) | S | 练习/研究 · Apple 标签题 | on-device decode 每步读取历史 KV，显存和带宽可先按 $2 L H_{\mathrm{kv}} d_h S b$ 估算。GQA 减少 KV head，8-bit cache 减少每元素字节，2025 公开的跨块 KV 共享再减少有效存储深度；long context 要重点检查手机 DRAM / ANE SRAM 的预算。 |
| [Apple：on-device speculative decoding 值得上吗，草稿模型放哪？](../us-tech/questions/apple/apple-spec-edge.md) | A | 练习/研究 · Apple 标签题 | on-device speculative decoding 是否值得，要看草稿成本、平均接受长度、KV 回滚和稳态功耗；草稿很便宜、acceptance rate 高时才可能省时。草稿宜与目标同设备、同静态档位，TTS 只能读已验证 token；Apple 公开的 30 token/s 是投机之前的数字。 |
| [Apple：low-rank adapter 做个性化，和检索怎么选，数据如何不出设备？](../us-tech/questions/apple/apple-rank-adapter.md) | S | 练习/研究 · Apple 标签题 | 会变的事实走本地检索，稳定格式和任务行为走 LoRA；按用户训练时，数据和权重应留在设备。公开产品 adapter 常为 rank 16，开发者 toolkit 提到 rank 32，16-bit 存储约几十 MB，可在冻结 quantization 底模上热切换；遗忘和版本绑定也要设计。 |

## 11 · Agent 与系统设计（34 题）

tool-use trajectories、环境、失败恢复、搜索、服务与长视频摘要

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Recommendation Flywheel：观看行为怎样变成标签，又怎样避免 feedback bias？](questions/systems/afm-web-video-feedback.md) | S | 公开培训材料改编/导读 | 记录 exposure 与上下文，分离显式反馈和行为代理，用独立实验验证变化。 体验与覆盖改善，而不是只强化已有热门内容。 |
| [Apple Siri：工具结果必须 grounding 的回复，怎么设计生成和评测？](../us-tech/questions/apple/apple-siri-grounded.md) | S | 面经依据；细节见来源 · Apple 标签题 | Siri 的关键事实要能逐条定位到工具或检索证据，缺证据时追问或拒答，再把已核对的文字压到语音预算内。比如日历返回「下午三点」，口播压缩时不能丢掉「下午」；评测要拆开证据支持、正确性、语音可读性、拒答和上下文增长后的表现。 |
| [设计：内容安全分级，延迟、申诉、模型+规则](../us-tech/questions/design/design-moderation.md) | A | 练习/研究 · Apple 标签题 | 先按类别和严重度规定放行、折叠、删除、封号等动作，再用规则和哈希处理高确信命中、模型处理语义判断、人工处理灰色案例与申诉。发送路径做低延迟检查，回溯扫描可异步；false rejection 和漏杀按严重度分别评估。 |
| [tool calls 合成：Gorilla / ToolLLM / APIGen 这类 pipeline，grader 是什么？](../data-team-interview/questions/posttrain-data/dt-tool-apigen.md) | S | 练习/研究 · AFM Data Team 备考 | grader 是由便宜到贵的三层检查：JSON 能解析、工具存在、必填字段齐全；参数符合 schema 的类型、枚举和范围；能执行的调用真的执行成功。只训 JSON 格式、不跑环境，模型学会了接口长什么样，却会编造「已添加」这类结果，schema 一变也容易失效。 |
| [工具数据要不要造并行调用？串行 trajectories 会教出什么坏习惯？](../data-team-interview/questions/posttrain-data/dt-tool-parallel.md) | A | 练习/研究 · AFM Data Team 备考 | 要造，但按数据依赖决定：天气、日历这类独立读取放在同一轮并行，先查 id 再写入必须串行。只有串行 ReAct trajectories，模型会把能并行的也排成多轮，延迟和轮次都会涨。环境要真的并跑，部分失败时保留成功结果、只恢复失败项；写操作默认不并行，工具返回不计生成损失。 |
| [工具失败之后怎么改，这种 trajectories 为什么比再堆 10 万成功 JSON 值钱？](../data-team-interview/questions/posttrain-data/dt-tool-error-recover.md) | S | 练习/研究 · AFM Data Team 备考 | 因为只训成功 JSON，模型从没见过合法的失败，遇到 stderr 就可能谎称「已经办好了」。恢复 trajectories 要覆盖参数错误、空结果、权限拒绝和超时，示范改参数、有限重试或诚实停止。失败那一跳不当正例，恢复后的正确调用当正例，工具报错不计生成损失；报错要来自真实环境，失败比例也要控制。 |
| [会改状态的工具，数据里要不要先确认再写？](../data-team-interview/questions/posttrain-data/dt-tool-write-confirm.md) | A | 练习/研究 · AFM Data Team 备考 | 假设用户说“帮我看看能否改签”，这不一定授权助手立即付款改签。查询与提交是两个不同动作。 |
| [Agent SFT：500 条 GPT-4 trajectories 就够吗，多样从哪来？](../data-team-interview/questions/posttrain-data/dt-agent-fireact.md) | A | 练习/研究 · AFM Data Team 备考 | 几百条可 replay 的成功 trajectories，够教会模型调用格式和什么时候停，泛化还不够。多样性来自不同的任务、格式和 teacher，同一条 ReAct 复制再多遍也学不到新东西。FireAct 的约 500 条适合短程、好验证的搜索 QA，SWE、GUI、多轮客服要更多可执行任务。 |
| [SWE-Gym：用可执行仓库当数据工厂，trajectories 怎么留、verifier 怎么训？](../data-team-interview/questions/posttrain-data/dt-agent-swegym.md) | S | 练习/研究 · AFM Data Team 备考 | SWE-Gym 把真实 Python 任务、可执行环境和单测做成一个训练工厂：current policy sampling，测试判成败，成功 trajectories 做 SFT，成败 trajectories 一起训 outcome verifier。任务池要和评测隔开。过测只是必要条件，改测试、漏回归和环境漂移要另外拦。 |
| [Agent 多轮数据里的「用户」用 LLM 模拟，坑在哪？](../data-team-interview/questions/posttrain-data/dt-agent-user-sim.md) | A | 练习/研究 · AFM Data Team 备考 | 模拟器只负责生成用户的话，看不到隐藏数据库和完整的内部政策；成功由真实环境状态和政策 grader 判，模拟器说满意不能当 oracle。要查过度配合、泄密、文风单一和停不下来这几类问题，评测时换 seed 或 teacher 并人工抽查，免得 agent 只学会适应模拟用户。 |
| [Agent RL 数据：怎么判断这批环境是好的，怎么把它造出来？](../data-team-interview/questions/posttrain-data/dt-agent-rl-map.md) | S | 练习/研究 · AFM Data Team 备考 | Agent RL 的数据是任务、可执行环境和可复现奖励三样一起，trajectories jsonl 只拿来冷启动。判断一批环境好不好，看说明是否完整、测试是否稳定、奖励会不会被钻空子，以及当前模型是否偶尔能做对。要扩量就先筛现有任务，或按任务维度合成环境，再并行跑 rollout。 |
| [设计：语音 agent 的打断、端到端延迟、ASR 错误传播](../us-tech/questions/design/design-voice-agent.md) | S | 练习/研究 · Apple 标签题 | 语音 agent 要能在用户开口时停止播放，并从生成状态退回听取新输入，同时区分可取消查询和已发出的写操作。先定首包音频、打断后静音间隔的 SLO，再分配 ASR、LLM、TTS 预算；金额、药名等低置信槽位要确认，避免识别错误沿工具链放大。 |
| [Agent RL 的数据集是什么？为什么说「环境」替代了「jsonl」？](../data-team-interview/questions/posttrain-data/dt-agent-env-is-data.md) | S | 练习/研究 · AFM Data Team 备考 | Agent RL 的数据集是一批能装起来、能打分、能并行跑的任务环境：current policy 进去生成新 trajectories，grader 看结果给奖励。手里的演示 jsonl 只是某个策略在某版环境上采的样，策略或环境一变就过时，主要拿来做 SFT 冷启动。所以盘点时要记环境和奖励版本，训练和评测任务分开。 |
| [Panel：tool-use trajectories 哪一段进 SFT，失败枝怎么用？](../data-team-interview/questions/panel/dt-traj-quality.md) | A | 练习/研究 · AFM Data Team 备考 | 用于 SFT 的 tool-use trajectories 要逐步过检查，每一步参数合法、结果真实、写操作确实完成，最后的回答和实际状态一致，并能在对应环境版本重放。工具返回内容是模型读取的输入，不算进损失。失败尝试可以做恢复示范或偏好负例。 |
| [Apple：on-device agent，工具本地跑、写操作确认、离线怎么收？](../us-tech/questions/apple/apple-ondevice-agent.md) | S | 练习/研究 · Apple 标签题 | on-device agent 由模型输出结构化调用，再由 App 的 `Tool` 或系统 App Intent 执行；发、删、付款等副作用要经过确认。离线时只暴露本地工具，宿主程序限制轮数、耗时和资源，工具失败也要按真实状态返回。 |
| [怎么判断一条 agent 训练任务质量好不好？](../data-team-interview/questions/posttrain-data/dt-agent-task-quality.md) | S | 练习/研究 · AFM Data Team 备考 | 好任务要满足五条：参考修复让测试从失败变成通过，说明足够定位问题，测试考的正是说明里的要求，环境能从头复现，任务和评测隔开。题面像 issue 还说明不了它能用；人审也只代表当时的质量，之后还要复查 contamination 和失效测试。 |
| [2 万条 SWE 任务，怎么滤成能拿来做 Agent RL 的集合？](../data-team-interview/questions/posttrain-data/dt-agent-rl-filter.md) | S | 练习/研究 · AFM Data Team 备考 | 先做四项静态检查：任务是否有效、复杂度是否合适、LLM 质量标签是否过关、测试是否稳定。SWE-rebench 的原始任务不能直接拿去做 Agent RL，公开做法从 21336 条滤到 7249 条。进入训练后，再移除当前模型始终失败或太容易的任务，留下能学、能复现的部分。 |
| [Agent RL 的奖励怎么写，怎样才不算被 hack？](../data-team-interview/questions/posttrain-data/dt-agent-reward-spec.md) | S | 练习/研究 · AFM Data Team 备考 | 奖励 $r$ 以 hidden tests 或最终状态检查为准，可以是 0/1，也可以按测试点计分。可见测试的结果只当环境反馈给模型看，不进最终奖励。补丁和标准补丁的文本相似度会压低功能等价但写法不同的解，最多当辅助信号。 |
| [Agent 环境要打包成什么，才能既评又训？](../data-team-interview/questions/posttrain-data/dt-agent-env-stack.md) | S | 练习/研究 · AFM Data Team 备考 | 打包成一个能 pip install 的任务环境，里面有任务说明和初始资源、把 tool calls 接到真实系统的 harness、给结果打分的 rubric。三样都要能安装、能版本化，训练和评测共用同一套执行和评分逻辑，两边的目标才一致。只有 prompt 模板、没有可执行动作和 scorer，撑不起 Agent RL。 |
| [Agent RL 怎么把环境扩到能真正跑起来？Qwen 和 SkyRL 各做了什么？](../data-team-interview/questions/posttrain-data/dt-agent-scale-env.md) | S | 练习/研究 · AFM Data Team 备考 | 先让单个任务在干净容器里稳定复现，再加并行环境，Agent RL 的瓶颈在环境规模。Qwen 同时跑 2 万个独立环境，SkyRL 用异步执行、任务调度和工具服务把 throughput 提到朴素实现的约 4 到 5 倍。扩之前先查超时、依赖和文件系统隔离。 |
| [为什么 OpenAI 不再用 SWE-bench Verified 报成绩？这对训练数据意味着什么？](../data-team-interview/questions/posttrain-data/dt-agent-verified-stale.md) | S | 练习/研究 · AFM Data Team 备考 | 不能直接算赢。分数涨了先查两件事：测试是不是在考题面没写的要求，题目和标准补丁有没有进训练。Verified 人审过 500 题，仍然有测试质量和 leakage 问题，OpenAI 2026-02 已停报。训练池和评测池要隔开，并留一份按时间划分、能刷新的 holdout。 |
| [Agent RL 一组 rollout 全零或全一对，这批任务还要不要？](../data-team-interview/questions/posttrain-data/dt-agent-passk-zero.md) | S | 练习/研究 · AFM Data Team 备考 | 假设同一道题采了 8 个回答，全部奖励为零。减去组均值后仍全是零，没有哪个回答相对更好；全部奖励为一时也一样。 |
| [GUI / 电脑使用的 Agent RL 数据，和写代码的环境差在哪？](../data-team-interview/questions/posttrain-data/dt-gui-agent-rl.md) | S | 练习/研究 · AFM Data Team 备考 | 差在观测、动作和奖励检查的对象。代码环境看 stdout、靠测试给奖励；GUI 任务是指令加初始桌面快照加状态 checker，模型读截图和无障碍树，点击、键入、滚动，奖励看文件、窗口、单元格这些最终状态。checker 要放在只读镜像里，和 agent 工作区隔离。 |
| [没有现成 GitHub issue 池，怎么合成一批能拿来做 Agent RL 的环境？](../data-team-interview/questions/posttrain-data/dt-agent-tmax-synth.md) | S | 练习/研究 · AFM Data Team 备考 | 没有现成 issue 池，就按技能、复杂度、资源这些维度组合出题，每题配 Docker 环境和程序 verifier，这是 Ai2 TMax 的做法。生成时只保证镜像能 build，全零题留给 RL 训练时剪掉。质量看 teacher pass@$k$ 和领域覆盖，再和 Terminal-Bench decontamination；checker 还要抽查，全对的简单题也要控制比例。 |
| [OpenAI Agent RFT talk：他们让客户怎么写环境和奖励？](../data-team-interview/questions/posttrain-data/dt-agent-rft-recipe.md) | S | 练习/研究 · AFM Data Team 备考 | 先在接近生产的任务分布上跑 baseline，把 prompt、任务范围和工具调好，确认还有提升空间再上 RFT。每条 rollout 用独立环境；reward 先检查 correctness，通过后再评 style，不给「尝试」部分分。多次 sampling 都找不到更好的解，训练就没有学习信号。 |
| [Codex 公开写了怎样的 Agent RL 环境？](../data-team-interview/questions/posttrain-data/dt-codex-rl-env.md) | S | 练习/研究 · AFM Data Team 备考 | Codex 给每个 agent 一个装好代码和依赖的云容器，trajectories 开始后断网，agent 在里面改代码、反复跑测试直到通过。正确性靠测试判，风格放在测过之后另评；断网是怕 agent 搜到标准补丁 contamination 奖励。没有 grader 的仓库，要先建好 checker 才能做 RL。 |
| [Panel 情景：工具选对了，任务成功率却掉了，怎么设计诊断实验？](../data-team-interview/questions/panel/dt-tool-gap-factorial.md) | S | 练习/研究 · AFM Data Team 备考 | 工具选对得更多，任务却更容易失败，说明“选工具”只是流程的一部分。我会先确认两版使用相同任务、工具版本和预算，再检查参数、执行、结果理解与恢复。 |
| [Gemini 2.5 技术报告怎么写 Agent 向的 RL 环境和奖励？](../data-team-interview/questions/posttrain-data/dt-gemini-rl-env.md) | S | 练习/研究 · AFM Data Team 备考 | Gemini 2.5 报告把奖励分成 verifiable reward 和模型生成式奖励，agent 环境以测试、解释器、状态 assertion 当主要判定依据，模型评分补规则覆盖不到的目标，并且要做 calibration。环境要支持多步动作和工具、保存中间状态，才能审计改测试、重复执行但没有推进任务、假装运行这类 hack。直接奖励「想得长」，模型会写更长的推理却没完成任务，所以长度要和最终对错绑在一起。 |
| [Thinking Machines 的 Tinker cookbook 把 Agent RL 环境写成怎样的代码合同？](../data-team-interview/questions/posttrain-data/dt-tinker-agent-rl.md) | S | 练习/研究 · AFM Data Team 备考 | 合同是可安装的 Env 加可复现的奖励：Env 走 reset / step 接口，同一道题起一组环境，组内算 GRPO 优势。有测试的 Harbor 任务以测试结果为奖励，没有测试的文档任务先看状态 diff、再按 rubric 逐条评分。解析失败、工具次数上限和清理规则都写进合同，LLM 法官只评测试覆盖不到的项。 |
| [一亩三分地 Apple Siri：设计搜索系统，数据与检索质量怎么贯通？](../data-team-interview/questions/panel/p3a-apple-siri-search-design.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先澄清搜索对象、权限与质量目标，再设计文档处理、候选召回、排序和评测。数据侧要解释版本、deduplication、负例与分组切分；不能只画服务架构，也不能把点击直接当成相关性真值。 |
| [一亩三分地 Apple MLE：从简单分类器讲到完整数据系统](../data-team-interview/questions/panel/p3a-apple-classifier-data-system.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 先定义标签与误判代价，建立简单分类器，再把标注、分组切分、阈值、部署与反馈串起来。系统质量取决于标签是否稳定、输入是否一致和错误是否被监测，不是只看模型复杂度。 |
| [一亩三分地 Apple AIML Infra：模型推理 Flask API，先把什么契约定义清楚？](../data-team-interview/questions/panel/p3a-apple-flask-inference-contract.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 将 HTTP 校验、预处理、模型推理和输出序列化分开，模型随进程启动加载并固定版本。先验证输入与离线结果一致，再检查超时、并发和资源；返回200不代表模型真正算对，也不能每次请求重新加载权重。 |
| [一亩三分地 Apple AIML Infra：补全有依赖的面向对象 task pipeline](../data-team-interview/questions/tech-screen/p3a-apple-task-dag-code.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 用任务 ID 保存函数和依赖，用入度与后继表做拓扑执行。一个任务只在全部前驱完成后计算，依赖结果按声明顺序传入；共享上游任务每次运行只执行一次，不能用递归重复计算整棵依赖树。 |
| [Apple MLE 原帖：相册照片怎么排序，训练信号与隐私怎样处理？](../data-team-interview/questions/panel/p3a-apple-photo-ranking.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先明确排序要服务的任务，再将可看性、重复 cluster、事件覆盖与用户偏好分开。先用质量和多样性 baseline，再比较个性化收益；未曝光照片没有点击不能直接当负例，私人照片也不能未经授权进入基础模型训练。 |

## 12 · 项目深挖与研究陈述（23 题）

数据项目、Why Apple、方案辩护、研究价值与投入决策

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Jiabao Ji × AFM：个人研究、Benchmark 与面试 Reference](questions/projects/afm-personal-reference.md) | S | 本册自拟/导读 | 主线用 DeepAmbigQA 谈合成与完整性，用 HarnessLLM/HardTestGen 谈奖励可靠性，用 Skill Usage/VisualSkill 谈 feedback loop 与 multimodal，再接工具 RL、效率和遗忘评测。公开团队成果、个人职责和建议实验分开表述。 |
| [个人 Reference 1：DeepAmbigQA，如何把“漏答”变成 synthetic data 问题？](questions/projects/afm-ref-qa-completeness.md) | S | 本册自拟/导读 | 我会讲 DeepAmbigQA：一个答案每句话都对，也可能漏掉另一种合理解释。这个问题让我更关注答案覆盖了什么，而不只是它有没有说错。 |
| [个人 Reference 2：HarnessLLM／HardTestGen，奖励错了比模型弱更危险？](questions/projects/afm-ref-verifier-reward.md) | S | 本册自拟/导读 | 我最直接的经验连接是代码验证：一个可重复运行的测试也会漏掉错误。如果模型一直优化这种反馈，就可能学会利用测试的盲点。 |
| [个人 Reference 3：Skill Usage，如何从评测失败构造 self-improvement feedback loop？](questions/projects/afm-ref-skill-flywheel.md) | S | 本册自拟/导读 | 我会从 skill 没有帮上忙的一次失败讲起，先找到失败发生在哪，再决定修 skill、补选择数据，还是训练适配能力。 |
| [个人 Reference 4：Joint Agent–Speculator RL，预测正确是否就是好奖励？](questions/projects/afm-ref-joint-tool-rl.md) | S | 本册自拟/导读 | 下一次 tool calls 是一个具体例子：从 agent 自己的 trajectories 里提取目标，但预测对了它要做什么，还要再检查它做的是不是对的。 |
| [个人 Reference 5：VisualSkill，怎么讲真实 multimodal 数据与评审偏差？](questions/projects/afm-ref-visual-setting.md) | S | 本册自拟/导读 | 我会用 VisualSkill 讲图像信息什么时候真的有帮助，并检查收益是不是来自多给了信息、或者换了一种评分方式。 |
| [个人 Reference 6：Unlearning，如何把 forget/retain 研究接到数据治理？](questions/projects/afm-ref-unlearning-governance.md) | S | 本册自拟/导读 | 它让我更注意“看不到答案”和“已经删掉信息”之间的区别。数据撤回时，还要同时检查保留能力和后续是否再次混入同一来源。 |
| [三条可讲到底的数据 Pipeline：Skill／Harness、Code 与 multimodal Tool Use](questions/projects/afm-pipeline-overview.md) | S | 本册自拟/导读 | 把三条 pipeline 分别落到技能选择与适配、代码 verifier、截图驱动工具操作。每条都有任务、数据契约、data quality checks、训练视图、独立评价和反馈迭代；已公开方法和建议扩展分别说明。 |
| [Pipeline 1：从 Skill 检索与执行失败，造出可训练的适配 trajectories](questions/projects/afm-pipeline-skill-harness.md) | S | 本册自拟/导读 | 我会先看 agent 为什么没用好现成 skill：是没找到、没选，还是照着做也失败。原因不同，要补的数据也不同。 |
| [Pipeline 2：从正确解、错误解与困难测试，构造代码 post-training 数据](questions/projects/afm-pipeline-code-verifier.md) | S | 本册自拟/导读 | 我最担心的是测试没发现错误，结果把错解当成好数据反复训练。所以我会先检查测试，再用它筛解答和提供奖励。 |
| [Pipeline 3：从票据截图到表格操作，合成 multimodal Tool-Use 数据](questions/projects/afm-pipeline-mm-tool-use.md) | S | 本册自拟/导读 | 我会从票据截图填表这种能检查结果的任务开始。先知道图片里正确的金额，再让 agent 操作，最后读导出的文件判断它到底做没做对。 |
| [Apple AI 项目追问：data gap、model choice、eval 与 production readiness 怎样讲清楚？](questions/projects/afm-web-apple-project-deepdive.md) | S | 公开培训材料改编/导读 | 选一个本人能解释的项目，明确已做部分、公开结果与拟议扩展。 回答能经得住追问，缺少线上结果时不虚构发布经历。 |
| [HM 30 分钟：怎么把项目讲成「数据解锁了能力」？](../data-team-interview/questions/hm-screen/dt-data-story.md) | S | 练习/研究 · AFM Data Team 备考 | 按数据方案讲，不按简历时间线：模型原来做不到什么、我认为原因是什么、改了哪些数据、对照实验支不支持，最后报一条能推翻这个判断的指标。架构只在解释资源限制时出现，主线别变成换了 MoE 或 GQA。 |
| [Director：pre-training / mid-training / post-training 的数据策略怎么切？](../data-team-interview/questions/senior/dt-pre-mid-post.md) | S | 练习/研究 · AFM Data Team 备考 | 先判断缺口属于哪一段再选数据：pre-training 扩知识覆盖、清理网页；mid-training 用高质量材料和验证过的合成调能力 data mix；post-training 用示范、过程监督、偏好和 rule-based reward 教行为。数学、multilingual、long context 这类覆盖性能力，SFT 的条数改不动 base model，所以 continued PT 和 SFT 要分开设计。 |
| [Why Apple, why now：怎么讲出你对 data-centric 的兴趣？](../data-team-interview/questions/hm-screen/dt-why-apple.md) | S | 练习/研究 · AFM Data Team 备考 | Why now 讲数据工作：公开报告里能力扩张越来越多写在过滤、data mix、合成验证，以及把评测失败转成训练数据上。Why Apple 讲我为什么愿意在不用用户私有日志训基础模型的约束下做这件事，再拿自己的经历证明。未公开的算力、团队情况别拿来当理由。 |
| [HM：讲一次数据干预失败了，你怎么知道失败、后来改了什么？](../data-team-interview/questions/hm-screen/dt-failed-data-bet.md) | A | 练习/研究 · AFM Data Team 备考 | 挑一个对照实验推翻了原先假说的数据实验：算力和 evaluation set 不变、只改数据，结果目标任务没涨，或者别的能力掉了。接着讲判断错在哪、后来怎么改过滤标准或配额。训练 loss 降了，证明不了数据方案成功。 |
| [HM：能力缺口和隐私 / 许可打架，你站哪边？](../data-team-interview/questions/hm-screen/dt-legal-capability.md) | A | 练习/研究 · AFM Data Team 备考 | 来源限制守住，能力缺口换合法的路补。先分清要改进的是全球基础模型、当前这次推理，还是这台设备上的 adapter：用户交互默认不进全球训练，PCC 推理也不等于拿到训练许可。来源不合格就换许可研究集、合成任务或 on-device 方案，匿名化替代不了使用授权。 |
| [Director / VP：论文一分钟怎么讲，才像 data team 的贡献？](../data-team-interview/questions/senior/dt-paper-pitch.md) | A | 练习/研究 · AFM Data Team 备考 | 一分钟按这个顺序讲：论文要解决什么问题、和原方法差在哪、一个靠得住的结果、局限，最后说它适合数据流程的哪一段。从 related work 讲起，或者只说「提出了一个框架」，听的人抓不到贡献。没有自己的论文，就讲真读过的工作，说明是别人的。 |
| [Director：怎么证明一批数据值得投入？](../data-team-interview/questions/senior/dt-cost-per-gain.md) | A | 练习/研究 · AFM Data Team 备考 | 按数据源一行一行报：目标任务的提升、regression tasks 有没有掉、contamination rate，以及花掉的 GPU 小时和人工小时。再测边际收益，这个源再加 10% 目标任务还涨不涨，涨不动就停止扩量。条数和 token 数只说明规模，证明不了价值。 |
| [Director 情景：self-training 连续三轮涨分，为什么你仍可能建议暂停？](../data-team-interview/questions/senior/dt-senior-stop-selftrain.md) | S | 练习/研究 · AFM Data Team 备考 | 连续涨分可能来自共同评价盲点、模板重复和对固定测试的过度适配。是否继续，应看独立迁移、覆盖、真实错误和单位预算收益，并让生成、筛选与最终验证保持足够独立。 |
| [Director 情景：small model 筛出的最佳 data mixture，large model 上失效，下一步投什么？](../data-team-interview/questions/senior/dt-senior-proxy-scale-reversal.md) | A | 练习/研究 · AFM Data Team 备考 | 题目里 1B 短训练的最佳配方，在 10B 长训练上失效，已经说明小实验的排序不能直接照搬。先保留源数据和候选版本，避免继续不可逆地过滤。 |
| [Apple AIML 研究面经：为什么需要 reasoning，你的研究证明了什么？](../data-team-interview/questions/senior/p3a-apple-research-why-reasoning.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 先说任务需要哪种可检验的多步能力，再用相同模型、任务和 inference budget 比较直接回答、推理或搜索方案。研究贡献应落在新增能力与证据上；更长的回答、单个榜单涨分或流畅的思考过程，都不能单独证明 reasoning 有效。 |
| [Apple AIML 面经：为什么用这个 data mix，你验证过哪些替代方案？](../data-team-interview/questions/panel/p3a-apple-aiml-mixture-defense.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 先说明 data mix 按文档、样本还是 token 计算，再给当时目标、候选配方和同预算对照。区分目标能力收益、其他能力回归与重复 sampling 成本；若只有一组经验 data mix，就坦承尚未证明最优，并提出预算内最有区分力的下一组实验。 |

## 13 · Culture 与协作（5 题）

See Around Corners、简化、信任、失败、纠错与发布决策

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [Culture：See Around Corners，怎么讲「缺口还没爆，我先用数据堵了」？](../data-team-interview/questions/culture/dt-see-around-corners.md) | S | 练习/研究 · AFM Data Team 备考 | 讲一次总体指标还正常、我已经从某个 evaluation slices 或即将上线的产品功能里看出风险，并在问题爆发前补了数据、做了验证的经历。时间线要能核对：当时的证据、做了什么、后来的结果。照着季度 OKR 做事，证明不了提前发现了风险。 |
| [Culture：你停过哪一批数据，理由是什么？](../data-team-interview/questions/culture/dt-killed-dataset.md) | A | 练习/研究 · AFM Data Team 备考 | 讲一次大家还想加数据、我却停掉某个来源的经历。先说证据，比如混进了评测题、合成样本没验证、加进去后某类能力持续下降，或者许可、隐私不合格；再说怎么隔离、留好恢复条件；最后报停掉后哪项固定评测恢复了。 |
| [Culture 演练：提前预警被证明只对了一半，你怎么讲判断与纠错？](../data-team-interview/questions/culture/dt-culture-falsifiable-warning.md) | S | 练习/研究 · AFM Data Team 备考 | 用当时能获得的证据讲风险预测，并说明预设的验证与停止条件。预判只有部分成立时，区分判断正确、attribution 错误和无效投入，讲清如何修正，不能用事后结果改写早期动机。 |
| [Culture 演练：发布前发现 evaluation protocol 错了，怎样纠正又不让协作停摆？](../data-team-interview/questions/culture/dt-culture-eval-deadline.md) | A | 练习/研究 · AFM Data Team 备考 | 先用最小复现 quantization 决策影响，再提出可执行的修复和临时发布范围，清楚说明证据与未知项。讲真实经历中的责任与沟通，既不隐藏问题，也不把合作方塑造成不在乎质量的人。 |
| [一亩三分地 Apple 文化主题延伸：Simplicity 与 Build Trust 怎么讲数据项目？](../data-team-interview/questions/culture/p3a-apple-simplicity-trust-practice.md) | A | 练习/研究 · AFM Data Team 备考 | Simplicity 讲你如何减少真实复杂度，并用质量、成本或恢复能力验证；Build Trust 讲你怎样暴露不确定性、兑现承诺和处理分歧。两者都需要真实行动与结果，不能只背价值观词语。 |

## 14 · 全流程模拟与个人材料（8 题）

两套45分钟技术卷、附件诊断、feedback loop实验、五场Panel、Director及个人证据模板

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [45 分钟模拟 A：从零完成 PyTorch 分类训练并口述 data pipeline](questions/mock/afm-mock-screen-a.md) | S | 本册自拟/导读 | 在 45 分钟内跑通 training set standardization、mini-batch SGD、验证与错误分析；同时解释来源、deduplication、分片和版本。先保证可复现且无验证 leakage，再谈模型复杂度。 |
| [45 分钟模拟 B：preference data 清洗、RM 训练与 bias 审计](questions/mock/afm-mock-screen-b.md) | A | 本册自拟/导读 | 先确认偏好、tie 和 confidence weight 的含义，再训练 RM，最后检查长度、位置与 source bias。模型跑通后仍要用独立执行结果判断选择质量。 |
| [附件诊断 1：总体成功率涨了，两个任务桶为什么都退化？](questions/mock/afm-mock-debug-tools.md) | A | 本册自拟/导读 | 先用统一分布重算指标，再用错误样本区分工具选择、参数与状态核验。当前汇总表只能说明分布混杂，不能单独证明某个训练源导致退化。 |
| [附件诊断 2：RM 分和自动胜率上涨，真实工具成功却下降](questions/mock/afm-mock-debug-reward.md) | A | 本册自拟/导读 | 将候选生成、奖励排序、judge 测量和任务真值拆开检查。扫描 best-of-N、交换位置、核对高分错例，再决定修 RM 数据、评测协议还是生成策略。 |
| [贯穿案例：截图创建日历事件，从合成到评测再到偏好 feedback loop](questions/mock/afm-case-endtoend.md) | A | 本册自拟/导读 | 用同一个任务贯穿视觉证据、字段抽取、工具执行、恢复 trajectories、偏好选择和隐私反馈。每轮只针对确认的缺口改数据，并用独立任务和副作用指标验收。 |
| [个人材料包：主项目、失败、提前预判、multimodal 与论文的可填写模板](questions/mock/afm-personal-evidence-pack.md) | A | 本册自拟/导读 | 把每个故事绑定真实证据、个人贡献和时间线，分别准备60秒、90秒和5分钟版本。没有经历的地方保留空白或标为设计方案，不能把示范改写成个人业绩。 |
| [Panel 五场模拟：四轮技术＋一轮 Culture 的题目、追问与评分](questions/mock/afm-panel-rubric.md) | A | 本册自拟/导读 | 四场技术分别练飞轮、合成、诊断和偏好，第五场使用真实提前预判故事。每场45分钟，有统一 scoring rubric、追问时点与复盘记录。 |
| [Director／VP 30 分钟模拟：预算、阶段选择与暂停 self-training](questions/mock/afm-director-mock.md) | A | 本册自拟/导读 | 先给可执行决策，再用证据解释取舍。面试官连续改变预算、来源和风险约束，候选人须说明哪些结论保持、哪些需新实验，而不是每次重新堆术语。 |

## 15 · 研究案例与跨团队迁移（64 题）

原 Data Team 手册的公开研究案例与其他实验室资料，保留归属

| 题目 | 级别 | 依据/范围 | 复习要点 |
| --- | --- | --- | --- |
| [准备三个案例，回答大部分「什么是好数据」类问题](../data-team-interview/questions/cases/dt-case-map.md) | S | 练习/研究 · AFM Data Team 备考 | 准备一个自己的案例和两个公开研究案例。被问到「什么是好数据」这种抽象问题时，先用一句话回答，再说「拿我做过的 X 举例」，讲其中最相关的那一步。 |
| [各家 data 岗公开在问什么？](../data-team-interview/questions/labs/dt-labs-map.md) | S | 练习/研究 · AFM Data Team 备考 | 这张卡按题型列出各家 data 岗公开在问什么，大多是同一组数据方法：网页抽取与 deduplication、data mix、代码执行合成、工具与 GUI trajectories、偏好标注、诚实评测，以及 data leakage 和 synthetic data 坍缩。每题都先给选择，再讲方法为什么有效、哪里要调，最后说数据从哪来、谁来验证；涉及用户日志的题，先确认这类来源能不能用。 |
| [案例 1/4：agent 做网页设计很弱，怎么确定弱在哪？](../data-team-interview/questions/cases/dt-case-web-diagnose.md) | S | 练习/研究 · AFM Data Team 备考 | 先把「不好看」拆开：能不能渲染、功能能不能用、设计好不好，分开打分，再去数失败样本落在哪一层。我们拆完发现页面大多能跑、功能也基本对，问题集中在设计都长一个样，说明模型缺的是设计上的取舍，所以下一步先试 skill。 |
| [OpenAI：无标 corpus 里怎么挖「新」数据并 bootstrap？](../data-team-interview/questions/labs/dt-novel-bootstrap.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 从少量 seed 开始迭代：seed 来自冻结评测的失败案例、研究集和许可领域 hard examples，用小分类器给未标注数据打分，综合质量、新颖度和不确定性挑出值得人看的样本，标完更新分类器再筛下一轮。分类器可以用合成标签起步、按语言做 calibration；每轮看冻结评测有没有真的改善，边际收益停了就停。 |
| [案例 2/4：先写 test-time skill 补能力，什么时候该训进权重？](../data-team-interview/questions/cases/dt-case-web-skill.md) | S | 练习/研究 · AFM Data Team 备考 | 先写一份几百 token 的设计 skill 放进上下文，当天就能对照。skill 能修好的部分说明模型会、只是缺引导，适合之后训进权重；修不好的才要去造数据。效果稳定、调用频繁、上下文成本明显的时候，就该把它训进模型。 |
| [OpenAI 练习题：用户对话怎么做成 SFT？](../data-team-interview/questions/labs/dt-userlog-contrast.md) | S | 练习/研究 · AFM Data Team 备考 | 假设用户把助手回答改写后才使用。改写可能修正事实，也可能只是调整语气，不能直接把原回答标成坏、改写标成好。 |
| [案例 3/4：用 rejection sampling + SFT + RL 把 skill 训进模型，哪些样本算好数据？](../data-team-interview/questions/cases/dt-case-web-internalize.md) | S | 练习/研究 · AFM Data Team 备考 | 带着 skill sampling，用渲染、功能、视觉三道检查过滤，训练时把 skill 从 prompt 里拿掉做 SFT，之后再上 RL。最值钱的样本是「不带 skill 失败、带 skill 成功」的那些，它们正好是 skill 补上的能力。 |
| [FineWeb：跨所有 crawl 快照做全局 MinHash，为什么可能更差？](../data-team-interview/questions/labs/dt-global-dedup.md) | S | 练习/研究 · AFM Data Team 备考 | 因为跨快照反复出现的往往是优质网页，全局 near-duplicate deduplication 把它们只留一份，一次性出现的低质页面比例就上去了。网页先在快照内去 near-duplicates，跨快照重点处理页脚、导航和评测指纹，范围用 small model 的下游对照来定。 |
| [案例 4/4：网页里的数字是模型编的，怎么设计 hallucination penalty？](../data-team-interview/questions/cases/dt-case-web-grounding.md) | S | 练习/研究 · AFM Data Team 备考 | 让模型写每个数字时带上它在数据里的地址，再按地址回查，对不上就扣分，扣多少按错的类型定。只罚错的话模型会少写数字，所以另加一项覆盖率。最理想是数字直接由渲染器按地址填，当时工程上没做成。 |
| [DoReMi：small model Group DRO 学出的 data mix，能不能直接拿来训 large model？](../data-team-interview/questions/labs/dt-doremi-mix.md) | A | 练习/研究 · AFM Data Team 备考 | 不能直接用，拿来当 core pre-training data mix 的初值比较合适。DoReMi 优化的是相对 reference model 的最坏域损失，目标里没有摘要 human evaluation 或工具成功率，所以还要在 large model 和下游 evaluation slices 上验证。另外要先清理并合理划分数据域，否则最差域是垃圾时它会被一直加权。 |
| [研究案例：想在 Terminal-Bench 上爬坡，RL 环境数据怎么做？](../data-team-interview/questions/cases/dt-case-tbench-climb.md) | S | 练习/研究 · AFM Data Team 备考 | 几篇公开工作放在一起看，结论是环境要贴近真实任务、难度卡在中间、verifier 靠得住，环境数量排在最后。Endless Terminals 在自己的 development set 上涨了很多，到 Terminal-Bench 几乎不动；River 只用不到三成的环境，过滤掉坏 verifier 后增益更大。 |
| [Llama 3：pre-training 最后抬高质代码 / 数学（annealing），有什么用？](../data-team-interview/questions/labs/dt-llama-anneal.md) | A | 练习/研究 · AFM Data Team 备考 | Annealing 在主 pre-training 末段降 learning rate、上 sampling 高质量数学和代码，补可验证的能力，格式和工具行为留给 post-training。Llama 3 最后约 40M token 是它自己的公开配方，换模型要重新定，常用基准的 training set 不能混进来。它还能拿来低成本评估新数据源。 |
| [研究案例：tool calls RL，奖励粒度和合成环境怎么决定数据质量？](../data-team-interview/questions/cases/dt-case-toolcall-rl.md) | S | 练习/研究 · AFM Data Team 备考 | tool calls RL 里，奖励就是数据的标签。ToolRL 说明奖励要拆到工具名、参数名、参数值三层，额外鼓励长思考会掉点；Kimi K2 说明没有真实工具时可以大规模模拟，但模拟环境和 judge 的偏差要靠真实执行来校。 |
| [Llama / Phi / FineWeb-Edu：质量分类器用合成标签训，坑在哪？](../data-team-interview/questions/labs/dt-quality-clf-synth.md) | A | 练习/研究 · AFM Data Team 备考 | 坑在于一个分类器、一个阈值套所有数据：teacher 偏爱正式英文时，论坛内容和 low-resource 语言会被大量误删，和评测同族的分类器还会让 contamination 更容易混进来。所以按语言和领域分别训练或 calibration，代码、数学、对话不用网页教育价值标准；阈值用 small model 下游实验选，teacher 版本和抽查一致率记进 dataset card。 |
| [Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？](../data-team-interview/questions/labs/dt-synth-bench-trap.md) | S | 练习/研究 · AFM Data Team 备考 | 假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。 |
| [Anthropic：RLAIF / 宪法反馈，judge 开始喜欢自己的文风怎么办？](../data-team-interview/questions/labs/dt-rlaif-loop.md) | A | 练习/研究 · AFM Data Team 备考 | 固定 judge 的版本，再用 human evaluation 和规则独立检查结果。策略会越来越会模仿 judge 偏爱的长文和套话，judge 要是每轮换成 current policy，就等于让模型给自己打分，最后 judge 给高分、human evaluation 却不涨。能直接验证的任务优先用 rule-based reward，human evaluation 分歧明显的题留给人来判断。 |
| [Anthropic：RLHF 什么时候会奖励不诚实？数据上怎么拆？](../data-team-interview/questions/labs/dt-sycophancy-data.md) | A | 练习/研究 · AFM Data Team 备考 | human evaluation 更偏爱客气附和的回答、给简短纠正打低分时，RLHF 就会奖励不诚实。数据上要拆开：用成对样本教模型纠正错误前提（chosen 按证据纠正，rejected 附和），annotation guidelines 把事实忠实和礼貌分成不同维度，评测单列 sycophancy evaluation slices。满意度高，单独证明不了模型诚实。 |
| [Tesla / Scale：车队 trigger 和影子模式，接到 LLM 评测失败怎么说？](../data-team-interview/questions/labs/dt-trigger-ood.md) | A | 练习/研究 · AFM Data Team 备考 | 把车队 trigger 的思路换成「评测失败触发收集」：固定评测失败、judge 或人与 RM 的分歧、工具验证失败和低置信步骤，才值得进 feedback loop，再用许可或 synthetic data 复现。影子模式的输出当不了 gold labels，用户没改摘要也不等于认可。可验证样本自动扩，主观 hard examples 按人工预算处理。 |
| [Llama 3 §3.1：自研 HTML 抽取，URL / 文档 / 行三级 deduplication，哪级会 false rejection 好文本？](../data-team-interview/questions/labs/dt-llama-extract.md) | A | 练习/研究 · AFM Data Team 备考 | 最容易 false rejection 好文本的是行级 deduplication：它删掉导航这类重复模板，也会删掉反复出现的好句，所以要按内容类型抽查。URL 级保留最新版本，文档级 near-duplicates 的范围用下游实验选；抽取阶段数学、代码和 multilingual 分开处理，保留数学和代码结构以及图片 alt 文本。「每 30M 篇中超过 6 次」是 Llama 自己的阈值，换数据要重新验证。 |
| [Anthropic 编程题：带权重的 DataBatcher，断点续跑怎么写？](../data-team-interview/questions/labs/dt-weighted-batcher.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 按 token 预算组 batch，checkpoint 保存每个数据源的读取 offset 和随机数状态，恢复时从原位置继续读；只恢复 random seed 的话，每个源会从头再读一遍。数据源耗尽时把它的概率设为零并报告，不悄悄改变 data mix。权重本身由上层决定，调 data mix 就是改 `weights`。 |
| [xAI：从 X 时间线灌进 Grok 的 data pipeline 怎么设计？](../data-team-interview/questions/labs/dt-x-feed.md) | A | 练习/研究 · AFM Data Team 备考 | 按时间分区的流式 pipeline 来设计：摄入时删帖用墓碑记录，过滤做语言识别并去掉广告、机器人和刷屏，转发按 URL deduplication 并保留引用计数，时效源放进 mid-training 或 annealing 阶段。来源要先过许可，公开帖子不等于能进基础模型，大规模汇聚 personally identifiable information (PII) 的时间线要排除。实时数据值不值，用训练截止后的事件问答来证明。 |
| [DataComp-LM：从 Common Crawl WET 起步，为什么公开集常吃亏？](../data-team-interview/questions/labs/dt-dclm-wet.md) | A | 练习/研究 · AFM Data Team 备考 | 因为瓶颈常在正文抽取。WET 是 Common Crawl 预先抽好的纯文本，抽错漏掉的内容后面的质量分类器补不回来。DCLM 固定同一套过滤、只把 WET 换成从 WARC 原始 HTML 重新抽取，Core 就高了至少 2.5 点，所以先定抽取，再调分类器和阈值。 |
| [Anthropic 风格：safety evaluation gate 被训练数据看见了，你先停什么？](../data-team-interview/questions/labs/dt-contam-hold.md) | A | 练习/研究 · AFM Data Team 备考 | 假设模型能背出评测答案，但逐字匹配没有发现重复。我会怀疑翻译、改写或同一题的变体，先保留证据并隔离可疑数据，避免继续混入训练。 |
| [Tulu 3 / 迭代 DPO：离线 preference pairs 过期了怎么办？](../data-team-interview/questions/labs/dt-onpolicy-pref.md) | S | 练习/研究 · AFM Data Team 备考 | 用当前模型重新 sampling，再重新比较好坏。旧 preference pairs 来自 old policy，模型现在会写的回答没人监督；直接拿 UltraFeedback 这类现成偏好集来训，监督的是别的模型的回答分布。可验证任务在线 sampling、用 rule-based reward 评分，主观偏好定期用 current policy 重采，交给人或 经过 calibration 的 judge 标。 |
| [Llama 3：为什么 preference pairs 要有 edited，还要丢掉「差不多」的对？](../data-team-interview/questions/labs/dt-llama-edit-pref.md) | A | 练习/研究 · AFM Data Team 备考 | 两个做法都是为了让偏好信号更干净。chosen 只是两条里较好的那条、未必达标，所以 Llama 3 让 annotator 再改一遍，得到 edited > chosen > rejected；差距很小的对 label noise 大，reward model 只用清晰的 preference pairs，DPO 只留「明显更好」和「更好」两档。AFM 用 cohesion 优先选 human evaluation 一致的 prompt，也是在减少弱信号。 |
| [OpenAI：过程监督标签怎么采？DeepSeek 为什么后来不用神经 PRM？](../data-team-interview/questions/labs/dt-prm-steps.md) | A | 练习/研究 · AFM Data Team 备考 | 先问这道题能不能直接验证：能执行验证的先用 rule-based reward，只有最终答案检查发现不了的过程错误，才值得做人工或神经 PRM。逐步监督更省样本，但人工标注贵，要先统一步骤怎么划分并保留独立的结果检查，过程编造的 trajectories 不进 CE 正例。DeepSeek 不用神经 PRM，是因为它在大规模 RL 里会被 hack，重训又贵。 |
| [DeepSeek-R1 / Tulu RLVR：verifiable reward 的「数据」到底是什么？](../data-team-interview/questions/labs/dt-rlvr-data.md) | A | 练习/研究 · AFM Data Team 备考 | RLVR 的数据是题目加可验证的 scorer。数学答案、代码测试和工具状态能给 rule-based reward；开放摘要和自然度判不了对错，要单独用人类偏好，和 rule-based reward 分开记。每题绑定 scorer 版本，全对或全错的题先调难度，必要时先用 SFT 冷启动。 |
| [Anthropic 笔试：fine-tuning 之后怎么证明模型相对 base model「漂了」？](../data-team-interview/questions/labs/dt-value-drift.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 漂本身不坏，要证明的是偏离发生在声明的轴上、已有能力还在。用同一批固定 prompt 对比 base model 和 fine-tuned model：按 evaluation slices 算 KL，跑行为套件，分开报安全与有用性，再做分维度 human evaluation。KL 大只说明分布变了，好坏要靠行为套件和 human evaluation 判断，总 loss 和 Arena 赢率给不出这些信息。对照数据用研究集和 frozen evaluation set。 |
| [Llama 3：工具对话按整段标偏好，还是按每一跳？](../data-team-interview/questions/labs/dt-tool-turn-pref.md) | A | 练习/研究 · AFM Data Team 备考 | 按每一跳标：在相同上下文中生成两条助手消息让人选择或编辑，把选中或编辑后的回答写回对话再继续。工具返回 annotator 不能修改，也不作为偏好候选，调用对错交给可执行检查。整段只标一个成败，reward model 会把运气算进调用质量，也定位不到哪一步出错。 |
| [Llama 3：代码 post-training 合成，模型改自己的单测算过关吗？](../data-team-interview/questions/labs/dt-code-exec-synth.md) | S | 练习/研究 · AFM Data Team 备考 | 不算。模型改测试才通过，等于改了判分条件，这种 trajectories 要隔离，不当 SFT 正例。做法是在模型动手前记下测试的哈希、条数和 assertion，只有通过原测试的修复才算成功；执行反馈可以拿来学修复，编译器输出不计入生成 loss。 |
| [开源代码合成集自称 HumanEval +9%，你先查什么？](../data-team-interview/questions/labs/dt-code-bench-bleed.md) | A | 练习/研究 · AFM Data Team 备考 | 假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。 |
| [SWE trajectories：测试过了就能整段进 SFT 吗？](../data-team-interview/questions/labs/dt-swe-success-noise.md) | S | 练习/研究 · AFM Data Team 备考 | 不能。hidden tests 通过只说明最终补丁对，过程里仍可能有改测试、重复执行但没有推进任务和反复失败的 tool calls，整段进 SFT 会把这些一起教给模型。先丢掉改过测试文件的 trajectories，再按过程质量筛片段，loss 只算助手生成的编辑和推理。SWE-Prime 筛出的约 10% 子集胜过全部已解决 trajectories，这个比例是论文 ablation study 结果，换了数据要重新定。 |
| [BFCL：目录里没有能用的工具，模型还是调了，数据上怎么拆？](../data-team-interview/questions/labs/dt-tool-irrelevance.md) | A | 练习/研究 · AFM Data Team 备考 | 补两类示范：当前工具目录完成不了请求时，正确做法是不调用，说明限制或询问用户；缺少信息时，先调只读查询再执行。SFT 如果总假设有工具可用，模型就学会见 schema 就填，编造名称和参数。BFCL 的 Function Relevance Detection 专门测第一类，负例要用语义相近的无关工具来造。 |
| [trajectories SFT 之后，换个工具名就不会了，学的是语义还是接口？](../data-team-interview/questions/labs/dt-tool-alias.md) | A | 练习/研究 · AFM Data Team 备考 | 多半学的是接口。检验方法是同一任务换工具名和 schema 再评，原接口能完成、换名就失败，说明模型依赖接口记忆。训练时同一能力要覆盖多套工具名和 schema，示范格式贴近部署时真正注入的工具规格，并在 dataset card 的 `surface` 中记录接口版本。 |
| [Agent 终局状态对了，中间少调一次只读工具，算不算过？](../data-team-interview/questions/labs/dt-agent-state-path.md) | A | 练习/研究 · AFM Data Team 备考 | 不算过。少调一次必经的只读查询，说明参数是猜的，最终状态碰巧对了也该判失败。做法是在题卡里用 `must_call` 列出必须拿到的证据，逐个核对参数是否来自前一步的工具返回，再确认写入落了库；模拟用户的对白不直接当 gold labels。 |
| [RLEF：执行反馈进对话，奖励却看私有测试，数据怎么切？](../data-team-interview/questions/labs/dt-rlef-split.md) | A | 练习/研究 · AFM Data Team 备考 | 每题准备两套测试：公开测试的结果可以作为 observation 返回给模型，最终奖励只由不展示的私有测试决定。两套混用，模型会背公开测试、改代码迎合样例。两套测试分别记录哈希，stderr 不进 cross-entropy 训练目标，公开测试全过但私有测试失败，奖励仍为 0。 |
| [OpenAI：工具返回里写着「忽略以上指令」，训练数据怎么造？](../data-team-interview/questions/labs/dt-tool-inject.md) | S | 练习/研究 · AFM Data Team 备考 | 造权限冲突的成对样本。按 system > developer > user > tool 的层级，工具、网页和邮件里的指令只是数据，改变不了原任务；chosen 遵守高权限要求并完成任务，rejected 服从注入。高权限要求要能自动核对，工具返回保留原样，模型才练得到识别攻击。 |
| [OSWorld / AndroidWorld：屏幕 trajectories 哪一段能进 SFT？](../data-team-interview/questions/labs/dt-gui-traj.md) | A | 练习/研究 · AFM Data Team 备考 | 只有能对上执行当时屏幕元素、能 replay 的动作才能进 SFT；依据过期截图的操作和犹豫点击要丢掉或 mask，任务成功与否由环境状态判。OSWorld 发现文本操作历史有帮助，堆历史截图没有同样的收益。trajectories 用研究集、合成界面或许可演示，用户真实屏幕涉及隐私。 |
| [WebGPT：为什么没有引用，事实偏好几乎标不动？](../data-team-interview/questions/labs/dt-webgpt-cite.md) | A | 练习/研究 · AFM Data Team 备考 | 因为没有引用，annotator 只能凭记忆或文笔判断真假，事实 preference labels 噪声很大。WebGPT 把数据拆成两部分：浏览 trajectories 教模型怎么搜，带引用的答案让 annotator 逐句核对出处。「引用是否支持」和「来源是否可信」要分开评，评测时再去掉引用比一次，防止引用格式本身让答案显得可信。 |
| [Llama 3：post-training 怎么让模型「知道自己会什么」？](../data-team-interview/questions/labs/dt-knows-what.md) | A | 练习/研究 · AFM Data Team 备考 | 先探测模型已经会什么，再教它对不会的题承认不知道。拿事实题反复问，模型多次给出具体但错误的回答，就配上承认不知道的示范；用 SFT 硬灌新知识更容易引发 hallucination，新事件交给搜索。探测题从许可的 pre-training 材料里生成。 |
| [Llama 3：什么题该调搜索，什么题不该？数据怎么切桶？](../data-team-interview/questions/labs/dt-when-to-search.md) | A | 练习/研究 · AFM Data Team 备考 | 按三类切桶：必须搜（时事、截止日后的信息）、禁止开放搜索（邮件、日历、图片里的私人信息，用对应工具读）、可搜可答（稳定常识，两种示范都留一点）。只教「有搜索就搜」，模型会把常识题也拖去检索，增加延迟和隐私风险。读私人数据的工具和开放搜索分成两套 mix，配额分开记。 |
| [τ-bench：过一次库状态，为什么还不够当正例？](../data-team-interview/questions/labs/dt-tau-passk.md) | A | 练习/研究 · AFM Data Team 备考 | 假设同一道工具任务跑了五次，只成功一次。Pass@5 关心至少一次成功，因此可能很好看；pass^5 关心五次都成功，就会很低。它们回答的是探索能力和执行可靠性两种问题。 |
| [DeepSeek-R1：800k distillation 集是怎么滤的，small model 为什么只做 SFT？](../data-team-interview/questions/labs/dt-r1-distill.md) | A | 练习/研究 · AFM Data Team 备考 | R1 在 RL 收敛后做 rejection sampling，只留正确且可读的 trajectories，再加通用任务一起做 SFT：约 600k 推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。small model 只做 SFT，是为了单独看这些 trajectories 能不能把能力传过去。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。 |
| [OpenAI deliberative alignment：政策写进思考，训练时为什么要把 spec 撕掉？](../data-team-interview/questions/labs/dt-deliberate-spec.md) | S | 练习/研究 · AFM Data Team 备考 | 为了让模型学会自己回忆该用哪条规则。生成安全示范时让模型看着政策、在推理里引用条款，SFT 时把政策正文拿掉，模型只能靠回忆；RL 的 scorer 仍看着政策来核对。验证同时看越狱抵抗和 over-refusal，并记下条款版本。 |
| [WebArena：812 道网页任务，动作序列对了就能进 SFT 吗？](../data-team-interview/questions/labs/dt-webarena-traj.md) | A | 练习/研究 · AFM Data Team 备考 | 不能。同一任务有多条合法路径，判断标准是最终功能 assertion 是否通过，再查过程中有没有改了不该改的状态，逐次点击不必和人类一致。失败 replay 可作负例或恢复材料，不能直接当成功示范。训练实例还要和评测模板 deduplication。 |
| [IFEval 只有 541 条，post-training 能不能直接拿来训？](../data-team-interview/questions/labs/dt-ifeval-overlay.md) | A | 练习/研究 · AFM Data Team 备考 | 不能。IFEval 的 541 条英文题是 evaluation set，拿来训就失去评测意义。要借它的思路另造 training set：从自己的 SFT 数据抽任务、叠同类的可执行约束，生成独立的 RLVR 数据；同时检查约束能否同时满足，按语言改写 checker，并单独评内容质量，免得只学会格式。 |
| [s1：1000 条推理 SFT 为什么够用，多堆 59k 为什么未必更好？](../data-team-interview/questions/labs/dt-s1k.md) | A | 练习/研究 · AFM Data Team 备考 | 1000 条够不够，取决于 student model 已经会多少，以及示范是否同时兼顾难度、多样性和质量。s1K 是在已指令对齐的 32B 上补一点推理，条数没法和别的配方横比；多堆 59k，质量和难度跟不上就只是加噪声。Budget forcing 是 inference 时控制思考长度的 decoding 方法，不算训练数据；student 学不会的超长推理要过滤，分布一偏还得靠 RLVR。 |
| [OpenAI 高频笔试：现场训分类器、摸数据集，data 岗怎么开口？](../data-team-interview/questions/labs/dt-oai-classifier.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 先看清字段、标签来源和缺失，再按文档或 near-duplicates cluster 划分训练、开发和固定 evaluation set，然后建简单 baseline，按语言、长度、来源分析误差并对 threshold 做 calibration。这题考的是数据和标签靠不靠得住：只调用 fit、报一个总体 AUC，说明不了分类器能拿去过滤数据。 |
| [OpenAI：从聊天日志里怎么挖新概念的代表图？](../data-team-interview/questions/labs/dt-chatlog-concept.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 分两步：先从聊天日志和评测失败里找出新出现的概念，再从有许可的图库和验证过的合成图片描述里给它挑代表图。挑图先过 data quality checks，再看新颖度，最后保证多样性，因为离群的图很多只是损坏或带水印。人工优先看质量合格、又和已有类别差得远的图。 |
| [OpenAI：用户上传工具照片做识别，训练数据从哪来？](../data-team-interview/questions/labs/dt-tool-photo.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 来自许可产品目录、厂商授权图、受控拍摄和验证过的 synthetic data。用户上传的识别图片只说明产品需要认它，没有明确的训练许可，就不能用作 base model 训练或固定评测。hard examples 从评测失败和许可 long-tail SKU 里挖，评测用按时间留出的新 SKU 和内部拍摄图。 |
| [Anthropic：怎么评模型是诚实，还是只是流畅？](../data-team-interview/questions/labs/dt-honest-fluent.md) | S | 面经依据；细节见来源 · AFM Data Team 备考 | 两者拆开测、分开报。诚实是按证据回答、没依据时承认不知道，流畅只是读着顺。做法是把「流畅但错」和「简短但对」的回答配成对，事实忠实度和表达质量分开打分；只看 Arena 或满意度，附和错误前提的回答也可能拿高分。 |
| [Anthropic Sleeper Agents：后门怎么进训练数据，安全训为什么清不掉？](../data-team-interview/questions/labs/dt-sleeper-data.md) | A | 练习/研究 · AFM Data Team 备考 | 后 gate 是训练中学到的条件行为，可以通过被投毒的来源、供应商 synthetic data 进入训练。Sleeper Agents 的实验里，后续安全 SFT / RL 和对抗训练都没清除已植入的行为，对抗训练还可能让模型学会隐藏。所以要在数据侧防：审计来源、隔离供应商数据，成对评测触发与非触发条件，事后仅靠 post-training 并不可靠。 |
| [Anthropic：只用 token logprob，怎么做成质量 / 安全二分类器？](../data-team-interview/questions/labs/dt-llm-clf-logprob.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 让模型只输出 Yes 或 No，用这两个 token 的 logprob 算一个连续分数，再按语言和数据域在 development set 上分别对 threshold 做 calibration。连续分数能画 calibration curve、按需挪阈值；先写长解释再用正则找词，输出不稳，也没法 calibration。模型分只当开发过滤器，误差靠独立人标和固定评测来查。 |
| [DeepMind：评测台怎么按生产软件的标准来设计？](../data-team-interview/questions/labs/dt-eval-harness.md) | S | 练习/研究 · AFM Data Team 备考 | 核心是每个分数都能复现、能公平比较：每次评测记下模型、题集、提示模板、decoding 参数和 seed，scorer 版本也固定。小幅涨分要做逐题 paired test。日常跑快速检查、夜间跑全套，保存逐题结果来定位回归。 |
| [Gemini pre-training 评测岗：leakage 和记忆怎么分开测？](../data-team-interview/questions/labs/dt-canary-leak.md) | A | 练习/研究 · AFM Data Team 备考 | 分两步测：先查训练内容和评测有没有重叠，再查这种重叠有没有把分数抬高。重叠用 n-gram 扫描和金丝雀字符串查，是否虚高就把题目改数字、改变量名再测一遍。teacher model 间接 leakage n-gram 扫不到，要靠 embedding nearest neighbors 和私有评测。 |
| [DeepSeek 会问的 data chemistry：反复用 synthetic data 训练，模型会怎么塌？](../data-team-interview/questions/labs/dt-synth-collapse.md) | S | 练习/研究 · AFM Data Team 备考 | 会先丢掉分布尾部：反复用上一代输出训练下一代，少见情况越来越少，表达越来越像 teacher。应对是每代都保留真人或许可原始数据，只让独立 oracle 验证过的合成进训练，并追踪少见题和表达多样性。答案验证正确，也保证不了风格和覆盖不退化。 |
| [Microsoft Phi：教科书式 synthetic data 为什么有效，局限在哪？](../data-team-interview/questions/labs/dt-phi-textbook.md) | A | 练习/研究 · AFM Data Team 备考 | Phi 有效是因为提高了每个 token 的信息质量：Phi-1 用过滤代码加合成教材，让 1.3B 模型在 HumanEval 上超过更大的模型。局限在规模和 contamination，世界知识和 multilingual 仍需要足够多的许可网页，后续几代 Phi 也都加了数据量；teacher model 和改写带来的考题 leakage，n-gram deduplication 挡不住，要用新题和私有评测检查。 |
| [Cohere / xAI：preference data 怎么采，一致率低了改什么？](../data-team-interview/questions/labs/dt-pref-collect.md) | S | 练习/研究 · AFM Data Team 备考 | preference data 的质量主要看 annotation guidelines：先写清比较哪些维度、什么算 tie，再让当前模型生成待比较的回答。一致率 $\kappa$ 低时，先查题目、标准和示例是否含糊，改完再采；分歧来自标准本身时，加 annotator 也压不下去。能执行验证的任务优先用 rule-based reward，人只判断自动检查不了的维度。 |
| [Cohere / Harvey：没有 gold labels、专家很贵，evaluation set 怎么造？](../data-team-interview/questions/labs/dt-eval-no-gold.md) | A | 练习/研究 · AFM Data Team 备考 | 先按任务能不能自动判分来分配专家时间。能执行、有标准答案的做成自动评测，人只抽查；专家写评分标准、标 edge cases，再用少量样本 对 model scores 做 calibration。未经 calibration 的 LLM judge 只能辅助开发，生产日志也不能直接当 evaluation set。 |
| [Cognition：榜涨了，用户说更差，数据侧先查哪几层？](../data-team-interview/questions/labs/dt-bench-vs-user.md) | A | 练习/研究 · AFM Data Team 备考 | 先诊断断在哪，再动数据。我会按顺序查四层：training set 有没有 leakage 评测题，scorer 是不是偏爱某种文风，基准题和测试本身有没有错，榜单任务和用户的实际工作差多远。没找到原因就加数据，很可能只是把榜单继续往上推。 |
| [OpenAI / Cohere / Mistral：Prompt、RAG、fine-tuning，数据岗怎么站队？](../data-team-interview/questions/labs/dt-prompt-rag-ft.md) | S | 练习/研究 · AFM Data Team 备考 | 依次问三个问题：知识经常变，或来源不允许进基础模型，就用带权限的 RAG 或工具；要改回答格式、工具习惯和拒答行为，做 SFT / RL；许可的世界知识属于 pre-training 或 continued PT。租户私有文件走带租户键的检索，不写进权重。 |
| [Mistral：fine-tuning 之后旧能力掉了，数据怎么保住已有能力？](../data-team-interview/questions/labs/dt-forget-sft.md) | A | 练习/研究 · AFM Data Team 备考 | 通过 replay 旧任务数据来保住已有能力。SFT 数据里留着通用指令、multilingual、安全和 tool calls 这些旧任务，每轮同时评新旧能力，旧能力退步超过阈值就减新任务权重或停训。KL 约束和 LoRA 只能让遗忘变慢，代替不了 replay。 |
| [Perplexity：线上评测记什么、抽什么、怎么 A/B？](../data-team-interview/questions/labs/dt-online-eval.md) | A | 练习/研究 · AFM Data Team 备考 | 线上评测用来发现失败类型、验证产品收益和成本。记录版本、延迟和工具行为是否合法，按失败类型分层抽查；A/B 尽量只换权重，正确率、安全和延迟分开报。用户原文进训练要有明确授权，补数据就用许可研究集复现失败，或者做验证过的合成。 |
| [Anthropic 作业：样本轴 double descent，对 data mix 意味着什么？](../data-team-interview/questions/labs/dt-sample-descent.md) | A | 面经依据；细节见来源 · AFM Data Team 备考 | 意味着增加样本不保证评测一直变好：在插值区附近，测试误差可能先升再降，同类数据翻倍也可能变差。所以调 data mix 时，在相同计算预算下对比新旧 data mix 在固定 evaluation set 上的表现，同时看目标任务和旧能力。double descent 只是提醒结果可能非单调，比例还是由 ablation study 来定。 |

