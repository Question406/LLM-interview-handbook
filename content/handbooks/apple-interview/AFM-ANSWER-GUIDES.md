# Apple 面试：完整回答与思路

本稿包含当前题本全部 340 题。每题先列背景、任务、做法与原因、结果或验证，再给口述回答。编程题原始实现、测试及全部来源仍在网页题本的原题内容中。

设计方案没有实际结果时写验证条件；个人项目仍须填真实职责和指标。

## 01 · 总览与练习路线

### Apple 面试 Question Book：怎么选题、怎么练、怎样判断来源？

> **回答思路**  
> **背景：** 题本混合了编程、设计和研究材料。  
> **任务：** 先按当前面试轮次选择练习重点。  
> **做法与原因：** 先写二面代码，再用具体案例串起 Panel。  
> **结果／验证：** 闭卷完成并能接受追问，再标记掌握。

#### 可以这样回答

题本混合了编程、设计和研究材料。

技术二面先练 cumsum／matrix／mask、Python 与 ML Coding 和 data pipeline；Panel 再练合成、评测、偏好与 multimodal。原帖题、主题扩展、公开研究和跨公司迁移分别保留来源，不能用题本数量推算出题频率。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=guide&question=apple-book-guide)

### AFM 网站参考题：13 张练习卡、来源与筛选入口

> **回答思路**  
> **背景：** AFM 面试说明跨 coding、数据、评估和 alignment。  
> **任务：** 用真实网站题目练习相近能力，并保留归属和 access restrictions。  
> **做法与原因：** 13 张练习按章节分类，用统一标签和本导读连接。  
> **结果／验证：** 可以逐题练习与核查来源，不把网站题或设计扩展当作 Apple 原题。

#### 可以这样回答

这批题的用法是先读题独立回答，再看 callout 检查自己是否说明了问题、选择与验证，最后读完整口述稿和技术备查。

外部链接用于核对题目与学习案例，手册答案则针对 AFM 的 data strategy 和 evaluation 重点重新组织。个人项目题只使用自己真实做过的部分；没有实测结果时，回答如何验证。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=guide&question=afm-web-reference-guide)

### Apple Foundation Models Data Team：整条 loop 按哪几轮准备？

> **回答思路**  
> **背景：** 不同轮次考察的深度和输出不同。  
> **任务：** 把准备分到技术屏幕、Panel 和文化轮。  
> **做法与原因：** 每轮准备一个可展示的结果，避免只背知识目录。  
> **结果／验证：** 代码能跑、设计能解释、项目有真实证据。

#### 可以这样回答

不同轮次考察的深度和输出不同。

按面试轮次准备：HM 30 分钟讲清一个数据项目；Technical Screen 45 分钟在 CoderPad 写 data pipeline，边写边讲规模和质量检查；Panel 是四轮技术加一轮 See Around Corners，之后可能还有 Director / VP。数据岗的重点是数据选择、合成和评测，模型架构只当背景。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=guide&question=dt-prep-map)


## 02 · cumsum、Matrix Operations 与 Mask

### cumsum 入门：从 padding mask 生成 position IDs

> **回答思路**  
> **背景：** padding 可能在左侧、右侧或中间。  
> **任务：** 给每行有效 token 连续编号。  
> **做法与原因：** 累计有效位置再减一，最后单独覆盖无效位。  
> **结果／验证：** 用空维度、全 padding 和中间空位检查编号。

#### 可以这样回答

padding 可能在左侧、右侧或中间。

对每行有效位置做 cumsum 后减一，再把无效位置设为 -1。按位置是否有效计数，不根据 token ID 猜 padding；同一实现支持左 padding、右 padding 及中间空位。

测试时，我会用空维度、全 padding 和中间空位检查编号。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=apple-mask-position-ids)

### cumsum 与 cummax：从文档起始标记构造 doc IDs、段内位置和 mask

> **回答思路**  
> **背景：** 同一行包含多篇独立文档。  
> **任务：** 同时得到文档号、段内位置和可见性。  
> **做法与原因：** 起点累计编号，传播最近起点，再组合三种 mask 条件。  
> **结果／验证：** 手算两篇文档，确认不跨文档且不看未来。

#### 可以这样回答

同一行包含多篇独立文档。

对 starts 做 cumsum 得到文档编号，用 cummax 传播最近起点下标，再相减得到段内位置。可见性是同文档、key 不晚于 query、两端有效三个条件同时成立。

测试时，我会手算两篇文档，确认不跨文档且不看未来。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=apple-starts-doc-mask)

### cumsum＋scatter/gather：按 mask 压缩 token 并还原

> **回答思路**  
> **背景：** 有效 token 被 padding 分散在不同位置。  
> **任务：** 压紧数据后还能按原位置恢复。  
> **做法与原因：** 有效位 prefix sum 提供全局下标，配合 scatter 和 gather。  
> **结果／验证：** 恢复有效特征，检查空输入、全空和 gradient。

#### 可以这样回答

有效 token 被 padding 分散在不同位置。

将 valid 展平做 cumsum，得到每个真实 token 的全局紧凑下标；scatter 写入 packed，gather 按下标还原。用额外的零行处理无效位置，避免 -1 索引误读最后一个 token。

测试还要满足这个条件：恢复有效特征，检查空输入、全空和 gradient。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=apple-mask-pack-unpack)

### Apple / Siri MLE：手写 Multi-Head Attention，shape 和 mask 怎么收？

> **回答思路**  
> **背景：** 多头、padding 与 cache 容易造成形状错位。  
> **任务：** 实现完整 attention 并保持位置语义一致。  
> **做法与原因：** 先明确 Q/K/V 形状，再计算得分、mask 和合并 heads。  
> **结果／验证：** 整段与逐 tokendecoding 对齐，检查输出和 gradient。

#### 可以这样回答

多头、padding 与 cache 容易造成形状错位。

我会先把 $[B,T,d]$ 的输入投影并拆成 $[B,H,T,d_h]$ 的 Q/K/V，计算 $QK^\top/\sqrt{d_h}$，在 softmax 前加 causal 和 padding mask，再乘 V、合并 heads。比如带 cache decoding 时，新 query 的绝对位置从旧 cache 长度开始，完整序列与逐 token 结果应一致。

测试还要满足这个条件：整段与逐 tokendecoding 对齐，检查输出和 gradient。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=apple-mha-code)

### 手写从 logits gather token logprob，并乘 response mask

> **回答思路**  
> **背景：** 当前位置 logits 预测的是下一个 token。  
> **任务：** 只累计回答部分的 token 概率。  
> **做法与原因：** 先 shift，再 gather，最后应用同样 shift 的 mask。  
> **结果／验证：** 用两三个 token 手算，确认 prompt 和 pad 不计分。

#### 可以这样回答

当前位置 logits 预测的是下一个 token。

取 `logits[:, :-1]` 做 `log_softmax`，用 `token_ids[:, 1:]` 去 `gather`，再乘 shift 后的 response mask，prompt 和 pad 位都是 0。SFT、DPO、GRPO 都用这个原语，最容易错的是忘了 shift 和 prompt 没 mask 掉。

测试时，我会用两三个 token 手算，确认 prompt 和 pad 不计分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=code-logprob-gather)

### 白板：LayerNorm vs 在 feature 维上的 standardization，eps 和仿射

> **回答思路**  
> **背景：** 每个 token 需要独立的特征 normalization。  
> **任务：** 沿最后一维计算均值方差与仿射变换。  
> **做法与原因：** 使用总体方差和 eps，保留 gamma/beta 可学习。  
> **结果／验证：** 对照参考实现，测试常数输入和 gradient。

#### 可以这样回答

每个 token 需要独立的特征 normalization。

对 $[B,T,D]$ 的每个 token，沿 $D$ 减均值、除以 $\sqrt{\sigma^2+\varepsilon}$，再乘 $\gamma$ 加 $\beta$。统计量只来自这个 token 的特征，方差除以 $D$，训练和推理都不依赖 batch 统计。

测试时，我会对照参考实现，测试常数输入和 gradient。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=coding-layernorm)

### CoderPad：packed SFT 的 loss mask 怎么写，哪些 token 不能进 gradient？

> **回答思路**  
> **背景：** 拼接样本后，监督和 attention boundaries 会混在一起。  
> **任务：** 只学习助手回复且不跨样本读答案。  
> **做法与原因：** loss mask 与文档 attention mask 分别构造。  
> **结果／验证：** 改变 prompt 或工具 token 不应新增监督项。

#### 可以这样回答

拼接样本后，监督和 attention boundaries 会混在一起。

SFT 学的是给定上下文时助手怎么回答，所以只对助手回复算 cross-entropy，prompt、padding 和工具返回都不进监督目标。packed 序列里不同样本之间还要切断 attention，不然后一个样本能看到前一个的答案。漏掉 mask，模型就会同时学着重建用户文本和工具返回。

测试还要满足这个条件：改变 prompt 或工具 token 不应新增监督项。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-packed-sft-code)

### 白板：packed sequences 的 cu_seqlens 和 document boundaries mask

> **回答思路**  
> **背景：** 变长样本需要压紧存放。  
> **任务：** 记录每段起止并保持文档隔离。  
> **做法与原因：** 用长度 prefix sum 建立 cu_seqlens，配合分段 causal attention。  
> **结果／验证：** 检查零长段、最后一个 document offset 和跨文档位置。

#### 可以这样回答

变长样本需要压紧存放。

先按真实长度拼接有效 token，用长度为 $B+1$ 的 `cu_seqlens` prefix sum 标出各段起止。同一行放多篇独立文档时，要用块对角 causal mask，或把每篇当 varlen 序列，防止跨文档 attention。

测试时，我会检查零长段、最后一个 document offset 和跨文档位置。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=coding-packed-lm)

### 手写 causal linear attention：并行形式和 O(1) 状态递推要对上

> **回答思路**  
> **背景：** 历史 attention 的开销随序列增长。  
> **任务：** 实现核化 attention 的并行与递推形式。  
> **做法与原因：** 将历史压成键值统计量，利用结合律累计。  
> **结果／验证：** 两种计算逐位置一致，说明数值与状态限制。

#### 可以这样回答

历史 attention 的开销随序列增长。

把 softmax 换成非负核 $\phi(q)^\top\phi(k)$，靠结合律把历史累加成 $S_t=\sum\phi(k)v^\top$ 和 $z_t=\sum\phi(k)$。decode 时只更新这两个量，输出 $\phi(q)^\top S_t/\phi(q)^\top z_t$，状态大小和序列长度无关；训练用的并行形式和这个递推要数值一致。

测试还要满足这个条件：两种计算逐位置一致，说明数值与状态限制。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=code-linear-attn)

### 白板：sliding window 和 causal mask 合成，prefill 与 decode 的 shape

> **回答思路**  
> **背景：** 窗口限制与 cache 绝对位置需要同时满足。  
> **任务：** 只保留窗口内且不在未来的 key。  
> **做法与原因：** 用 query 绝对下标判断 causal 和距离。  
> **结果／验证：** 手算窗口边缘，分别检查 prefill 与 decode 形状。

#### 可以这样回答

窗口限制与 cache 绝对位置需要同时满足。

把 causal 和窗口两个条件相与：位置 $i$ 只看满足 $i-W \lt j \le i$ 的 key，其他位置设成 $-\infty$。Prefill 偏置是 `[1, 1, T, S]`，decode 只有一个 query，偏置是 `[1, 1, 1, S]`，query 的绝对下标取 cache 长度。

测试时，我会手算窗口边缘，分别检查 prefill 与 decode 形状。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=coding-swa-mask)

### CoderPad：把变长对话组成 SFT batch，截断后还能保住监督信号吗？

> **回答思路**  
> **背景：** 对话长度不一，截断可能删光监督。  
> **任务：** 组成有效 batch 并正确标记 labels。  
> **做法与原因：** 先定截断契约，再按真实位置生成 mask。  
> **结果／验证：** 检查真实 pad_id、无回答和超长样本。

#### 可以这样回答

对话长度不一，截断可能删光监督。

先按明确的截断规则裁剪，再按 token 位置构造 attention mask 和 labels；padding 与 prompt 不参与 loss。不能通过 token 是否等于 pad_id 判断 padding，因为真实 token 也可能使用相同 ID。

测试时，我会检查真实 pad_id、无回答和超长样本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-sft-collate-code)

### CoderPad：批量计算回答 log probability，EOS 和 padding 怎么对齐？

> **回答思路**  
> **背景：** 序列得分容易漏 shift 或混入 prompt。  
> **任务：** 批量得到回答的序列 log probability。  
> **做法与原因：** 从目标 token 位置取分，再按回答 mask 求和。  
> **结果／验证：** 核对 EOS 与 padding，并区分求和和长度平均。

#### 可以这样回答

序列得分容易漏 shift 或混入 prompt。

先用前一位置 logits 预测后一 token，再按目标位置的回答 mask 选取 log probability。序列概率取 token log probability 的和；长度平均是另一种评分，不能无说明替换标准 DPO 的序列求和。

测试时，我会核对 EOS 与 padding，并区分求和和长度平均。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-response-logprob-code)

### CoderPad：实现带 reference policy 的 DPO loss，并验证 gradient 方向

> **回答思路**  
> **背景：** 偏好目标依赖策略与 reference policy 的相对差。  
> **任务：** 实现稳定且 gradient 方向正确的 DPO loss。  
> **做法与原因：** 构造两组 log-ratio 差，reference 保持冻结。  
> **结果／验证：** 相对差相同时为 log(2)，检查 chosengradient 方向。

#### 可以这样回答

偏好目标依赖策略与 reference policy 的相对差。

DPO 比较策略与 reference policy 对 chosen/rejected 的序列 log probability 差，用稳定的负 log-sigmoid 求 loss。参考分数不应收到 gradient；当两组相对差相同时 loss 为 log(2)。

测试还要满足这个条件：相对差相同时为 log(2)，检查 chosengradient 方向。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-dpo-batch-code)

### 白板：causal、padding、document boundaries 合成一张 attention mask

> **回答思路**  
> **背景：** causal、padding 和 document boundaries 同时影响可见性。  
> **任务：** 构造指定形状和语义的 attention bias。  
> **做法与原因：** 分别广播条件再相与，明确 bool 和加性 mask 约定。  
> **结果／验证：** 检查全屏蔽行、跨文档和 cache 位置。

#### 可以这样回答

causal、padding 和 document boundaries 同时影响可见性。

先把 causal $j\le i$、key 非 pad、query 与 key 同文档三个条件按位与，再生成 `[B, 1, T, S]` 的加性 bias。合法位填 $0$，非法位填 $-\infty$；比如 packing 后第二篇文档不能读第一篇，一行全屏蔽时还要由 softmax 端处理 NaN。

测试时，我会检查全屏蔽行、跨文档和 cache 位置。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=coding-attn-mask)

### CoderPad：变长 microbatch gradient accumulation，为什么平均 loss 会训练错？

> **回答思路**  
> **背景：** 不同 microbatch 有效 token 数不同。  
> **任务：** 让累积 gradient 等价于按 token 平均。  
> **做法与原因：** 各批 loss 总和除以整个窗口 token 数，只更新一次。  
> **结果／验证：** 与合并 batch 的 gradient 比较，覆盖空监督批。

#### 可以这样回答

不同 microbatch 有效 token 数不同。

当每个 microbatch 的有效 token 数不同，应把各批 token loss 总和除以整个累积窗口的有效 token 总数，再分别 backward；直接平均各批均值会把短批放大。一次窗口只清 gradient 和更新一次。

测试还要满足这个条件：与合并 batch 的 gradient 比较，覆盖空监督批。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-token-accum-code)

### 手写数值稳定 Softmax：减 max、全 mask 行、以及和 CE 的关系

> **回答思路**  
> **背景：** 大 logit 或全 mask 行会产生数值问题。  
> **任务：** 实现稳定且 edge-case behavior 明确的 softmax。  
> **做法与原因：** 先减最大值，再单独处理无有效元素的行。  
> **结果／验证：** 与参考分布对比，检查极值和全 mask 不出 NaN。

#### 可以这样回答

大 logit 或全 mask 行会产生数值问题。

沿计算轴先减最大值再 $\exp$ 和 normalization，分布不变，指数落在 $(0,1]$ 不会上溢。整行都被 mask 成 $-\infty$ 时会出 NaN，要把这一行的概率置 0。

测试还要满足这个条件：与参考分布对比，检查极值和全 mask 不出 NaN。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=code-softmax-stable)

### CoderPad：实现带 confidence weight 的 pairwise reward loss，全零权重怎么 backpropagation？

> **回答思路**  
> **背景：** preference pairs 的 confidence weight 不同甚至全零。  
> **任务：** 计算稳定的加权 pairwise loss。  
> **做法与原因：** softplus 处理分差，用实际权重和 normalization。  
> **结果／验证：** 手算 log(2)，检查小权重和全零 gradient。

#### 可以这样回答

preference pairs 的 confidence weight 不同甚至全零。

对 chosen 与 rejected 奖励差使用 softplus，再按 confidence weight normalization。分母是权重总和，不是样本数；全零权重时返回仍连着计算图的零，使 backward 有定义但 gradient 为零。

测试时，我会手算 log(2)，检查小权重和全零 gradient。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-rm-weighted-loss-code)

### 手写 packed sequence 的 document boundaries mask：`cu_seqlens` 怎么变成 keep matrix

> **回答思路**  
> **背景：** 一条 packed 序列包含多个独立样本。  
> **任务：** 根据 document offsets 构造块对角 causal mask。  
> **做法与原因：** 先定位 doc id，再比较同段与先后位置。  
> **结果／验证：** 各段首尾和空段不能引入跨文档可见性。

#### 可以这样回答

一条 packed 序列包含多个独立样本。

用 prefix sum `cu_seqlens` 给每个位置算出所属的 doc id，keep 的条件是同一文档且 $j\le i$。跨文档的位置要设成 $-\infty$，否则后一条样本能看到前一条。

测试还要满足这个条件：各段首尾和空段不能引入跨文档可见性。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=code-packed-mask)

### CoderPad：手写 temperature-scaled distillation KL，teacher、student 和 reduction 哪个方向？

> **回答思路**  
> **背景：** teacher 和 student 的分布方向不能混用。  
> **任务：** 实现有效 token 上的 temperature-scaled distillationKL。  
> **做法与原因：** teacher 冻结，vocabulary 维求和，再按 token 平均。  
> **结果／验证：** 同分布 KL 为零，检查温度系数与 teacher gradient。

#### 可以这样回答

teacher 和 student 的分布方向不能混用。

本题用 teacher 分布到 student 分布的 forward KL，在 vocabulary 维求和，再按有效 token 平均并乘温度平方。teacher 必须冻结，不能把 KL 的输入顺序或对 vocabulary 的平均与 token 平均混淆。

测试还要满足这个条件：同分布 KL 为零，检查温度系数与 teacher gradient。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-distill-forward-kl-code)

### CoderPad：构造 packed causal attention mask，padding query 怎么处理？

> **回答思路**  
> **背景：** padding query 与真实 query 契约不同。  
> **任务：** 实现题目指定的安全 packed 可见性。  
> **做法与原因：** 真实位置同文档且 causal，padding 按约定处理。  
> **结果／验证：** padding 输出和 loss 丢弃，避免全屏蔽 NaN。

#### 可以这样回答

padding query 与真实 query 契约不同。

真实 query 只能看到同文档、不晚于自己的真实 key。padding query 本题只允许看自身以避免全屏蔽行，且其输出与 loss 必须丢弃；注意不同 PyTorch attention 接口的 bool mask 语义可能相反。

测试还要满足这个条件：padding 输出和 loss 丢弃，避免全屏蔽 NaN。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-packed-attention-code)

### Apple CV/ML 面经形式练习：读公式实现可训练的 gated residual layer

> **回答思路**  
> **背景：** 论文公式尚未转为明确 tensor 运算。  
> **任务：** 写出可训练的 gated residual layer。  
> **做法与原因：** 先核对 matrix 方向和广播，再注册参数。  
> **结果／验证：** 手算初值，检查参数更新与自动求导。

#### 可以这样回答

论文公式尚未转为明确 tensor 运算。

先澄清 tensor 形状、matrix 乘法方向、广播与 parameter sharing，再从公式写 forward。用可手算的初始状态检查输出，用 gradient 和参数注册检查能否真正训练；本题公式自拟，原帖未公开论文或层名。

测试时，我会手算初值，检查参数更新与自动求导。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=dt-p3a-paper-gated-layer)

### OpenAI：NumPy 1-NN 向 quantization 与神经网络形式

> **回答思路**  
> **背景：** 逐点计算最 nearest neighbors 成本高且难向 quantization。  
> **任务：** 把平方欧氏1-NN 写成线性得分。  
> **做法与原因：** 展开距离，去掉对候选相同的查询范数。  
> **结果／验证：** 随机小样本对照暴力距离，保留平票契约。

#### 可以这样回答

逐点计算最 nearest neighbors 成本高且难向 quantization。

展开平方欧氏距离后，查询自身范数对所有候选都相同，可以去掉，剩下比较 2q·x - ||x||²。把训练点的两倍作权重、负平方范数作偏置，一次 Wx + b 再 argmax 就得到 1-NN。L1 没有同样的点积展开，要另算广播距离，并注意中间内存。

测试还要满足这个条件：随机小样本对照暴力距离，保留平票契约。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=p3a-openai-numpy-1nn-wx-b)

### OpenAI：matrix prefix product：手写 backpropagation 与并行扫描

> **回答思路**  
> **背景：** matrix prefix product 要保留非交换的乘法顺序。  
> **任务：** 实现扫描及其 backpropagation。  
> **做法与原因：** 结合律只允许重分组，不允许交换左右因子。  
> **结果／验证：** 用自动求导对照，检查非交换 matrix 与容差。

#### 可以这样回答

matrix prefix product 要保留非交换的乘法顺序。

我会保存 forward prefix product，backward 从后往前累积每个输出传回的 gradient，再按 matrix 乘法的左右顺序求导。Hillis–Steele 每层读上一层副本，用结合律并行合并；比如左块与右块交换会算错，浮点结果则用容差比较。

测试时，我会用自动求导对照，检查非交换 matrix 与容差。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=p3a-openai-autograd-hillis-steele-scan)

### Self-Attention Coding：实现 batched causal attention，并处理全 padding 行

> **回答思路**  
> **背景：** 多个序列带 padding，并要求 causal attention。  
> **任务：** 输出数值正确且全 padding 行不产生 NaN 的 attention。  
> **做法与原因：** 先推导 mask 的 query/key 方向，再安全地处理无可见 key 的行。  
> **结果／验证：** 通过手算、独立循环对照、future invariance 和 finite-gradient 检查。

#### 可以这样回答

我会先确认形状和 mask 的语义：每个有效 query 只能看当前和之前的有效 keys。算完 scaled dot-product 后，用这三个条件构造 keep mask。

全 padding 行是最容易漏掉的 edge case。如果直接对全负无穷做 softmax，会产生 NaN。我会先把这种行的 scores 替换为零，softmax 后再把所有不可见位置的 weights 置零，所以无效 query 的最终输出也是零。

测试先用零 scores 得到可手算的平均值，再用显式循环对照不规则 padding，检查 future values 不影响较早输出，同时检查 backward 没有非有限值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=tensor&question=afm-web-attention-code)


## 03 · Decoding 解码算法

### Decoding 练习路线：greedy、beam search、sampling 与约束 decoding 怎么选？

> **回答思路**  
> **背景：** 会对 [V] 选一个 token，不等于能让不同长度的多条请求完成生成。  
> **任务：** 分清批量 token selection、完整生成循环和 serving 调度的范围。  
> **做法与原因：** 先写批量 selector，再维护 EOS、mask、positions 和 KV，最后处理 beam parent 重排。  
> **结果／验证：** 用手算样例、随机频率、完整前缀 logits 与独立搜索参考验证实现。

#### 可以这样回答

我会先写 [B,V] 到 [B] 的 token selection，再接入完整生成循环。不同请求要独立处理 EOS 和长度，left padding 后的逻辑 position 也不能直接用矩阵列数。

先完成 [[apple-batched-token-selection]] 和 [[apple-batched-generation]]，确认 greedy、multinomial、Gumbel 都能多步运行，再做 [[apple-batched-beam-search]]，验证 parent 改变时 cache 与状态一起移动。

原来的单请求入门题仍然保留。新版本是 static batch generation；continuous batching、speculative serving 和 grammar compiler 没有被悄悄算作已实现。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=apple-decoding-guide)

### Batch token selection：greedy、top-k/top-p 与 Gumbel-max

> **回答思路**  
> **背景：** B 条请求的 logits 是 [B,V]，每行可能有不同温度和合法集合。  
> **任务：** 返回每条请求的下一 token，保留确定性 tie rule 与正确 sampling 分布。  
> **做法与原因：** 逐行 mask、temperature、top-k，再在重新 normalization 后做 top-p；只让随机行消耗 RNG。  
> **结果／验证：** 手算 greedy 与跨阈值样例，再用固定 seed 和频率检查两种随机实现。

#### 可以这样回答

我会先把单步选择与完整生成分开。这里每行是一条独立请求，所有排序和累计概率都沿 vocabulary 维进行，不能让其他请求影响本行候选。

确定性行直接返回合法最大值；随机行完成 temperature、top-k 和 top-p 后，再用 multinomial 或 Gumbel-max 选择。Top-p 保留跨阈值的 token，排序结果还要 gather 回原始 token ID。

我会用三行不同配置手算结果，再检查 mask、seed replay 和长期频率。下一张卡才负责 EOS、padding 与 cache。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=apple-batched-token-selection)

### 完整 Batch generation：greedy / sampling、独立 EOS 与 KV cache

> **回答思路**  
> **背景：** 两条不同长度的 prompts 同批生成，一条先出现 EOS，另一条还要继续。  
> **任务：** 完成 greedy 与两种 sampling 的生成循环，正确维护长度、mask、positions 和 KV。  
> **做法与原因：** Left padding 后 prefill 一次，只给 active rows 选 token，随后按有效 token 数设置位置并用单 token decode。  
> **结果／验证：** 逐步比较 cached 与完整前缀 logits，检查独立 EOS、pad=EOS、零步数及 batch/单条 greedy 一致。

#### 可以这样回答

假设两条请求的 prompt 长度分别是 1 和 3，第一条生成 EOS 后，第二条还需要继续。共同的矩阵宽度不能决定它们各自的逻辑 position。

我会先 prefill 一次，之后只送新 token 更新 KV；每条请求独立记录 finished 和 lengths。Finished 请求保留 static batch slot，后续 filler 被 mask，既不 sampling，也不增加真实长度。

先验证 cached logits 与完整前缀重算一致，再验证 greedy、multinomial 和 Gumbel 的完整生成。这里实现 static batch，不把它说成 continuous batching 服务。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=apple-batched-generation)

### 完整 Batched Beam Search：EOS、parent gather、KV 重排与 length penalty

> **回答思路**  
> **背景：** 同一请求的两个新候选可能都来自同一条旧 beam。  
> **任务：** 为 B 条请求完成独立 K-beam 搜索，保证输出状态与 cache 指向同一历史。  
> **做法与原因：** 只在各自 K*V 内选择；恢复 parent 后同步 gather cache、mask、prefix 与状态，再 decode 新 token。  
> **结果／验证：** 用手算转移与独立完整前缀搜索比对 tokens/score，测试重复 parent、EOS、tie 和不足 K 个合法候选。

#### 可以这样回答

假设本轮两个最好的 child 都来自 beam 0。它们不仅需要相同的 token 前缀，还必须从 beam 0 的 K/V 继续计算。

我会把每个请求自己的 K*V 候选排序，整除和取模得到 parent 与新 token，再加请求 offset 重排整个 cache。已结束候选只携带旧分数，不重复生成 EOS；候选不足时保留明确的 invalid 空位。

最后按题目约定做 length penalty 重排，并与逐条重算完整前缀的参考搜索比较。搜索中的剪枝与最终重排是两件事，不能混用。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=apple-batched-beam-search)

### Apple 电面：温度、top-k、nucleus 顺序，on-device 为什么常 top-k？

> **回答思路**  
> **背景：** on-device sampling 既要合法也受延迟约束。  
> **任务：** 正确组合温度、top-k 与 top-p。  
> **做法与原因：** 先屏蔽再调温度，筛候选后重新 normalization。  
> **结果／验证：** 检查全 mask、零温度、固定 seed 与候选数。

#### 可以这样回答

on-device sampling 既要合法也受延迟约束。

sampling 先屏蔽非法 token，再除温度、做 top-k、在 renormalization 后的分布上做 nucleus，最后 sampling。比如温度为 0 直接选合法 token 中的最大值，全 mask 则报错；on-device top-k 候选数固定，便于控制延迟和 ANE 静态 shape。

测试时，我会检查全 mask、零温度、固定 seed 与候选数。


本题保留单请求 `[V]` 入门接口。完整 batched greedy / sampling、独立 EOS 与 KV cache 版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-generation)。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=apple-topk-sample)

### 白板：温度 → top-k → nucleus 的顺序，实现细节

> **回答思路**  
> **背景：** 变换顺序会改变最终候选分布。  
> **任务：** 实现题目规定的 sampling 流程。  
> **做法与原因：** 温度先改变概率，再做 top-k 和累计概率截断。  
> **结果／验证：** 手算小 vocabulary，测试 p 的极端取值与保留首个越界项。

#### 可以这样回答

变换顺序会改变最终候选分布。

sampling 先屏蔽非法 token，再除温度 $T$，做 top-k，随后在剩余质量重新 normalization 的分布上做 nucleus 并 sampling。温度会改变 top-p 的累计质量，所以这一步必须在温度化之后；$T=0$ 或 $p=0$ 直接走 greedy。

测试时，我会手算小 vocabulary，测试 p 的极端取值与保留首个越界项。


本题的函数只接收一条请求的 `[V]` logits，返回一个 token。支持 `[B,V]`、逐行参数与两种随机实现的版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-token-selection)。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=coding-topk-nucleus)

### 白板：beam search vs greedy vs sampling，length penalty

> **回答思路**  
> **背景：** 局部最大不一定是最好完整序列。  
> **任务：** 维护多个前缀并正确终止和评分。  
> **做法与原因：** 扩展累计 logprob，EOS 停止，length penalty 按约定使用。  
> **结果／验证：** beam=1对齐 greedy，核对完成序列和 length bias。

#### 可以这样回答

局部最大不一定是最好完整序列。

Greedy 每步取 $\arg\max$，beam 保留 $k$ 条前缀按累计 log-prob 扩展，$k=1$ 就退化为 greedy，sampling 则按指定分布随机选 token。beam 要让 EOS 后停止扩展、按 parent 重排 KV，并用 length penalty 缓解短句分数偏高；最后重排与搜索中使用惩罚也要分清。

测试还要满足这个条件：beam=1对齐 greedy，核对完成序列和 length bias。


本题是单 prompt 的完整搜索，width=1 只得到单请求 greedy；不包含 batch KV 推理。完整 `[B,K,V]` 搜索和 cache 重排见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-beam-search)。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=coding-beam-search)

### 白板：Gumbel-max sampling，和 softmax 温度的关系

> **回答思路**  
> **背景：** 硬 sampling 与连续松弛中的温度含义不同。  
> **任务：** 分别实现指定分布与 differentiable 近似。  
> **做法与原因：** 明确噪声加在缩放前还是缩放后。  
> **结果／验证：** 检查频率分布及固定噪声下 argmax 行为。

#### 可以这样回答

硬 sampling 与连续松弛中的温度含义不同。

硬 sampling 先缩放 logits，再用 argmax(z/τ+g)，得到 temperature sampling。Gumbel-softmax 松弛用 softmax((z+g)/τ)，它的 τ 只改变连续输出和 gradient，在固定噪声下不改变选中的类别。

测试时，我会检查频率分布及固定噪声下 argmax 行为。


本题已经沿最后一维支持 `[B,V]` 等 batch 单步选择，但没有多步生成。使用同一 Gumbel 方法的完整 batch loop 见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-generation)。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=coding-gumbel-max)

### Microsoft：约束 decoding / JSON 文法，和自由生成的质量

> **回答思路**  
> **背景：** 下游工具需要结构化且可解析的输出。  
> **任务：** 保证格式同时保留答案质量。  
> **做法与原因：** 用文法限制合法 token，内容仍单独评价。  
> **结果／验证：** 分别报告解析率、事实正确与运行权限。

#### 可以这样回答

下游工具需要结构化且可解析的输出。

约束 decoding 把 JSON Schema / 文法变成逐 token mask，保证机器接口的字段和语法合法。格式约束也会改变生成分布，multi-step reasoning 可先得出结果再填结构。验收分别看可解析率与答案正确率，副作用与权限仍由工具运行时检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=msft-constrained-decode)

### 白板：speculative decoding 接受规则，拒绝后从哪一步 resampling

> **回答思路**  
> **背景：** 草稿分布与目标分布并不相同。  
> **任务：** 接受草稿时仍保持目标 sampling distribution。  
> **做法与原因：** 逐步接受，首拒绝处用残差分布 resampling。  
> **结果／验证：** 检查全接受、首拒绝和总体 sampling 频率。

#### 可以这样回答

草稿分布与目标分布并不相同。

草稿 token 从左到右按 $\min(1,p/q)$ 接受，第一次在第 $i$ 步拒绝时，就在同一步从 normalization 残差 $\max(0,p-q)$ resampling，并丢掉后续草稿。全部接受则从 $p$ 多抽一个 token。接受与残差两条路径的概率相加等于目标分布，因此保持 sampling distribution 不变。

测试时，我会检查全接受、首拒绝和总体 sampling 频率。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=coding-spec-accept)

### 手写 Beam Search 一步：累计 logprob、flatten top-k、backpointer 父 beam

> **回答思路**  
> **背景：** 批量 beam 扩展要同时找父 prefix sum 新 token。  
> **任务：** 从三维得分选出每批最优候选。  
> **做法与原因：** 展平 beam 和 vocabulary 后 top-k，再整除和取模 backpointer。  
> **结果／验证：** 手算父 beam 索引，核对前缀与 cache 同步重排。

#### 可以这样回答

批量 beam 扩展要同时找父 prefix sum 新 token。

每步把 $K$ 条 beam 的累计 logprob 加到 $[B,K,V]$ 的 log-softmax 上，展平成 $[B,KV]$ 取 top-$K$。下标整除 $V$ 得到父 beam，模 $V$ 得到新 token，再用父 beam 去 gather prefix sum KV cache。

测试时，我会手算父 beam 索引，核对前缀与 cache 同步重排。


本题只完成一次 batched beam step。包括多步生成、EOS、parent gather 与真实 KV cache 的完整版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-beam-search)。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=decoding&question=code-beam-search)


## 04 · Python 与 ML Coding

### Apple coding：k-means / nearest neighbors，作为电面算法题怎么答到 ML 岗标准？

> **回答思路**  
> **背景：** 聚类迭代要处理 empty cluster 和停止后的标签。  
> **任务：** 完成向 quantization 分配及中心更新。  
> **做法与原因：** 明确距离、empty cluster 策略和最终重分配。  
> **结果／验证：** 对照小数据聚类，说明时间与中间内存。

#### 可以这样回答

聚类迭代要处理 empty cluster 和停止后的标签。

我会用向 quantization 距离计算实现 Lloyd 迭代：每个点分到最近中心，再把中心更新为均值，empty cluster 按约定处理，结束后重新分配标签。时间是 $O(n k d I)$，距离可写成 $[n,k]$；广播实现还要检查中间 tensor 内存，再讨论 k-means++ 和 16 个中心 $\approx$ 4-bit 的码本。

测试时，我会对照小数据聚类，说明时间与中间内存。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=apple-kmeans)

### Apple Siri MLE 原帖：判断两句话是否恰好相差一次编辑

> **回答思路**  
> **背景：** 恰好一次与至多一次会改变相同字符串结果。  
> **任务：** 判断指定编辑单位下的一次编辑。  
> **做法与原因：** 双指针只允许一次差异，按长度决定跳过位置。  
> **结果／验证：** 覆盖相同串、插删替换和长度差超过一。

#### 可以这样回答

恰好一次与至多一次会改变相同字符串结果。

先确认编辑单位以及要求恰好一次还是至多一次。恰好一次时，相同输入应返回 False；长度差不超过一，用双指针只允许一次替换或跳过较长串的一个字符，避免完整编辑距离 DP。

测试时，我会覆盖相同串、插删替换和长度差超过一。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-sentence-one-edit)

### Apple Foundation Model 原帖扩展：小数时间预约的最大重叠数

> **回答思路**  
> **背景：** 小数端点不能套整数加一减一。  
> **任务：** 计算半开区间的最大同时预约数。  
> **做法与原因：** 精确解析端点，同一时刻先合并净变化。  
> **结果／验证：** 相接预约不重叠，检查小数精度和零长契约。

#### 可以这样回答

小数端点不能套整数加一减一。

小数端点不能直接沿用整数区间算法里 endpoint 加一减一的做法。先明确时间精度和半开区间语义；本练习从字符串解析 Decimal，在起点加一、终点减一，并按同一端点的净变化做扫描。

测试还要满足这个条件：相接预约不重叠，检查小数精度和零长契约。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-decimal-calendar)

### Apple CVML 面经：手写 kNN end-to-end，standardization 在哪里 fit？

> **回答思路**  
> **背景：** 预处理和选邻居都可能 leakage 验证信息。  
> **任务：** 构建只拟合 training set 的 kNN 流程。  
> **做法与原因：** 训练统计应用到查询，距离和投票平票明确。  
> **结果／验证：** 测试零方差、平票和验证输入不影响拟合。

#### 可以这样回答

预处理和选邻居都可能 leakage 验证信息。

只用 training set 拟合均值与标准差，再对查询应用同一变换，按距离稳定选邻居并投票。距离平票、投票平票和零方差都要提前定义；把 validation set 一起拟合预处理会 leakage 分布，调 k 也只能用 development set。

测试还要满足这个条件：测试零方差、平票和验证输入不影响拟合。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=p3a-apple-cvml-knn-pipeline)

### Apple Sr MLE 原帖扩展：TTL 缓存到底何时过期、何时删除？

> **回答思路**  
> **背景：** 读取、覆盖和清理有不同的时间语义。  
> **任务：** 实现明确的 TTL 缓存契约。  
> **做法与原因：** 注入时钟，逻辑过期与物理删除分开。  
> **结果／验证：** 到期等号、覆盖重置及读不续期都单测。

#### 可以这样回答

读取、覆盖和清理有不同的时间语义。

先定义过期语义，再实现数据结构：本练习在 now 达到写入时刻加 TTL 时过期，读取不续期，覆盖写入重置期限。逻辑上过期与物理删除分开，测试用注入时间，不依赖 sleep。

测试还要满足这个条件：到期等号、覆盖重置及读不续期都单测。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-ttl-cache-contract)

### Apple MLE 原帖：拿到数据后现场完成预处理、训练、评测与可视化

> **回答思路**  
> **背景：** 面试要求从原始表格跑到可解释结果。  
> **任务：** 完成预处理、训练、指标和投影。  
> **做法与原因：** 先划分再拟合，简单 baseline 用于暴露数据问题。  
> **结果／验证：** 改变 test set 不影响模型，检查缺失值和类别指标。

#### 可以这样回答

面试要求从原始表格跑到可解释结果。

先冻结 train/test split，只在 training set 拟合缺失值填补、standardization、模型和降维投影；test set 只做 transform 与最终指标计算。先跑通简单 baseline，再解释降维图和误差，不用复杂网络掩盖 data leakage。

测试还要满足这个条件：改变 test set 不影响模型，检查缺失值和类别指标。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-tabular-full-pipeline)

### Apple DS 原帖：手写 K-fold CV，余数与预处理 leakage 怎么处理？

> **回答思路**  
> **背景：** 折分不均或先预处理会 contamination 交叉验证。  
> **任务：** 让每个样本恰好验证一次。  
> **做法与原因：** 一次打乱分配余数，每折重新拟合流程。  
> **结果／验证：** 检查折间覆盖、互斥与固定 seed 复现。

#### 可以这样回答

折分不均或先预处理会 contamination 交叉验证。

先生成一次可复现排列，把余数分给前几折；每个样本恰好一次进入 validation set，训练索引为该折的补集。执行模型比较时，每折重新拟合预处理与模型，不能在全数据上先 standardization 再交叉验证。

测试时，我会检查折间覆盖、互斥与固定 seed 复现。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-kfold-indices)

### Apple AIML 视频组原帖：手写 BatchNorm，并分清训练与推断状态

> **回答思路**  
> **背景：** 训练用当前批，推断用运行状态。  
> **任务：** 实现仿射参数和统计更新。  
> **做法与原因：** 分开处理训练方差与 running variance。  
> **结果／验证：** 对照训练/推断结果，检查状态不被误当参数。

#### 可以这样回答

训练用当前批，推断用运行状态。

BatchNorm 按特征聚合 batch 统计量；训练输出使用当前批的有偏方差，同时更新运行统计，推断只读运行均值方差。gamma/beta 是可学习仿射参数，running statistics 是状态，不能混为一谈。

测试时，我会对照训练/推断结果，检查状态不被误当参数。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=coding&question=dt-p3a-batchnorm-state)


## 05 · Data Pipeline 与 Data Strategy

### 通识：什么叫好数据，怎样才算把数据做对？

> **回答思路**  
> **背景：** 质量分高不一定带来模型收益。  
> **任务：** 建立可检验的好数据标准。  
> **做法与原因：** 把目标能力、negative transfer 和来源一起纳入对照。  
> **结果／验证：** 用一项真实数据干预解释标准是否成立。

#### 可以这样回答

质量分高不一定带来模型收益。

这章回答两件事：什么数据值得留，怎样证明一批数据有用。好数据让固定评测里的目标任务变好、保住其他重要能力、能追溯来源和版本；证明它要靠可被推翻的假设、对照和 ablation study，质量分只是其中一个信号。这章准备 Panel / HM 的解释，实现题在 CoderPad 部分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-good-data-map)

### CoderPad：边写边讲，一条 pre-training / SFT data pipeline 怎么画？

> **回答思路**  
> **背景：** 边写代码时还要解释规模与质量。  
> **任务：** 先实现 pipeline 中被要求的一步。  
> **做法与原因：** 澄清输入输出，再把局部代码接回整个流程。  
> **结果／验证：** 代码通过小例子，并能解释失败和扩展方式。

#### 可以这样回答

边写代码时还要解释规模与质量。

先问清数据类型、这轮要实现哪一步、输出什么格式，再边写边讲每一步筛掉什么、为什么。整条流程是来源、抽取、过滤、deduplication、data mix、评测隔离；现场只实现被要求的那部分，其余口头补齐版本、失败处理和大规模扩展。

测试还要满足这个条件：代码通过小例子，并能解释失败和扩展方式。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-pipeline-talk)

### 什么叫好数据？别用「高质量」三个字糊过去

> **回答思路**  
> **背景：** 同一批数据对不同阶段可能价值不同。  
> **任务：** 说明什么叫对当前模型有用。  
> **做法与原因：** 固定模型换数据，判断目标收益与保留能力。  
> **结果／验证：** 独立评测支持收益且来源版本可追溯。

#### 可以这样回答

我会先问，这批数据要帮哪个模型解决什么问题。“像教科书”或者分类器分很高，都不能单独说明它对这个任务有用。

比如模型已经会调用工具，但经常漏掉权限失败后的恢复。我更想要一批能验证的恢复 trajectories，而不是再加很多容易的成功调用。换成知识覆盖不足的任务，选择就可能完全不同。

我会固定模型和训练预算，比较加这批数据前后在独立任务上的变化。目标能力提高、重要旧任务没掉，来源和处理过程也能追溯，我才会说它是这次实验里的好数据。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-good-data-def)

### CoderPad：手写 MinHash + LSH，near-duplicate deduplication 怎么讲规模？

> **回答思路**  
> **背景：** 全量两两比较网页不可扩展。  
> **任务：** 找到 near-duplicates 候选并准确复核。  
> **做法与原因：** MinHash 压签名，LSH 召回候选，精确 Jaccard 确认。  
> **结果／验证：** 对照暴力 nearest neighbors，报告候选数和漏召回。

#### 可以这样回答

全量两两比较网页不可扩展。

先把文档拆成 shingle 集合并生成 MinHash 签名，再用 LSH 分段找候选：签名某一维相等的概率等于 Jaccard，任一 band 完全相等就进候选。候选最后仍要用精确 Jaccard 复核。规模分析要估候选对数，因为总成本取决于候选数量。

测试时，我会对照暴力 nearest neighbors，报告候选数和漏召回。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-minhash-code)

### 堆更多数据，还是把现有的做干净？这题怎么站队？

> **回答思路**  
> **背景：** 预算有限，加量和清理不能同时无限做。  
> **任务：** 判断当前瓶颈是覆盖还是噪声。  
> **做法与原因：** 先按失败类型比较新增覆盖、deduplication 和精标。  
> **结果／验证：** 相同预算下比较目标收益及 long-tail 变化。

#### 可以这样回答

我不会只按数据量作决定，会先看失败样本告诉我缺什么。如果很多题涉及根本没覆盖的语言或知识，清理旧数据不能补上这个缺口，新增覆盖更重要。

如果现有数据里重复模板很多，或者标签本身不可靠，继续加同类数据可能只是放大问题。这时我会先做 deduplication、re-annotation 或过滤。已有能力却表现不好，也可能只需要更好的示范。

预算有限时，我会各做一个小对照：新增一批覆盖，和改善一批现有数据，训练成本尽量相同。用目标任务和旧能力的结果来选下一步。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-more-vs-better)

### CoderPad：质量过滤怎么写，启发式和模型分怎么叠？

> **回答思路**  
> **背景：** 统一过滤阈值可能误删 low-resource 语言。  
> **任务：** 实现可解释的多级质量筛选。  
> **做法与原因：** 先便宜规则后模型打分，按语言做 calibration。  
> **结果／验证：** 抽查 false rejection 并比较各组通过率和下游收益。

#### 可以这样回答

统一过滤阈值可能误删 low-resource 语言。

过滤分三步：先做便宜的语言、长度、PII 和重复字符检查，再用按语言做 calibration 的质量模型打分，最后按阈值和配额选。全局取 top-$k$ 容易把 low-resource 语言整个丢掉。AFM 2025 公开的经验是过强的启发式会误删有价值的数据，所以要查 false rejection，并按语言分别对 threshold 做 calibration。

测试还要满足这个条件：抽查 false rejection 并比较各组通过率和下游收益。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-quality-filter-code)

### Data Cascade：数据上的错，为什么会在很后面才爆？

> **回答思路**  
> **背景：** 上游错误可能直到训练后才暴露。  
> **任务：** 找出错误何时进入并被放大。  
> **做法与原因：** 记录各阶段版本与拒收原因，沿链路回溯。  
> **结果／验证：** 复跑能定位同批问题并阻止再次进入训练。

#### 可以这样回答

上游错误可能直到训练后才暴露。

因为训练 loss 看不出来：上游数据错了，模型只是更好地拟合了错误数据，loss 照样往下走。抽取错误、阈值不合适、teacher 版本变化、evaluation contamination 会沿处理流程一步步放大，最后才在下游任务里暴露，这就是 Data Cascade。每一步都留下处理原因和版本，出事时才能回溯。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-data-cascade)

### CoderPad：exact deduplication 怎么写，Bloom 和哈希表怎么选？

> **回答思路**  
> **背景：** 海量指纹无法都放进内存。  
> **任务：** 稳定识别完全重复的文档。  
> **做法与原因：** 规范化后哈希，Bloom 只预筛，精确记录复核。  
> **结果／验证：** 检查 false positive 不误删，撤回使用可删除的精确表。

#### 可以这样回答

海量指纹无法都放进内存。

先规范化正文再生成指纹，内存够时用 set 判断见没见过。十亿级时用 Bloom 先筛出「可能见过」的文档，再查落盘的精确记录复核，免得误删。exact deduplication 只管规范化后相同的内容，near-duplicates 另用 MinHash；opt-out 撤回要用精确墓碑表，因为 Bloom 不支持删除。

测试时，我会检查 false positive 不误删，撤回使用可删除的精确表。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-exact-dedup-code)

### 还没过滤之前，怎么知道 corpus 里到底有什么？

> **回答思路**  
> **背景：** 不了解原始分布就无法合理设过滤规则。  
> **任务：** 先弄清 corpus 包含什么和缺什么。  
> **做法与原因：** 全库统计配合按语言、长度、来源 sampling。  
> **结果／验证：** 发现的异常能回到样本与来源，而非只看均值。

#### 可以这样回答

不了解原始分布就无法合理设过滤规则。

先对全库做计数和检索，再 sampling 看。统计语言、长度、重复率、评测重叠、PII、密钥和抽取错误，才知道该滤什么。WIMBD 就是这样检查大规模 corpus 的；Datasheets 把来源、用途、偏差和处理版本记下来，方便以后复盘。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-inspect-corpus)

### Panel：data mix 怎么定，怎么证明没有在背某一个源？

> **回答思路**  
> **背景：** 大来源容易挤掉稀缺但重要的能力。  
> **任务：** 把 token 预算对应到能力需求。  
> **做法与原因：** 小规模 data mix 实验，保留来源独立测试。  
> **结果／验证：** target evaluation slices 提高，来源替换和旧能力仍稳定。

#### 可以这样回答

大来源容易挤掉稀缺但重要的能力。

按能力类别分配 token 预算，预算来自冻结评测上的缺口，初值用小规模 data mix 实验或 mixing law 来定。要证明没背某个源，每个来源都留去过污的独立 test set，做 leave-one-source-out，并报 near-duplicates contamination rate。只看总 loss，或凭经验定 1:1:1，都说明不了问题。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-data-mix-quota)

### 质量过滤会不会滤过头？FineWeb 和 AFM 的公开教训是什么？

> **回答思路**  
> **背景：** 严格过滤可能同时删掉好代码和方言。  
> **任务：** 找到质量与覆盖的合适取舍。  
> **做法与原因：** 扫描阈值并抽查被丢弃数据。  
> **结果／验证：** 分组下游收益支持阈值，long-tail 没有被隐藏。

#### 可以这样回答

严格过滤可能同时删掉好代码和方言。

会。过滤器偏好「像英语维基或教科书」的文本，就可能把代码、公式、论坛答疑和 low-resource 语言一起删掉。阈值要试几档，比较各语言通过率和下游指标变化。FineWeb 和 AFM 2025 都提到减弱过强的启发式，滤到多严要靠实验定。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-filter-too-hard)

### LIMA 说 1000 条精标就够对齐，那 pre-training 为什么还要上 T token？

> **回答思路**  
> **背景：** 少量精标与海量 pre-training 看似矛盾。  
> **任务：** 区分学习知识与学习回答行为。  
> **做法与原因：** 先判断 base model 已有能力，再选示范或覆盖数据。  
> **结果／验证：** 比较能力题和行为题，不把文风迁移当知识提升。

#### 可以这样回答

少量精标与海量 pre-training 看似矛盾。

两个阶段解决的问题不同。LIMA 的 1000 条精标示范，教的是已有能力的模型怎么回答；pre-training 让模型学到知识、覆盖更多任务。base model 本来不会的事，少量漂亮示范补不上，False Promise 也发现模仿 teacher 的风格不等于学到 teacher 的能力。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-lima-vs-scale)

### CoderPad：域配额加 temperature sampling 怎么写，low-resource 语言怎么避免 overfitting？

> **回答思路**  
> **背景：** 来源体量不同，直接按条数抽会失衡。  
> **任务：** 按域预算做可复现 sampling。  
> **做法与原因：** 域间配额、域内温度，明确不足与重复上限。  
> **结果／验证：** 检查空域、配额偏差及 low-resource 重复次数。

#### 可以这样回答

来源体量不同，直接按条数抽会失衡。

sampling 分两层：先按能力需求给各分组分配 token 预算，再在组内用 $p_i\propto n_i^{\alpha}$ 平衡来源，$\alpha=1$ 是按体积抽，趋近 0 时更均匀。low-resource 数据重复太多会出现 overfitting，所以要配合课程和 English regression data。实际数据不足或某组为空时必须报告。

测试时，我会检查空域、配额偏差及 low-resource 重复次数。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-temp-mix-code)

### CoderPad：对着冻结评测建 13-gram 倒排，训练文档怎么 quarantine？

> **回答思路**  
> **背景：** 训练 corpus 可能包含冻结评测题面。  
> **任务：** 标出达到命中阈值的训练文档。  
> **做法与原因：** 评测建倒排索引，训练侧逐 gram 查询。  
> **结果／验证：** 手算重叠计数，隔离训练文档并保留评测。

#### 可以这样回答

训练 corpus 可能包含冻结评测题面。

把评测题面切成 13-gram 建倒排索引，训练文档逐个 gram 查表，命中数过阈值的训练文档进 quarantine，评测题留着不删。改写数字或翻译会让 n-gram false negative，所以还要配合 URL 检查和 embedding nearest neighbors，见 `dt-contamination`。

测试时，我会手算重叠计数，隔离训练文档并保留评测。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-ngram-contam-code)

### unique token 不够，把同一批数据再读几遍行不行？

> **回答思路**  
> **背景：** 新 token 不足但训练预算还有余量。  
> **任务：** 判断重复数据是否仍值得用。  
> **做法与原因：** 先 deduplication，再用重复次数对照估边际收益。  
> **结果／验证：** 独立能力不再提高时停止继续重复。

#### 可以这样回答

新 token 不足但训练预算还有余量。

可以，但先 deduplication，再有限地重复。Muennighoff 等的 datablations 发现，固定算力下重复到约 4 个 epoch，效果接近用新数据，再多收益就很小。near-duplicates 文档不能算新数据，也别为了凑 token 数放松必要的质量过滤。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-repeat-epoch)

### 监督数据「好」吗，怎么发现标签本身是错的？

> **回答思路**  
> **背景：** 更多标签可能只是放大错误标准。  
> **任务：** 定位错标与合法分歧。  
> **做法与原因：** 先查协议和一致性，再用模型提疑交人复核。  
> **结果／验证：** re-annotation sampling 改善一致性与独立评测。

#### 可以这样回答

更多标签可能只是放大错误标准。

先查 annotation guidelines 和人际一致性 $\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 能估计 label noise，找出来的样本由人确认后再改，别让模型自动翻转全部标签。training set 和 evaluation set 都要查，错标多的时候，加样本只会放大问题。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-label-noise)

### Director：一周后这批数据还能复现吗，lineage 要记什么？

> **回答思路**  
> **背景：** 一周后可能需要解释增益或撤回来源。  
> **任务：** 复现同一数据版本和处理过程。  
> **做法与原因：** 保存来源、teacher、过滤器及 mix 的版本依赖。  
> **结果／验证：** 同配置可重建，指定来源能准确移除。

#### 可以这样回答

一周后可能需要解释增益或撤回来源。

能不能复现，看每条样本能不能追到来源和版本：来源 URL、许可集或研究协议，加上抽取器、过滤器、teacher、verifier 和 dataset_version。这样每次增益都能对应固定评测和具体 mix，opt-out 也能按精确记录撤回。只有文件目录、没有来源和版本，说明不了数据可复现。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-repro-lineage)

### CoderPad：十亿文档装不进内存，按 token 配额怎么流式抽？

> **回答思路**  
> **背景：** 流式文档总量超过内存。  
> **任务：** 在有限空间做带权无放回 sampling。  
> **做法与原因：** 维护随机优先键的固定大小水库。  
> **结果／验证：** 统计频率符合权重，条数与 token 预算分开检查。

#### 可以这样回答

流式文档总量超过内存。

用加权水库 sampling：每条文档生成随机键 $k_i = u_i^{1/w_i}$，流式保留键最大的 $k$ 条，权重可以取 token 数乘质量分。按域各维护一个水库，不用把全量装进内存。水库控制的是条数，要和 token 预算对上，超长文档要切块或限制权重；空域要报告。

测试还要满足这个条件：统计频率符合权重，条数与 token 预算分开检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-reservoir-code)

### 怎样证明一批数据是好的？固定模型，只换数据

> **回答思路**  
> **背景：** 模型或算力变化会混淆数据收益。  
> **任务：** 让增益能 attribution 于具体数据变化。  
> **做法与原因：** 固定训练条件，只替换一项数据因素。  
> **结果／验证：** 同套独立评测比较，并验证规模迁移。

#### 可以这样回答

模型或算力变化会混淆数据收益。

固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务和其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都是这个对照思路。small model 也能做，但选出的方案最后要在 large model 上确认一次。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-hold-model-vary-data)

### CoderPad：SimHash 怎么写，什么时候不用 MinHash？

> **回答思路**  
> **背景：** 短文本的 shingle 集合很小。  
> **任务：** 快速寻找短文本 near-duplicates。  
> **做法与原因：** 加权哈希位投票，再用汉明距离筛候选。  
> **结果／验证：** 小样本与相似度直觉对齐，说明适用范围。

#### 可以这样回答

短文本的 shingle 集合很小。

SimHash 把每个特征哈希到 $f$ 维，按权重给每个 bit 投 +1 或 -1，最后取各维的符号当指纹，汉明距离小就是 near-duplicates。它适合短标题、URL 和 query，因为短文本的 shingle 集合太小，Jaccard 不稳；长网页 near-duplicates 仍用 `dt-minhash-code` 的 Jaccard。

测试还要满足这个条件：小样本与相似度直觉对齐，说明适用范围。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-simhash-code)

### CoderPad：PII 门怎么写，信用卡 Luhn 和代码假阳性怎么处理？

> **回答思路**  
> **背景：** 规则匹配可能把 ISBN 或示例号当敏感信息。  
> **任务：** 找到候选并区分真命中与假阳性。  
> **做法与原因：** 正则定位后做 Luhn 或格式校验，保留位置。  
> **结果／验证：** 有效卡号、无效校验和与代码样例分别测试。

#### 可以这样回答

规则匹配可能把 ISBN 或示例号当敏感信息。

先用正则找可能的 personally identifiable information (PII)，再做校验：信用卡号用 Luhn，邮箱和电话查格式。命中后记下文本位置，隔离还是脱敏交给单独的规则决定。代码里的示例卡号 `4111-1111-1111-1111` 和 ISBN 会 false positive，要按领域设白名单，命中都记录下来再处理。

测试还要满足这个条件：有效卡号、无效校验和与代码样例分别测试。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-pii-luhn-code)

### 数据选择能不能讲成一个效用函数？

> **回答思路**  
> **背景：** 高质量不能只靠一个模糊形容词。  
> **任务：** 把选择标准转成可讨论的效用。  
> **做法与原因：** 明确收益目标，再选阈值、配额或加权 sampling。  
> **结果／验证：** 效用排序需要下游实验支持而非自证。

#### 可以这样回答

高质量不能只靠一个模糊形容词。

可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛、按桶分配额，还是按分数加权 sampling。Albalak 等 2024 年的综述就是这样拆成两步的。启发式、ppl、分类器、EL2N 和 RL sampling，区别主要在效用怎么估。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-utility-select)

### CoderPad：精确哈希之前，Unicode / 零宽字符怎么规范化？

> **回答思路**  
> **背景：** 视觉相同的文本可能得到不同哈希。  
> **任务：** 在不破坏语义的前提下规范化。  
> **做法与原因：** 按场景做 NFKC 与空白处理，慎用形近字映射。  
> **结果／验证：** 检查等价文本合并及真实差异不被误合并。

#### 可以这样回答

视觉相同的文本可能得到不同哈希。

算精确哈希之前，先用 NFKC 统一兼容字符和全角形式，按场景去掉零宽和控制字符，再压缩空白。规范化过度会把本来不同的文本变成一样，所以规则按数据类型开；跨文字体系的形近字映射只用在需要复核的高价值数据上。

测试时，我会检查等价文本合并及真实差异不被误合并。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-unicode-canon-code)

### 用 LLM 把网页改写成干净段落，这算做好数据吗？

> **回答思路**  
> **背景：** 原网页有内容价值但表达不利于学习。  
> **任务：** 判断改写是否提高样本效率。  
> **做法与原因：** 保留原文和来源，验证改写事实与覆盖。  
> **结果／验证：** 固定预算比较，不把新措辞当新增知识。

#### 可以这样回答

原网页有内容价值但表达不利于学习。

算一种有用的 data augmentation，前提是和原文一起用：清理后的原文和改写版本一起训，再验证样本效率有没有提高。WRAP 在 C4 上公开报告过约 3 倍样本效率，但改写不增加新事实，也解决不了许可、evaluation contamination 和 teacher 错误，所以要保留原文，记下 teacher 和来源。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-wrap-rephrase)

### C4 那种块名单过滤，质量上去了，谁被切掉了？

> **回答思路**  
> **背景：** 块名单不理解词语所在的语境。  
> **任务：** 识别过滤伤害了哪些人群与主题。  
> **做法与原因：** 按语言和身份话题抽查丢弃样本。  
> **结果／验证：** 报告 false rejection 与能力变化，而非只报平均质量。

#### 可以这样回答

块名单不理解词语所在的语境。

常被切掉的是正常的身份讨论、方言、非英语页面和对话。块名单按词匹配、不看上下文，清理有害内容时会把这些一起删掉。所以过滤后除了看平均分和 perplexity，还要按语言、主题统计通过率，抽查被丢弃的样本，看清哪些人和话题被排除了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-c4-side-effect)

### CoderPad：embedding nearest neighbors 去语义重复，什么子集才值得上？

> **回答思路**  
> **背景：** 改写后的重复可能绕过字符串 deduplication。  
> **任务：** 控制高价值子集的语义重复。  
> **做法与原因：** 先便宜 deduplication，再用 embeddingnearest neighbors 复核。  
> **结果／验证：** 抽查同义与相关但不同的内容，评估成本。

#### 可以这样回答

改写后的重复可能绕过字符串 deduplication。

MinHash 抓不到换了说法的重复，这一层用 embedding 来补：对已经过精确哈希和 MinHash 的高价值子集，用 ANN 取 top-$k$ nearest neighbors，余弦相似度超过阈值的归入同一个 cluster，保留质量最高的一条。适合许可书、SFT 和通过 verifier 的 synthetic data；成本高，十亿级网页不宜直接全量跑。

测试还要满足这个条件：抽查同义与相关但不同的内容，评估成本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-semdedup-code)

### CoderPad：HTML 去导航条，文本密度怎么写，什么时候才上 LLM 抽取？

> **回答思路**  
> **背景：** 网页正文混入导航和页脚。  
> **任务：** 保留信息主体并减少处理成本。  
> **做法与原因：** 先用文本/链接密度规则，难域再上复杂抽取。  
> **结果／验证：** 正文召回和模板残留都要 sampling 检查。

#### 可以这样回答

网页正文混入导航和页脚。

先用块级的文本密度和链接密度把导航、页脚这类模板块滤掉，这一步最便宜。按域统计抽取失败率，静态抽取失败的域再开 headless 渲染，仍失败才上 LLM 抽取。每页都调 large model 成本高，抽取带来的变化也难追踪；用了 LLM 要记模型版本，抽出的正文照样过质量检查和 evaluation contamination 检查。

测试还要满足这个条件：正文召回和模板残留都要 sampling 检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-boilerplate-code)

### 许可、opt-out、PII 为什么也算数据质量问题？

> **回答思路**  
> **背景：** 有能力价值的数据也可能不可用于训练。  
> **任务：** 把许可和撤回当作数据可用性条件。  
> **做法与原因：** 摄入前检查用途，保存精确来源依赖。  
> **结果／验证：** 不合格来源无法进入 mix，撤回可追踪。

#### 可以这样回答

有能力价值的数据也可能不可用于训练。

因为能不能合法用于训练，本身就是质量条件。许可不合格、opt-out 执行不了、或者带着不该用的 personally identifiable information (PII)，评测分再高也可能被迫撤回重训。所以要把这些约束放进数据选择流程，追踪来源、拒绝记录、teacher 和合成 seed。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-license-is-quality)

### 怎样才算把数据做对：一次干预从假设跑到能不能上 mix？

> **回答思路**  
> **背景：** 知道某 evaluation slices 差，还不足以决定该加什么。  
> **任务：** 完成一次可 attribution 的数据实验。  
> **做法与原因：** 提出竞争假设，固定预算只改一项。  
> **结果／验证：** 独立 evaluation slices 收益与旧能力回归共同决定入 mix。

#### 可以这样回答

知道某 evaluation slices 差，还不足以决定该加什么。

先写一个能被推翻的假设，固定评测，一次只改一项数据因素，比如来源、过滤或 data mix。用同模型、同预算的对照看目标能力和其他能力，再查 contamination、隐私、许可和版本记录。通过了才进训练 mix，没通过就隔离，记下失败原因。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-data-intervention)

### Panel：long context 数据怎么造，短了补长度、长了丢能力怎么避免？

> **回答思路**  
> **背景：** 拉长文本不等于模型会用远处证据。  
> **任务：** 培养跨距离检索与组合能力。  
> **做法与原因：** 保留真实结构并构造位置、距离和干扰对照。  
> **结果／验证：** 分长度测能力和短上下文回归，不只测能否装下。

#### 可以这样回答

拉长文本不等于模型会用远处证据。

长度本身教不会模型跨段检索，要用真实长文（许可书籍、代码仓库），加上把可核验答案埋在不同位置的合成长文，同时混入上一阶段的短数据，防止短任务退步。单纯 padding 或重复拼接短文只增加长度，没有需要查找的信息。AFM 用这三类数据把序列扩展到 65K。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-longctx-data)

### CoderPad：语言识别怎么写，文档级和段落级差在哪？

> **回答思路**  
> **背景：** 一篇文档可能混合多种语言。  
> **任务：** 按题目要求判断文档或段落语言。  
> **做法与原因：** 先明确单位和 confidence threshold，再汇总段落信息。  
> **结果／验证：** 混语、短文本和未知语言保留不确定性。

#### 可以这样回答

一篇文档可能混合多种语言。

现场写一个字符 3-gram 朴素贝叶斯来识别语言。先剥掉代码块，再按段落分别识别，否则英语页里的中文段会被一起标成英语。分数低于阈值时输出 `und`，表示判断不了，别硬猜。

测试还要满足这个条件：混语、短文本和未知语言保留不确定性。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-lid-code)

### CoderPad：LSH 候选对怎么并成 near-duplicates cluster，cluster 里留哪一条？

> **回答思路**  
> **背景：** near-duplicates 关系以候选对形式分散。  
> **任务：** 合并 cluster 并选择保留代表。  
> **做法与原因：** 精确复核后并查集合并，保留策略明确。  
> **结果／验证：** 检查传递关系与链式误合并，代表可追溯。

#### 可以这样回答

near-duplicates 关系以候选对形式分散。

对 LSH 候选对先算精确 Jaccard，只给达到阈值的文档对连边，再用并查集求连通分量，得到 near-duplicates cluster。每个 cluster 保留质量最高的一条，缺质量分时才看长度。异常大的 cluster 多半是公共模板造成的误连，要剥掉模板、分域后重新聚类。

测试时，我会检查传递关系与链式误合并，代表可追溯。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-lsh-cluster-code)

### CoderPad：精确子串 deduplication 怎么写，滚动哈希怎么扫 evaluation leakage？

> **回答思路**  
> **背景：** 整篇不重复也可能包含 leakage 片段。  
> **任务：** 发现精确子串或评测重叠。  
> **做法与原因：** 滚动哈希提速，命中后核对原文。  
> **结果／验证：** 覆盖 edge cases 和 hash collisions，避免哈希相同直接判真。

#### 可以这样回答

整篇不重复也可能包含 leakage 片段。

把评测内容切成固定长度的字符或 token 窗口，用滚动哈希扫训练文档，命中后再比原文，排除哈希碰撞。它能发现整篇哈希漏掉的局部片段复制。窗口太短会 false rejection 常见代码，太长会漏掉变体，规范化按域选；训练内部的子串 deduplication 和评测隔离用不同的表和阈值。

测试时，我会覆盖 edge cases 和 hash collisions，避免哈希相同直接判真。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-substr-dedup-code)

### CoderPad：KenLM / perplexity data quality checks 怎么写，阈值按语言怎么切？

> **回答思路**  
> **背景：** perplexity 的正常范围随语言和领域改变。  
> **任务：** 用可进行 calibration 的分数筛明显异常文本。  
> **做法与原因：** 按分组设阈值并抽查，不全局只留低 ppl。  
> **结果／验证：** 比较误删和下游覆盖，保留有用难文本。

#### 可以这样回答

perplexity 的正常范围随语言和领域改变。

用小语言模型算文档的平均 cross-entropy 或 perplexity，可以当质量的间接信号，但它只说明文本像不像参考 corpus。阈值要按语言和数据域取分位数，代码、公式和论坛要各设阈值，维基的阈值套不上。synthetic data 要用独立 verifier，筛得好不好靠下游对照判断。

测试时，我会比较误删和下游覆盖，保留有用难文本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-ppl-filter-code)

### Panel：网页抽取失败有哪些，LLM 抽取什么时候才上？

> **回答思路**  
> **背景：** 正文可能来自脚本、扫描件或复杂布局。  
> **任务：** 先确定抽取失败发生在哪。  
> **做法与原因：** 按域审计规则，再决定渲染或模型抽取。  
> **结果／验证：** 核对数学代码结构与来源事实，不只看流畅。

#### 可以这样回答

正文可能来自脚本、扫描件或复杂布局。

LLM 抽取放在最后一档。先用静态规则抽，失败了用 headless 浏览器重试，规则仍处理不好的领域页面才用 LLM 抽主内容，因为每页都跑 large model 太贵。常见失败是把导航当正文、JavaScript 页面为空、扫描 PDF、广告打断正文；抽取器本身会改写文本，版本要记录，便于追查数据变化。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-web-extract)

### CoderPad：pre-training 怎么把文档拼进固定长度，是否在 document boundaries 切断 causal attention？

> **回答思路**  
> **背景：** 文档长度不同，需要填满固定训练块。  
> **任务：** 高效打包并明确跨文档语义。  
> **做法与原因：** 保留 document offsets，按训练契约决定 attention 隔离。  
> **结果／验证：** token 守恒、尾块和跨文档位置的 loss 均需检查。

#### 可以这样回答

文档长度不同，需要填满固定训练块。

把文档贪心装进长度为 `seq_len` 的序列，文档之间插 BOS/EOS，在 document boundaries 切断 attention，padding 不算 loss。这样算力不浪费在 pad 上，模型也不会跨篇续写。pre-training 一般监督文档里的大部分 token，SFT 还要按角色限制监督范围，见 `dt-packed-sft-code`。

测试还要满足这个条件：token 守恒、尾块和跨文档位置的 loss 均需检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-pretrain-pack-code)

### CoderPad：代码近克隆怎么指纹，Winnowing 窗口怎么写？

> **回答思路**  
> **背景：** 代码改名改格式后仍可能近克隆。  
> **任务：** 生成稳定的局部代码指纹。  
> **做法与原因：** 规范化 token，用窗口最小哈希保留局部特征。  
> **结果／验证：** 改格式仍匹配，真正不同逻辑不过度合并。

#### 可以这样回答

代码改名改格式后仍可能近克隆。

先规范化源码，切成 k-gram 算哈希，每个窗口只留最小的哈希当指纹，再用 Jaccard 比较指纹集合。许可证头和 import 块要先剥掉，否则大量无关的 Python 文件也会显得相似。

测试还要满足这个条件：改格式仍匹配，真正不同逻辑不过度合并。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-winnow-code)

### CoderPad：爬到的网页和仓库里，API 密钥怎么扫出来？

> **回答思路**  
> **背景：** 公开仓库也可能 leakage 可用密钥。  
> **任务：** 定位敏感候选并控制 false positive。  
> **做法与原因：** 模式与上下文、熵等信号结合，记录位置。  
> **结果／验证：** 检查示例值和真实格式，结果不直接外泄。

#### 可以这样回答

公开仓库也可能 leakage 可用密钥。

用提供商前缀加字符串熵来找凭证，命中后整个文件隔离，高价值来源再人工核对。示例密钥可以白名单；只做脱敏的文件仍可能教会模型密钥格式，来源和安全检查都要做。检测覆盖不了所有提供商，teacher model 的合成输出也要扫。

测试时，我会检查示例值和真实格式，结果不直接外泄。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-secret-scan-code)

### CoderPad：训练 / 开发 / evaluation gate 怎么稳定切开，怎样才不会 leakage？

> **回答思路**  
> **背景：** 重跑和新增数据不能改变已有 split。  
> **任务：** 按稳定单位隔离训练与评价。  
> **做法与原因：** 对实体或重复 cluster 的规范键做哈希分桶。  
> **结果／验证：** 同组不跨 split，新增记录不移动旧样本。

#### 可以这样回答

重跑和新增数据不能改变已有 split。

对稳定的 group_id 做哈希再取模，让同一仓库、书、线程或 near-duplicates cluster 整组落在训练或评测的同一侧。随机 shuffle 会把同一篇转载拆到两边，让记忆看起来像泛化。seed 和规范化版本要记录，重跑才稳定；时间 leakage 和生成 prompt 里混入评测题，哈希解决不了，要单独查。

测试还要满足这个条件：同组不跨 split，新增记录不移动旧样本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-hash-split-code)

### CoderPad：URL 怎么规范化，opt-out / robots 怎么落到一条拒绝函数？

> **回答思路**  
> **背景：** URL 变体可能绕过重复与撤回规则。  
> **任务：** 统一身份并正确处理拒绝条件。  
> **做法与原因：** 规范化时保留语义参数，精确检查政策。  
> **结果／验证：** 别名、查询参数及拒收优先级按契约测试。

#### 可以这样回答

URL 变体可能绕过重复与撤回规则。

URL 先统一规范化，再拿去做 deduplication、许可拒绝表和评测匹配：scheme 和 host 转小写，去掉默认端口和 fragment，只删跟踪类 query，保留分页参数。host 后缀匹配要检查 domain matching rules。原 URL 和规范化后的 URL 都要记录，robots 和 opt-out 由上游另做检查。

测试还要满足这个条件：别名、查询参数及拒收优先级按契约测试。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-url-canon-code)

### CoderPad：按长度分层 sampling 怎么写，短模板淹没长文档怎么避免？

> **回答思路**  
> **背景：** 按篇 sampling 会被短模板支配。  
> **任务：** 保持目标长度覆盖并遵守预算。  
> **做法与原因：** 分长度桶 sampling，条数和 token 分别记账。  
> **结果／验证：** 检查空桶、长样本与实际 token 占比。

#### 可以这样回答

按篇 sampling 会被短模板支配。

按 token 数把文档分进长度桶（2k / 8k / 32k），每桶单独设 token 配额，再从桶里按文档抽。文档是 sampling 单位，token 是预算单位。只按文档数随机打乱的话，海量短网页会占满名额，书和长文档被抽得太少。

测试时，我会检查空桶、长样本与实际 token 占比。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-length-bucket-code)

### CoderPad：十亿文档里找高频样板 n-gram，Count-Min 怎么写？

> **回答思路**  
> **背景：** 精确记录全部 n-gram 占用太多内存。  
> **任务：** 近似估计高频模板并说明误差。  
> **做法与原因：** 多哈希计数取最小值，候选再精确复核。  
> **结果／验证：** 估计不低于真实频次，误差与空间配置相关。

#### 可以这样回答

精确记录全部 n-gram 占用太多内存。

要找的是跨文档反复出现的片段，比如版权声明、导航和 cookie 提示。精确计数要一张十亿级哈希表，所以用 Count-Min sketch：$d$ 行 $w$ 列计数器，每个 n-gram 经 $d$ 个哈希各加一，查询取 $d$ 行最小值。碰撞只会让估计偏高，阈值留余量，超阈值的候选抽查复核后再剥除。

测试还要满足这个条件：估计不低于真实频次，误差与空间配置相关。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-countmin-code)

### Panel 情景：数据任务重跑后样本翻倍，怎么恢复并防止训练重复？

> **回答思路**  
> **背景：** 重试后重复样本可能进入训练。  
> **任务：** 先恢复数据正确性再修重试机制。  
> **做法与原因：** 冻结受影响版本，按稳定样本 ID 对账和 idempotent write 入。  
> **结果／验证：** 重跑不再增量翻倍，修复后下游版本可追溯。

#### 可以这样回答

重试后重复样本可能进入训练。

把原始样本身份、变换版本与运行尝试分开，写入不可变分片并用完整 manifest 原子发布。恢复时检查训练已消费的数据版本和位置；deduplication 必须明确区分重复交付与有意的 data augmentation。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-data-replay-incident)

### CoderPad：按 padding 后 token 预算组 batch，遇到超长样本怎么办？

> **回答思路**  
> **背景：** padding 开销取决于批中最大长度。  
> **任务：** 按真实计算预算组 batch。  
> **做法与原因：** 加入样本前计算新最大长度乘批大小。  
> **结果／验证：** 检查最后一批、超长单例和顺序守恒。

#### 可以这样回答

padding 开销取决于批中最大长度。

预算按 batch 内最大长度乘样本数计算，不能只累加真实长度。顺序扫描，加入下一条会超预算时先交付当前 batch；单条超长样本单独记录为拒收，其他样本不丢失、不重排。

测试时，我会检查最后一批、超长单例和顺序守恒。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-token-budget-batch-code)

### CoderPad：IterableDataset 多进程读取，怎样避免每个 worker 都读一遍？

> **回答思路**  
> **背景：** 每个 worker 可能各读一遍同样的数据。  
> **任务：** 让并行迭代覆盖且不重复。  
> **做法与原因：** 按 worker/rank 统一分片并记录恢复位置。  
> **结果／验证：** 多 worker 合并后每条恰好消费一次。

#### 可以这样回答

每个 worker 可能各读一遍同样的数据。

先把 rank 与 worker 映射成全局消费者编号，再按稳定分片编号取模分配。必须说明 worker 数固定的假设；重新洗牌、弹性扩容和 checkpoint 恢复不能靠这个映射自动解决。

测试还要满足这个条件：多 worker 合并后每条恰好消费一次。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-worker-shard-code)

### CoderPad：无限数据流如何用固定缓冲区近似打乱？

> **回答思路**  
> **背景：** 无限流不能先全量洗牌。  
> **任务：** 用有限缓冲区近似打乱。  
> **做法与原因：** 随机替换和出队，明确尾部清空规则。  
> **结果／验证：** 样本不丢不重，固定 seed 可复现。

#### 可以这样回答

无限流不能先全量洗牌。

维护固定容量缓冲区，新元素到达时随机交付一个旧元素并替换它，结束时随机清空。这样每条数据恰好交付一次且内存有界，但小缓冲区无法产生全局均匀排列。

测试还要满足这个条件：样本不丢不重，固定 seed 可复现。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-buffer-shuffle-code)

### Panel 情景：数学和工具数据单独都有效，一起加入为什么掉点？

> **回答思路**  
> **背景：** 两类数据单独有效，混合反而掉点。  
> **任务：** 区分交互、预算挤占和测量问题。  
> **做法与原因：** 做受控组合及等 token 对照，检查 task slices。  
> **结果／验证：** 联合收益和 negative transfer 需同条件证据支持。

#### 可以这样回答

两类数据单独有效，混合反而掉点。

用固定总预算的四组实验估计单独效果与交互，排查替换基础数据、重复率、gradient 与格式冲突。单独收益不能简单相加，组合表现差也不能直接推出“这两种能力互斥”。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-mixture-factorial-budget)

### Panel 情景：换 tokenizer 后 loss 更低，为什么 multilingual 能力和 long context 都退化？

> **回答思路**  
> **背景：** tokenizer 改变后 loss 单位也变了。  
> **任务：** 判断是真能力退化还是指标不可比。  
> **做法与原因：** 比较原始文本覆盖、长度预算与独立任务。  
> **结果／验证：** 不跨 tokenizer 直接比 loss，报告语言和长度 evaluation slices。

#### 可以这样回答

tokenizer 改变后 loss 单位也变了。

不同 tokenizer 的每 token loss 不可直接比较。先用相同原始文本与统一 normalization 对照，再检查切分膨胀、特殊 token、截断与监督对齐，避免把 data pipeline 错误误判为模型退化。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=dt-tokenizer-migration-gap)

### 一亩三分地 Apple AIML Infra：从 JSON 字符串清洗文档记录并汇总拒收原因

> **回答思路**  
> **背景：** 原始 JSON 字符串可能损坏或字段不合法。  
> **任务：** 清洗记录并准确汇总拒收原因。  
> **做法与原因：** 解析、schema 校验和业务规则分开执行。  
> **结果／验证：** 正常、缺失、类型错误和重复规则逐项手算。

#### 可以这样回答

原始 JSON 字符串可能损坏或字段不合法。

先解析 JSON，再按明确顺序校验字段、应用阈值和按 ID 保留最佳记录。要区分数据无效、质量不足与重复三种计数，避免一条记录被多个拒收原因重复统计，也要说明布尔值不能当质量数字。

测试还要满足这个条件：正常、缺失、类型错误和重复规则逐项手算。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=p3a-apple-json-clean-code)

### Data Pipeline：怎样从杂乱语料构建可追溯、可扩展的训练数据？

> **回答思路**  
> **背景：** 新增数据量很大，但低质量、重复与 contamination 可能抵消收益。  
> **任务：** 把数据来源、质量判断和训练版本连接起来。  
> **做法与原因：** 先建立可追溯的小规模流程，再以稳定 record ID 扩展处理。  
> **结果／验证：** 能复现 data mix，并证明质量收益不是仅来自更多训练 tokens。

#### 可以这样回答

我会先问这批数据要补什么能力。如果目标是 tool use，普通网页文本再多也未必解决参数选择问题，所以我不会一开始就把问题理解成 throughput 优化。

以新增技术文档为例，我会保留原始文件、来源许可和版本，然后依次做解析、敏感信息处理、质量检查、deduplication 和 evaluation contamination 检查。每层都保存拒绝原因，并抽查被拒绝的数据，防止过滤器把少数语言或特殊格式一起删掉。

规模变大以后，我会用稳定 record ID 和版本化 manifest 分配工作，让 worker 重试不会重复加入样本。训练读取冻结的 manifest，而不是随时变化的目录；这样发现坏数据时，能找到受影响的数据版本和 checkpoints。

最后，我会固定训练预算比较旧 data mix 和新 data mix，检查目标能力与 regression tasks。清洗后保留了多少数据只是过程指标，独立评估是否变好才决定这条 pipeline 有没有价值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=data&question=afm-web-data-pipeline)


## 06 · Synthetic Data 与 Self-Improvement

### post-training 数据：数学、代码、工具、agent，各自的 acceptance criteria 是什么？

> **回答思路**  
> **背景：** 数学、代码和工具需要不同的正确性证据。  
> **任务：** 先给任务选可靠监督再谈混合。  
> **做法与原因：** 可执行任务先验证，主观任务明确偏好协议。  
> **结果／验证：** 各任务独立验收，不能用总奖励代替能力。

#### 可以这样回答

数学、代码和工具需要不同的正确性证据。

post-training 的数据单位是题目、trajectories 和 grader，各类任务的 acceptance criteria 就是 grader 如何判断正确性：数学看标准答案、解释器或 Lean，代码看冻结的测试，工具看 schema 和环境状态，agent 还要看 trajectories 能否 replay、多跑几次是否稳定。四类检查各管一个域，要分开建；post-training 要准备的是题目、trajectories 和 grader，多加网页解决不了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-posttrain-map)

### 数学 SFT 题太简单或太难，数据侧怎么切 difficulty band？

> **回答思路**  
> **背景：** 太容易或完全不会的题都可能缺学习信号。  
> **任务：** 找到 current policy 可学习的难度范围。  
> **做法与原因：** 多次 sampling 估难度，兼顾覆盖和课程变化。  
> **结果／验证：** 看独立难度段收益，避免只筛出熟题。

#### 可以这样回答

太容易或完全不会的题都可能缺学习信号。

按当前 student model 每题 sampling $k$ 次、做对几次来切，竞赛名称只能粗分。全对的太易少留；部分对的是中间带，成功 trajectories 做 SFT、错的做负样本；全错的先降难度或找 teacher / 解释器，RLVR 也需要模型有机会拿到非零奖励。换 student 要重切，还要防止中间带被 GSM8K 改写题填满。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-math-passk-band)

### Director：模型怎么给自己造训练数据，limitations 是什么？

> **回答思路**  
> **背景：** 模型重复自己的输出可能只强化旧错误。  
> **任务：** 解释自生成数据何时带来新信号。  
> **做法与原因：** 用外部执行、独立验证和多样任务约束迭代。  
> **结果／验证：** 真实 holdout 与 long-tail 提高，否则停或改策略。

#### 可以这样回答

我觉得 self-improvement 最关键的问题是，新一轮究竟得到了什么新信息。只是把自己的答案改写几遍，再拿回来训练，原来的错误很可能也一起被强化。

我更愿意从有外部反馈的任务开始。比如模型写代码，实际执行告诉它哪些测试失败；或者工具操作以后，环境告诉它状态有没有改变。模型可以生成候选和修复，但判定不能只靠它自己说“这次更好”。

每轮我会保留原始数据和独立评测，检查新任务、long-tail 和成本。如果验证收益停了，或者只是在适应同一套 scorer，就暂停这轮做法。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-self-improve)

### Panel：推理 synthetic data 怎么做，什么样的 pipeline 你能画出来？

> **回答思路**  
> **背景：** teacher 能写长推理，但过程未必正确。  
> **任务：** 构造自然且可验证的推理数据。  
> **做法与原因：** 从许可 seed 生成，分开检查答案、过程和难度。  
> **结果／验证：** 新题收益支持合成，contamination 与旧能力同时审计。

#### 可以这样回答

我会先选一个能检查答案的任务，比如数学或代码，从少量许可 seed 开始生成不同问题和解法。先把题目是否有效、答案是否正确检查清楚，再看推理过程有没有明显跳步或矛盾。

数据也不能全是最容易通过的题。我会用当前 student model 多采几次，看看哪些难度还有学习空间，同时保留不同题型。teacher 写得很长但 student 根本学不会的 trajectories，不会因为看起来厉害就全部留下。

最后先做一轮固定预算的训练，在没参与生成和筛选的新题上看收益。如果只在合成题上涨，我会查 teacher 风格和题目模板，而不是马上扩大生成量。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-synth-reasoning)

### 数学 post-training：纯 CoT、PAL 程序、还是 ToRA 那种边想边跑代码？

> **回答思路**  
> **背景：** 纯文字推理和执行程序有不同错误。  
> **任务：** 为数学任务选择合适的工具监督。  
> **做法与原因：** 比较 CoT、程序及混合 trajectories 的可验证性与预算。  
> **结果／验证：** 同一任务同预算测正确率和工具错误传播。

#### 可以这样回答

纯文字推理和执行程序有不同错误。

按任务分，需要计算的步骤用 TIR 交给解释器，心算、不等式、证明思路仍用自然语言。PAL / PoT 把题意转成程序，ToRA / OpenMathInstruct 让推理和代码调用交替。代码必须在沙箱里真实执行，最终答案再对 gold labels；解释器输出作为输入，不计入 CE。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-math-tir-data)

### Panel：tool calls 和 multimodal 合成，你能画出哪条具体 pipeline？

> **回答思路**  
> **背景：** 合法 JSON 或好看截图不代表任务完成。  
> **任务：** 构建带环境反馈的工具/multimodal 样本。  
> **做法与原因：** 从状态与证据生成任务，真实执行后核验。  
> **结果／验证：** 同初态能 replay，新任务和视觉变化可迁移。

#### 可以这样回答

合法 JSON 或好看截图不代表任务完成。

工具和视觉是两条 pipeline，要分别讲生成和验证。工具数据在可重置的执行环境里生成，reference model 调用工具，人能回滚纠错，保存成功路径和被放弃的尝试，oracle 是环境状态，最后一句话说得对不算数。视觉数据要补详细描述、代码渲染的图表和可核验问答，还要教模型拒绝回答图中没有的信息。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-synth-tool-mm)

### Lean / 形式化证明能不能当数学 post-training 的 oracle？

> **回答思路**  
> **背景：** 自然语言论证不容易自动判定。  
> **任务：** 判断形式化验证可覆盖哪些任务。  
> **做法与原因：** 将命题和证明分开验证，检查形式化忠实度。  
> **结果／验证：** 证明通过且命题对应原题，不外推到全部数学。

#### 可以这样回答

自然语言论证不容易自动判定。

能，但只覆盖形式化证明。Lean 的 kernel 逐步检查证明，通过编译和证明检查才算正例，比只看最终 boxed 答案可靠；DeepSeek-Prover 先用成功证明和子目标冷启动，再用 Lean 反馈做 RL。自然语言计算题仍要靠 TIR 等方法验证，两类数据和 grader 分开记录、分开评测。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-math-lean-prover)

### MetaMath 那种改写 GSM8K，什么时候是 data augmentation，什么时候是 leakage？

> **回答思路**  
> **背景：** 改写会保留原题答案与结构。  
> **任务：** 区分训练增强和 evaluation contamination。  
> **做法与原因：** 先按原题家族划分，评价题不参与生成。  
> **结果／验证：** 改写 deduplication 与未见新题共同检查泛化。

#### 可以这样回答

改写会保留原题答案与结构。

三条都满足才算增强：seed 不来自冻结评测题、答案重新计算、评测用独立题目。训练和测试都围着 GSM8K 同一题族时，换数字、换问法也可能只是让模型记住题族，换到 SVAMP、GSM-Hard 就掉分。看到合成集自称 MATH 提高 15%，先查 seed 和重叠。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-math-rewrite-leak)

### CoderPad：手写 rejection sampling，verifier 和 $k$ 怎么选？

> **回答思路**  
> **背景：** 多个候选中只有部分可靠。  
> **任务：** 按题目定义筛出合格样本。  
> **做法与原因：** 逐候选运行 verifier，明确数量和无通过结果。  
> **结果／验证：** 检查顺序、上限、全部失败与验证成本。

#### 可以这样回答

多个候选中只有部分可靠。

同一道题采 $k$ 条回答，用独立 oracle 判对错，只留对的；生成器和 verifier 要分开。代码要处理全错、全对和过程假三种情况。$k$ 由当前 pass@$1$ 决定；没有 oracle 就别写 `if judge(y): keep`。

测试时，我会检查顺序、上限、全部失败与验证成本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-rejection-sample-code)

### 代码指令数据：从开源片段造题（OSS-Instruct），比让 teacher 空手编好在哪？

> **回答思路**  
> **背景：** 无上下文造代码题容易脱离真实用法。  
> **任务：** 把许可代码转成有依据的指令任务。  
> **做法与原因：** 保留源码语义与出处，执行验证新指令答案。  
> **结果／验证：** 独立题型有效，许可和近克隆不越界。

#### 可以这样回答

无上下文造代码题容易脱离真实用法。

从许可仓库抽真实代码片段，让 teacher 照着片段出题，题目会覆盖 API、并发、文件和错误处理这些实际问题，比 teacher 凭空反复出教材题更能保持多样性。片段许可证、执行测试和与 HumanEval 的重叠仍然要查。OSS-Instruct 管覆盖，Evol-Instruct 管难度，两者可以叠着用。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-code-oss-instruct)

### 代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？

> **回答思路**  
> **背景：** 公开样例覆盖很有限。  
> **任务：** 防止模型只适应已见测试。  
> **做法与原因：** 公开反馈与隐藏验收分离，扩充独立 edge-case tests。  
> **结果／验证：** 原测试与新测试都通过且没有修改 grader。

#### 可以这样回答

公开样例覆盖很有限。

三套测试三种用途：公开测试给模型当改代码的反馈，hidden tests 决定能不能当正例和 RL 奖励，EvalPlus 或新竞赛题做独立评测。hidden tests 要固定哈希，改过测试的 trajectories 要隔离；只过了公开样例或只是编译成功，都不算正确解。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-code-hidden-tests)

### 函数级 HumanEval 数据，和仓库级 SWE 数据，post-training 怎么分桶？

> **回答思路**  
> **背景：** 单函数正确不代表能修完整仓库。  
> **任务：** 按能力需求分配代码数据。  
> **做法与原因：** 函数题教局部逻辑，仓库题保留环境与 tool-use trajectories。  
> **结果／验证：** 分别测函数正确、跨文件修复及回归。

#### 可以这样回答

单函数正确不代表能修完整仓库。

分成两个桶，分别 data mix、分别评测。函数级是短 prompt、单文件、单测；仓库级要读 issue、定位多个文件、在执行环境里跑 regression tests，混在一起训，模型会把写独立函数的做法搬到仓库任务上。仓库 trajectories 要保留检索和失败恢复的过程，只训最终补丁，模型学不会定位；SWE-Gym 这类可执行环境里的成功 trajectories 也要再筛，见 `dt-swe-success-noise`。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-code-repo-vs-fn)

### Panel：最强 teacher 生成的数据，为什么 student 不一定学得最好？

> **回答思路**  
> **背景：** 最强 teacher 的输出可能不适合较小 student。  
> **任务：** 选择 student 能学且覆盖真实任务的数据。  
> **做法与原因：** 比较 teacher 风格、难度和验证后 learnability。  
> **结果／验证：** 同预算 student 收益决定选择，不只看 teacher 分数。

#### 可以这样回答

最强 teacher 的输出可能不适合较小 student。

teacher 回答正确，不代表 student 能学会。还要查过程是否过长、是否用了 student 没有的工具，以及 student 自己 sampling 时能不能找到类似的正确解。太难的示范可以压缩、拆成子任务，或改用 student 自己生成且验证通过的回答。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-teacher-bias)

### Panel：什么时候不要上 synthetic data？

> **回答思路**  
> **背景：** 缺少真值时合成可能循环复制错误。  
> **任务：** 判断是否值得继续生成。  
> **做法与原因：** 先查验证能力、来源覆盖与真实需求。  
> **结果／验证：** 无法独立确认收益时改用许可材料或人工标注。

#### 可以这样回答

缺少真值时合成可能循环复制错误。

先问生成结果靠什么独立验证，答不出来就不该合成。停下来的信号是没有独立验证手段、需要真实世界的 long-tail、评测和生成器同族，或者已经多轮 synthetic-data reuse。合成适合补能验证的任务覆盖，其他缺口用人写 seed、许可采集或改进评测来解决。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-when-not-synth)

### 数学、代码、工具、聊天 post-training 配在一起，怎么避免互相打掉？

> **回答思路**  
> **背景：** 一种 post-training 数据可能挤掉其他行为。  
> **任务：** 平衡新技能和通用能力。  
> **做法与原因：** 固定预算做 data mix ablation study，保留 regression tasks。  
> **结果／验证：** 逐任务回归和成本决定 mix，而非统一比例。

#### 可以这样回答

一种 post-training 数据可能挤掉其他行为。

四类数据分别设 token 配额和 loss 范围再混，可验证任务用 rule-based reward，主观偏好用 human evaluation 或 RM，奖励尺度不同的任务不放进同一个 GRPO 分组，工具返回不计入损失。每加一类数据都回看其余能力，防止代码伤拒答、工具 JSON 伤自然语言。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-posttrain-mix)

### CoderPad：数学合成怎么验， boxed 答案怎么抽，过程假怎么办？

> **回答思路**  
> **背景：** 答案抽取正确也可能掩盖过程问题。  
> **任务：** 可靠解析结果并区分验证范围。  
> **做法与原因：** 明确 boxed 规则与数值等价，再独立审查过程。  
> **结果／验证：** 覆盖多答案、缺失和格式错误，未知不当正确。

#### 可以这样回答

答案抽取正确也可能掩盖过程问题。

从模型输出里抽最后一个 `\boxed{}` 或最终数字，规范化后和独立的标准答案比较，抽不到或对不上就扔。最终答案对、过程自相矛盾的样本，也别直接当 SFT 正例。没有独立 gold labels 时，不能让模型给自己判对。

测试时，我会覆盖多答案、缺失和格式错误，未知不当正确。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-math-verifier-code)

### OpenAI 的 Shunyu Yao 把 Agent RL 配方写成什么？数据岗听哪一句？

> **回答思路**  
> **背景：** Agent 改进依赖环境和交互，不只是静态文本。  
> **任务：** 把公开观点转成可操作数据职责。  
> **做法与原因：** 围绕任务分布、环境反馈与 verifiable reward 解释。  
> **结果／验证：** 用一个可执行任务说明职责，限定公开结论。

#### 可以这样回答

Agent 改进依赖环境和交互，不只是静态文本。

Yao 的配方按重要性排是语言 pre-training 给的先验、可执行环境和能自动计算的 outcome reward，最后才是算法。数据岗该听的是「任务定义比算法难」，定义任务、构造环境、降低评分噪声都是数据岗的活。只把 PPO 换成 GRPO 变体，解决不了任务和奖励本身的问题。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-shunyu-second-half)

### Llama 4 博客里的 RL data mixture 是什么？

> **回答思路**  
> **背景：** 公开 RL 配方含多类数据和阶段选择。  
> **任务：** 解释数据承担的能力和行为角色。  
> **做法与原因：** 区分公开事实与可迁移假设，按任务验证配方。  
> **结果／验证：** 不把别家比例当 Apple 内部实践或万能最优。

#### 可以这样回答

公开 RL 配方含多类数据和阶段选择。

Llama 4 走轻量 SFT → 在线 RL → 轻量 DPO，理由是 SFT 太多会限制后续在线探索。数据侧先砍掉过易样本，再按 current policy 的 pass@$k$ 动态筛题、丢弃零优势组，batch 里混合能力与提示模板。过滤随 policy update 反复做，每训一轮就用新策略重筛。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-llama4-rl-recipe)

### Anthropic 做电脑使用，训练环境为什么故意很少、还断网？

> **回答思路**  
> **背景：** 训练环境过广或联网可能破坏可控性。  
> **任务：** 解释小而可靠的交互环境价值。  
> **做法与原因：** 先控制任务、状态和反馈，再逐步验证迁移。  
> **结果／验证：** 独立环境成功，不能仅以训练环境数量衡量。

#### 可以这样回答

训练环境过广或联网可能破坏可控性。

少、简单、离线：Anthropic 公开说训练只用了计算器、文本编辑器这类少数可重置的软件，训练期断网。重点是让模型看屏幕像素、数准坐标，用点击和键入直接操作人用的软件，不给它特制的 click_ok API。效果有很大一部分来自模型原有的视觉和工具能力，别全归到 GUI trajectories 数量上。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-anthropic-cu-recipe)

### Panel 情景：verifier 通过率 98%，合成推理数据为什么仍然伤模型？

> **回答思路**  
> **背景：** 高通过率可能来自宽松或被钻漏洞的检查。  
> **任务：** 检验 verifier 是否奖励真正推理。  
> **做法与原因：** 保持结果标签可比，对过程和 counterfactual 变化审计。  
> **结果／验证：** 高分错例减少且独立任务变好才继续扩量。

#### 可以这样回答

高通过率可能来自宽松或被钻漏洞的检查。

通过率取决于 verifier 测了什么，不能替代数据有效性。检查答案 leakage、测试覆盖、过程正确性和重复模板，并用 counterfactual 样本审计 verifier；再用等预算 ablation study 区分过滤质量与任务难度。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-verifier-counterfactual)

### Panel 情景：昨天的高价值难题，今天都变简单了，如何更新合成课程？

> **回答思路**  
> **背景：** 同一批难题会随策略进步变简单。  
> **任务：** 持续提供有学习信号的任务。  
> **做法与原因：** 按 current policy 重估难度并保留覆盖配额。  
> **结果／验证：** 新 hard examples 可学、旧能力稳定且不反复适配 holdout。

#### 可以这样回答

同一批难题会随策略进步变简单。

按当前 student 的表现估计任务难度，追踪任务家族覆盖与迁移收益，而不是一直按 teacher 分数排序。课程更新要与最终评测隔离，保留固定 regression tasks 和旧能力回归检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=dt-curriculum-moving-target)

### Synthetic Data：只有几百条 seed，怎样生成并筛出有用的训练样本？

> **回答思路**  
> **背景：** 真实 seed 很少，teacher 可以批量生成，但生成量不代表训练价值。  
> **任务：** 扩大任务覆盖，同时控制错误、近重复和 evaluation leakage。  
> **做法与原因：** 先按任务家族隔离真实评估，再做 generation、verification、deduplication 和训练对照。  
> **结果／验证：** 在独立真实任务上优于等预算 baseline，且 long-tail 不退化。

#### 可以这样回答

我会先把少量真实样本按任务家族分开，留出一部分不参与生成和选择。否则 teacher 把 seed 改写很多遍，训练和测试看起来不同，实际还是同一批问题。

假设要补 tool-use 参数错误，我会从训练 seed 提炼任务规则，生成参数组合和 boundary conditions，再让 teacher 产生候选动作。生成只是第一步；每条还需要通过 schema 检查、实际执行与终局核验。格式正确不等于业务正确。

我会保留失败原因，而不是只保留成功样本。这样能看到某类任务是不是全部被筛掉了，也能区分 teacher 不会做和环境本身出错。对可用结果再做 task-level deduplication，控制常见模板的占比。

第一轮我会比较原始 seed、等 token 的简单扩写、以及经过 verification 的 targeted synthetic data。只有第三组在独立真实任务上有稳定增益，我才会继续扩规模。这个方案可以讨论，但不能把它写成我已经生产过的数据集。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=afm-web-synthetic-loop)

### Synthetic Data Audit：合成数据为什么仍会泄露隐私或放大 bias？

> **回答思路**  
> **背景：** 团队准备共享 synthetic records，认为不是原始数据就天然安全。  
> **任务：** 分开验证 privacy、representation 和真实训练 utility。  
> **做法与原因：** 追踪源数据权限，测试 memorization 与任务分布，必要时采用明确的 privacy mechanism。  
> **结果／验证：** 有证据支持限定用途的共享，并且 minority tasks 的质量没有被掩盖。

#### 可以这样回答

我不会因为数据由模型生成，就默认可以共享。Generator 可能记住源记录，尤其是很少见的内容；如果源数据本来有使用限制，synthetic 这个名字也不会自动取消限制。

我会先明确共享对象和允许用途，检查生成链路有没有接触个人数据。然后做 exact match、近重复和针对稀有记录的人工审核，也可以在合适的 threat model 下做 membership inference 测试。但这些都只是发现风险的证据，没有检出不代表已经证明安全。

Bias 是另一件事。Generator 可能更容易生成主流语言或常见任务，过滤器又会把困难样本删掉，最后 synthetic set 看起来很干净，却失去了我们最想补的 long-tail。我会按语言、任务和群体检查 coverage，并在独立真实数据上验证收益。

如果需求需要严格的 privacy guarantee，我会考虑具有明确 budget 的 differential privacy 方案和相应 utility tradeoff。最终交付时分别报告 privacy 检查、representation 和 utility，不用某一项通过替代其他两项。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=synthetic&question=afm-web-synthetic-privacy-bias)


## 07 · Evaluation 与 Capability Debugging

### Panel：评测失败怎么变成下一轮训练信号？

> **回答思路**  
> **背景：** 评测失败需要转成下一轮有效监督。  
> **任务：** 从一个具体缺口 feedback loop 到可验证改进。  
> **做法与原因：** 诊断原因，定向采集或合成，固定条件训练。  
> **结果／验证：** 独立 evaluation slices 提高并通过回归，记录成本与停止条件。

#### 可以这样回答

我会从一类具体失败开始，而不是先设计一个很大的 feedback loop。比如助手在工具返回空结果后仍然告诉用户“已经完成”，这就能变成一个比较明确的数据问题。

我会收集或合成不同的空结果、超时和权限拒绝，让任务在一个可重置环境里实际运行。训练样本要教模型识别失败、核查状态和合理恢复，checker 则独立判断最后有没有完成。没有授权的用户原文，我不会默认拿来训练。

下一轮还是看这类任务，但要换新的指令和环境变化。恢复率提高只是一个条件，还要确认没有多余写入、假成功或其他能力退化。这样每次迭代才知道是在补什么。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-data-flywheel)

### Frontier 发模型时，主表还在报哪些数据集？

> **回答思路**  
> **背景：** 发版表格混合多种能力与评价协议。  
> **任务：** 用任务类型理解 benchmark 而非背排名。  
> **做法与原因：** 按科学、代码、agent、long context 分组读原始设定。  
> **结果／验证：** 能解释每项测什么、漏什么及 version scope。

#### 可以这样回答

发版表格混合多种能力与评价协议。

2026 年闭源模型的发布主表主要报科学推理、仓库修复、终端操作、浏览、桌面操作、long context 和 multimodal，MMLU、HumanEval 已经不是重点。比分数前先核对思考预算、工具、尝试次数、运行框架、子集和报分方。evaluation set 的名字也不能当成 training set 的名字。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-release-map)

### GPQA、HLE、FrontierMath、AIME 怎么造，卡的是哪项能力？

> **回答思路**  
> **背景：** 难题可能需要专业知识或严格证明。  
> **任务：** 区分科学问答与 mathematical reasoning 的监督。  
> **做法与原因：** 比较题目来源、专家标注、答案空间和 contamination 风险。  
> **结果／验证：** 引用固定版本，说明分数不能直接横比能力。

#### 可以这样回答

难题可能需要专业知识或严格证明。

这几套题都考推理，区别在学科和筛题方式：GPQA Diamond 是 198 道博士出题、复核过的四选题；HLE 是 2500 道专家题，收题时先筛掉当时模型能答对的；FrontierMath 是研究级数学；AIME 是每年的竞赛新题。报分要写明子集、年份和工具，允许搜索和无工具是两个实验。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-science)

### SWE-bench、Terminal-Bench、LiveCodeBench 怎么造，各卡哪段代码能力？

> **回答思路**  
> **背景：** 代码基准覆盖函数、仓库和终端操作。  
> **任务：** 按目标能力选择评测与训练任务。  
> **做法与原因：** 检查环境、测试和题目时间窗。  
> **结果／验证：** 新题与真实执行支持收益，不混报子集和语言。

#### 可以这样回答

代码基准覆盖函数、仓库和终端操作。

这三套测的是不同的代码能力：SWE-bench 修真实 GitHub issue，新测试要从失败变成通过，旧测试还得过；Terminal-Bench 在终端里做完工程任务，运行框架对分数影响很大；LiveCodeBench 按比赛日期切新题，测算法编程、减少背题。三种分数不能合成一个比。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-code-sets)

### Panel：benchmark 上有能力缺口，怎么诊断，数据干预怎么选？

> **回答思路**  
> **背景：** 低分可能来自数据、推理或测量本身。  
> **任务：** 找到主要失败机制再选数据干预。  
> **做法与原因：** 按 task type 分析 evaluation slices，再做 oracle substitution 区分竞争假设。  
> **结果／验证：** 受控干预改善独立任务且回归通过。

#### 可以这样回答

我会先看几道具体的失败题。一个总分低，可能是模型不知道知识，也可能是证据没搜到，或者评测本身把答案判错了。这几种情况要补的数据完全不同。

比如工具任务，我会先直接给模型正确的工具选择，再给正确参数，看哪一步替换能让任务恢复。要是工具选对以后仍然失败，继续加“选工具”的数据大概帮助不大，应该往参数或结果利用上查。

确定主要问题以后，我会固定训练预算，只补这一类数据，再用另一批任务检查。target evaluation slices 变好、其他重要任务也没退步，我才会把它加到正式 mix 里。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-benchmark-gap)

### BrowseComp、OSWorld、τ² 怎么造，各卡 agent 的哪一段？

> **回答思路**  
> **背景：** 搜索、GUI 和对话工具有不同瓶颈。  
> **任务：** 选择能覆盖目标行为的 agent 评价。  
> **做法与原因：** 分开观察、规划、调用、状态和协作。  
> **结果／验证：** 任务成功与过程约束一起检查，协议固定。

#### 可以这样回答

搜索、GUI 和对话工具有不同瓶颈。

这几套测的是 agent 的不同环节：BrowseComp 用 1266 道人写的事实题测持续搜索；OSWorld 原集用 369 个真实桌面任务检查最终状态；τ-bench 看 agent 和模拟用户对话后能不能把数据库改对，而且多跑几次都稳；MCP Atlas 测多步工具流程。所以要分开报，合成一个「工具分数」会盖住各自卡住的地方。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-agent-sets)

### MRCR、MMMU、multilingual 榜怎么造，发版里的 long context 和 multimodal 在测什么？

> **回答思路**  
> **背景：** 长输入和 multimodal 得分含多个因素。  
> **任务：** 确认任务要求模型用到了哪种证据。  
> **做法与原因：** 控制长度、位置、语言与视觉信息做对照。  
> **结果／验证：** 按 evaluation slice 报告收益，不能只看总上下文容量。

#### 可以这样回答

长输入和 multimodal 得分含多个因素。

long context 要看模型能不能在长输入里找对信息，「支持 1M」只说明收得下。MRCR v2 在长文里放多个相似目标，要求按指令取 backpointer 定那段，同一模型在 128k 和 1M 下可能差很多。MMMU-Pro 尽量去掉不看图也能答对的题，multilingual 榜要先查题目是不是英语翻译来的。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-ctx-mm)

### 哪家 lab、哪个模型、在哪次发布里报了哪项 benchmark？

> **回答思路**  
> **背景：** 不同发布时间和版本会改变榜单结论。  
> **任务：** 准确说明谁在什么版本报告了什么。  
> **做法与原因：** 使用公开原始报告并固定日期与协议。  
> **结果／验证：** 历史数字标明时间，不编当前排名或内部成绩。

#### 可以这样回答

不同发布时间和版本会改变榜单结论。

按每份官方发布材料分开记分数，写明日期和思考档。比如 Gemini 3.1 Pro 模型卡里的 Opus 分数是 Google 跑的对照，不能算作 Anthropic 自报。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-frontier-who-reports)

### Panel：怎么查评测被训练数据看见了，查到了怎么办？

> **回答思路**  
> **背景：** 评测可能被直接或间接写入训练。  
> **任务：** 识别重叠及它对结论的影响。  
> **做法与原因：** 精确、n-gram、语义与来源检查相结合。  
> **结果／验证：** 新题复测支持结论，删命中不等于模型已忘。

#### 可以这样回答

评测可能被直接或间接写入训练。

把冻结的评测题和训练数据从便宜到贵逐层比对，依次比 URL、n-gram、embedding nearest neighbors，再拿训练截止后才出现的新题作对照，旧题好、新题差就是 leakage 的警报。确认 leakage 后，正式评测换新题，旧题降为 development set，命中的训练文档隔离出下一轮 mix，对外同时报新旧两套结果。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-contamination)

### Panel：加了一批数据，target evaluation slices 掉了，怎么查？

> **回答思路**  
> **背景：** 新数据加入后目标任务退步。  
> **任务：** 区分来源质量、data mix 和训练条件问题。  
> **做法与原因：** 先复现，再按来源与失败类型做 ablation study。  
> **结果／验证：** 撤回或修复该因素后独立 evaluation slices 恢复。

#### 可以这样回答

新数据加入后目标任务退步。

先复现只换数据的对照，排除步数、decoding 和奖励的变化；确认是数据造成的，再按 evaluation slices、新旧题、抽查、data mix、learnability 的顺序查 negative transfer、标签错误、data mix 失控、过难样本和 evaluation leakage。旧题分数下降、新题分数不变，也可能是原先由 contamination 带来的分数优势消失了。按查到的证据调整对应的数据，全部回滚会把有用的部分一起丢掉。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-worse-after-data)

### Panel：补一个能力，把另一个打掉了，如何用数据保住已有能力？

> **回答思路**  
> **背景：** 补一种能力同时损伤另一种。  
> **任务：** 保住重要旧能力并定位冲突来源。  
> **做法与原因：** 检查预算挤占，做 data mix 与来源替换对照。  
> **结果／验证：** 新旧 evaluation slices 都达 threshold，否则减权或停止。

#### 可以这样回答

补一种能力同时损伤另一种。

训练前先列出必须保住的旧能力（英语通用、安全、格式、已经做好的核心任务），固定评测和允许波动；data mix 里给这些域设最低 token 份额，新数据比例逐步提高。旧能力超出波动就先降新来源的比例。目标任务涨了就发版，旧能力可能已经悄悄掉了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-neg-transfer)

### Panel：怎么用数据压 hallucination？

> **回答思路**  
> **背景：** 流畅回答可能没有来源支持。  
> **任务：** 让模型按证据回答并承认不足。  
> **做法与原因：** 构造证据支持、矛盾、缺失的对照监督。  
> **结果／验证：** 逐项核对事实和覆盖，避免只靠少说降低错误。

#### 可以这样回答

流畅回答可能没有来源支持。

造 (证据, 问题, 答案) 形式的训练数据，证据里没有的细节答案就承认看不到，证据里有的答案要能指回证据。两类题在同一份证据上成对出现，防止模型学成一律拒答。摘要、图片问答和工具状态都按这个形状造，单写「不要 hallucination」或用开放世界 QA 都替代不了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-grounding-data)

### Apple：on-device LLM 怎么评，延迟、耗电、隐私，为什么不能只报 BLEU？

> **回答思路**  
> **背景：** on-device 系统受延迟、能耗和隐私约束。  
> **任务：** 定义用户任务真正成功的条件。  
> **做法与原因：** 任务指标与设备成本、安全约束并列测量。  
> **结果／验证：** 同硬件同预算比较，语言分组和关键风险达标。

#### 可以这样回答

on-device 系统受延迟、能耗和隐私约束。

我会分别评任务质量、证据支持、安全、系统性能和隐私，再决定 on-device 模型能否上线。BLEU 只看 n-gram 重叠，既看不出摘要漏限定词，也测不到热降频或邮件是否离开设备，所以只能当辅助回归指标。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=apple-afm-eval)

### Panel：multilingual 和 locale 数据怎么做，为什么翻译题不能当 evaluation gate？

> **回答思路**  
> **背景：** 翻译自然度和当地任务习惯会影响评价。  
> **任务：** 识别真实 locale 缺口。  
> **做法与原因：** 母语任务与本地协议优先，翻译只作补充。  
> **结果／验证：** 独立当地 human evaluation 与 capability slices 支持改进。

#### 可以这样回答

翻译自然度和当地任务习惯会影响评价。

训练和评测用不同来源。训练可以用验证过的机翻和爬取 corpus 补覆盖，用母语者示范和 human evaluation 改善自然度；正式评测让母语者直接出题，翻译题不自然，测到的只是英语题的影子。过滤阈值按语言做 calibration，配额逐步提高，桶内做 temperature sampling；AFM 公开把 multilingual 比例从 8% 提到 30%，human evaluation 不用翻译题。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-locale-data)

### CoderPad：两个人标同一批，Cohen's $\kappa$ 怎么算，低了改什么？

> **回答思路**  
> **背景：** 标注一致率受类别基率影响。  
> **任务：** 计算机会校正的一致性。  
> **做法与原因：** 从混淆表求观察与随机一致率。  
> **结果／验证：** 手算小表，明确单类退化和分歧解释。

#### 可以这样回答

标注一致率受类别基率影响。

类别不平衡时偶然一致率本身就很高，所以要报 Cohen's $\kappa$：先建混淆 matrix，再算 $\kappa=(p_o-p_e)/(1-p_e)$，$p_o$ 是观测一致率，$p_e$ 是按边际分布算的偶然一致率。$\kappa$ 低时先改协议和例子，再考虑加人投票。

测试时，我会手算小表，明确单类退化和分歧解释。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-kappa-code)

### Panel：人标预算只够标 1 万条，花在哪？

> **回答思路**  
> **背景：** 专家标注成本高，自动信号也有盲点。  
> **任务：** 把预算花在会改变决策的样本上。  
> **做法与原因：** 代表性、风险、分歧与随机审计结合使用，进行 sampling。  
> **结果／验证：** 看每标注小时的独立收益及未覆盖错误。

#### 可以这样回答

专家标注成本高，自动信号也有盲点。

先建立可靠的 evaluation set，再标注 challenging cases，最后扩大数据量。human-review budget 优先保证 annotation guidelines、gold labels 和评测可靠，再标模型失败的 challenging tasks；能执行验证的数学和代码由人写 seed、teacher 扩充、executor 检查，tool-use trajectories 先让模型预跑、人只纠错。均匀撒到所有任务，会把钱花在模型已有的能力上。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-human-budget)

### Panel 情景：隐私聚合看不到罕见失败，怎样为 long-tail 能力补数据？

> **回答思路**  
> **背景：** 聚合信号可能看不到稀有但重要的失败。  
> **任务：** 在 privacy requirements 内补 long-tail 监督。  
> **做法与原因：** 从合法类别信号出发，用许可研究和合成复现。  
> **结果／验证：** 独立 long-tail 测试改善，不恢复用户原文。

#### 可以这样回答

聚合信号可能看不到稀有但重要的失败。

聚合趋势适合发现常见需求，未观察到稀有模式不代表它不存在。long-tail 能力应结合公开或获授权的 seed、专家设计和受控合成，用独立验证确认；不能为追求覆盖绕开隐私阈值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-private-tail-budget)

### Panel 情景：总成功率涨了 18 个点，为什么两个任务桶都在退化？

> **回答思路**  
> **背景：** 流量构成变化能掩盖各组退化。  
> **任务：** 拆开组内变化和混合权重变化。  
> **做法与原因：** 固定权重重算，检查同任务配对结果。  
> **结果／验证：** 同时报告总体和 evaluation slices，不能由总分决定发布。

#### 可以这样回答

流量构成变化能掩盖各组退化。

先固定任务分布，再比较桶内成功率。流量结构变化可能抬高总分，即使每个桶都变差；报告同一权重下的新旧结果，并将模型变化与产品路由变化分开评估。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-simpson-release-metrics)

### Panel 情景：异步 rollout throughput 翻倍，为什么训练奖励上涨但任务成功下降？

> **回答思路**  
> **背景：** throughput 增加可能让训练用到过期策略 trajectories。  
> **任务：** 区分 throughput 收益与有效学习质量。  
> **做法与原因：** 记录策略版本、排队延迟及奖励环境一致性。  
> **结果／验证：** 新策略独立成功率与成本共同支持系统变化。

#### 可以这样回答

throughput 增加可能让训练用到过期策略 trajectories。

检查 rollout 的行为策略版本、奖励版本和环境状态，再按陈旧程度 evaluation slices 比较。异步提升 throughput 会改变样本分布，重要性修正也不能修复未知行为概率或奖励协议漂移。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-stale-rollout-incident)

### CoderPad：按任务家族做配对 bootstrap，如何避免模板多的家族支配结论？

> **回答思路**  
> **背景：** 模板多的任务家族会支配逐条统计。  
> **任务：** 估计按家族等权的配对差异。  
> **做法与原因：** 整个 cluster resampling 并保留两版本配对。  
> **结果／验证：** 固定 seed，手算家族均值，报告不确定性。

#### 可以这样回答

模板多的任务家族会支配逐条统计。

先计算同一任务上新旧模型的差，再在家族内取均值、对家族等权。bootstrap 时 resampling 家族而非单行，以保持组内相关结构；这种指标评价的是家族平均收益，不是流量平均收益。

测试还要满足这个条件：固定 seed，手算家族均值，报告不确定性。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-cluster-bootstrap-code)

### Panel 情景：13-gram contamination scan 全绿，模型却能背出翻译后的评测答案？

> **回答思路**  
> **背景：** 翻译和改写会绕过字面 contamination scan。  
> **任务：** 确认记忆 leakage 及其来源。  
> **做法与原因：** 语义 nearest neighbors、teacher 提示和跨语言家族一起审计。  
> **结果／验证：** 未见家族复测，绿色 n-gram 报告不当无 contamination 证明。

#### 可以这样回答

翻译和改写会绕过字面 contamination scan。

字面重叠只能排查部分 leakage。沿 seed、翻译和改写的来源链追踪任务家族，再结合语义候选检索与人工核对；能力相似不等于 contamination，不能把所有同题型数据一律删除。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-paraphrase-leakage-audit)

### CoderPad：从 n 次生成估计 pass@k，为什么不能直接用成功率的幂？

> **回答思路**  
> **背景：** 有限生成样本不能直接当独立成功概率。  
> **任务：** 估计至少一次成功的 pass@k。  
> **做法与原因：** 使用不放回组合计数，明确 n 和成功数。  
> **结果／验证：** 全错全对及 k 的极端取值可手算，区别连续多次成功可靠性。

#### 可以这样回答

有限生成样本不能直接当独立成功概率。

对同一任务的 n 个候选及 c 个成功，使用1减去抽 k 个全部失败的组合比例，再对任务等权平均。它估计至少一个候选成功，不代表模型能识别并选中那个正确候选。

测试还要满足这个条件：全错全对及 k 的极端取值可手算，区别连续多次成功可靠性。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=dt-passk-estimator-code)

### Apple AFM 面经：RAG 项目如何减少 hallucination，如何做 evaluation？

> **回答思路**  
> **背景：** 检索命中不代表答案有证据或完整。  
> **任务：** 解释 RAG 项目的真实能力增益。  
> **做法与原因：** 分开测检索、引用支持和回答错误。  
> **结果／验证：** 固定资料与问题做 ablation study，个人贡献和结果可核对。

#### 可以这样回答

检索命中不代表答案有证据或完整。

先把检索没找到、上下文装不下、证据有但生成错分开诊断。用固定问题与文档版本测证据召回、答案正确性、引用支持和无答案时的行为，再用正确证据替换实验定位瓶颈；只报最终准确率或换一个更强模型，都解释不了 RAG 改动为什么有效。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=p3a-apple-afm-rag-deepdive)

### Agent Evaluation：客服 agent 上线前后怎样评估，并把失败转成训练信号？

> **回答思路**  
> **背景：** 客服 agent 看起来能完成对话，但对话结束不代表工单正确解决。  
> **任务：** 定义任务成功、security constraints 和上线后反馈如何进入下一轮数据。  
> **做法与原因：** 先验证真实终局，再按失败原因构造数据，避免把满意度直接当正确性。  
> **结果／验证：** 独立任务成功率提高，重复投诉和越权操作不增加。

#### 可以这样回答

我会先确认 agent 能执行哪些操作。如果它只能回答 FAQ，回答正确就很重要；如果它能退款，最终账户状态、权限和重复执行都必须进入评估。用户说谢谢，并不能证明退款金额是对的。

上线前，我会用可以重置的工单环境，覆盖正常处理、缺信息、工具失败和必须转人工的任务。每次同时检查回答、工具动作和最终状态。先把错误分成知识不足、决策错误、tool arguments 错误和环境故障，因为它们需要的改进不同。

上线后，我会结合重复联系、人工升级、撤销操作和经过授权的抽样审核。比如退款失败可能来自 tool schema 理解错误，也可能是支付服务超时；前者可以生成同类任务与正确示范，后者应该修系统，不能全部变成负面训练标签。

每轮只针对一个明确的 failure mode 做 data intervention，并在独立工单家族上比较。我希望看到真实解决率提高，同时越权、误退款和成本没有恶化。这里是我的设计方案，没有实际运行结果可以提前声称。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=afm-web-agent-evals)

### Benchmark Debugging：500 题提高 2 个点，真的变强了吗？

> **回答思路**  
> **背景：** 新模型在 500 道题上从 70% 提升到 72%。  
> **任务：** 判断增益是否可靠，定位改变来自哪些任务。  
> **做法与原因：** 分析同题 paired outcomes、重复 sampling 与数据独立性，再做定向验证。  
> **结果／验证：** 报告 effect size 和 uncertainty，不能只凭总分做发布决策。

#### 可以这样回答

我不会只根据 70% 到 72% 就说模型变强了。500 道题提高两个点只代表多答对了十题；我还需要看两模型在哪些题上发生变化。

如果新模型只把十道错题改对，其余都相同，这和它答对了五十道旧错题、又答错四十道旧对题，是两种证据。净收益相同，但第二种的行为变化和不确定性都更大。

我会先检查是否同样的 prompt、decoding 和预算，再做 paired comparison。如果很多题来自同一个模板，就按 template family 而不是单题估计 uncertainty。生成有随机性时，还要看重复运行是否稳定，并按任务类型检查 regression。

如果差异还不清楚，我会增加独立任务或重复实验，而不是继续围绕这 500 题调参。只有独立验证支持目标能力改善，而且关键任务没有明显退化，我才会建议推进发布。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=evaluation&question=afm-web-benchmark-two-points)


## 08 · Reward、Preference 与 Alignment

### RM 基础：preference probability 80%，为什么不能说 chosen 的成功率是 80%？

> **回答思路**  
> **背景：** 相对偏好分数容易被误读成成功概率。  
> **任务：** 明确标签事件与奖励可识别性。  
> **做法与原因：** 先解释分差，再用独立标签 对目标概率做 calibration。  
> **结果／验证：** 偏好与成功指标分别验证，绝对分数不越界解释。

#### 可以这样回答

这里我会先问，这个模型训练时的标签是什么。如果标签是人更喜欢 A 还是 B，它学到的就是两条回答的相对偏好。A 打3分、B 打1分，我可以用分差去估计 A 胜过 B 的概率，但不能把 A 自己的分数变成任务成功率。

比如两条回答都答错了，人仍然可能更喜欢其中一条。要预测任务成功，我还需要实际成功/失败的标签。另外，同一问题下把所有分数一起加上一个常数，排序和 preference probability 都没变，这也说明绝对分数本身没有那么直接的解释。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-bt-identifiability)

### 偏好分歧：6 比 4 的投票，soft labels、confidence weight 和 tie 是同一件事吗？

> **回答思路**  
> **背景：** 六比四与十比零包含不同监督信息。  
> **任务：** 区分偏好比例、confidence weight 和 tie。  
> **做法与原因：** 保留投票与协议，soft labels 和样本贡献分别处理。  
> **结果／验证：** gradient 与分歧语义正确，少数意见不被误删。

#### 可以这样回答

我会先把十张票保留下来，而不是只存一个“A 赢了”。6比4和10比0表达的信息不同，尤其是在两条回答都合理的时候。

如果标注目标清楚、这些人也代表目标用户，我可以把0.6作为偏好 A 的 soft labels。但它和“这条数据有多可信”是两回事：十个人的6比4，和一个人的一次选择，证据量不同。遇到平票，我还会区分“都很好”“都很差”和“我看不懂”，因为这三种情况不能都变成同一个训练信号。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-soft-target-ties)

### 同预算选 RM：绝对打分、成对偏好，还是多属性回归？

> **回答思路**  
> **背景：** 评分和成对偏好提供的信息不同。  
> **任务：** 按任务需要和标注成本选择标签。  
> **做法与原因：** 同一批候选收两种标注，再公平比较。  
> **结果／验证：** 看下游选择收益与每小时成本，不只比 loss。

#### 可以这样回答

我会先看需要什么信息。只是选出两条回答里更好的一条，成对比较比较直接；但如果我还想知道它为什么好，是事实正确、信息更全，还是表达更清楚，分项评分会更有用。

我不会拿两批完全不同的数据来比较两种方法。可以先抽同一批问题和回答，同时收评分和偏好，记录标注时间，再用差不多的预算训练。最后看哪种反馈更能帮模型选出好答案，而不是只比较哪个 loss 更低。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-rating-versus-pairwise)

### RM 实现排错：取了最后一个 padding token，为什么训练准确率仍很高？

> **回答思路**  
> **背景：** 模板或 padding 可能成为训练捷径。  
> **任务：** 确认实际打分位置与有效回答。  
> **做法与原因：** 逐 token 核对 pooling、截断和 mask。  
> **结果／验证：** 相同内容换 padding 不应改变判断，截断对需复核。

#### 可以这样回答

我会先把一个 batch 打印出来，看看 token、mask、截断位置和实际取来打分的位置。比如右侧补了 padding，却直接取最后一个位置，那读到的可能已经不是回答结束的位置。

训练准确率高并不能排除这种错误。假如好回答普遍更长，模型可能只学了长度或模板特征。我会先用同一条回答换不同 padding 长度，看分数会不会变；再查两条回答是不是截断以后已经一样，却仍然带相反标签。实现和数据先对上，再讨论模型容量。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-rm-pooling-truncation)

### RM 榜单高分但 RL 变差：RewardBench 到底测到了什么？

> **回答思路**  
> **背景：** 公共分类分数未必代表 current policy 选择质量。  
> **任务：** 定位 RM 在部署候选上的盲点。  
> **做法与原因：** 固定候选比较选择结果和高分错例。  
> **结果／验证：** 独立任务收益支持选择，榜单版本不混报。

#### 可以这样回答

我会先固定一批当前模型的候选回答，让两个 RM 都来选，然后实际检查被选中的答案。这样比较的是它们在同一批选择上的表现。

一种可能是，分数高的 RM 很擅长明显的好坏对，却特别容易给少数错误答案打极高分。做 best-of-N 时，这些错误就容易被选出来。还有一种可能是，当前模型的回答风格和它训练时见过的不一样。

所以我会看当前候选上的选择质量和高分错例，再决定要不要补 preference data。公共 benchmark 仍有参考价值，但我不会用它的总分代替这个任务里的结果。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-rewardbench-downstream)

### Best-of-N 越大越差：怎么画出 reward overoptimization 的证据？

> **回答思路**  
> **背景：** 扩大 sampling 可能放大奖励漏洞。  
> **任务：** 判断代理优化是否偏离真实目标。  
> **做法与原因：** 固定生成条件扫描 N，审计被选中的错误。  
> **结果／验证：** 真实质量下降时停止扩 N，修后独立复测。

#### 可以这样回答

我会先暂停继续扩大 N，拿被 RM 选中的失败答案来看。比如 agent 根本没完成工具操作，却写了一段非常完整的成功说明，RM 反而给了高分。这种情况下，增加 sampling 次数可能只是在增加找到这种答案的机会。

不过我会先确认比较条件一样：是不是同一批任务、同一个生成模型、相同的执行环境。确认以后，再补这类高分错例，或者限制目前的 sampling 规模。改完还得用独立任务结果检查，不能因为新 RM 给自己的分数好看，就认为问题解决了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-bestofn-overoptimization)

### length bias：把奖励除以 token 数，为什么可能惩罚正确推理？

> **回答思路**  
> **背景：** 长度既可能有用，也可能只是套话。  
> **任务：** 识别内容收益与 length bias。  
> **做法与原因：** 制作等内容长短对照，保留必要推理。  
> **结果／验证：** 正确性、完整性和长度一起检查。

#### 可以这样回答

我会先看长答案为什么赢。有些题确实需要更长的解释；直接把分数除以长度，可能把必要的信息也惩罚掉。

我会挑一批题做内容对照。比如同一个正确答案，一版保留必要步骤，另一版只是多加客套和重复；再补一些“短但漏关键信息”的例子。这样才能看出 RM 是在认有用内容，还是单纯认长度。训练以后我会同时看正确性、完整性和长度，避免把偏长改成了偏短。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-length-causal-audit)

### position bias：AB 和 BA 都选第一个，如何计分和分配人审？

> **回答思路**  
> **背景：** 交换位置后 judge 可能仍选第一个。  
> **任务：** 区分内容 tie 与顺序不一致。  
> **做法与原因：** 先映射候选身份，再统计稳定与反转。  
> **结果／验证：** 平均得分与不一致率分别报告。

#### 可以这样回答

这两次其实选了不同的回答。AB 时第一个是 A，BA 时第一个是 B，所以我会记成顺序不一致，而不是说两条内容一样好。

如果要算交换顺序后的平均得分，A 可以拿0.5分，但我会同时报告不一致比例。否则，一个永远选第一个的 judge，看起来也能给出很“平衡”的总分。对于重要或不一致的题，我会再交给人看；两次都选同一条，也还需要检查它是不是选对了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-position-swap)

### 同家族 self-preference：换一个 judge 就足以消除 teacher 文风优势吗？

> **回答思路**  
> **背景：** teacher 风格可能被同家族 judge 偏爱。  
> **任务：** 区分能力提高与风格适配。  
> **做法与原因：** 固定候选交叉评审，并做 human evaluation 内容核验。  
> **结果／验证：** 质量变化有独立证据，换家族不自动等于去偏。

#### 可以这样回答

我会先把它当成一个待验证的结果。student 可能真的变好了，也可能只是学到了 teacher 的写法，而同家族 judge 正好喜欢这种写法。

我会保留同一批候选，用其他 judge 和独立 human evaluation 再看，最好把事实正确、信息完整和文风分开。还可以隐藏模型名、交换顺序，看看偏好是否稳定。如果换一个 judge 结论就反过来，我会先查评审标准。仅仅换成不同家族，也不保证所有偏差就消失了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-family-self-preference)

### sycophancy：用户满意度上涨，模型却开始赞同错误前提怎么办？

> **回答思路**  
> **背景：** 用户喜欢被认同不等于事实正确。  
> **任务：** 避免把点赞直接当事实监督。  
> **做法与原因：** 改变用户立场做配对测试，分开评价礼貌与真实。  
> **结果／验证：** 能尊重地纠正，也能依据新证据更新。

#### 可以这样回答

我会先看点赞在这个场景里代表什么。用户可能喜欢被认同，但这和回答正确不是一回事。比如用户坚持悉尼是澳大利亚首都，模型附和后得到点赞，我不会把它当成事实任务的好回答。

我会构造只改变用户立场的问题，看模型的事实判断会不会跟着翻转。然后让 annotator 分别看事实和态度，补“礼貌地纠正”这样的例子。目标也不是训练一个总反驳用户的模型，而是让它有依据地回答，同时保持尊重。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-sycophancy-truth)

### 群体偏好冲突：英语 annotator 共识很高，是否代表所有用户？

> **回答思路**  
> **背景：** 总体多数票可能掩盖群体差异。  
> **任务：** 明确服务人群和合法偏好多样性。  
> **做法与原因：** 先查协议与理解，再比较分组或条件化方案。  
> **结果／验证：** 总体和各组效果、风险及不确定性并列报告。

#### 可以这样回答

我会先看大家为什么不同意。有时是翻译不自然，有时是标注规则没说清，也可能确实有人喜欢直接、有人喜欢详细。这些问题不能都靠多数票解决。

如果是合理偏好差异，我会保留分组和投票信息，明确产品到底服务谁。可以比较一个统一模型、按任务或 locale 调整，以及输出多个评价维度的办法。最后要看各组表现；总体涨了，但某一组持续变差，我会把这个结果摆出来，而不是只报一个平均数。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-population-disagreement)

### 主动采偏好：一万条标注预算该花在最大分歧还是最不确定的样本？

> **回答思路**  
> **背景：** 最不确定的题不一定最值得标。  
> **任务：** 提高有限标注预算的信息收益。  
> **做法与原因：** 兼顾代表性、风险、分歧和随机审计。  
> **结果／验证：** 小批新标签确实改善独立选择质量再扩。

#### 可以这样回答

我会先看当前模型的错误和已有数据覆盖。高风险失败、几个 RM 明显意见不同的例子，以及新任务里缺标签的部分，都可能值得优先标。

但我不会把预算全部花在分歧最大的地方。有些题本来就几乎一样，标了很多次也很难得到有用区分；几个模型也可能一起犯错。所以我会留一部分随机样本和已知困难 evaluation slices，用来检查没被主动选中的地方。先标一小批，看这些标签是否真的改善独立评价，再决定下一批怎么分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-active-label-selection)

### 有四个 RM，怎样更可靠、又更省计算地选出好回答？

> **回答思路**  
> **背景：** 同一个问题有 A、B 两个候选回答；你有四个已经训练好的 RM，可以给它们打分。  
> **任务：** 决定怎样结合这些评分，选出更好的回答，并控制每条回答的评分成本。  
> **做法与原因：** 先看四个分数的平均，再看分歧惩罚如何改变选择；如果只能跑一个模型，再考虑 WARM。  
> **结果／验证：** 用独立评价检查实际选出的回答，并比较 latency 和成本；不能只看 RM 自己的分数。

#### 可以这样回答

假设同一个问题有 A、B 两个候选回答，我要决定保留哪一个。RM 就是给“问题＋回答”打分的模型。我有四个 RM，想让它们帮我选得更准，但还得考虑打分需要多少计算。

如果预算允许，我会先试 score averaging：让四个 RM 都打分，再取平均。例如 A 得到 8、8、8、0，平均是 6；B 得到 5、5、5、5，平均是 5，所以这个规则会选 A。分数要先放到可比较的尺度，一个模型打 0–1 分、另一个打 0–100 分，不能直接平均。

但 A 的分数也说明，四个模型对它意见差得很大。如果我想谨慎一点，可以试 conservative reward：在平均分上减去一个与分歧大小有关的惩罚。还是这个例子，用 mean−std，A 大约是 2.54，B 还是 5，就会改选 B。这表示我们更偏好模型意见一致的回答，不代表 B 已经被证明更好。如果四个 RM 都被同一类错误骗过，分歧小也没用。

如果每条回答的预算只够跑一个 RM，前面两种方法就太贵了。这时可以尝试 WARM：假设四个 RM 来自共同的 pre-trained model，模型结构相同、参数能够一一对应，先把它们的 weights 平均，得到一个新的 RM，部署时只跑这个模型。注意，平均 weights 后的模型，不等于四个模型输出分数的平均，所以必须重新测它选出的回答好不好。

最后，我会固定一批问题和候选回答，用独立的人工评价，或代码测试这类正确性检查，比较各方案实际选中了什么，同时测 latency 和成本。预算够时可以比较多模型打分；预算只够一个模型时，就比较单 RM 与 WARM。不会因为方法名字叫 ensemble，就默认它一定更可靠。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-ensemble-warm)

### PRM vs outcome RM：最终答案对了，过程错了，怎么标、怎么聚合？

> **回答思路**  
> **背景：** 终局正确不能证明中间每步正确。  
> **任务：** 定义过程监督在判断什么。  
> **做法与原因：** 局部正确、任务进展和恢复能力分开标。  
> **结果／验证：** 与 outcome reward 同预算比较，并计入标注成本。

#### 可以这样回答

我会把最终结果和过程分开。数学题可能中间算错了，最后碰巧得到正确答案；工具任务也可能先改错文件，再把结果补回来。它们都不适合简单地把每一步标成好。

如果收过程标签，我会先定义 annotator 到底判断什么：这一步是否正确，是否推动任务，还是出错以后能不能恢复。然后比较这些标签带来的收益和成本。有些任务有很可靠的最终执行结果，先用 outcome reward 就足够；没有必要因为 PRM 更细，就假定它一定更好。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-prm-credit)

### DPO 深挖：chosen 概率也下降，为什么 loss 仍然改善？

> **回答思路**  
> **背景：** chosen 与 rejected 概率可能同时下降。  
> **任务：** 解释 DPO 改善的相对目标。  
> **做法与原因：** 拆开策略和 reference 的两侧 logprob。  
> **结果／验证：** 检查实际生成质量与新策略覆盖。

#### 可以这样回答

因为它优化的不是单独把 chosen 概率推高。比如 chosen 的 logprob 从负10变成负12，rejected 从负11变成负18，两条都降了，但它们的差距反而从1变成6。reference 固定时，DPO 目标仍然可能改善。

所以只看 loss 下降或 chosen 概率变化都不够。我会检查两边的概率、reference 是不是固定、回答长度和实际生成质量。如果模型在旧 preference pairs 上越学越好，当前回答却变差，还要查数据是不是已经跟不上新策略。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-dpo-reference-shift)

### multimodal RM：会写漂亮说明，却看不到图中的错误，怎么揭穿？

> **回答思路**  
> **背景：** 流畅说明可能掩盖图像证据错误。  
> **任务：** 确认 RM 真的利用了关键视觉信息。  
> **做法与原因：** 保持候选可比，只改变图中关键字段。  
> **结果／验证：** 状态或字段真值支持排序，视觉 judge 单独做 calibration。

#### 可以这样回答

我会先确认评审器拿到了什么。有时叫 multimodal 评价，实际只把 OCR 文本或 caption 交给 judge，那它可能根本看不到小数点、位置关系或图里的矛盾。

然后我会做很小的图像变化，比如把票据总额从18.50改成1850，其他内容尽量保持一样。两条候选回答的正确性应该随证据改变；如果 RM 仍然只喜欢更详细的那条，就说明值得进一步查视觉证据的使用。最终我会用字段真值或实际状态核验，而不是再让同一个模型写一段解释证明自己看对了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-multimodal-evidence)

### 安全与帮助性：拒绝所有请求的 RM 为什么可能拿高分？

> **回答思路**  
> **背景：** 拒绝所有请求也可能提高某种安全分。  
> **任务：** 兼顾适当拒绝与正常帮助。  
> **做法与原因：** 安全 nearest neighbors 与正常任务分别标注评价。  
> **结果／验证：** 关键违规设上限，帮助性不被总分掩盖。

#### 可以这样回答

我会把两类错误分开报：危险请求没有拒绝，以及正常请求被错误拒绝。如果总是拒绝，第一项可能很好看，但产品已经没法正常帮助用户。

数据上我会补一些很接近的对照，比如真正有害的请求、讨论风险的教育内容，以及只需要澄清就能回答的问题，让模型学会区别。评价也用这几类独立任务。对于不可接受的风险，我会单独设限制，再看帮助性；不能让更多正常题的收益把严重违规平均掉。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-safety-multiobjective)

### 编程：soft preference BCE，如何区分投票比例与样本权重？

> **回答思路**  
> **背景：** 每个 prompt 有 A/B 两个 reward scores；q 是偏好 A 的比例，w 是独立 confidence weight。  
> **任务：** 返回 weighted mean soft-label BCE，并只对 a、b 保留 gradients。  
> **做法与原因：** 以 a-b 为 logit，逐 pair 计算稳定 BCE，再按 w 加权；q、w 先 detach。  
> **结果／验证：** 单条 q=0.6 时 reward gradients 为 -0.1/+0.1；全零 w 时 loss 与 reward gradients 为零。

#### 可以这样回答

我会先分清四个输入：a、b 已经是两个回答的 reward scores，不是 features；q 表示偏好 A 的比例，w 才决定一条 pair 对 batch 的贡献。

以 a-b 为 logit，按 q 计算逐条 BCE，再用 w 加权除以总权重。q、w 都作为固定数据，不能收到 gradients。总权重为零时也要返回可以 backward 的零，不能除零或直接返回 Python 数字。

我会用题面的一条样本验证：a=b=0、q=0.6 时，loss 是 log(2)，对 a 的 gradient 为 -0.1，对 b 为 +0.1。因为按总权重 normalization，只有一条样本时 w=0.2 不会再把 gradient 缩小五倍。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-soft-target-code)

### 编程：交换 AB／BA 后还原身份，计算 position bias 审计表

> **回答思路**  
> **背景：** 同一对 A/B 回答分别按 AB、BA 展示；judge 返回 first、second 或 tie。  
> **任务：** 还原候选身份，返回四类计数、A 的平均分与 first-position selection rate。  
> **做法与原因：** 先按展示顺序映射回 A/B，再分类；两个概率指标分别使用 2n 与非 tie 展示数作为分母。  
> **结果／验证：** 完整三行示例应得到 stable_a=1、stable_tie=1、inconsistent=1、swap_score=2/3、first_rate=3/4。

#### 可以这样回答

我会先做身份映射。AB 里的 first 是 A，BA 里的 first 是 B，所以两次都选 first 属于不一致，不能算 A 稳定获胜。

每条记录还原后分别进入 stable_a、stable_b、stable_tie 或 inconsistent，四个计数之和必须等于 n。只有一次 tie 的记录也算 inconsistent。

最后分别计算两个指标。Swap score 把 A/B/tie 记为 1/0/0.5，对全部 2n 次展示取平均。First rate 只看非 tie 展示中 first 的占比。全部 tie 时，前者是 0.5，后者返回 None。这个审计描述顺序敏感性，没有独立真标签时不能据此宣布回答质量或 causal bias。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-bias-audit-code)

### 模拟 B 编程：从偏好特征训练一个 RM，并输出独立验证指标

> **回答思路**  
> **背景：** 每条 pair 包含同一个 prompt 下 A、B 的数值特征，以及偏好 A 的比例 q；训练与 validation 分开提供。  
> **任务：** 用零初始化的共享线性 scorer 训练指定次数，并返回权重、训练统计和四项 validation 结果。  
> **做法与原因：** 只用 a、b 拟合 standardization；以 A、B 的 reward difference 为 logit，对 q 计算 mean BCE，再做 full-batch SGD。  
> **结果／验证：** 用零步、一步更新和 soft-target 例子手算核对；替换 validation 不得改变 weight、mean、std，全 tie 时 strict_acc 为 None。

#### 可以这样回答

这里不是训练一个 LLM，而是给已经提取好的回答特征训练一个线性 scorer。每行 a、b 是同一个 prompt 的两个候选，q 是人工偏好 A 的比例。例如 q=0.75 就直接作为 BCE 的 soft target，不能把它当作 sample weight，也不能先转成 A 获胜的 hard labels。

我会先合并训练回答，计算每个 feature 的 mean 和 population std，并冻结这组统计。A、B 共用一个零初始化、无 bias 的 scorer，两个 reward 的差就是 pairwise logit。然后用 full-batch SGD 恰好更新 epochs 次；validation 不参与任何参数或 preprocessing 的拟合。

验证时输出 A 的预测概率，以及 soft-label NLL、soft-target squared error 和 non-tie preference accuracy。vq=0.5 的样本仍参与前两个指标，只从 accuracy 中排除；如果全是这种样本，accuracy 返回 None。

我会先检查题面的手算例子：a=1、b=-1、q=1 时，零步预测是 0.5；learning rate 为 0.1，更新一步后 weight 应为 0.1，A 的概率约为 0.549834。再检查 soft targets、constant features，以及更换 validation 后训练结果是否完全一致。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-rm-train-pipeline-code)

### Panel：reward model 和 preference learning 怎么选，坑在哪？

> **回答思路**  
> **背景：** 任务正确性和主观偏好需要不同信号。  
> **任务：** 选择 RM、DPO 或在线 RL。  
> **做法与原因：** 按可验证性、探索需求和预算比较。  
> **结果／验证：** 独立 human evaluation 或执行结果支持选择，不看自家奖励。

#### 可以这样回答

我会先看任务能不能直接验证。代码是否通过独立测试、工具状态是否正确，这些通常先用执行反馈；开放写作或回答是否有帮助，才更需要 preference labels 和 reward model。

方法上，如果现有 preference pairs 覆盖得不错、主要是在调整回答行为，我会先比较 DPO 这样的离线方法。需要探索新的 tool-use trajectories，而且奖励比较可靠时，再考虑在线 RL。这里还有标注、运行和维护成本的区别。

最后我会用独立的任务结果或 human evaluation 来选。训练奖励更高，只说明模型更会得到这个奖励，不足以证明用户得到更好的答案。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-reward-pref)

### Panel：人标协议怎么写，一致率低怎么办？

> **回答思路**  
> **背景：** 标准含糊会让更多人重复不同理解。  
> **任务：** 建立可复用且可检查的 annotation guidelines。  
> **做法与原因：** 明确维度、tie、弃权和 edge cases。  
> **结果／验证：** 一致性与错误审计改善，合法分歧被保留。

#### 可以这样回答

标准含糊会让更多人重复不同理解。

先写协议再开标，每个维度写清定义、正例、反例和不允许的判断捷径，再让两人独立标、算一致率。一致率低先查原因，是协议含糊、题本身不可比还是有长度捷径，查清了再决定要不要加人。AFM 报告里 20-30% 的 preference pairs 人与人之间不同意，他们用 cohesion 挑更容易达成一致的 prompt。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-annotator-protocol)

### Panel：LLM-as-judge 会偏什么，什么时候能用？

> **回答思路**  
> **背景：** judge 可能偏爱长度、位置或同家族风格。  
> **任务：** 界定自动评价能承担什么角色。  
> **做法与原因：** 交换候选顺序、控制内容差异，并用 independent human evaluation 做 judge calibration。  
> **结果／验证：** 按 evaluation slice 一致性支持使用，执行真值不被替代。

#### 可以这样回答

我会把 judge 先当一个需要做 calibration 的评审器。它可能很擅长快速检查普通回答，但在长度、顺序或者熟悉的文风上偏掉。

我会抽一批题给人标，再让 judge 评同一批候选。交换顺序，看结论会不会变；挑一些长而错、短而对的例子，看它有没有被表达方式带走。数学、代码和工具状态能直接检查的部分，我会保留执行检查。

对得比较稳定以后，可以用它加快开发迭代。重要发布结论仍需要独立证据，特别是换了模型或任务以后，要重新看它还准不准。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-judge-bias)

### CoderPad：preference pairs 怎么滤，margin、长度、差不多的对谁扔掉？

> **回答思路**  
> **背景：** 差异小、标签弱或长度混杂的 preference pairs 有噪声。  
> **任务：** 按明确规则筛选可用对。  
> **做法与原因：** 先校验同 prompt 与标签，再检查 margin 和长度。  
> **结果／验证：** edge cases、tie、missing values 与拒收原因准确。

#### 可以这样回答

差异小、标签弱或长度混杂的 preference pairs 有噪声。

preference pairs 要先过滤再用：丢掉 $y_w\approx y_l$ 的对、长度差过大的对，以及 annotator 自己标了「难分」的对。能执行的任务用独立 verifier 的结果当 margin，不让生成模型给自己打分。Llama 3 公开的排序是 edited > chosen > rejected，弱档不进 DPO。

测试还要满足这个条件：edge cases、tie、missing values 与拒收原因准确。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-pref-pair-code)

### Panel：偏好和 RM 爱上长答案，数据侧怎么拆？

> **回答思路**  
> **背景：** RM 可能把详细误当成正确。  
> **任务：** 补能区分质量和冗长的数据。  
> **做法与原因：** 加入短而正确、长而必要与长而错误的对照。  
> **结果／验证：** 独立内容评价提高，不能只让答案变短。

#### 可以这样回答

RM 可能把详细误当成正确。

问题出在 preference data 里长回答总是赢，只调优化参数压不住。数据侧构造信息相同、长度不同的回答对，协议写明同等忠实且完整时选短的；human evaluation 和 RM 结果按长度分层分析，BoN 候选中保留简短的 SFT 回答。平均长度增加不代表能力提高。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-length-hack-data)

### Panel：安全 / 拒答数据怎么配，才不会变成一律拒绝？

> **回答思路**  
> **背景：** 安全训练容易把模糊主题一律拒绝。  
> **任务：** 学会按意图和证据给适当回应。  
> **做法与原因：** 覆盖有害、无害 nearest neighbors、部分可答和澄清。  
> **结果／验证：** 不当遵从和 over-refusal 同时达标。

#### 可以这样回答

安全训练容易把模糊主题一律拒绝。

应该拒绝和应该回答的题要成对出现，明确有害的请求配简短拒答，看起来敏感、实际无害的请求配正常回答。只喂有害请求和拒答示范，模型会把拒绝当成通用答案，连正常问题也不回答。评测分开报攻击成功率、over-refusal 和任务有用性。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-safety-refuse)

### Panel 情景：自动 judge 胜率涨了，human evaluation 却反转，先修模型还是修测量？

> **回答思路**  
> **背景：** 自动胜率与 human evaluation 结论反向。  
> **任务：** 先确认测量标准是否一致。  
> **做法与原因：** 冻结候选、顺序和协议，审计分歧样本。  
> **结果／验证：** 修测量后再比较策略，避免追逐错误 judge。

#### 可以这样回答

自动胜率与 human evaluation 结论反向。

先对同一输出做盲评、交换位置和长度分层，确认自动评价是否偏向风格或来源。冻结 calibration 集与训练用途，再决定修 judge、改偏好采集还是训练策略，避免用同一 judge 造标签又证明收益。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-judge-ranking-reversal)

### Panel 情景：组内奖励几乎都一样，RL 数据怎样恢复学习信号？

> **回答思路**  
> **背景：** 组内全对或全错缺少相对信号。  
> **任务：** 恢复可学习且真实的训练反馈。  
> **做法与原因：** 调整任务难度、组 sampling 和冷启动。  
> **结果／验证：** 有效组增加且独立成功提高，不伪造奖励差。

#### 可以这样回答

组内全对或全错缺少相对信号。

先查奖励执行和任务可解性，再看全对、全错和组内候选重复的比例。组内中心化奖励相同时任务优势为零；可调整任务难度、生成多样性与验证信号，但不能制造虚假的相对分数。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-zero-advantage-groups)

### Panel 情景：英文 preference labels 很一致，换语言后“好答案”标准冲突怎么办？

> **回答思路**  
> **背景：** 不同语言对好答案可能有不同规范。  
> **任务：** 区分翻译问题与真实偏好差异。  
> **做法与原因：** 当地专家改协议，按 locale 保留 evaluation slices。  
> **结果／验证：** 各语言收益与约束独立验收。

#### 可以这样回答

不同语言对好答案可能有不同规范。

把事实正确性、任务完成与语言风格分开，先确认原生语言语境与评分规则，再保留合法偏好多样性。不能把英文标签自动翻译后当成各语言的统一 gold standard。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=dt-preference-multilingual-conflict)

### Reward Model：怎样训练，并识别高分却退化的 reward hacking？

> **回答思路**  
> **背景：** Policy 的 reward score 持续上升，但回答更冗长，独立质量没有提高。  
> **任务：** 区分 reward model 学错、policy distribution shift 与真正的能力提升。  
> **做法与原因：** 用同 prompt 的 preference 数据训练，再用独立评价检查 score 与行为是否一致。  
> **结果／验证：** 真实质量提高，而非只提高被优化的 proxy。

#### 可以这样回答

我会用同一个 prompt 下的可比回答收集 preference labels，让 reward model 学习哪个回答更好，而不是把不同难度任务的答案随意配对。标签需要明确 rubric，也要保留 disagreement，不能假设所有人都偏好同一种风格。

如果训练时 reward 上升，但回答越来越长，我会先检查独立 human evaluation 和可执行任务结果有没有同步改善。然后按长度、任务类型和 policy checkpoint 分析，看看 reward model 是不是把冗长当成质量，或者遇到了训练时没有见过的回答分布。

确认问题后，我会补充能区分内容质量与表面风格的对照数据，例如同样正确但长度不同的答案，以及很流畅但实际上错误的答案。再限制继续优化的幅度，必要时回滚到独立质量尚未退化的 checkpoint。KL constraint 可以帮助限制漂移，但不能修复一个学错的 reward。

我会用新的 held-out prompts 和独立评审验收。如果只有 reward model 自己给分更高，我不会把它报告成 alignment 改善。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-web-reward-hacking)

### DPO：β 控制什么，为什么不能只用“大或小”解释训练行为？

> **回答思路**  
> **背景：** DPO 有 reference policy 和 β，但常被误说成直接控制 sampling temperature。  
> **任务：** 从 objective 解释 β，并说明它与数据和优化共同作用。  
> **做法与原因：** 先看相对 log-prob margin，再区分理论 regularization 与实际 gradient scale。  
> **结果／验证：** 能给出检查 KL、preference 和任务质量的 tuning 实验。

#### 可以这样回答

β 不是生成时的 temperature。DPO 关注的是 preferred answer 相对 rejected answer 的 log-probability，以及这个差值相对 reference policy 改了多少；β 会缩放进入 logistic loss 的这个 margin。

从推导里的 KL-regularized objective 看，更大的 β 对偏离 reference 的约束更强。但在实际训练里，它也改变 gradient 和饱和区间，所以不能只说 β 越大，模型实际 KL 就一定越小。

例如从 reference 初始化时，relative margin 是零，gradient 对 margin 的系数是负 β 除以二。β 很小，初始更新信号也会变小；β 较大，已经分对的 pair 可能更快进入饱和，但分错的 pair 仍可能产生较大的更新。这也说明 β 和 learning rate 不能分开看。

我会用相同数据、训练预算和 reference 比较几个 β，同时看独立 preference win rate、任务正确性、实际 KL 和长度变化。离线 preference pairs 是否覆盖当前模型的错误，也会影响选择，不能只靠一个超参数补救数据不匹配。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-web-dpo-beta)

### Post-Training Design：从 base model 到可靠 assistant，数据怎样分工？

> **回答思路**  
> **背景：** 新的 base model 有语言能力，但 instruction following、安全和 reasoning 不稳定。  
> **任务：** 为不同 capability gaps 选择对应的训练信号与验收。  
> **做法与原因：** 先建立基线，区分 SFT、preference 与 verifiable reward 的作用，再逐步干预。  
> **结果／验证：** 目标能力提高，同时保留通用能力并控制 over-refusal。

#### 可以这样回答

我不会先决定必须做几轮 RL，而会先测 base model：它是不会执行指令，还是能理解任务但经常推理错误？这决定我们缺的是行为示范，还是能区分好坏的反馈。

第一步可以用高质量 SFT 建立对话格式、tool calls 和基础行为。对回答有多种合理方式的任务，再用 preference data 改善有用性与安全取舍。数学和代码如果有可信 checker，可以增加 verifiable reward；但需要先验证 checker，避免模型学会利用测试漏洞。

数据也要分别管理。SFT 需要正确示范，preference 需要同 prompt 的可比候选，online RL 需要可以采集 current policy rollouts 的任务环境。不能因为它们都来自同一批日志，就直接共用一个训练文件。

每增加一个阶段，我会用同一套独立 evaluation 查看目标收益、通用能力、over-refusal 和成本。如果 preference 训练提高了安全分却让正常问题被大量拒绝，就需要检查标签和 data mix，而不是把它当成必然代价。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-web-posttraining)

### LLM-as-a-Judge：怎样发现 position、verbosity 和 self-preference bias？

> **回答思路**  
> **背景：** Judge 偏好更长、更像自己风格的回答，可能把风格当正确性。  
> **任务：** 验证 judge 是否真正测量目标质量，并决定哪些标签可用于训练。  
> **做法与原因：** 用对照 pairs 分离内容、顺序和长度，结合 blind human labels calibration。  
> **结果／验证：** 判断稳定且与独立正确性相符，保留 disagreement 和不确定样本。

#### 可以这样回答

我会先定义 judge 要评什么。代码能否运行可以先用测试检查；是否解释清楚可以用 rubric。把所有维度合成一个看起来权威的总分，很容易掩盖问题。

我会做几组有控制的 pairs：交换两个答案的顺序，比较同一正确答案的长短版本，再比较正确但简洁与流畅却错误的答案。如果顺序一换 winner 就变了，或者总是更长的获胜，我们就知道标签里混入了与目标无关的偏好。

然后用不显示模型来源的 human labels calibration，并检查不同任务的 agreement。Judge 自己生成的解释不能替代 calibration；换一个 model family 也不是自动消除 bias。

如果这些标签要进入 reward model 或 DPO，我会保留 judge 版本、rubric、顺序和置信信息。对不稳定或 human disagreement 高的样本先审核，不强行输出 winner。最终还是用独立任务质量验证训练收益，避免 judge 的偏好在数据迭代里被不断放大。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=alignment&question=afm-web-judge-bias)


## 09 · Multimodal：Vision、Audio 与 Video

### Director：multimodal 数据举一个你能讲到底的例子

> **回答思路**  
> **背景：** multimodal 问题需要说清证据和监督链路。  
> **任务：** 用一个具体任务讲到底。  
> **做法与原因：** 固定图文来源、标注与状态验证，做信息对照。  
> **结果／验证：** 未见布局/来源有效，个人经历与方案分开。

#### 可以这样回答

我会选一个有明确结果的例子，比如把票据截图里的金额和日期填进表格。它同时需要理解图片和操作软件，最后也能检查导出的文件。

我会先从有结构化真值的合成票据开始，记录 agent 操作前看到的截图和每一步 tool calls。失败以后区分它是读错金额，还是读对了却填错位置，这决定下一批数据该补视觉理解还是界面操作。

验证要换新的票据布局，并直接检查文件内容。这个例子是我会设计的方案；如果讲我参与的 multimodal 研究，就另外说明真实做过的模块和实验。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=dt-multimodal-data)

### 设计：multimodal 助手（图/屏/语音），模态延迟不齐

> **回答思路**  
> **背景：** 图像、音频和文本到达时间不同。  
> **任务：** 保证助手在正确证据下及时回应。  
> **做法与原因：** 对齐时间与状态，明确缓存、等待和缺模态行为。  
> **结果／验证：** 端到端质量、延迟及错误动作共同验收。

#### 可以这样回答

图像、音频和文本到达时间不同。

语音、图像、屏幕三路到达时间差一个数量级。契约是：没到的模态不当证据，先到的可以先应答或先问。on-device 保隐私和首包；云端跑重视觉。评测分别看答案是否有证据、是否正确、是否适合口头播报，以及各模态超时后的行为。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=design-multimodal-prod)

### Apple：图文 / 屏幕理解 grounding，引用的是像素区域还是 OCR 文本？

> **回答思路**  
> **背景：** OCR 文本未必能表达空间与像素证据。  
> **任务：** 选择可核查的视觉 grounding 表示。  
> **做法与原因：** 按任务保留区域、文字与出处。  
> **结果／验证：** 引用区域真正支持结论，换布局仍有效。

#### 可以这样回答

OCR 文本未必能表达空间与像素证据。

屏幕 grounding 要同时保留像素区域和 OCR 文本：点击、高亮依赖框或 mask，朗读、复制和填槽依赖文本 span。比如模型读出「下午三点」还要指向对应控件，两种输出必须共用能对齐的 id，避免说对内容却点错按钮。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=apple-multimodal)

### Apple：on-device / server-side multimodal 训练，视觉塔冻结还是联合，分辨率怎么选？

> **回答思路**  
> **背景：** 视觉训练受数据、算力与分辨率约束。  
> **任务：** 决定冻结视觉塔还是联合训练。  
> **做法与原因：** 先查缺口，再比较连接器、分辨率和更新范围。  
> **结果／验证：** 同预算视觉收益与语言回归支持取舍。

#### 可以这样回答

视觉训练受数据、算力与分辨率约束。

我会先定任务需要的分辨率和视觉 token 数，再决定是否解冻视觉塔。MM1 的公开 ablation study 中，低分辨率时冻结更好，高分辨率或偏离 pre-training 分辨率时解冻更好；on-device 还要按 ANE 静态档位训练和导出，server-side 切块方案不能直接搬过去。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=apple-mm-train)

### Apple：on-device 视觉 token 预算和 ANE 静态 shape 怎么卡？

> **回答思路**  
> **背景：** 视觉 token 会挤占 on-device 内存和时延。  
> **任务：** 在设备预算内保留必要信息。  
> **做法与原因：** 按任务分辨率与静态形状控制 token。  
> **结果／验证：** 小字、图表与关键区域不因平均提速被牺牲。

#### 可以这样回答

视觉 token 会挤占 on-device 内存和时延。

视觉 token 与文本、输出共享上下文和 KV，先按 $(H/P)\times(W/P)$ 算数量，再检查总数是否在 $S_{\max}$ 内。比如多张截图会挤占工具证据和生成空间；on-device 要预编译分辨率与切块档位，按任务选缩略图、ROI 或 PCC，并验证计算仍留在 ANE。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=apple-vision-edge)

### 设计：multimodal 助手的引用区域与视觉 token 预算

> **回答思路**  
> **背景：** 助手需将答案绑定到实际图像位置。  
> **任务：** 设计证据引用和视觉预算。  
> **做法与原因：** 区域选择与生成分开，预算由任务信息需求决定。  
> **结果／验证：** 区域正确、内容受支持且端到端成本可接受。

#### 可以这样回答

助手需将答案绑定到实际图像位置。

回答要能指回图上的框或屏幕区域，引用对不上就删句，尚未到达的模态不能当证据。视觉 token 按 patch 占上下文，高分辨率图先粗定位、再裁剪细看；模态延迟状态机见 `design-multimodal-prod`。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=design-mm-assistant)

### Apple：语音进 LLM，流式 ASR 文本还是音频 token？

> **回答思路**  
> **背景：** 文字转写会损失部分语音信息。  
> **任务：** 选择 ASR 链路或直接音频表示。  
> **做法与原因：** 比较语义、时序、语气需求和流式延迟。  
> **结果／验证：** 操作成功、必要声学线索与延迟一起测。

#### 可以这样回答

文字转写会损失部分语音信息。

我会让 ASR 文本负责工具参数和事实核对，写操作等最终识别稳定再执行。音频 token 能保留韵律、叠音等信息，但前缀更长、静态 shape 和证据对齐更难，适合在需要这些信息时补一条短窗口通道。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=apple-audio-llm)

### Apple：视觉 token 剪枝 / 合并，质量和延迟怎么折？

> **回答思路**  
> **背景：** 视觉 token 冗余但关键小区域可能稀有。  
> **任务：** 减少成本同时保留任务证据。  
> **做法与原因：** 剪枝/合并按证据价值比较，保留困难区域。  
> **结果／验证：** 同预算测细粒度任务和 long-tail 退化。

#### 可以这样回答

视觉 token 冗余但关键小区域可能稀有。

视觉 token 可以按 attention 剪掉或按相似度合并，减少后续 prefill 和 KV 开销，但小字和定位通常先受损。on-device 要把剩余数量固定为 $K$ 并保留原图索引；分别测 OCR、grounding 和 VQA，再决定压缩比例。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=apple-token-prune)

### CoderPad：image-text pairs CLIP 分怎么滤，合成 caption 要不要同一阈值？

> **回答思路**  
> **背景：** 相似度高不保证 caption 事实全对。  
> **任务：** 按来源过滤 image-text pairs 且控制 false rejection。  
> **做法与原因：** 真实和合成 caption 分别对 threshold 做 calibration。  
> **结果／验证：** 抽查错配、难图与保留覆盖，不只看均分。

#### 可以这样回答

相似度高不保证 caption 事实全对。

图像和文本各自编码成向量，用余弦相似度当图文匹配分，再按语言和来源分桶，每桶取分位数当阈值。合成 caption 的 CLIP 分会向 teacher model 的分布靠拢而虚高，所以要和网页 alt-text 分开设阈值。重复和安全 CLIP 分管不到，要用各自的 checker，误删靠下游对照来验证。

测试还要满足这个条件：抽查错配、难图与保留覆盖，不只看均分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=dt-clip-filter-code)

### Panel 情景：截图问答高分，换一套 UI 就失败，如何排查视觉捷径？

> **回答思路**  
> **背景：** 截图题在新 UI 上突然失效。  
> **任务：** 区分内容理解与布局捷径。  
> **做法与原因：** 布局、文字、区域和证据做 controlled substitution。  
> **结果／验证：** 未见 UI 表现支持数据干预，模板 near-duplicates 隔离。

#### 可以这样回答

截图题在新 UI 上突然失效。

用图像、文字与布局的受控干预判断模型是否利用视觉证据，再按组件和模板隔离训练测试。synthetic data 要覆盖未见组合、信息缺失和视觉冲突，验证必须依赖实际渲染内容。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=dt-mm-shortcut-audit)

### Panel 情景：语音识别 WER 降了，语音助手却更容易做错操作？

> **回答思路**  
> **背景：** 字错率变低但操作更容易出错。  
> **任务：** 定位关键语义与下游决策损失。  
> **做法与原因：** 按实体、否定、数字和权限 evaluation slices replay。  
> **结果／验证：** 任务成功与关键语义错误优先于总体 WER。

#### 可以这样回答

字错率变低但操作更容易出错。

字词错误率不区分错误的任务代价。把音频、转录、意图参数和执行状态分段替换，检查否定词、数字与实体，再用有语义对照的授权音频与合成扰动验证。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=dt-audio-semantic-regression)

### Panel 情景：视频问答能识物却分不清先后，如何造时序训练数据？

> **回答思路**  
> **背景：** 识别物体不等于理解事件先后。  
> **任务：** 训练和测量真正的时序依赖。  
> **做法与原因：** 保持物体相似，交换事件顺序构造对照。  
> **结果／验证：** 时序题随证据变化，静态视觉能力不退。

#### 可以这样回答

识别物体不等于理解事件先后。

先验证答案是否真的依赖帧序，再用相同对象不同动作顺序的受控视频建立时序对照。按源视频分组隔离派生片段，并检查 sampling 帧是否包含回答所需事件。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=dt-video-temporal-shortcut)

### Apple CVML 面经：手写二维 circular padding，怎样保留自动求导？

> **回答思路**  
> **背景：** image boundaries 需要环绕而非补零。  
> **任务：** 实现可求导的二维周期填充。  
> **做法与原因：** 用模索引处理大 padding 与任意空间维。  
> **结果／验证：** 手算边角，检查超宽 padding 和 gradient 累加。

#### 可以这样回答

image boundaries 需要环绕而非补零。

把输出行列映射到原图的模索引，再用 index_select 取值。这样能处理非对称及超过图像尺寸的补边，并保留 gradient；环形补边会改变 boundary conditions，不能不加分析地替换普通图像的零补边。

测试时，我会手算边角，检查超宽 padding 和 gradient 累加。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=p3a-apple-cvml-circular-padding)

### Apple CVML 面经：怎样评测生成式图像，而不只看好不好看？

> **回答思路**  
> **背景：** 生成图像好看不等于满足指令。  
> **任务：** 分别评质量、条件一致和局部正确。  
> **做法与原因：** 客观检查与分维度 human evaluation 结合。  
> **结果／验证：** 困难指令与偏差 evaluation slices 可靠，不用单一美学分。

#### 可以这样回答

生成图像好看不等于满足指令。

把图像质量、文本遵循、组合关系、多样性与安全分开测。用成对提示控制颜色、数量、位置等因素，自动评分先与盲评 calibration；FID 不能证明某条提示被满足，单个相似度总分也会掩盖属性绑定错误。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=p3a-apple-cvml-image-evaluation)

### Apple MLE 原帖：设计大型 video summary 系统，怎样保住证据与时序？

> **回答思路**  
> **背景：** 长视频会丢掉时间和证据链。  
> **任务：** 生成可追溯且完整的摘要。  
> **做法与原因：** 分段索引、事件聚合与时间戳引用。  
> **结果／验证：** 重要事件覆盖、先后正确和检索延迟都验收。

#### 可以这样回答

长视频会丢掉时间和证据链。

先明确输出是文字摘要还是视频片段，再把音频、视觉和时间证据对齐，分段提取后做带时间戳的全局汇总。评测覆盖事实性、关键事件与时序，不能只看与参考摘要的字面相似度。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=p3a-apple-video-summary-design)

### Multimodal Search：私人照片搜索的数据、评估和 model upgrade 怎么设计？

> **回答思路**  
> **背景：** 用户用自然语言搜索自己的照片，query 同时包含视觉内容和个人上下文。  
> **任务：** 设计 retrieval、训练数据、隐私友好的 evaluation 和 embedding migration。  
> **做法与原因：** 分开视觉语义与时间人物信息，使用获授权的数据验证，版本化 embedding。  
> **结果／验证：** 搜索成功改善，同时不跨用户访问且升级期间结果可用。

#### 可以这样回答

我会先把 query 拆开。“海边的狗”主要是图像与文本语义；“Emma 在 2019 年的生日”还需要人物分组和时间信息。单纯提高 image-text similarity 不一定能解决后者。

我会用 dual encoder 做视觉语义 retrieval，再结合时间、OCR 和经过授权的个人上下文处理约束。训练阶段可以先用许可清楚的 image-text pairs，不能默认把用户私有照片拿给标注人员。针对个人查询的 evaluation，需要明确授权的数据或可控的 synthetic libraries。

我会分别评估视觉概念、时间人物、多条件和容易混淆的任务。线上也可以看经过隐私审核的 aggregate signals，但点击一张图并不总表示它是正确答案，所以不能直接把每次点击当正标签。

升级模型时，我会给 embedding 和 encoder 记录版本，分批 backfill，并保证同一次搜索的 query 与 image vectors 处于兼容空间。新模型离线更强，如果全量照片还没有重新编码，也不能直接切换。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=multimodal&question=afm-web-photos-search)


## 10 · On-Device、Privacy 与 Inference

### Apple：on-device 权重 quantization / KV quantization，ANE 上 mask 的 -inf 还安全吗？

> **回答思路**  
> **背景：** 低比特可能破坏数值和关键算子行为。  
> **任务：** 估算收益并定位 quantization 误差。  
> **做法与原因：** 权重/KV 分别做 calibration，检查 mask 与设备支持。  
> **结果／验证：** 同设备质量、内存和延迟支持方案。

#### 可以这样回答

低比特可能破坏数值和关键算子行为。

权重 palettization、激活和 KV quantization 要分别看：2024 公开方案混合 2/4-bit 权重、约 3.7 bpw，KV 用 8-bit，再用 LoRA 恢复质量。ANE 上 mask 应在反 quantization 后加 fp16 有限大负数，检查非法位置的 softmax 是否为零，避免 $-\infty$ 和 int8 截断导致错误。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-ondevice-quant)

### Director：真实世界反馈怎么用，还不把用户数据喂进基础模型？

> **回答思路**  
> **背景：** 产品反馈不能默认成为全球训练原文。  
> **任务：** 合法利用失败信号改善模型。  
> **做法与原因：** 区分 on-device 适配、聚合统计和许可研究数据。  
> **结果／验证：** privacy requirements 可核验，合成复现也有独立收益。

#### 可以这样回答

我会先把“知道用户哪里不满意”和“拿到用户内容做训练”分开。比如知道摘要经常漏掉限定词，这个失败类型很有价值，但不意味着就能把原邮件拿来做 SFT。

如果用途允许，可以在设备上处理反馈，或者使用合法的聚合统计。要改进共享模型，我会用许可研究数据或合成材料复现同类问题，再独立验证。个性化留在 on-device，也是另一条路径。

所以这条飞轮首先要说清每一种信号允许做什么，再谈模型收益。匿名化、inference 时能访问和允许训练，是不同的条件。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=dt-privacy-feedback)

### Apple：differential privacy 在个性化语言模型里怎么讲 ε，和「数据不出设备」的关系？

> **回答思路**  
> **背景：** 数据不出设备不自动意味着有 DP 保证。  
> **任务：** 说清保护对象与 privacy budget。  
> **做法与原因：** 定义邻居关系、裁剪、加噪和组合。  
> **结果／验证：** 报告效用与预算，不将匿名化当形式保证。

#### 可以这样回答

数据不出设备不自动意味着有 DP 保证。

数据不出设备说明这条路径没有发布数据，本身没有一个可报的 $\varepsilon$。DP 约束的是发布结果对单条记录的敏感度；个性化上下文优先留在 on-device，只有发布人群统计时再讨论噪声、每日条数和合成预算。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-diff-privacy)

### Apple：Siri 语音链路延迟预算，流式 TTS vs 等完整答案？

> **回答思路**  
> **背景：** 语音助手多阶段等待会累积。  
> **任务：** 分配可测的端到端延迟预算。  
> **做法与原因：** 识别关键路径，比较流式输出与完整结果等待。  
> **结果／验证：** 首响应、最终完成及误打断质量一起测。

#### 可以这样回答

语音助手多阶段等待会累积。

我会分段记录端点检测、流式 ASR、工具与 LLM 首句、TTS 首包，再决定哪些阶段可以重叠。改写和已确认的长摘要可流式播报，时间、金额、身份和工具事实要等证据齐全再读；公开 on-device 约 0.6 ms/prompt-token、30 token/s，不能直接当整条语音链路的延迟。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-siri-latency)

### Director：这件事该改 base model 数据，还是只训 feature adapter？

> **回答思路**  
> **背景：** 能力缺口可能是普遍知识，也可能是局部行为。  
> **任务：** 选择 base model 数据或 feature adapter。  
> **做法与原因：** 按共享程度、更新频率和隐私范围做对照。  
> **结果／验证：** 目标改善且通用能力、部署成本达标。

#### 可以这样回答

能力缺口可能是普遍知识，也可能是局部行为。

看问题影响多少个功能。多个功能共有的缺口，比如工具 schema、multilingual 指令、有证据支持的拒答，补进 base model post-training；只属于一个功能的固定格式或口吻，训 feature adapter；用户私有偏好留在 on-device。全回 base model SFT 或全交给 LoRA，都说明范围没切清。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=dt-adapter-vs-base)

### Apple：Neural Engine 约束（静态 shape、算子白名单）对 Transformer 设计的影响？

> **回答思路**  
> **背景：** on-device 硬件限制形状与算子。  
> **任务：** 把模型设计落到可运行图。  
> **做法与原因：** 先核对算子支持和静态预算，再选近似。  
> **结果／验证：** 实际设备 profiling，而非仅凭理论 FLOPs。

#### 可以这样回答

on-device 硬件限制形状与算子。

我会按 ANE 能编译的静态图来设计 Transformer：固定 shape 和 KV 槽位，采用合适的布局、算子与 dtype，再验证整网是否驻留。某层回退到 CPU/GPU 会增加拷贝和耗电，quantization 之前先把这类问题定位清楚。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-ane)

### Director：on-device distillation 该蒸哪些数据，为什么不从头蒸 14T？

> **回答思路**  
> **背景：** distillation 预算不足以重放全部 pre-training。  
> **任务：** 选择 on-device 最需要的监督。  
> **做法与原因：** 目标任务、困难 evaluation slices 和语言覆盖优先。  
> **结果／验证：** 同成本 student 收益与 teacher 事实正确性均检查。

#### 可以这样回答

distillation 预算不足以重放全部 pre-training。

AFM 公开的 on-device 配方没有从头蒸：先用 1T 高质量数据把 dense on-device 模型 sparse-upcycle 成 MoE teacher，再只在 dense student 最后约 10% 的 token（约 1.4T）上加 distillation 损失，teacher 训练成本因此降了约 90%。蒸什么还要看 3B student 学不学得会、对不对得上产品任务，server 的长 RL trajectories 不宜原样蒸。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=dt-ondevice-distill-data)

### Apple：个性化不能上传全量私有上下文，adapter / 本地检索怎么选？

> **回答思路**  
> **背景：** 个性化知识含私有且经常变化的内容。  
> **任务：** 选择本地检索还是参数适配。  
> **做法与原因：** 按事实更新、风格行为及撤回需求分工。  
> **结果／验证：** 收益在 on-device 测，私有内容不默认进入共享权重。

#### 可以这样回答

个性化知识含私有且经常变化的内容。

会变的事实用本地检索，稳定的任务格式用功能 LoRA：比如日程走工具，邮件摘要和通知摘要切换各自的 adapter。公开 adapter 常为 rank 16、16-bit、几十 MB，基础模型冻结 quantization；私有上下文默认留在设备，需要人群统计时再考虑 DP，见 `apple-diff-privacy`。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-personalize)

### Director：guided generation / 约束 decoding 要什么样的 post-training 数据？

> **回答思路**  
> **背景：** 格式约束不能教会何时调用正确工具。  
> **任务：** 补结构合法之外的行为监督。  
> **做法与原因：** 明确 schema 条件、工具选择和失败恢复。  
> **结果／验证：** 合法率、任务正确与权限分别验收。

#### 可以这样回答

格式约束不能教会何时调用正确工具。

训练样本要和框架真正给模型的输入一样：用户请求、框架注入的结构定义，加一个既符合定义、字段也填对的输出。约束 decoding 只保证格式合法，内容填对要靠数据教。只给几条「请输出 JSON」的示范，和框架的实际输入对不上。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=dt-guided-gen-data)

### Apple：Foundation Models 公开叙事怎么讲，on-device 和云各自干什么、capability limits 在哪？

> **回答思路**  
> **背景：** on-device 与 server-side 承担不同约束与任务。  
> **任务：** 准确解释公开模型定位。  
> **做法与原因：** 用公开报告连接能力、成本与 privacy requirements。  
> **结果／验证：** 不推测内部细节，任务路由有证据。

#### 可以这样回答

on-device 与 server-side 承担不同约束与任务。

Apple 的公开方案是 on-device 与 PCC 上的 server 模型互补：约 3B 的 on-device 模型处理日常、低延迟和私有上下文任务，更难的推理交给 server-side。on-device 擅长摘要、抽取和短对话，设计时要按能力与隐私要求决定路由，并保留拒答或非生成 UI。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-foundation-models)

### Apple：on-device KV 的显存和带宽怎么估，GQA 加 quantization cache 各省哪一刀？

> **回答思路**  
> **背景：** long contextKV 占用内存并受带宽限制。  
> **任务：** 计算 cache 预算并比较压缩方案。  
> **做法与原因：** 从层数、KV heads、长度和精度逐项估算。  
> **结果／验证：** 理论字节与实际 profiling 一致，质量回归可接受。

#### 可以这样回答

long contextKV 占用内存并受带宽限制。

on-device decode 每步读取历史 KV，显存和带宽可先按 $2 L H_{\mathrm{kv}} d_h S b$ 估算。GQA 减少 KV head，8-bit cache 减少每元素字节，2025 公开的跨块 KV 共享再减少有效存储深度；long context 要重点检查手机 DRAM / ANE SRAM 的预算。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-ondevice-kv)

### Apple：on-device speculative decoding 值得上吗，草稿模型放哪？

> **回答思路**  
> **背景：** 草稿模型本身也消耗 on-device 资源。  
> **任务：** 判断 speculative decoding 是否有净收益。  
> **做法与原因：** 合并 acceptance rate、草稿成本、验证与内存测量。  
> **结果／验证：** 同设备净延迟和能耗提高，分布要求保持。

#### 可以这样回答

草稿模型本身也消耗 on-device 资源。

on-device speculative decoding 是否值得，要看草稿成本、平均接受长度、KV 回滚和稳态功耗；草稿很便宜、acceptance rate 高时才可能省时。草稿宜与目标同设备、同静态档位，TTS 只能读已验证 token；Apple 公开的 30 token/s 是投机之前的数字。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-spec-edge)

### Apple：low-rank adapter 做个性化，和检索怎么选，数据如何不出设备？

> **回答思路**  
> **背景：** 检索事实和学习偏好是不同个性化需求。  
> **任务：** 比较低秩适配与本地检索。  
> **做法与原因：** 按隐私、更新频率与可撤回性设计。  
> **结果／验证：** 用户任务改善且隔离、遗忘与成本可检查。

#### 可以这样回答

检索事实和学习偏好是不同个性化需求。

会变的事实走本地检索，稳定格式和任务行为走 LoRA；按用户训练时，数据和权重应留在设备。公开产品 adapter 常为 rank 16，开发者 toolkit 提到 rank 32，16-bit 存储约几十 MB，可在冻结 quantization 底模上热切换；遗忘和版本绑定也要设计。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=ondevice&question=apple-rank-adapter)


## 11 · Agent 与系统设计

### Apple Siri：工具结果必须 grounding 的回复，怎么设计生成和评测？

> **回答思路**  
> **背景：** 工具结果和自然语言总结可能不一致。  
> **任务：** 让回复只陈述已确认的状态。  
> **做法与原因：** 工具事实提取、引用和生成检查分开。  
> **结果／验证：** 空结果、失败和部分完成不被说成成功。

#### 可以这样回答

工具结果和自然语言总结可能不一致。

Siri 的关键事实要能逐条定位到工具或检索证据，缺证据时追问或拒答，再把已核对的文字压到语音预算内。比如日历返回「下午三点」，口播压缩时不能丢掉「下午」；评测要拆开证据支持、正确性、语音可读性、拒答和上下文增长后的表现。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=apple-siri-grounded)

### 设计：内容安全分级，延迟、申诉、模型+规则

> **回答思路**  
> **背景：** 风险内容、延迟和误伤目标存在冲突。  
> **任务：** 设计可解释的分级处理。  
> **做法与原因：** 规则与模型分层，保留申诉和人工复核。  
> **结果／验证：** 高风险 false negative、正常内容误伤及延迟分别达标。

#### 可以这样回答

风险内容、延迟和误伤目标存在冲突。

先按类别和严重度规定放行、折叠、删除、封号等动作，再用规则和哈希处理高确信命中、模型处理语义判断、人工处理灰色案例与申诉。发送路径做低延迟检查，回溯扫描可异步；false rejection 和漏杀按严重度分别评估。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=design-moderation)

### tool calls 合成：Gorilla / ToolLLM / APIGen 这类 pipeline，grader 是什么？

> **回答思路**  
> **背景：** 模型生成的调用不一定能执行。  
> **任务：** 获得可验证的工具示范。  
> **做法与原因：** 从规范生成任务，实际执行并核对参数和结果。  
> **结果／验证：** 跨接口泛化，schema 合法不代替任务成功。

#### 可以这样回答

模型生成的调用不一定能执行。

grader 是由便宜到贵的三层检查：JSON 能解析、工具存在、必填字段齐全；参数符合 schema 的类型、枚举和范围；能执行的调用真的执行成功。只训 JSON 格式、不跑环境，模型学会了接口长什么样，却会编造「已添加」这类结果，schema 一变也容易失效。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tool-apigen)

### 工具数据要不要造并行调用？串行 trajectories 会教出什么坏习惯？

> **回答思路**  
> **背景：** 全是串行示范可能教出无谓等待。  
> **任务：** 判断哪些调用能安全并行。  
> **做法与原因：** 按依赖图和副作用构造并行与串行对照。  
> **结果／验证：** 延迟改善且没有破坏状态与必经信息依赖。

#### 可以这样回答

全是串行示范可能教出无谓等待。

要造，但按数据依赖决定：天气、日历这类独立读取放在同一轮并行，先查 id 再写入必须串行。只有串行 ReAct trajectories，模型会把能并行的也排成多轮，延迟和轮次都会涨。环境要真的并跑，部分失败时保留成功结果、只恢复失败项；写操作默认不并行，工具返回不计生成损失。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tool-parallel)

### 工具失败之后怎么改，这种 trajectories 为什么比再堆 10 万成功 JSON 值钱？

> **回答思路**  
> **背景：** 真实工具会返回超时、空值和权限错误。  
> **任务：** 学习合理恢复而非一味报成功。  
> **做法与原因：** 合成可 replay 失败分支，检查重试与状态查询。  
> **结果／验证：** 独立失败任务恢复，重复写入和假成功下降。

#### 可以这样回答

真实工具会返回超时、空值和权限错误。

因为只训成功 JSON，模型从没见过合法的失败，遇到 stderr 就可能谎称「已经办好了」。恢复 trajectories 要覆盖参数错误、空结果、权限拒绝和超时，示范改参数、有限重试或诚实停止。失败那一跳不当正例，恢复后的正确调用当正例，工具报错不计生成损失；报错要来自真实环境，失败比例也要控制。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tool-error-recover)

### 会改状态的工具，数据里要不要先确认再写？

> **回答思路**  
> **背景：** 写操作可能产生不可逆副作用。  
> **任务：** 在适当时机确认授权与目标。  
> **做法与原因：** 按产品权限契约覆盖确认、拒绝和澄清。  
> **结果／验证：** 未授权写入受控，必要确认与多余确认分开评。

#### 可以这样回答

写操作可能产生不可逆副作用。

要，但按副作用分。工具目录标记 read / write，读取按任务自动执行；含糊的写操作先澄清、确认，已有明确且唯一的授权可以按协议直接执行。训练要覆盖用户拒绝后停止；评分同时检查确认轮和实际状态，只看写入结果会漏掉未经确认的误操作。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tool-write-confirm)

### Agent SFT：500 条 GPT-4 trajectories 就够吗，多样从哪来？

> **回答思路**  
> **背景：** 少量优质 trajectories 可能覆盖不足。  
> **任务：** 理解示范质量和多样性的作用。  
> **做法与原因：** 保留可执行路径，按任务与工具变化扩展。  
> **结果／验证：** 新任务收益验证，不能把固定条数当普适配方。

#### 可以这样回答

少量优质 trajectories 可能覆盖不足。

几百条可 replay 的成功 trajectories，够教会模型调用格式和什么时候停，泛化还不够。多样性来自不同的任务、格式和 teacher，同一条 ReAct 复制再多遍也学不到新东西。FireAct 的约 500 条适合短程、好验证的搜索 QA，SWE、GUI、多轮客服要更多可执行任务。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-fireact)

### SWE-Gym：用可执行仓库当数据工厂，trajectories 怎么留、verifier 怎么训？

> **回答思路**  
> **背景：** 仓库可执行性决定反馈是否可信。  
> **任务：** 将修复任务转成可重复训练环境。  
> **做法与原因：** 固定代码快照、依赖和 hidden tests，保存 tool-use trajectories。  
> **结果／验证：** 重置能复现，补丁正确且没有修改评测器。

#### 可以这样回答

仓库可执行性决定反馈是否可信。

SWE-Gym 把真实 Python 任务、可执行环境和单测做成一个训练工厂：current policy sampling，测试判成败，成功 trajectories 做 SFT，成败 trajectories 一起训 outcome verifier。任务池要和评测隔开。过测只是必要条件，改测试、漏回归和环境漂移要另外拦。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-swegym)

### Agent 多轮数据里的「用户」用 LLM 模拟，坑在哪？

> **回答思路**  
> **背景：** 模拟用户可能 leakage 目标或过度配合。  
> **任务：** 获得可信的多轮交互训练。  
> **做法与原因：** 约束用户可见信息与状态，独立核对终局。  
> **结果／验证：** 真实或人工抽查支持，换模拟器仍有效。

#### 可以这样回答

模拟用户可能 leakage 目标或过度配合。

模拟器只负责生成用户的话，看不到隐藏数据库和完整的内部政策；成功由真实环境状态和政策 grader 判，模拟器说满意不能当 oracle。要查过度配合、泄密、文风单一和停不下来这几类问题，评测时换 seed 或 teacher 并人工抽查，免得 agent 只学会适应模拟用户。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-user-sim)

### Agent RL 数据：怎么判断这批环境是好的，怎么把它造出来？

> **回答思路**  
> **背景：** 大量环境不一定产生有效学习。  
> **任务：** 建立 Agent RL 任务质量标准。  
> **做法与原因：** 先审计任务可解、反馈可靠和难度可学。  
> **结果／验证：** 独立环境收益和成本支持扩量。

#### 可以这样回答

大量环境不一定产生有效学习。

Agent RL 的数据是任务、可执行环境和可复现奖励三样一起，trajectories jsonl 只拿来冷启动。判断一批环境好不好，看说明是否完整、测试是否稳定、奖励会不会被钻空子，以及当前模型是否偶尔能做对。要扩量就先筛现有任务，或按任务维度合成环境，再并行跑 rollout。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-rl-map)

### 设计：语音 agent 的打断、端到端延迟、ASR 错误传播

> **回答思路**  
> **背景：** ASR、推理、工具与 TTS 互相影响。  
> **任务：** 设计可打断且可靠的语音流程。  
> **做法与原因：** 状态机管理流式结果、取消与动作确认。  
> **结果／验证：** 语义成功、首响应和打断恢复均测。

#### 可以这样回答

ASR、推理、工具与 TTS 互相影响。

语音 agent 要能在用户开口时停止播放，并从生成状态退回听取新输入，同时区分可取消查询和已发出的写操作。先定首包音频、打断后静音间隔的 SLO，再分配 ASR、LLM、TTS 预算；金额、药名等低置信槽位要确认，避免识别错误沿工具链放大。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=design-voice-agent)

### Agent RL 的数据集是什么？为什么说「环境」替代了「jsonl」？

> **回答思路**  
> **背景：** 交互中的下一状态取决于策略动作。  
> **任务：** 解释环境为何是训练数据的一部分。  
> **做法与原因：** 保存初态、动作接口、转移和评分版本。  
> **结果／验证：** 同任务能重置 resampling，而不只是复用旧 JSONL。

#### 可以这样回答

交互中的下一状态取决于策略动作。

Agent RL 的数据集是一批能装起来、能打分、能并行跑的任务环境：current policy 进去生成新 trajectories，grader 看结果给奖励。手里的演示 jsonl 只是某个策略在某版环境上采的样，策略或环境一变就过时，主要拿来做 SFT 冷启动。所以盘点时要记环境和奖励版本，训练和评测任务分开。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-env-is-data)

### Panel：tool-use trajectories 哪一段进 SFT，失败枝怎么用？

> **回答思路**  
> **背景：** 最终成功 trajectories 也可能包含坏过程。  
> **任务：** 决定哪些片段适合监督。  
> **做法与原因：** 按证据、权限、恢复和无效动作审核。  
> **结果／验证：** 被学到的行为可迁移，失败片段不冒充正例。

#### 可以这样回答

最终成功 trajectories 也可能包含坏过程。

用于 SFT 的 tool-use trajectories 要逐步过检查，每一步参数合法、结果真实、写操作确实完成，最后的回答和实际状态一致，并能在对应环境版本重放。工具返回内容是模型读取的输入，不算进损失。失败尝试可以做恢复示范或偏好负例。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-traj-quality)

### Apple：on-device agent，工具本地跑、写操作确认、离线怎么收？

> **回答思路**  
> **背景：** 离线执行与私有状态限制 on-deviceagent。  
> **任务：** 选择本地工具与 on-device / server 分工。  
> **做法与原因：** 按权限和可用性规划，写入前核对状态。  
> **结果／验证：** 离线和失败条件下不编造完成，设备成本达标。

#### 可以这样回答

离线执行与私有状态限制 on-deviceagent。

on-device agent 由模型输出结构化调用，再由 App 的 `Tool` 或系统 App Intent 执行；发、删、付款等副作用要经过确认。离线时只暴露本地工具，宿主程序限制轮数、耗时和资源，工具失败也要按真实状态返回。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=apple-ondevice-agent)

### 怎么判断一条 agent 训练任务质量好不好？

> **回答思路**  
> **背景：** 无解或容易作弊的任务会扭曲奖励。  
> **任务：** 筛出真实、明确且可验证的任务。  
> **做法与原因：** 检查目标、初态、权限和独立 oracle。  
> **结果／验证：** 多策略审计通过，无法判定的任务隔离。

#### 可以这样回答

无解或容易作弊的任务会扭曲奖励。

好任务要满足五条：参考修复让测试从失败变成通过，说明足够定位问题，测试考的正是说明里的要求，环境能从头复现，任务和评测隔开。题面像 issue 还说明不了它能用；人审也只代表当时的质量，之后还要复查 contamination 和失效测试。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-task-quality)

### 2 万条 SWE 任务，怎么滤成能拿来做 Agent RL 的集合？

> **回答思路**  
> **背景：** 两万条仓库任务含依赖与评分噪声。  
> **任务：** 保留可运行且提供学习信号的子集。  
> **做法与原因：** 先验证环境，再看难度、测试与重复家族。  
> **结果／验证：** 过滤收益在新任务复测，不只提高训练通过率。

#### 可以这样回答

两万条仓库任务含依赖与评分噪声。

先做四项静态检查：任务是否有效、复杂度是否合适、LLM 质量标签是否过关、测试是否稳定。SWE-rebench 的原始任务不能直接拿去做 Agent RL，公开做法从 21336 条滤到 7249 条。进入训练后，再移除当前模型始终失败或太容易的任务，留下能学、能复现的部分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-rl-filter)

### Agent RL 的奖励怎么写，怎样才不算被 hack？

> **回答思路**  
> **背景：** 模型会优化 scorer 遗漏的条件。  
> **任务：** 让奖励对应任务与权限约束。  
> **做法与原因：** 真实状态为主，过程和成本项明确优先级。  
> **结果／验证：** 对抗 replay 不易骗分，独立任务结果同步改善。

#### 可以这样回答

模型会优化 scorer 遗漏的条件。

奖励 $r$ 以 hidden tests 或最终状态检查为准，可以是 0/1，也可以按测试点计分。可见测试的结果只当环境反馈给模型看，不进最终奖励。补丁和标准补丁的文本相似度会压低功能等价但写法不同的解，最多当辅助信号。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-reward-spec)

### Agent 环境要打包成什么，才能既评又训？

> **回答思路**  
> **背景：** 评测与训练需要共享可复现环境。  
> **任务：** 打包完整任务而非零散容器。  
> **做法与原因：** 版本化初态、工具、依赖、reset 和 verifier。  
> **结果／验证：** 干净实例可反复 replay，训练看不到隐藏真值。

#### 可以这样回答

评测与训练需要共享可复现环境。

打包成一个能 pip install 的任务环境，里面有任务说明和初始资源、把 tool calls 接到真实系统的 harness、给结果打分的 rubric。三样都要能安装、能版本化，训练和评测共用同一套执行和评分逻辑，两边的目标才一致。只有 prompt 模板、没有可执行动作和 scorer，撑不起 Agent RL。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-env-stack)

### Agent RL 怎么把环境扩到能真正跑起来？Qwen 和 SkyRL 各做了什么？

> **回答思路**  
> **背景：** 并行环境可能被启动、依赖和重置成本限制。  
> **任务：** 提高有效训练 throughput。  
> **做法与原因：** 先 profiling 瓶颈，再分离环境与模型服务。  
> **结果／验证：** 每小时有效 rollout 增长，质量和策略新鲜度不降。

#### 可以这样回答

并行环境可能被启动、依赖和重置成本限制。

先让单个任务在干净容器里稳定复现，再加并行环境，Agent RL 的瓶颈在环境规模。Qwen 同时跑 2 万个独立环境，SkyRL 用异步执行、任务调度和工具服务把 throughput 提到朴素实现的约 4 到 5 倍。扩之前先查超时、依赖和文件系统隔离。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-scale-env)

### 为什么 OpenAI 不再用 SWE-bench Verified 报成绩？这对训练数据意味着什么？

> **回答思路**  
> **背景：** 公开评测会随可解性和 contamination 审计变化。  
> **任务：** 理解基准失效对训练选择的影响。  
> **做法与原因：** 回到公开说明核对问题，不只记一个排名。  
> **结果／验证：** 使用可审计的新任务，历史成绩保留 version scope。

#### 可以这样回答

公开评测会随可解性和 contamination 审计变化。

不能直接算赢。分数涨了先查两件事：测试是不是在考题面没写的要求，题目和标准补丁有没有进训练。Verified 人审过 500 题，仍然有测试质量和 leakage 问题，OpenAI 2026-02 已停报。训练池和评测池要隔开，并留一份按时间划分、能刷新的 holdout。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-verified-stale)

### Agent RL 一组 rollout 全零或全一对，这批任务还要不要？

> **回答思路**  
> **背景：** 某些任务的整组 rollout 奖励都相同。  
> **任务：** 判断保留、降难度还是冷启动。  
> **做法与原因：** 区分题太难、题太易和 scorer 没区分力。  
> **结果／验证：** 有效学习信号提高且任务覆盖没有被清空。

#### 可以这样回答

某些任务的整组 rollout 奖励都相同。

全 0 或全 1 的组分不出好坏，组内优势为零，可以丢掉或降权。预算优先给当前模型偶尔能做对、多数时候还做错的中间带任务；从来没解出过的先查环境是不是坏了，再决定要不要搁置。policy update 后要重算 pass@$k$，难度分组不能一直冻着。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-passk-zero)

### GUI / 电脑使用的 Agent RL 数据，和写代码的环境差在哪？

> **回答思路**  
> **背景：** GUI 状态受视觉布局、时序和工具影响。  
> **任务：** 构建可对齐可 replay 的交互监督。  
> **做法与原因：** 固定截图动作语义，状态检查独立于模型自报。  
> **结果／验证：** 新 UI 成功与权限、坐标和延迟错误都检查。

#### 可以这样回答

GUI 状态受视觉布局、时序和工具影响。

差在观测、动作和奖励检查的对象。代码环境看 stdout、靠测试给奖励；GUI 任务是指令加初始桌面快照加状态 checker，模型读截图和无障碍树，点击、键入、滚动，奖励看文件、窗口、单元格这些最终状态。checker 要放在只读镜像里，和 agent 工作区隔离。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-gui-agent-rl)

### 没有现成 GitHub issue 池，怎么合成一批能拿来做 Agent RL 的环境？

> **回答思路**  
> **背景：** 没有现成 issue 池仍需要真实可执行任务。  
> **任务：** 从环境目标构造有效训练分布。  
> **做法与原因：** 生成状态差异和可验证目标，检查可解与多样性。  
> **结果／验证：** 新任务迁移有效，不能只在合成器偏好上进步。

#### 可以这样回答

没有现成 issue 池仍需要真实可执行任务。

没有现成 issue 池，就按技能、复杂度、资源这些维度组合出题，每题配 Docker 环境和程序 verifier，这是 Ai2 TMax 的做法。生成时只保证镜像能 build，全零题留给 RL 训练时剪掉。质量看 teacher pass@$k$ 和领域覆盖，再和 Terminal-Bench decontamination；checker 还要抽查，全对的简单题也要控制比例。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-tmax-synth)

### OpenAI Agent RFT talk：他们让客户怎么写环境和奖励？

> **回答思路**  
> **背景：** 奖励和环境接口决定可训练行为。  
> **任务：** 解释公开 RFT 中的数据职责。  
> **做法与原因：** 明确任务、可见观察、评分与 resampling。  
> **结果／验证：** 奖励有独立验证，公开接口不推成内部配方。

#### 可以这样回答

奖励和环境接口决定可训练行为。

先在接近生产的任务分布上跑 baseline，把 prompt、任务范围和工具调好，确认还有提升空间再上 RFT。每条 rollout 用独立环境；reward 先检查 correctness，通过后再评 style，不给「尝试」部分分。多次 sampling 都找不到更好的解，训练就没有学习信号。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-agent-rft-recipe)

### Codex 公开写了怎样的 Agent RL 环境？

> **回答思路**  
> **背景：** 代码 agent 依赖真实软件环境交互。  
> **任务：** 说明环境设计怎样影响学习。  
> **做法与原因：** 对照公开任务、工具和测试约束解释。  
> **结果／验证：** 不编内部数据规模，用可执行示例验证理解。

#### 可以这样回答

代码 agent 依赖真实软件环境交互。

Codex 给每个 agent 一个装好代码和依赖的云容器，trajectories 开始后断网，agent 在里面改代码、反复跑测试直到通过。正确性靠测试判，风格放在测过之后另评；断网是怕 agent 搜到标准补丁 contamination 奖励。没有 grader 的仓库，要先建好 checker 才能做 RL。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-codex-rl-env)

### Panel 情景：工具选对了，任务成功率却掉了，怎么设计诊断实验？

> **回答思路**  
> **背景：** 工具名称选对仍可能在参数或结果利用上失败。  
> **任务：** 定位调用链中真正瓶颈。  
> **做法与原因：** 逐项用 oracle 工具、参数、返回信息做 controlled substitution。  
> **结果／验证：** 能区分假设后才补数据，避免多因素同时改。

#### 可以这样回答

工具名称选对仍可能在参数或结果利用上失败。

把工具选择、参数构造、执行与结果解释拆开，利用固定工具或注入正确中间结果做受控实验。定位主要失败阶段后，再用等预算数据干预验证；单个指标的改善不能推出端到端改善。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tool-gap-factorial)

### Gemini 2.5 技术报告怎么写 Agent 向的 RL 环境和奖励？

> **回答思路**  
> **背景：** 报告中的 Agent 训练包含不同反馈来源。  
> **任务：** 提取可迁移的环境和数据原则。  
> **做法与原因：** 分开任务生成、执行验证与 policy optimization。  
> **结果／验证：** 按原文限定事实，方案要独立实验支持。

#### 可以这样回答

报告中的 Agent 训练包含不同反馈来源。

Gemini 2.5 报告把奖励分成 verifiable reward 和模型生成式奖励，agent 环境以测试、解释器、状态 assertion 当主要判定依据，模型评分补规则覆盖不到的目标，并且要做 calibration。环境要支持多步动作和工具、保存中间状态，才能审计改测试、重复执行但没有推进任务、假装运行这类 hack。直接奖励「想得长」，模型会写更长的推理却没完成任务，所以长度要和最终对错绑在一起。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-gemini-rl-env)

### Thinking Machines 的 Tinker cookbook 把 Agent RL 环境写成怎样的代码合同？

> **回答思路**  
> **背景：** 训练代码接口体现数据与环境契约。  
> **任务：** 把公开 cookbook 解释成可运行流程。  
> **做法与原因：** 跟踪 rollout、奖励、版本与 update schedule。  
> **结果／验证：** 复现接口语义，明确离线数据与在线 sampling 区别。

#### 可以这样回答

训练代码接口体现数据与环境契约。

合同是可安装的 Env 加可复现的奖励：Env 走 reset / step 接口，同一道题起一组环境，组内算 GRPO 优势。有测试的 Harbor 任务以测试结果为奖励，没有测试的文档任务先看状态 diff、再按 rubric 逐条评分。解析失败、工具次数上限和清理规则都写进合同，LLM 法官只评测试覆盖不到的项。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=dt-tinker-agent-rl)

### 一亩三分地 Apple Siri：设计搜索系统，数据与检索质量怎么贯通？

> **回答思路**  
> **背景：** 搜索结果相关不等于用户任务完成。  
> **任务：** 串起索引、检索与答案质量。  
> **做法与原因：** 先界定任务和数据，再做召回排序与证据检查。  
> **结果／验证：** 离线检索与真实任务指标共同验证。

#### 可以这样回答

搜索结果相关不等于用户任务完成。

先澄清搜索对象、权限与质量目标，再设计文档处理、候选召回、排序和评测。数据侧要解释版本、deduplication、负例与分组切分；不能只画服务架构，也不能把点击直接当成相关性真值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=p3a-apple-siri-search-design)

### 一亩三分地 Apple MLE：从简单分类器讲到完整数据系统

> **回答思路**  
> **背景：** 一个分类器还不足以构成可维护系统。  
> **任务：** 从标签到上线反馈说明完整流程。  
> **做法与原因：** 先简单 baseline，再围绕错误改数据和阈值。  
> **结果／验证：** 划分不 leakage、关键 evaluation slices 和版本监控可用。

#### 可以这样回答

一个分类器还不足以构成可维护系统。

先定义标签与误判代价，建立简单分类器，再把标注、分组切分、阈值、部署与反馈串起来。系统质量取决于标签是否稳定、输入是否一致和错误是否被监测，不是只看模型复杂度。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=p3a-apple-classifier-data-system)

### 一亩三分地 Apple AIML Infra：模型推理 Flask API，先把什么契约定义清楚？

> **回答思路**  
> **背景：** 推理服务可能收到坏请求或超预算输入。  
> **任务：** 先确定 API 和失败行为。  
> **做法与原因：** 明确 schema、资源限制、批处理与错误返回。  
> **结果／验证：** 合法输入结果稳定，异常不破坏服务隔离。

#### 可以这样回答

推理服务可能收到坏请求或超预算输入。

将 HTTP 校验、预处理、模型推理和输出序列化分开，模型随进程启动加载并固定版本。先验证输入与离线结果一致，再检查超时、并发和资源；返回200不代表模型真正算对，也不能每次请求重新加载权重。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=p3a-apple-flask-inference-contract)

### 一亩三分地 Apple AIML Infra：补全有依赖的面向对象 task pipeline

> **回答思路**  
> **背景：** 任务有依赖，执行失败会影响后继。  
> **任务：** 按依赖正确运行面向对象 pipeline。  
> **做法与原因：** 检查环与就绪节点，状态和重试语义明确。  
> **结果／验证：** 正常 DAG、失败依赖、环和重复运行都验证。

#### 可以这样回答

任务有依赖，执行失败会影响后继。

用任务 ID 保存函数和依赖，用入度与后继表做拓扑执行。一个任务只在全部前驱完成后计算，依赖结果按声明顺序传入；共享上游任务每次运行只执行一次，不能用递归重复计算整棵依赖树。

测试还要满足这个条件：正常 DAG、失败依赖、环和重复运行都验证。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=p3a-apple-task-dag-code)

### Apple MLE 原帖：相册照片怎么排序，训练信号与隐私怎样处理？

> **回答思路**  
> **背景：** 相册偏好与内容相关性涉及私人数据。  
> **任务：** 定义排序目标与合法反馈。  
> **做法与原因：** 使用许可研究或 on-device 信号，相关性和偏好分开。  
> **结果／验证：** 用户任务与隐私约束达标，不默认回收照片。

#### 可以这样回答

相册偏好与内容相关性涉及私人数据。

先明确排序要服务的任务，再将可看性、重复 cluster、事件覆盖与用户偏好分开。先用质量和多样性 baseline，再比较个性化收益；未曝光照片没有点击不能直接当负例，私人照片也不能未经授权进入基础模型训练。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=p3a-apple-photo-ranking)

### Recommendation Flywheel：观看行为怎样变成标签，又怎样避免 feedback bias？

> **回答思路**  
> **背景：** 推荐系统持续收集观看数据，但用户只能反馈已经被展示的内容。  
> **任务：** 设计 labels、evaluation 和新数据迭代，分清偏好与曝光影响。  
> **做法与原因：** 记录 exposure 与上下文，分离显式反馈和行为代理，用独立实验验证变化。  
> **结果／验证：** 体验与覆盖改善，而不是只强化已有热门内容。

#### 可以这样回答

我会先确认优化目标。观看时长可以作为信号，但它不是用户价值的完整定义；误导性内容也可能让人停留很久，所以需要结合满意度、负反馈和内容安全。

数据上我会保存哪些视频被展示、排序位置、观看过程和上下文。如果只保留点击过的视频，就无法知道用户看到了什么却没有选择，也容易把未曝光的视频当成用户不喜欢。

我会用 candidate retrieval 和 ranking 两层逐步设计。每一层都需要自己的 coverage 与质量指标，再看 end-to-end 用户体验。新反馈进入训练之前，检查标签延迟、重复事件以及 ranking policy 改变造成的 distribution shift。

这个例子可以迁移到 AFM data flywheel：模型当前的行为决定能收集到什么反馈，所以日志不是天然无偏的训练分布。但推荐点击与 assistant 正确性不同；迁移时必须重新定义任务、可验证结果和数据采集机制。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=systems&question=afm-web-video-feedback)


## 12 · 项目深挖与研究陈述

### Jiabao Ji × AFM：个人研究、Benchmark 与面试 Reference

> **回答思路**  
> **背景：** 公开研究很多，面试需要一条清晰主线。  
> **任务：** 把实际研究连接到 AFM 数据问题。  
> **做法与原因：** 用 QA、verifier 与 skill 解释具体判断。  
> **结果／验证：** 只报真实贡献和结果，设计扩展另标。

#### 可以这样回答

公开研究很多，面试需要一条清晰主线。

主线用 DeepAmbigQA 谈合成与完整性，用 HarnessLLM/HardTestGen 谈奖励可靠性，用 Skill Usage/VisualSkill 谈 feedback loop 与 multimodal，再接工具 RL、效率和遗忘评测。公开团队成果、个人职责和建议实验分开表述。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-personal-reference)

### 个人 Reference 1：DeepAmbigQA，如何把“漏答”变成 synthetic data 问题？

> **回答思路**  
> **背景：** 答案可能每句话都对却漏掉解释分支。  
> **任务：** 将完整性缺口转成可验证任务。  
> **做法与原因：** 区分消歧、检索和聚合，再做定向数据。  
> **结果／验证：** 独立答案集合与证据支持，训练收益不虚构。

#### 可以这样回答

我会讲 DeepAmbigQA。这项工作里有一个很直观的问题：有些问题里的名字对应不止一个实体，模型可能只选了其中一个，然后给出一个完全正确、但不完整的答案。只检查它说出来的内容，很容易漏掉这种失败。

我们在这篇工作里研究了这类歧义和多跳问题。对这个岗位来说，我觉得有价值的是把“答案不够全”变成可以检查的数据问题：有哪些解释、每个解释需要找什么证据、最后应该包含哪些答案。这样比只让一个 judge 给整体印象分，更容易看清缺口。

如果继续往训练上做，我会先检查模型是没发现另一种解释，还是发现了却没找到证据。前者补消歧和分支探索的例子，后者补检索或证据整合。这个训练扩展是我的方案；论文里的 benchmark 工作，以及我本人负责的部分，需要分别讲清楚。

#### 被追问时再展开

**面试官问你具体做了什么？** 回到你实际负责的数据生成、质量检查或实验模块，选一个真实决定讲清原因。公开作者名单无法替你补这一段。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-qa-completeness)

### 个人 Reference 2：HarnessLLM／HardTestGen，奖励错了比模型弱更危险？

> **回答思路**  
> **背景：** 测试会决定什么代码被奖励和保留。  
> **任务：** 把验证经验连接到 RM 数据可靠性。  
> **做法与原因：** 固定候选审计误放与 false rejection。  
> **结果／验证：** 独立下游收益支持反馈，而非自家通过率。

#### 可以这样回答

我比较直接的连接是代码验证。在我参与的测试生成研究里，我们关心的是：一个程序看起来能通过测试，它到底是不是真的正确？因为测试一旦漏掉某类错误，这些错误程序就可能被选进 training set，或者在 RL 里拿到正奖励。

我觉得这和 learned RM 有一个共同点：模型得到的是评审器的判断，而这个判断可能和我们真正想要的质量有差距。代码里可能是漏了长链这种 edge-case inputs，preference model 里可能是把回答长、语气自信当成质量好。

所以我会先看评审器在哪些样本上容易错，再决定补什么标签。然后用另一套独立检查验证模型有没有变好。我没有负责过生产级 preference model 的话，会直接说明这一点；我能深入讲的是验证反馈怎么影响数据选择和优化。

#### 被追问时再展开

**那两种奖励能直接互换吗？** 不能。代码测试对应一个明确的功能要求；preference labels 还涉及谁来评、按什么标准评，以及分歧怎么处理。共同的问题是反馈可靠性，具体标签和验证办法仍然不同。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-verifier-reward)

### 个人 Reference 3：Skill Usage，如何从评测失败构造 self-improvement feedback loop？

> **回答思路**  
> **背景：** 理想提供 skill 不代表真实检索使用有效。  
> **任务：** 用失败分层推动下一轮改进。  
> **做法与原因：** 分别修检索、选择和适配，区分运行时与权重更新。  
> **结果／验证：** 新任务迁移验证，不把文件改进冒充训练结果。

#### 可以这样回答

我会用 skill 的例子。给 agent 一条写得很好的 skill，它做得更好了，这还不能说明真实使用时也会更好，因为真实情况下它首先得找到这条 skill，还得判断什么时候用。

我们在相关研究里看了更接近这种使用方式的设置。对数据迭代来说，我会把任务失败和 skill 使用过程放在一起看。相关 skill 没找到，就先查检索；找到了却没用，要看选择；用了还是失败，再看它缺什么步骤，或者是不是没有适配当前任务。

下一轮我会围绕那个具体问题补数据，再换一批任务验证。这里也要分清两件事：把 skill 文件改得更好，是运行时改进；让模型本身学会选择和适配，需要另外的训练实验。我不会把前者的收益直接算成后者的证据。

#### 被追问时再展开

**什么时候值得训进模型？** 当同一种行为在很多任务里反复有用，而且外部 skill 已经很清楚、模型仍然不会用时，我会考虑训练。经常变化的知识则可能更适合继续放在 skill 里。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-skill-flywheel)

### 个人 Reference 4：Joint Agent–Speculator RL，预测正确是否就是好奖励？

> **回答思路**  
> **背景：** 预测策略下一步可能匹配它自己的错误。  
> **任务：** 获得分布匹配且任务有用的信号。  
> **做法与原因：** 记录策略版本，预测命中与任务反馈分别优化。  
> **结果／验证：** 净延迟、任务成功和副作用同时检查。

#### 可以这样回答

一个具体例子是我们做的下一次 tool calls 预测。agent 运行以后，会留下“在这段历史之后，它实际调用了什么工具”的记录。这些记录可以拿来训练预测器，而且比一个完全不同的模型生成的 trajectories，更接近当前 agent 的行为。

但我会特别注意，预测正确和任务正确不是一回事。假如 agent 本来就要调用一个错误工具，预测器猜中了，也不代表用户的任务完成得更好。所以我会同时看调用预测和最后的任务结果。

另一个问题是策略会变。训练了几轮以后，它的调用方式可能已经不同了，旧 trajectories 就没那么合适。我会保留 trajectories 对应的模型版本，并检查新策略上的表现。至于是否真的节省时间，还得算上预测开销和白做的调用，不能只拿命中率来推断。

#### 被追问时再展开

**可以提前执行所有预测的工具吗？** 不能一概而论。只读查询和会创建订单、改文件的调用风险不同；写操作需要单独的执行条件和权限判断。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-joint-tool-rl)

### 个人 Reference 5：VisualSkill，怎么讲真实 multimodal 数据与评审偏差？

> **回答思路**  
> **背景：** 图文技能的增益可能混入更多内容。  
> **任务：** 确定视觉信息的真实贡献。  
> **做法与原因：** 同源文字对照，agent 与工具固定。  
> **结果／验证：** 状态型和 VLM 评价分开，个人分工据实说明。

#### 可以这样回答

我会用参与的 VisualSkill 工作来讲。界面操作里，有些东西用文字解释很费劲，一张图可能更直接，比如按钮在对话框的哪个位置。但图片也会占上下文，过期的截图甚至可能误导模型，所以我关心的是它在哪些任务上有实际帮助。

如果做对照，我会尽量让文字版和图文版来自同一份材料，用相同的 agent 和工具跑。否则图文版多知道了几个操作步骤，最后分数更高，也很难说是视觉信息带来的。

评价这里也有一个我觉得值得讨论的点：看截图给分，和检查文件、应用状态，测到的东西可能不同。一个表格外观很整齐，数字仍然可能填错。我会把这些结果分开看，再抽查它们不一致的任务。具体我本人负责了哪部分，面试时仍然按实际贡献来讲。

#### 被追问时再展开

**这等于训练过 multimodal 模型吗？** 不一定。这是 multimodalagent、技能内容和评价的研究。有没有更新视觉模型权重，需要按实际实验回答。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-visual-setting)

### 个人 Reference 6：Unlearning，如何把 forget/retain 研究接到数据治理？

> **回答思路**  
> **背景：** 原问法答不出不等于信息不可提取。  
> **任务：** 解释遗忘与保留的 evidence limitations。  
> **做法与原因：** 多问法攻击、retain 效用和来源追踪结合。  
> **结果／验证：** 限定威胁模型，不把研究方法当删除认证。

#### 可以这样回答

我觉得最直接的联系是，数据要撤回以后，我们怎么知道模型的行为真的改变了。在 unlearning 研究里，一个很容易产生误解的结果是：原来的问题答不出来了，但换一种问法，信息又出来了。

所以我会同时看忘记和保留两边。目标信息是否还能通过改写或间接问题取出来，其他正常能力有没有受到影响。只看原问题的准确率下降，我觉得证据还不够。

如果接到实际数据流程，我还会先检查数据来源和版本。模型这次做了 unlearning，但下一轮训练又把同一来源加回来，问题仍然存在。我的研究可以支持我讨论这些评价和权衡；它不能自动证明我处理过用户私有数据，也不能保证一种方法删除了所有可能提取的信息。

#### 被追问时再展开

**那 unlearning 能替代数据许可吗？** 不能。允许不允许收集和训练，应当在前面决定。unlearning 是已经训练之后可能采用的一种补救办法，还需要验证。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-ref-unlearning-governance)

### 三条可讲到底的数据 Pipeline：Skill／Harness、Code 与 multimodal Tool Use

> **回答思路**  
> **背景：** 不同任务需要不同的可验证反馈。  
> **任务：** 选一条能讲清数据到改进的 pipeline。  
> **做法与原因：** skill、code 和视觉操作分别确定真值与训练视图。  
> **结果／验证：** 独立任务收益成立，示例不冒充已采集数据。

#### 可以这样回答

不同任务需要不同的可验证反馈。

把三条 pipeline 分别落到技能选择与适配、代码 verifier、截图驱动工具操作。每条都有任务、数据契约、data quality checks、训练视图、独立评价和反馈迭代；已公开方法和建议扩展分别说明。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-pipeline-overview)

### Pipeline 1：从 Skill 检索与执行失败，造出可训练的适配 trajectories

> **回答思路**  
> **背景：** agent 可能没找到或没用好现成 skill。  
> **任务：** 决定应该补哪一类训练 trajectories。  
> **做法与原因：** 先做 oracle skill 对照，再收选择和适配例子。  
> **结果／验证：** 未见任务有效，不能只提高加载率。

#### 可以这样回答

我会先找一批已经能自动验收的任务，让 agent 带着现有 skill 跑一遍。比如让它整理一份有重复记录的 CSV，最后检查输出的统计有没有把重复数据算进去。这样我知道任务到底做对没有，也能回头看它用了哪条 skill。

接下来我想分清楚失败发生在哪。有时相关 skill 已经搜出来了，agent 却没打开；有时它打开了，但是文档里的列名和当前文件对不上。前一种情况，我会收集选择 skill 的例子；后一种情况，就收集把已有方法改到当前任务上，以及出错后怎么恢复的 trajectories。把这些混在一起，只说“多收一些成功数据”，很难知道模型学到了什么。

开始时我会先做一轮 SFT，用实际跑对、过程也合理的 trajectories 教这些行为。新一轮再看没见过的任务组合有没有变好。如果只在原来的 CSV 格式上提高，我会怀疑它记住了模板。等任务和检查方法比较稳定，再考虑在线 RL；这个阶段最重要的是先确认我收的数据确实对应那个失败原因。

#### 被追问时再展开

**怎么知道是检索的问题，还是模型不会做？** 我会直接给它一条确认相关的 skill 再跑。如果这样能做对，先查检索和选择；如果仍然失败，就看 skill 内容和执行过程。这个对照比直接重训便宜。

**需要记录哪些东西？** 我最先要的是任务、当时能看到的信息、搜到和打开的 skill、tool calls，以及最后的检查结果。具体存储字段我会在实现时补齐，先保证能用一条记录解释一次失败。

#### 英文口述参考

I would start with tasks that already have a reliable checker, and run the agent with the skills it currently has. What I want to understand is why the skill did not help. Did the agent fail to retrieve it, choose not to open it, or use it incorrectly?

Those cases need different data. If the skill was available but ignored, I would collect examples of when to load it. If the agent loaded it but could not adapt it, I would collect successful adaptations and recovery attempts. I would start with supervised training on verified traces, then check whether the improvement transfers to new tasks. Before collecting more data, I would also try giving the agent the right skill directly. That tells me whether retrieval is actually the bottleneck.

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-pipeline-skill-harness)

### Pipeline 2：从正确解、错误解与困难测试，构造代码 post-training 数据

> **回答思路**  
> **背景：** 错解可能通过不完整测试进入训练。  
> **任务：** 先获得可靠的代码反馈。  
> **做法与原因：** 补定向困难输入，并用正确程序检查 false rejection。  
> **结果／验证：** 固定训练条件换 verifier，独立题验证收益。

#### 可以这样回答

我最担心的是我们生成了很多代码，测试也都通过了，但里面其实有错解。如果这些代码拿去做 SFT，或者测试结果拿来做 RL 奖励，模型反而会越来越擅长通过不完整的测试。

所以我会先从一批题意和正确解比较可信的题开始。每道题生成几个候选解，然后针对常见错误补测试。比如树上的题，随机生成的树可能都比较平衡，一个低效算法看起来也能跑完；换成很长的链，它的问题才会暴露。这时我需要补的是这种输入，而不只是继续生成更多随机树。

不过，测试更严格也不一定更好。我还要拿确认正确的程序跑一遍，看看有没有错误 assertion、非法输入，或者机器太慢造成的误判。等这两边都检查过，再用测试筛 SFT 数据，或者给当前模型的代码打奖励。

最后我会固定训练题和训练预算，只换测试这一个因素，看模型在另一批题上是否更好。训练时的通过率涨了，只能说明它更会过这套测试；我还想知道代码能力有没有真的提高。

#### 被追问时再展开

**错误程序从哪来？** 优先用模型实际写错的程序，因为它们更接近训练时会遇到的错误。也可以人为改出 edge-case bugs，但要先确认改出来的程序确实错了。

**两个程序都通过，preference labels 怎么给？** 我不会仅凭哪个解释更长来选。功能上还分不出好坏，就先保留这种不确定；如果要比较效率，需要额外的、可靠的性能测量。

#### 英文口述参考

The part I would be most careful about is the verifier. If the tests let a wrong solution pass, that solution can become SFT data or receive a positive RL reward.

I would start with problems and reference solutions I trust, generate candidate programs, and add tests for the mistakes those programs make. A simple example is a tree problem where random balanced trees fail to expose an algorithm that becomes too slow on a long chain. I would also run known-correct programs through the tests, because a bad assertion or an unrealistic timeout can reject good code.

Once the tests look reliable, I would use them for data selection or rewards. To measure the benefit, I would keep the training problems and compute fixed, change the verifier, and evaluate on separate problems.

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-pipeline-code-verifier)

### Pipeline 3：从票据截图到表格操作，合成 multimodal Tool-Use 数据

> **回答思路**  
> **背景：** 读图与界面操作都可能造成填表错误。  
> **任务：** 采集对齐且可检查的 tool-use trajectories。  
> **做法与原因：** 合成真值、动作前截图和导出文件核验。  
> **结果／验证：** 新布局有效，读图错与点击错分别补数据。

#### 可以这样回答

我会选一个比较容易检查结果的任务，比如给 agent 一张票据截图，让它把日期、币种和总额填进表格，再导出文件。这样既要读图，也要实际操作软件，最后还有一个可以检查的结果。

最开始我会用合成票据。先确定日期和金额，再把它们渲染成不同样式的图片，所以我知道正确答案是什么。让 agent 在固定的软件环境里操作，记录它每一步看到的截图和接下来的动作。结束以后，我直接检查导出的表格，不能因为 agent 说“已经完成”就算成功。

如果金额填错了，我会先看它是把图读错了，还是知道金额却填错了格子。比如小计是115，总额是128.50，它填了115，这更像是字段理解的问题；如果它正确说出了128.50，却输入到日期那一格，问题就更接近界面操作。这两种错误，我会补不同的数据。

训练时先用实际完成、过程也合理的 trajectories。评价时换一批票据布局，而不只是换金额。如果换个排版就不会了，说明它可能记住了位置，没有真正学会找总额。这条 pipeline 是我会设计的扩展；和我参与的 VisualSkill 工作可以连接起来讲，但不能把这套票据实验说成已经做过。

#### 被追问时再展开

**为什么不用 OCR 加脚本？** 我会把它作为 baseline。如果固定票据模板用 OCR 就能很好解决，那没有必要强行做复杂 agent。这个例子更适合需要理解变化的页面、再跨软件完成操作的场景。

**数据怎么扩大？** 我会根据真实失败补变化，比如小计和总额很接近、日期格式不同、表格需要滚动。先确认是哪一种变化带来错误，再生成对应的新样本，而不是只把同一个模板复制很多遍。

#### 英文口述参考

I would use a task with an outcome I can check, such as reading a receipt image, entering the date and total into a spreadsheet, and exporting the file.

I would begin with synthetic receipts, so I know the correct fields before rendering the image. During collection, I would record the screenshot the agent saw before each action. Afterwards, I would inspect the exported spreadsheet. The agent saying it succeeded would not be enough.

If it failed, I would separate reading errors from action errors. Entering the subtotal instead of the total suggests a different data problem from reading the amount correctly but typing it into the wrong cell. I would collect examples for the failure I actually observed, and test on new receipt layouts to see whether the model learned more than a fixed screen position.

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-pipeline-mm-tool-use)

### HM 30 分钟：怎么把项目讲成「数据解锁了能力」？

> **回答思路**  
> **背景：** 项目需要说明数据为何改变能力。  
> **任务：** 讲清本人决策而非罗列技术。  
> **做法与原因：** 从具体缺口、baseline、干预和对照展开。  
> **结果／验证：** 用真实数字、成本和局限回答追问。

#### 可以这样回答

我会先把项目压成一个具体问题：模型原来在哪类任务上不行，这件事为什么重要。接着说明我负责的数据或评价环节，让面试官知道哪些决定是我做的。

主体只讲一个最关键的选择：我为什么认为问题在数据上，改了什么，为什么没有先换模型。最好能拿一个失败样本和一个对照实验来解释，而不是从头报完所有组件。

最后讲真实结果和代价，包括新任务改善、旧能力有没有受影响，以及仍没证明的部分。结果是团队做出来的，就明确说团队结果和我的贡献。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-data-story)

### Director：pre-training / mid-training / post-training 的数据策略怎么切？

> **回答思路**  
> **背景：** 知识覆盖和行为格式属于不同缺口。  
> **任务：** 决定数据应投哪个训练阶段。  
> **做法与原因：** 按能力来源、预算和遗忘风险做阶段对照。  
> **结果／验证：** 目标与 regression tasks 证据支持，不靠阶段名称判断。

#### 可以这样回答

我会先判断这个问题是不会，还是会但没有按需要表现出来。比如一种语言的基本理解和知识都很弱，少量聊天示范通常补不了整个 base model 覆盖。

这类问题我会比较 pre-training 或 continued pre-training 的数据干预。如果基础能力已经有了，主要是工具协议、回复格式或拒答方式不对，就更接近 post-training。领域材料和 long context 覆盖，也要看当前 base model 和 training recipe，不能只靠阶段名字分类。

我会先用小规模对照看目标能力、旧能力和成本，再决定投入哪一段。不会把所有缺口都默认变成再加一批 SFT。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-pre-mid-post)

### Why Apple, why now：怎么讲出你对 data-centric 的兴趣？

> **回答思路**  
> **背景：** 泛泛赞美公司不能解释岗位匹配。  
> **任务：** 说明为何想做这个数据问题。  
> **做法与原因：** 用真实研究连接质量、评测和隐私约束。  
> **结果／验证：** 贡献范围可证明，动机能接具体工作。

#### 可以这样回答

我会从这个岗位具体要解决的问题讲起，比如怎样把模型反馈变成更可靠的数据，而不是泛泛讲我喜欢 Apple 的产品。

然后连接自己的真实研究：我在哪个项目里处理过任务生成、验证反馈或能力诊断，哪些经验能直接迁移。选择一两个最相关的例子就够，个人责任和论文结果按事实讲。

最后说明希望进一步承担什么工作，例如从研究 setting 走到更大规模的数据迭代。这个部分可以表达兴趣，但不把没做过的生产经验包装成已经掌握。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-why-apple)

### HM：讲一次数据干预失败了，你怎么知道失败、后来改了什么？

> **回答思路**  
> **背景：** 数据实验失败也能体现判断能力。  
> **任务：** 说明何时发现原假设不成立。  
> **做法与原因：** 讲事前预测、反证、修复或停止。  
> **结果／验证：** 结果与损失据实，区分学到什么和后来补救。

#### 可以这样回答

我会选一次自己最初判断有问题的数据实验。先说当时为什么认为这批数据会有用，让面试官知道这是一个可以检验的假设，而不是事后总结。

再讲第一个反证是什么。比如合成题涨得很快，真实来源的任务却不动；或者目标能力提高，另一个重要 evaluation slices 持续下降。我具体做了哪些检查，何时决定停或改方案，也要说清楚。

最后讲真实损失和后来改变的工作方式。失败本身不用包装成成功，关键是我有没有及时识别，以及有没有把下一次实验做得更容易判断。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-failed-data-bet)

### HM：能力缺口和隐私 / 许可打架，你站哪边？

> **回答思路**  
> **背景：** 最有帮助的候选数据也可能不允许训练。  
> **任务：** 在合法来源内补能力缺口。  
> **做法与原因：** 区分单次推理、本地适配和全球训练用途。  
> **结果／验证：** 许可与效果都可验证，不用匿名化代替授权。

#### 可以这样回答

最有帮助的候选数据也可能不允许训练。

来源限制守住，能力缺口换合法的路补。先分清要改进的是全球基础模型、当前这次推理，还是这台设备上的 adapter：用户交互默认不进全球训练，PCC 推理也不等于拿到训练许可。来源不合格就换许可研究集、合成任务或 on-device 方案，匿名化替代不了使用授权。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-legal-capability)

### Director / VP：论文一分钟怎么讲，才像 data team 的贡献？

> **回答思路**  
> **背景：** 一分钟无法覆盖论文所有细节。  
> **任务：** 讲核心问题、贡献和最可靠证据。  
> **做法与原因：** 挑一个与数据岗位相关的对照和局限。  
> **结果／验证：** 结果来自论文，个人贡献明确且经得起追问。

#### 可以这样回答

我会先用一句话说论文要解决什么具体问题，再说最接近的方法为什么还不够。方法只讲那个真正改变结果的部分，不从相关工作列表开始。

证据我会选一个最可靠的对照，说清固定了什么、改了什么，以及论文实际报告的结果。自己的贡献单独说，合作者负责的部分也说明。

最后留一句局限，以及这件事和 AFM 的数据问题有什么联系。如果没有自己的发表经历，就明确介绍一篇读过的工作，不把它讲成个人项目。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-paper-pitch)

### Director：怎么证明一批数据值得投入？

> **回答思路**  
> **背景：** 生成量大不代表投入值得。  
> **任务：** 按预算决定继续或换方案。  
> **做法与原因：** 把标注、执行、训练和验收计入边际成本。  
> **结果／验证：** 每单位成本的独立收益及风险支持投入。

#### 可以这样回答

生成量大不代表投入值得。

按数据源一行一行报：目标任务的提升、regression tasks 有没有掉、contamination rate，以及花掉的 GPU 小时和人工小时。再测边际收益，这个源再加 10% 目标任务还涨不涨，涨不动就停止扩量。条数和 token 数只说明规模，证明不了价值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-cost-per-gain)

### Director 情景：self-training 连续三轮涨分，为什么你仍可能建议暂停？

> **回答思路**  
> **背景：** 连续涨公开榜仍可能是适配和奖励偏差。  
> **任务：** 作出继续、缩小或暂停的决策。  
> **做法与原因：** 检查独立任务、long-tail、成本和新信息来源。  
> **结果／验证：** 预设条件和可反证据明确，未证明收益就不承诺。

#### 可以这样回答

连续涨公开榜仍可能是适配和奖励偏差。

连续涨分可能来自共同评价盲点、模板重复和对固定测试的过度适配。是否继续，应看独立迁移、覆盖、真实错误和单位预算收益，并让生成、筛选与最终验证保持足够独立。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-senior-stop-selftrain)

### Director 情景：small model 筛出的最佳 data mixture，large model 上失效，下一步投什么？

> **回答思路**  
> **背景：** small model 选出的 mix 可能在 large model 失效。  
> **任务：** 判断规模迁移是否成立。  
> **做法与原因：** 控制训练预算与数据，少量 large model 对照验证。  
> **结果／验证：** 按真实 large model 收益重新分配预算。

#### 可以这样回答

small model 选出的 mix 可能在 large model 失效。

small model 实验是筛选证据，不保证排序跨规模保持。检查训练阶段、token 预算、容量与目标任务差异，在少量代表配方上做跨规模验证，再决定继续调数据还是修代理实验设计。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=dt-senior-proxy-scale-reversal)

### Apple AIML 研究面经：为什么需要 reasoning，你的研究证明了什么？

> **回答思路**  
> **背景：** 更长思考未必解决目标任务。  
> **任务：** 解释研究为何需要推理。  
> **做法与原因：** 用具体失败和简单 baseline 证明必要性。  
> **结果／验证：** 收益 attribution 清楚，也说明不需要推理的场景。

#### 可以这样回答

更长思考未必解决目标任务。

先说任务需要哪种可检验的多步能力，再用相同模型、任务和 inference budget 比较直接回答、推理或搜索方案。研究贡献应落在新增能力与证据上；更长的回答、单个榜单涨分或流畅的思考过程，都不能单独证明 reasoning 有效。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=p3a-apple-research-why-reasoning)

### Apple AIML 面经：为什么用这个 data mix，你验证过哪些替代方案？

> **回答思路**  
> **背景：** 当前 data mix 只是众多可能方案之一。  
> **任务：** 为数据 mix 提供可检验证据。  
> **做法与原因：** 说明候选、预算、ablation study 和被排除替代方案。  
> **结果／验证：** 独立 evaluation slices 与规模复测支持，未试的不说最优。

#### 可以这样回答

当前 data mix 只是众多可能方案之一。

先说明 data mix 按文档、样本还是 token 计算，再给当时目标、候选配方和同预算对照。区分目标能力收益、其他能力回归与重复 sampling 成本；若只有一组经验 data mix，就坦承尚未证明最优，并提出预算内最有区分力的下一组实验。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=p3a-apple-aiml-mixture-defense)

### Apple AI 项目追问：data gap、model choice、eval 与 production readiness 怎样讲清楚？

> **回答思路**  
> **背景：** 面试官围绕同一个 AI 项目连续追问，泛泛介绍无法支持技术判断。  
> **任务：** 用真实职责连接 data gap、模型选择、评估证据和上线条件。  
> **做法与原因：** 选一个本人能解释的项目，明确已做部分、公开结果与拟议扩展。  
> **结果／验证：** 回答能经得住追问，缺少线上结果时不虚构发布经历。

#### 可以这样回答

我会选一个我能解释失败样本和个人贡献的项目，而不是只挑名称最像 AFM 的项目。开场先说具体任务、原有方法的不足，以及我实际负责哪一部分。

对于 data challenges，我会拿一个真实 failure case 说明问题：它为什么发生，我们凭什么认为是数据覆盖或标签问题，而不是模型或 evaluation 的错误。然后再讲我实际做过的处理，以及没有尝试过的替代方案。

Model choice 需要对应约束，比如算力、latency、输入形式和 baseline。评估则说明 split、主要指标、关键 slices 和失败分析。如果项目只做了 research evaluation，我就明确说没有生产上线，不把 benchmark 结果说成用户收益。

如果被问到 production readiness，我会补充“如果产品化，我会怎样验证”：包括独立任务集、真实环境兼容性、privacy review、监控和 rollback。这些是后续设计，而不是已经完成的履历。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=projects&question=afm-web-apple-project-deepdive)


## 13 · Culture 与协作

### Culture：See Around Corners，怎么讲「缺口还没爆，我先用数据堵了」？

> **回答思路**  
> **背景：** 总指标正常时仍可能出现未来风险。  
> **任务：** 讲一次有事前证据的能力预判。  
> **做法与原因：** 说明当时信号、判断、行动与最小验证。  
> **结果／验证：** 真实时间线和结果，不能事后修复改成预判。

#### 可以这样回答

这道题我会选一个真的有事前证据的经历来讲，不能把问题已经爆发以后的修复包装成提前预判。

可以这样组织：“当时[整体指标或当前功能]还正常，但我从[具体 evaluation slices 或下一步需求]里发现了[风险]。我担心[哪种条件变化后会出问题]，所以先做了[小实验或数据干预]。”这里都要换成自己的事实。

最后再讲真实结果：风险是否被证实，干预有没有帮助，哪些判断后来发现不准。如果没有这种产品经历，也可以讲研究中提前发现评价盲点的过程，但要保留真实时间线。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=culture&question=dt-see-around-corners)

### Culture：你停过哪一批数据，理由是什么？

> **回答思路**  
> **背景：** 团队可能想继续用一批有问题的数据。  
> **任务：** 解释为何暂停及怎样推进决策。  
> **做法与原因：** 用 contamination、质量或许可证据隔离来源。  
> **结果／验证：** 真实影响与恢复条件清楚，个人贡献不夸大。

#### 可以这样回答

我会挑一次真的暂停过数据来源的经历，先说明为什么当时大家还想继续用它。这样面试官才能理解这个决定有什么难度。

然后讲我拿到了什么证据，例如 evaluation contamination、错误标签、持续 negative transfer，或者许可不满足。需要说清我负责的是发现、验证还是推动停用，不把整个团队的工作都归到自己身上。

结果也按实际讲：停用后哪些指标恢复，付出了什么代价，有没有定义将来重新启用的条件。还没测到的收益就不补数字。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=culture&question=dt-killed-dataset)

### Culture 演练：提前预警被证明只对了一半，你怎么讲判断与纠错？

> **回答思路**  
> **背景：** 提前预警可能只有一部分被证实。  
> **任务：** 表现判断与纠错能力。  
> **做法与原因：** 分开当时依据、后来反证和修正。  
> **结果／验证：** 承认不准部分，讲真实行动而非完美故事。

#### 可以这样回答

提前预警可能只有一部分被证实。

用当时能获得的证据讲风险预测，并说明预设的验证与停止条件。预判只有部分成立时，区分判断正确、attribution 错误和无效投入，讲清如何修正，不能用事后结果改写早期动机。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=culture&question=dt-culture-falsifiable-warning)

### Culture 演练：发布前发现 evaluation protocol 错了，怎样纠正又不让协作停摆？

> **回答思路**  
> **背景：** 发布前发现 evaluation protocol 有错。  
> **任务：** 纠正结论并协调依赖团队。  
> **做法与原因：** 先说明影响范围，再复测与调整发布计划。  
> **结果／验证：** 可信结果恢复且协作继续，时间代价据实。

#### 可以这样回答

发布前发现 evaluation protocol 有错。

先用最小复现 quantization 决策影响，再提出可执行的修复和临时发布范围，清楚说明证据与未知项。讲真实经历中的责任与沟通，既不隐藏问题，也不把合作方塑造成不在乎质量的人。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=culture&question=dt-culture-eval-deadline)

### 一亩三分地 Apple 文化主题延伸：Simplicity 与 Build Trust 怎么讲数据项目？

> **回答思路**  
> **背景：** 复杂流程和不透明结论会伤害协作。  
> **任务：** 用真实项目解释简化与信任。  
> **做法与原因：** 讲一个删掉复杂度或公开不确定性的决定。  
> **结果／验证：** 效果与合作反馈可核对，不背文化口号。

#### 可以这样回答

复杂流程和不透明结论会伤害协作。

Simplicity 讲你如何减少真实复杂度，并用质量、成本或恢复能力验证；Build Trust 讲你怎样暴露不确定性、兑现承诺和处理分歧。两者都需要真实行动与结果，不能只背价值观词语。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=culture&question=p3a-apple-simplicity-trust-practice)


## 14 · 全流程模拟与个人材料

### 45 分钟模拟 A：从零完成 PyTorch 分类训练并口述 data pipeline

> **回答思路**  
> **背景：** 输入已划分的数值特征 x/vx 与 binary labels y/vy；只需训练指定的线性二分类器。  
> **任务：** 返回 standardized-space 参数、训练统计、validation probabilities、NLL、accuracy 和 update 次数。  
> **做法与原因：** 训练数据拟合 mean/std，零初始化 Linear，以固定顺序执行 mini-batch SGD；validation 只做 eval/no_grad。  
> **结果／验证：** 单 epoch 的手算例子得到 weight=0.05、bias=0、steps=1；更换 validation 不得改变训练结果。

#### 可以这样回答

这道题的输入已经是数值 features 和 0/1 labels，不需要下载数据或选择复杂模型。我会先只在 x 上拟合 mean 和 population std，再把同一变换应用到 training 和 validation。

模型固定为零初始化的 Linear，带 bias。每个 epoch 按输入顺序做 mini-batch SGD，最后不足一批也单独更新，loss 按该批样本数平均。Epochs 为零时不更新参数，但仍返回 preprocessing statistics 和 validation 指标。

我会检查题面的手算场景：x 为 -1、1，标签为 0、1；一个 full-batch update、lr=0.1 后，weight 应为 0.05、bias 为 0、steps 为 1。然后检查 constant features、末批以及 validation isolation，最后再讨论十亿行数据如何分片和恢复。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-mock-screen-a)

### 45 分钟模拟 B：preference data 清洗、RM 训练与 bias 审计

> **回答思路**  
> **背景：** preference labels 和偏差审计需要同时讲清。  
> **任务：** 跑通 RM 并解释分数何时可信。  
> **做法与原因：** 共享 scorer 训练，固定候选查长度和位置。  
> **结果／验证：** calibration、选择质量与训练隔离均检查。

#### 可以这样回答

preference labels 和偏差审计需要同时讲清。

先确认偏好、tie 和 confidence weight 的含义，再训练 RM，最后检查长度、位置与 source bias。模型跑通后仍要用独立执行结果判断选择质量。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-mock-screen-b)

### 附件诊断 1：总体成功率涨了，两个任务桶为什么都退化？

> **回答思路**  
> **背景：** 总体上涨可能来自任务构成变化。  
> **任务：** 用附件重算指标并诊断工具失败。  
> **做法与原因：** 固定 mix 权重，再按选择、参数和状态 replay。  
> **结果／验证：** 拿到配对独立结果后再决定干预和发布。

#### 可以这样回答

总体上涨可能来自任务构成变化。

先用统一分布重算指标，再用错误样本区分工具选择、参数与状态核验。当前汇总表只能说明分布混杂，不能单独证明某个训练源导致退化。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-mock-debug-tools)

### 附件诊断 2：RM 分和自动胜率上涨，真实工具成功却下降

> **回答思路**  
> **背景：** 奖励和胜率提高却不代表工具成功。  
> **任务：** 区分生成、排序和评价的错误。  
> **做法与原因：** 扫描 N 并审计顺序、长度与 model-family bias。  
> **结果／验证：** 独立执行支持改进，示意数据不作总体推断。

#### 可以这样回答

奖励和胜率提高却不代表工具成功。

将候选生成、奖励排序、judge 测量和任务真值拆开检查。扫描 best-of-N、交换位置、核对高分错例，再决定修 RM 数据、评测协议还是生成策略。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-mock-debug-reward)

### 贯穿案例：截图创建日历事件，从合成到评测再到偏好 feedback loop

> **回答思路**  
> **背景：** 截图到日历需要视觉证据和状态安全。  
> **任务：** 串起生成、训练、评测与反馈。  
> **做法与原因：** 任务真值与 executor 独立，每轮只改确认的缺口。  
> **结果／验证：** 新模板成功、无重复写入并符合 privacy requirements。

#### 可以这样回答

截图到日历需要视觉证据和状态安全。

用同一个任务贯穿视觉证据、字段抽取、工具执行、恢复 trajectories、偏好选择和隐私反馈。每轮只针对确认的缺口改数据，并用独立任务和副作用指标验收。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-case-endtoend)

### 个人材料包：主项目、失败、提前预判、multimodal 与论文的可填写模板

> **回答思路**  
> **背景：** 模板不能自动变成个人项目经历。  
> **任务：** 准备可核对的项目和论文材料。  
> **做法与原因：** 按问题、职责、选择、对照、结果填写。  
> **结果／验证：** 未知写未测，实际贡献和时间线一致。

#### 可以这样回答

模板不能自动变成个人项目经历。

把每个故事绑定真实证据、个人贡献和时间线，分别准备60秒、90秒和5分钟版本。没有经历的地方保留空白或标为设计方案，不能把示范改写成个人业绩。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-personal-evidence-pack)

### Panel 五场模拟：四轮技术＋一轮 Culture 的题目、追问与评分

> **回答思路**  
> **背景：** 五场面试需要不同主线和连续追问。  
> **任务：** 把知识转成可交流的完整方案。  
> **做法与原因：** 每场练澄清、选择、证据和变化约束。  
> **结果／验证：** 按手册自拟标准复盘。

#### 可以这样回答

五场面试需要不同主线和连续追问。

四场技术分别练飞轮、合成、诊断和偏好，第五场使用真实提前预判故事。每场45分钟，有统一 scoring rubric、追问时点与复盘记录。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-panel-rubric)

### Director／VP 30 分钟模拟：预算、阶段选择与暂停 self-training

> **回答思路**  
> **背景：** 预算与风险变化时需要作出优先级决策。  
> **任务：** 先给结论，再解释本周投入。  
> **做法与原因：** 用低成本诊断和一项可 attribution 实验确定方向。  
> **结果／验证：** 里程碑、停止条件和改判证据具体。

#### 可以这样回答

预算与风险变化时需要作出优先级决策。

先给可执行决策，再用证据解释取舍。面试官连续改变预算、来源和风险约束，候选人须说明哪些结论保持、哪些需新实验，而不是每次重新堆术语。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=mock&question=afm-director-mock)


## 15 · 研究案例与跨团队迁移

### 准备三个案例，回答大部分「什么是好数据」类问题

> **回答思路**  
> **背景：** 抽象数据问题需要具体案例支撑。  
> **任务：** 准备自己的主案例和公开研究对照。  
> **做法与原因：** 围绕一个关键决定讲问题、做法和证据。  
> **结果／验证：** 个人经历与他人成果分开，结果可核对。

#### 可以这样回答

抽象数据问题需要具体案例支撑。

准备一个自己的案例和两个公开研究案例。被问到「什么是好数据」这种抽象问题时，先用一句话回答，再说「拿实际参与的 X 举例」，讲其中最相关的那一步。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-map)

### 各家 data 岗公开在问什么？

> **回答思路**  
> **背景：** 不同实验室常用相似的数据问题追问。  
> **任务：** 识别可迁移方法和 company attribution。  
> **做法与原因：** 按任务归类公开题，再解释本岗的数据选择。  
> **结果／验证：** 来源和限制明确，不把二手题当内部事实。

#### 可以这样回答

不同实验室常用相似的数据问题追问。

这张卡按题型列出各家 data 岗公开在问什么，大多是同一组数据方法：网页抽取与 deduplication、data mix、代码执行合成、工具与 GUI trajectories、偏好标注、诚实评测，以及 data leakage 和 synthetic data 坍缩。每题都先给选择，再讲方法为什么有效、哪里要调，最后说数据从哪来、谁来验证；涉及用户日志的题，先确认这类来源能不能用。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-labs-map)

### 案例 1/4：agent 做网页设计很弱，怎么确定弱在哪？

> **回答思路**  
> **背景：** 网页能运行却仍让用户觉得质量差。  
> **任务：** 把可用性和视觉设计失败拆开。  
> **做法与原因：** 分层评价渲染、功能和设计，检查实际样本。  
> **结果／验证：** 证据支持先补设计判断，而非盲增代码数据。

#### 可以这样回答

网页能运行却仍让用户觉得质量差。

先把「不好看」拆开：能不能渲染、功能能不能用、设计好不好，分开打分，再去数失败样本落在哪一层。公开案例中的团队拆完发现页面大多能跑、功能也基本对，问题集中在设计都长一个样，说明模型缺的是设计上的取舍，所以下一步先试 skill。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-web-diagnose)

### OpenAI：无标 corpus 里怎么挖「新」数据并 bootstrap？

> **回答思路**  
> **背景：** 未标注 corpus 很多，人工只能看少量。  
> **任务：** 从 seed 逐轮发现有价值的新覆盖。  
> **做法与原因：** 质量、新颖度和不确定性结合，人工复核更新。  
> **结果／验证：** 独立能力收益持续才迭代，不只找离群噪声。

#### 可以这样回答

未标注 corpus 很多，人工只能看少量。

从少量 seed 开始迭代：seed 来自冻结评测的失败案例、研究集和许可领域 hard examples，用小分类器给未标注数据打分，综合质量、新颖度和不确定性挑出值得人看的样本，标完更新分类器再筛下一轮。分类器可以用合成标签起步、按语言做 calibration；每轮看冻结评测有没有真的改善，边际收益停了就停。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-novel-bootstrap)

### 案例 2/4：先写 test-time skill 补能力，什么时候该训进权重？

> **回答思路**  
> **背景：** base model 可能已有能力但缺有效引导。  
> **任务：** 用低成本方法检验缺口是否可唤起。  
> **做法与原因：** 先在上下文加 skill 与同任务 baseline 对照。  
> **结果／验证：** 收益稳定且调用成本高时再考虑训练内化。

#### 可以这样回答

base model 可能已有能力但缺有效引导。

先写一份几百 token 的设计 skill 放进上下文，当天就能对照。skill 能修好的部分说明模型会、只是缺引导，适合之后训进权重；修不好的才要去造数据。效果稳定、调用频繁、上下文成本明显的时候，就该把它训进模型。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-web-skill)

### OpenAI 练习题：用户对话怎么做成 SFT？

> **回答思路**  
> **背景：** 生产对话不自动具有训练许可。  
> **任务：** 合法构建对话监督数据。  
> **做法与原因：** 先确认用途再筛质量，或用许可研究集复现。  
> **结果／验证：** 许可、版本和标签可信，隐式反馈偏差被审计。

#### 可以这样回答

生产对话不自动具有训练许可。

先确认这些对话有没有训练许可，再过 data quality checks：PII、毒性、deduplication、可复现的数据版本都要查。没有许可的生产日志，换成知情同意的研究集、许可 corpus 和按失败类型合成的复现。日志做了匿名化也不等于获得训练许可，点赞、重试这类隐式信号还要处理偏差。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-userlog-contrast)

### 案例 3/4：用 rejection sampling + SFT + RL 把 skill 训进模型，哪些样本算好数据？

> **回答思路**  
> **背景：** 运行时 skill 有效但长期占上下文。  
> **任务：** 判断能否将行为迁移到模型权重。  
> **做法与原因：** 带 skill 做 sampling 筛选，去 skill 训练并独立验收。  
> **结果／验证：** 不带 skill 的新任务也改善，避免只学模板。

#### 可以这样回答

运行时 skill 有效但长期占上下文。

带着 skill sampling，用渲染、功能、视觉三道检查过滤，训练时把 skill 从 prompt 里拿掉做 SFT，之后再上 RL。最值钱的样本是「不带 skill 失败、带 skill 成功」的那些，它们正好是 skill 补上的能力。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-web-internalize)

### FineWeb：跨所有 crawl 快照做全局 MinHash，为什么可能更差？

> **回答思路**  
> **背景：** 跨快照重复内容也可能是高价值来源。  
> **任务：** 确定 deduplication 范围与保留策略。  
> **做法与原因：** 比较快照内和全局方案，检查质量构成变化。  
> **结果／验证：** 同预算下游收益决定范围，不追最低重复率。

#### 可以这样回答

跨快照重复内容也可能是高价值来源。

因为跨快照反复出现的往往是优质网页，全局 near-duplicate deduplication 把它们只留一份，一次性出现的低质页面比例就上去了。网页先在快照内去 near-duplicates，跨快照重点处理页脚、导航和评测指纹，范围用 small model 的下游对照来定。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-global-dedup)

### 案例 4/4：网页里的数字是模型编的，怎么设计 hallucination penalty？

> **回答思路**  
> **背景：** 页面数字可能没有原始数据支持。  
> **任务：** 压住编造同时保留必要信息。  
> **做法与原因：** 数字绑定来源地址，分别检查错误与覆盖。  
> **结果／验证：** 真实引用支持且不靠少写数字获益。

#### 可以这样回答

页面数字可能没有原始数据支持。

让模型写每个数字时带上它在数据里的地址，再按地址回查，对不上就扣分，扣多少按错的类型定。只罚错的话模型会少写数字，所以另加一项覆盖率。最理想是数字直接由渲染器按地址填，当时工程上没做成。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-web-grounding)

### DoReMi：small model Group DRO 学出的 data mix，能不能直接拿来训 large model？

> **回答思路**  
> **背景：** 代理模型的最坏域目标不等于产品质量。  
> **任务：** 评估学到的 data mix 能否迁移。  
> **做法与原因：** 先审计域划分，再在 large model 和 task slices 验证。  
> **结果／验证：** 实际收益成立才采用，不把代理最优当普适最优。

#### 可以这样回答

代理模型的最坏域目标不等于产品质量。

不能直接用，拿来当 core pre-training data mix 的初值比较合适。DoReMi 优化的是相对 reference model 的最坏域损失，目标里没有摘要 human evaluation 或工具成功率，所以还要在 large model 和下游 evaluation slices 上验证。另外要先清理并合理划分数据域，否则最差域是垃圾时它会被一直加权。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-doremi-mix)

### 研究案例：想在 Terminal-Bench 上爬坡，RL 环境数据怎么做？

> **回答思路**  
> **背景：** 训练环境涨分可能不迁移到终端基准。  
> **任务：** 选择更有效的环境与反馈。  
> **做法与原因：** 先查真实性、可学难度和 verifier 质量。  
> **结果／验证：** 独立终端任务收益与单位成本共同确认。

#### 可以这样回答

训练环境涨分可能不迁移到终端基准。

几篇公开工作放在一起看，结论是环境要贴近真实任务、难度卡在中间、verifier 靠得住，环境数量排在最后。Endless Terminals 在自己的 development set 上涨了很多，到 Terminal-Bench 几乎不动；River 只用不到三成的环境，过滤掉坏 verifier 后增益更大。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-tbench-climb)

### Llama 3：pre-training 最后抬高质代码 / 数学（annealing），有什么用？

> **回答思路**  
> **背景：** pre-training 末期仍可用 data mix 补能力。  
> **任务：** 解释 annealing 数据的阶段作用。  
> **做法与原因：** 高质量域 data mix 与 learning rate 一起记录并控制变量。  
> **结果／验证：** 新能力与旧任务复测，公开配方不直接照搬。

#### 可以这样回答

pre-training 末期仍可用 data mix 补能力。

Annealing 在主 pre-training 末段降 learning rate、上 sampling 高质量数学和代码，补可验证的能力，格式和工具行为留给 post-training。Llama 3 最后约 40M token 是它自己的公开配方，换模型要重新定，常用基准的 training set 不能混进来。它还能拿来低成本评估新数据源。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-llama-anneal)

### 研究案例：tool calls RL，奖励粒度和合成环境怎么决定数据质量？

> **回答思路**  
> **背景：** 一个总奖励难定位调用哪里错。  
> **任务：** 让反馈对应工具选择和参数质量。  
> **做法与原因：** 拆分名称、参数和执行结果，校验模拟偏差。  
> **结果／验证：** 真实执行收益支持奖励粒度，不奖励无效长思考。

#### 可以这样回答

一个总奖励难定位调用哪里错。

tool calls RL 里，奖励就是数据的标签。ToolRL 说明奖励要拆到工具名、参数名、参数值三层，额外鼓励长思考会掉点；Kimi K2 说明没有真实工具时可以大规模模拟，但模拟环境和 judge 的偏差要靠真实执行来校。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-case-toolcall-rl)

### Llama / Phi / FineWeb-Edu：质量分类器用合成标签训，坑在哪？

> **回答思路**  
> **背景：** teacher 标签可能偏爱正式英语文风。  
> **任务：** 避免质量分类器系统性误删。  
> **做法与原因：** 按语言领域抽查、calibration，并记录 teacher 版本。  
> **结果／验证：** small model 下游实验支持阈值，long-tail 仍有覆盖。

#### 可以这样回答

teacher 标签可能偏爱正式英语文风。

坑在于一个分类器、一个阈值套所有数据：teacher 偏爱正式英文时，论坛内容和 low-resource 语言会被大量误删，和评测同族的分类器还会让 contamination 更容易混进来。所以按语言和领域分别训练或 calibration，代码、数学、对话不用网页教育价值标准；阈值用 small model 下游实验选，teacher 版本和抽查一致率记进 dataset card。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-quality-clf-synth)

### Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？

> **回答思路**  
> **背景：** 合成集声称大幅涨公开分可能含 leakage。  
> **任务：** 先确认结果是否代表泛化。  
> **做法与原因：** 检查改写、翻译和 teacher 提示，再用新题验证。  
> **结果／验证：** 去 contamination 后仍有独立收益，才讨论扩大使用。

#### 可以这样回答

合成集声称大幅涨公开分可能含 leakage。

先查 contamination，再谈质量。对照冻结评测做精确匹配、n-gram 和 embedding nearest neighbors 检索，抽查改写题、翻译题，再用按时间切出的新题验证增益；质量过滤和 MinHash deduplication 证明不了没训到测试题。排除 contamination 后，才检查答案和推理过程；自己 synthetic data 时，生成提示里也不能放评测题。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-synth-bench-trap)

### Anthropic：RLAIF / 宪法反馈，judge 开始喜欢自己的文风怎么办？

> **回答思路**  
> **背景：** 策略会适应 judge 的偏好与漏洞。  
> **任务：** 防止模型给自己循环打高分。  
> **做法与原因：** 冻结版本，规则与独立 human evaluation 持续校验。  
> **结果／验证：** 真实质量同步提高，不只看自评奖励。

#### 可以这样回答

策略会适应 judge 的偏好与漏洞。

固定 judge 的版本，再用 human evaluation 和规则独立检查结果。策略会越来越会模仿 judge 偏爱的长文和套话，judge 要是每轮换成 current policy，就等于让模型给自己打分，最后 judge 给高分、human evaluation 却不涨。能直接验证的任务优先用 rule-based reward，human evaluation 分歧明显的题留给人来判断。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-rlaif-loop)

### Anthropic：RLHF 什么时候会奖励不诚实？数据上怎么拆？

> **回答思路**  
> **背景：** 礼貌附和可能赢得偏好却违背事实。  
> **任务：** 让模型尊重用户也能纠正错误前提。  
> **做法与原因：** 事实与态度分开标，构造立场 counterfactual。  
> **结果／验证：** sycophancy evaluation slices 改善，主观偏好不被当事实错误。

#### 可以这样回答

礼貌附和可能赢得偏好却违背事实。

human evaluation 更偏爱客气附和的回答、给简短纠正打低分时，RLHF 就会奖励不诚实。数据上要拆开：用成对样本教模型纠正错误前提（chosen 按证据纠正，rejected 附和），annotation guidelines 把事实忠实和礼貌分成不同维度，评测单列 sycophancy evaluation slices。满意度高，单独证明不了模型诚实。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-sycophancy-data)

### Tesla / Scale：车队 trigger 和影子模式，接到 LLM 评测失败怎么说？

> **回答思路**  
> **背景：** 海量流量不能都当训练 gold labels。  
> **任务：** 发现值得复现的失败类型。  
> **做法与原因：** 用验证失败或分歧触发，再合法采集研究样本。  
> **结果／验证：** long-tail 收益真实，影子输出和沉默不直接当认可。

#### 可以这样回答

海量流量不能都当训练 gold labels。

把车队 trigger 的思路换成「评测失败触发收集」：固定评测失败、judge 或人与 RM 的分歧、工具验证失败和低置信步骤，才值得进 feedback loop，再用许可或 synthetic data 复现。影子模式的输出当不了 gold labels，用户没改摘要也不等于认可。可验证样本自动扩，主观 hard examples 按人工预算处理。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-trigger-ood)

### Llama 3 §3.1：自研 HTML 抽取，URL / 文档 / 行三级 deduplication，哪级会 false rejection 好文本？

> **回答思路**  
> **背景：** 行级重复既有模板也有有用内容。  
> **任务：** 避免抽取与 deduplication 误伤好文本。  
> **做法与原因：** 按 URL、文档、行分别审计，保留结构。  
> **结果／验证：** 数据类型 evaluation slices 支持阈值，不照搬论文参数。

#### 可以这样回答

行级重复既有模板也有有用内容。

最容易 false rejection 好文本的是行级 deduplication：它删掉导航这类重复模板，也会删掉反复出现的好句，所以要按内容类型抽查。URL 级保留最新版本，文档级 near-duplicates 的范围用下游实验选；抽取阶段数学、代码和 multilingual 分开处理，保留数学和代码结构以及图片 alt 文本。「每 30M 篇中超过 6 次」是 Llama 自己的阈值，换数据要重新验证。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-llama-extract)

### Anthropic 编程题：带权重的 DataBatcher，断点续跑怎么写？

> **回答思路**  
> **背景：** 只恢复 random seed 会重新消费数据。  
> **任务：** 按权重组 batch 并准确断点续跑。  
> **做法与原因：** 同时保存各源 offset、随机状态和耗尽状态。  
> **结果／验证：** 恢复后样本序列一致，缺源不偷偷改 data mix。

#### 可以这样回答

只恢复 random seed 会重新消费数据。

按 token 预算组 batch，checkpoint 保存每个数据源的读取 offset 和随机数状态，恢复时从原位置继续读；只恢复 random seed 的话，每个源会从头再读一遍。数据源耗尽时把它的概率设为零并报告，不悄悄改变 data mix。权重本身由上层决定，调 data mix 就是改 `weights`。

测试还要满足这个条件：恢复后样本序列一致，缺源不偷偷改 data mix。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-weighted-batcher)

### xAI：从 X 时间线灌进 Grok 的 data pipeline 怎么设计？

> **回答思路**  
> **背景：** 时效内容会编辑、删除且含许可限制。  
> **任务：** 构建可撤回的时间化数据流。  
> **做法与原因：** 时间分区、规范 URL 与墓碑记录联动。  
> **结果／验证：** 截止后任务支持收益，旧版本和敏感来源被排除。

#### 可以这样回答

时效内容会编辑、删除且含许可限制。

按时间分区的流式 pipeline 来设计：摄入时删帖用墓碑记录，过滤做语言识别并去掉广告、机器人和刷屏，转发按 URL deduplication 并保留引用计数，时效源放进 mid-training 或 annealing 阶段。来源要先过许可，公开帖子不等于能进基础模型，大规模汇聚 personally identifiable information (PII) 的时间线要排除。实时数据值不值，用训练截止后的事件问答来证明。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-x-feed)

### DataComp-LM：从 Common Crawl WET 起步，为什么公开集常吃亏？

> **回答思路**  
> **背景：** 下游过滤无法恢复抽取时丢掉的信息。  
> **任务：** 判断瓶颈在正文抽取还是质量分。  
> **做法与原因：** 固定过滤，只比较预抽文本与原 HTML 重抽。  
> **结果／验证：** 受控下游收益支持上游改进，非纯格式变化。

#### 可以这样回答

下游过滤无法恢复抽取时丢掉的信息。

因为瓶颈常在正文抽取。WET 是 Common Crawl 预先抽好的纯文本，抽错漏掉的内容后面的质量分类器补不回来。DCLM 固定同一套过滤、只把 WET 换成从 WARC 原始 HTML 重新抽取，Core 就高了至少 2.5 点，所以先定抽取，再调分类器和阈值。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-dclm-wet)

### Anthropic 风格：safety evaluation gate 被训练数据看见了，你先停什么？

> **回答思路**  
> **背景：** 被 contamination 的 evaluation gate 已无法支持可靠发布判断。  
> **任务：** 暂停依赖旧分数的决策并恢复评价。  
> **做法与原因：** 估影响、查来源，换独立新题复测。  
> **结果／验证：** 结论重建可信度，删数据不自动修复旧模型。

#### 可以这样回答

被 contamination 的 evaluation gate 已无法支持可靠发布判断。

先停所有依赖这份评测的模型比较和发布，它的分数已经不可信。然后按类别估计 contamination 影响，旧结论保留但降低可信度，再换训练截止后的新题或私有题重测。只从 training set 删掉命中内容，证明不了已训练模型的评测又可靠了。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-contam-hold)

### Tulu 3 / 迭代 DPO：离线 preference pairs 过期了怎么办？

> **回答思路**  
> **背景：** 旧 preference pairs 覆盖不到 current policy 的新回答。  
> **任务：** 让监督跟上模型分布变化。  
> **做法与原因：** current policy resampling 并独立标注或执行。  
> **结果／验证：** 新候选质量改善，旧对保留用途与适用版本。

#### 可以这样回答

旧 preference pairs 覆盖不到 current policy 的新回答。

用当前模型重新 sampling，再重新比较好坏。旧 preference pairs 来自 old policy，模型现在会写的回答没人监督；直接拿 UltraFeedback 这类现成偏好集来训，监督的是别的模型的回答分布。可验证任务在线 sampling、用 rule-based reward 评分，主观偏好定期用 current policy 重采，交给人或 经过 calibration 的 judge 标。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-onpolicy-pref)

### Llama 3：为什么 preference pairs 要有 edited，还要丢掉「差不多」的对？

> **回答思路**  
> **背景：** 两条中更好的回答也未必达到标准。  
> **任务：** 获得更清晰且有质量底线的偏好。  
> **做法与原因：** 编辑改善 chosen，区分强弱信号和 label noise。  
> **结果／验证：** 独立质量而非仅排序准确率支持选择。

#### 可以这样回答

两条中更好的回答也未必达到标准。

两个做法都是为了让偏好信号更干净。chosen 只是两条里较好的那条、未必达标，所以 Llama 3 让 annotator 再改一遍，得到 edited > chosen > rejected；差距很小的对 label noise 大，reward model 只用清晰的 preference pairs，DPO 只留「明显更好」和「更好」两档。AFM 用 cohesion 优先选 human evaluation 一致的 prompt，也是在减少弱信号。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-llama-edit-pref)

### OpenAI：过程监督标签怎么采？DeepSeek 为什么后来不用神经 PRM？

> **回答思路**  
> **背景：** 过程标签贵且可能被优化者利用。  
> **任务：** 判断何时值得增加逐步监督。  
> **做法与原因：** 可执行任务先用规则，过程缺口再标。  
> **结果／验证：** 成本与独立任务收益支持 PRM，不假定更细更好。

#### 可以这样回答

过程标签贵且可能被优化者利用。

先问这道题能不能直接验证：能执行验证的先用 rule-based reward，只有最终答案检查发现不了的过程错误，才值得做人工或神经 PRM。逐步监督更省样本，但人工标注贵，要先统一步骤怎么划分并保留独立的结果检查，过程编造的 trajectories 不进 CE 正例。DeepSeek 不用神经 PRM，是因为它在大规模 RL 里会被 hack，重训又贵。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-prm-steps)

### DeepSeek-R1 / Tulu RLVR：verifiable reward 的「数据」到底是什么？

> **回答思路**  
> **背景：** rule-based reward 需要可靠题目与 scorer。  
> **任务：** 定义 RLVR 真正的数据单元。  
> **做法与原因：** 题目、环境、verifier 和难度版本绑定。  
> **结果／验证：** 独立正确性与有效学习组验证反馈价值。

#### 可以这样回答

rule-based reward 需要可靠题目与 scorer。

RLVR 的数据是题目加可验证的 scorer。数学答案、代码测试和工具状态能给 rule-based reward；开放摘要和自然度判不了对错，要单独用人类偏好，和 rule-based reward 分开记。每题绑定 scorer 版本，全对或全错的题先调难度，必要时先用 SFT 冷启动。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-rlvr-data)

### Anthropic 笔试：fine-tuning 之后怎么证明模型相对 base model「漂了」？

> **回答思路**  
> **背景：** fine-tuning 后分布变化可能有益也可能有害。  
> **任务：** 证明变化发生在预期行为上。  
> **做法与原因：** 配对比较行为 evaluation slices、KL 和分维度 human evaluation。  
> **结果／验证：** 目标改善、regression tasks 稳定，不以 KL 大小定好坏。

#### 可以这样回答

fine-tuning 后分布变化可能有益也可能有害。

漂本身不坏，要证明的是偏离发生在声明的轴上、已有能力还在。用同一批固定 prompt 对比 base model 和 fine-tuned model：按 evaluation slices 算 KL，跑行为套件，分开报安全与有用性，再做分维度 human evaluation。KL 大只说明分布变了，好坏要靠行为套件和 human evaluation 判断，总 loss 和 Arena 赢率给不出这些信息。对照数据用研究集和 frozen evaluation set。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-value-drift)

### Llama 3：工具对话按整段标偏好，还是按每一跳？

> **回答思路**  
> **背景：** 整段胜负难判断哪次 tool calls 有问题。  
> **任务：** 收集同上下文的逐跳监督。  
> **做法与原因：** 相同 prefix 比较候选，工具返回不可随意修改。  
> **结果／验证：** 局部标签与真实执行一致，整段任务不退化。

#### 可以这样回答

整段胜负难判断哪次 tool calls 有问题。

按每一跳标：在相同上下文中生成两条助手消息让人选择或编辑，把选中或编辑后的回答写回对话再继续。工具返回 annotator 不能修改，也不作为偏好候选，调用对错交给可执行检查。整段只标一个成败，reward model 会把运气算进调用质量，也定位不到哪一步出错。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tool-turn-pref)

### Llama 3：代码 post-training 合成，模型改自己的单测算过关吗？

> **回答思路**  
> **背景：** 修改测试后通过等于改变判分条件。  
> **任务：** 保留真实修复而非作弊 trajectories。  
> **做法与原因：** 固定原测试 hash，独立检查补丁和权限。  
> **结果／验证：** hidden tests 与回归通过，编译输出不当生成目标。

#### 可以这样回答

修改测试后通过等于改变判分条件。

不算。模型改测试才通过，等于改了判分条件，这种 trajectories 要隔离，不当 SFT 正例。做法是在模型动手前记下测试的哈希、条数和 assertion，只有通过原测试的修复才算成功；执行反馈可以拿来学修复，编译器输出不计入生成 loss。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-code-exec-synth)

### 开源代码合成集自称 HumanEval +9%，你先查什么？

> **回答思路**  
> **背景：** 代码改名和改写可绕过简单 deduplication。  
> **任务：** 判断涨分是否来 self-training 评测重叠。  
> **做法与原因：** 题意、规范代码、issue 和测试来源联合扫描。  
> **结果／验证：** 新时间窗任务支持收益，旧题涨分不冒充泛化。

#### 可以这样回答

代码改名和改写可绕过简单 deduplication。

先查涨分是不是 leakage，再谈质量。拿固定的评测题和参考解，用精确匹配、13-gram、规范化后的代码和 embedding nearest neighbors 跟 training set 比对，再用训练截止后的 LiveCodeBench 新题看泛化。旧题涨、新题不动，这个涨分就算不上能力提升；SWE 类还要查 issue、PR 和测试文件。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-code-bench-bleed)

### SWE trajectories：测试过了就能整段进 SFT 吗？

> **回答思路**  
> **背景：** 终局补丁正确仍可能包含差的工具行为。  
> **任务：** 决定成功 trajectories 哪些部分值得学。  
> **做法与原因：** 剔除改测试和无效循环，审核恢复片段。  
> **结果／验证：** 新任务行为改善，筛选比例由当前数据决定。

#### 可以这样回答

终局补丁正确仍可能包含差的工具行为。

不能。hidden tests 通过只说明最终补丁对，过程里仍可能有改测试、重复执行但没有推进任务和反复失败的 tool calls，整段进 SFT 会把这些一起教给模型。先丢掉改过测试文件的 trajectories，再按过程质量筛片段，loss 只算助手生成的编辑和推理。SWE-Prime 筛出的约 10% 子集胜过全部已解决 trajectories，这个比例是论文 ablation study 结果，换了数据要重新定。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-swe-success-noise)

### BFCL：目录里没有能用的工具，模型还是调了，数据上怎么拆？

> **回答思路**  
> **背景：** 总有可用工具的训练会鼓励乱调用。  
> **任务：** 学会判断没有合适工具或缺信息。  
> **做法与原因：** 加入语义接近的无关工具与澄清示范。  
> **结果／验证：** 相关性判断和真实任务成功同时评。

#### 可以这样回答

总有可用工具的训练会鼓励乱调用。

补两类示范：当前工具目录完成不了请求时，正确做法是不调用，说明限制或询问用户；缺少信息时，先调只读查询再执行。SFT 如果总假设有工具可用，模型就学会见 schema 就填，编造名称和参数。BFCL 的 Function Relevance Detection 专门测第一类，负例要用语义相近的无关工具来造。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tool-irrelevance)

### trajectories SFT 之后，换个工具名就不会了，学的是语义还是接口？

> **回答思路**  
> **背景：** 换名称就失败可能是接口记忆。  
> **任务：** 训练工具语义而非固定字符串。  
> **做法与原因：** 同任务变化 schema 与工具名，保持功能可比。  
> **结果／验证：** 新接口仍能选对和填对参数。

#### 可以这样回答

换名称就失败可能是接口记忆。

多半学的是接口。检验方法是同一任务换工具名和 schema 再评，原接口能完成、换名就失败，说明模型依赖接口记忆。训练时同一能力要覆盖多套工具名和 schema，示范格式贴近部署时真正注入的工具规格，并在 dataset card 的 `surface` 中记录接口版本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tool-alias)

### Agent 终局状态对了，中间少调一次只读工具，算不算过？

> **回答思路**  
> **背景：** 终局碰巧正确可能绕过必需证据。  
> **任务：** 按任务要求验证状态与过程。  
> **做法与原因：** 仅对明确必需调用检查参数来源和权限。  
> **结果／验证：** 状态正确且满足声明约束，不强制唯一合法路径。

#### 可以这样回答

终局碰巧正确可能绕过必需证据。

不算过。少调一次必经的只读查询，说明参数是猜的，最终状态碰巧对了也该判失败。做法是在题卡里用 `must_call` 列出必须拿到的证据，逐个核对参数是否来自前一步的工具返回，再确认写入落了库；模拟用户的对白不直接当 gold labels。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-agent-state-path)

### RLEF：执行反馈进对话，奖励却看私有测试，数据怎么切？

> **回答思路**  
> **背景：** 把最终私测反馈暴露给策略会适配评分。  
> **任务：** 分开可观察反馈与隐藏验收。  
> **做法与原因：** 公开执行结果可入上下文，私测只定最终奖励。  
> **结果／验证：** 新私测有效，工具输出不被当助手监督。

#### 可以这样回答

把最终私测反馈暴露给策略会适配评分。

每题准备两套测试：公开测试的结果可以作为 observation 返回给模型，最终奖励只由不展示的私有测试决定。两套混用，模型会背公开测试、改代码迎合样例。两套测试分别记录哈希，stderr 不进 cross-entropy 训练目标，公开测试全过但私有测试失败，奖励仍为 0。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-rlef-split)

### OpenAI：工具返回里写着「忽略以上指令」，训练数据怎么造？

> **回答思路**  
> **背景：** 网页或工具返回可能包含恶意指令。  
> **任务：** 保持权限层级同时完成原任务。  
> **做法与原因：** 构造服从注入与按授权处理的对照。  
> **结果／验证：** 敏感目标不被触发，正常工具内容仍可利用。

#### 可以这样回答

网页或工具返回可能包含恶意指令。

造权限冲突的成对样本。按 system > developer > user > tool 的层级，工具、网页和邮件里的指令只是数据，改变不了原任务；chosen 遵守高权限要求并完成任务，rejected 服从注入。高权限要求要能自动核对，工具返回保留原样，模型才练得到识别攻击。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tool-inject)

### OSWorld / AndroidWorld：屏幕 trajectories 哪一段能进 SFT？

> **回答思路**  
> **背景：** 截图过期或动作错位会 contamination 监督。  
> **任务：** 筛选可对齐可 replay 的 GUItrajectories。  
> **做法与原因：** 核对动作前观察与状态，独立验证终局。  
> **结果／验证：** 新环境可复现成功，私人截图不默认训练。

#### 可以这样回答

截图过期或动作错位会 contamination 监督。

只有能对上执行当时屏幕元素、能 replay 的动作才能进 SFT；依据过期截图的操作和犹豫点击要丢掉或 mask，任务成功与否由环境状态判。OSWorld 发现文本操作历史有帮助，堆历史截图没有同样的收益。trajectories 用研究集、合成界面或许可演示，用户真实屏幕涉及隐私。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-gui-traj)

### WebGPT：为什么没有引用，事实偏好几乎标不动？

> **回答思路**  
> **背景：** 没有可查证据，human evaluation 容易按文风打分。  
> **任务：** 让事实偏好可逐项核对。  
> **做法与原因：** 分别记录搜索 trajectories、引用支持与来源可信度。  
> **结果／验证：** 去掉格式优势后内容仍正确，事实判断独立。

#### 可以这样回答

没有可查证据，human evaluation 容易按文风打分。

因为没有引用，annotator 只能凭记忆或文笔判断真假，事实 preference labels 噪声很大。WebGPT 把数据拆成两部分：浏览 trajectories 教模型怎么搜，带引用的答案让 annotator 逐句核对出处。「引用是否支持」和「来源是否可信」要分开评，评测时再去掉引用比一次，防止引用格式本身让答案显得可信。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-webgpt-cite)

### Llama 3：post-training 怎么让模型「知道自己会什么」？

> **回答思路**  
> **背景：** 强行回答未知事实容易制造 hallucination。  
> **任务：** 学会在缺乏证据时表达不确定。  
> **做法与原因：** 先探测已知知识，再构造承认不知道与检索示范。  
> **结果／验证：** 不该答时少编造，已知任务不一律拒绝。

#### 可以这样回答

强行回答未知事实容易制造 hallucination。

先探测模型已经会什么，再教它对不会的题承认不知道。拿事实题反复问，模型多次给出具体但错误的回答，就配上承认不知道的示范；用 SFT 硬灌新知识更容易引发 hallucination，新事件交给搜索。探测题从许可的 pre-training 材料里生成。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-knows-what)

### Llama 3：什么题该调搜索，什么题不该？数据怎么切桶？

> **回答思路**  
> **背景：** 总是搜索增加成本，私人内容还可能外泄。  
> **任务：** 学习何时搜及用哪种工具。  
> **做法与原因：** 区分必须搜、可答和禁止开放搜索的任务。  
> **结果／验证：** 事实、延迟与权限共同验收。

#### 可以这样回答

总是搜索增加成本，私人内容还可能外泄。

按三类切桶：必须搜（时事、截止日后的信息）、禁止开放搜索（邮件、日历、图片里的私人信息，用对应工具读）、可搜可答（稳定常识，两种示范都留一点）。只教「有搜索就搜」，模型会把常识题也拖去检索，增加延迟和隐私风险。读私人数据的工具和开放搜索分成两套 mix，配额分开记。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-when-to-search)

### τ-bench：过一次库状态，为什么还不够当正例？

> **回答思路**  
> **背景：** 单次通过可能来自运气。  
> **任务：** 测量多次执行的一致可靠性。  
> **做法与原因：** 同任务多次重置，核对政策和数据库状态。  
> **结果／验证：** 连续成功与至少一次成功分开报告。

#### 可以这样回答

单次通过可能来自运气。

因为一次通过可能是运气。τ-bench 看同题多次运行是否都遵守政策、正确更新数据库：gpt-4o 零售 $\mathrm{pass}^{1}$ 约 61%，到 $\mathrm{pass}^{8}$ 只剩约 25%。用 $\mathrm{pass}^{k}$ 当进 SFT 和发版的 evaluation gate，训练仍可用单次状态奖励；trajectories 还要查必经只读调用，用户模拟和 grader 标签需独立复核。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tau-passk)

### DeepSeek-R1：800k distillation 集是怎么滤的，small model 为什么只做 SFT？

> **回答思路**  
> **背景：** 长推理文本不自动适合作为 student 监督。  
> **任务：** 理解 distillation 数据的验证与筛选。  
> **做法与原因：** 保留正确可读 trajectories 并混合通用任务。  
> **结果／验证：** student 独立收益支持数据，条数不横比不同配方。

#### 可以这样回答

长推理文本不自动适合作为 student 监督。

R1 在 RL 收敛后做 rejection sampling，只留正确且可读的 trajectories，再加通用任务一起做 SFT：约 600k 推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。small model 只做 SFT，是为了单独看这些 trajectories 能不能把能力传过去。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-r1-distill)

### OpenAI deliberative alignment：政策写进思考，训练时为什么要把 spec 撕掉？

> **回答思路**  
> **背景：** 看着政策答对不等于学会适用规则。  
> **任务：** 把安全规则变成可迁移行为。  
> **做法与原因：** 生成可查示范，再按公开方法区分训练可见信息。  
> **结果／验证：** 越狱与 over-refusal 都评，条款版本明确。

#### 可以这样回答

看着政策答对不等于学会适用规则。

为了让模型学会自己回忆该用哪条规则。生成安全示范时让模型看着政策、在推理里引用条款，SFT 时把政策正文拿掉，模型只能靠回忆；RL 的 scorer 仍看着政策来核对。验证同时看越狱抵抗和 over-refusal，并记下条款版本。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-deliberate-spec)

### WebArena：812 道网页任务，动作序列对了就能进 SFT 吗？

> **回答思路**  
> **背景：** 同一网页任务可能有多条正确路径。  
> **任务：** 以功能目标评价 tool-use trajectories。  
> **做法与原因：** 验证终局与副作用，不机械模仿点击顺序。  
> **结果／验证：** 新任务模板有效，失败 replay 不冒充成功示范。

#### 可以这样回答

同一网页任务可能有多条正确路径。

不能。同一任务有多条合法路径，判断标准是最终功能 assertion 是否通过，再查过程中有没有改了不该改的状态，逐次点击不必和人类一致。失败 replay 可作负例或恢复材料，不能直接当成功示范。训练实例还要和评测模板 deduplication。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-webarena-traj)

### IFEval 只有 541 条，post-training 能不能直接拿来训？

> **回答思路**  
> **背景：** 评测题直接训练会失去评价意义。  
> **任务：** 构造同类但独立的指令约束数据。  
> **做法与原因：** 从自有任务组合可同时满足的规则。  
> **结果／验证：** 内容和格式分别检查，新语言验证 checker。

#### 可以这样回答

评测题直接训练会失去评价意义。

不能。IFEval 的 541 条英文题是 evaluation set，拿来训就失去评测意义。要借它的思路另造 training set：从自己的 SFT 数据抽任务、叠同类的可执行约束，生成独立的 RLVR 数据；同时检查约束能否同时满足，按语言改写 checker，并单独评内容质量，免得只学会格式。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-ifeval-overlay)

### s1：1000 条推理 SFT 为什么够用，多堆 59k 为什么未必更好？

> **回答思路**  
> **背景：** 少量高质数据的收益依赖 student 已有能力。  
> **任务：** 判断条数、难度与质量的关系。  
> **做法与原因：** 控制预算比较可学示范，decoding 预算另记。  
> **结果／验证：** 新题和 long-tail 有效，不能只模仿超长推理。

#### 可以这样回答

少量高质数据的收益依赖 student 已有能力。

1000 条够不够，取决于 student model 已经会多少，以及示范是否同时兼顾难度、多样性和质量。s1K 是在已指令对齐的 32B 上补一点推理，条数没法和别的配方横比；多堆 59k，质量和难度跟不上就只是加噪声。Budget forcing 是 inference 时控制思考长度的 decoding 方法，不算训练数据；student 学不会的超长推理要过滤，分布一偏还得靠 RLVR。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-s1k)

### OpenAI 高频笔试：现场训分类器、摸数据集，data 岗怎么开口？

> **回答思路**  
> **背景：** 现场 fit 模型无法替代数据与标签检查。  
> **任务：** 完成可信分类 baseline 和误差分析。  
> **做法与原因：** 先查字段与 cluster 级划分，再按来源 对 threshold 做 calibration。  
> **结果／验证：** 独立 evaluation slices 及 false rejection 检查支持过滤用途。

#### 可以这样回答

现场 fit 模型无法替代数据与标签检查。

先看清字段、标签来源和缺失，再按文档或 near-duplicates cluster 划分训练、开发和固定 evaluation set，然后建简单 baseline，按语言、长度、来源分析误差并对 threshold 做 calibration。这题考的是数据和标签靠不靠得住：只调用 fit、报一个总体 AUC，说明不了分类器能拿去过滤数据。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-oai-classifier)

### OpenAI：从聊天日志里怎么挖新概念的代表图？

> **回答思路**  
> **背景：** 新颖概念与损坏离群图片可能混淆。  
> **任务：** 选择质量合格又补覆盖的代表图。  
> **做法与原因：** 先确认数据用途，再做质量、新颖度和多样性筛选。  
> **结果／验证：** 人工抽查支持概念覆盖，不把自动把私人日志加入 training data。

#### 可以这样回答

新颖概念与损坏离群图片可能混淆。

分两步：先从聊天日志和评测失败里找出新出现的概念，再从有许可的图库和验证过的合成图片描述里给它挑代表图。挑图先过 data quality checks，再看新颖度，最后保证多样性，因为离群的图很多只是损坏或带水印。人工优先看质量合格、又和已有类别差得远的图。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-chatlog-concept)

### OpenAI：用户上传工具照片做识别，训练数据从哪来？

> **回答思路**  
> **背景：** 用户上传只说明需要识别，不说明可训练。  
> **任务：** 合法补足工具照片识别 long-tail。  
> **做法与原因：** 许可目录、受控拍摄与验证合成为主。  
> **结果／验证：** 新 SKU 与拍摄条件泛化，来源用途可追溯。

#### 可以这样回答

用户上传只说明需要识别，不说明可训练。

来自许可产品目录、厂商授权图、受控拍摄和验证过的 synthetic data。用户上传的识别图片只说明产品需要认它，没有明确的训练许可，就不能用作 base model 训练或固定评测。hard examples 从评测失败和许可 long-tail SKU 里挖，评测用按时间留出的新 SKU 和内部拍摄图。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-tool-photo)

### Anthropic：怎么评模型是诚实，还是只是流畅？

> **回答思路**  
> **背景：** 人类容易偏爱流畅但没有依据的回答。  
> **任务：** 分别测事实诚实与表达质量。  
> **做法与原因：** 构造流畅错与简短对的候选对。  
> **结果／验证：** 事实与礼貌分项改善，不拿满意度代替真实。

#### 可以这样回答

人类容易偏爱流畅但没有依据的回答。

两者拆开测、分开报。诚实是按证据回答、没依据时承认不知道，流畅只是读着顺。做法是把「流畅但错」和「简短但对」的回答配成对，事实忠实度和表达质量分开打分；只看 Arena 或满意度，附和错误前提的回答也可能拿高分。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-honest-fluent)

### Anthropic Sleeper Agents：后门怎么进训练数据，安全训为什么清不掉？

> **回答思路**  
> **背景：** 后门可能通过来源或合成供应链进入模型。  
> **任务：** 提前发现条件触发行为。  
> **做法与原因：** 来源隔离，触发/非触发成对检查。  
> **结果／验证：** 风险有独立证据，事后安全训练不当清除保证。

#### 可以这样回答

后门可能通过来源或合成供应链进入模型。

后 gate 是训练中学到的条件行为，可以通过被投毒的来源、供应商 synthetic data 进入训练。Sleeper Agents 的实验里，后续安全 SFT / RL 和对抗训练都没清除已植入的行为，对抗训练还可能让模型学会隐藏。所以要在数据侧防：审计来源、隔离供应商数据，成对评测触发与非触发条件，事后仅靠 post-training 并不可靠。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-sleeper-data)

### Anthropic：只用 token logprob，怎么做成质量 / 安全二分类器？

> **回答思路**  
> **背景：** 自由解释难稳定转换成过滤分数。  
> **任务：** 生成可进行 calibration 的二元分类信号。  
> **做法与原因：** 限制输出并从候选 token 概率算连续分数。  
> **结果／验证：** 按语言领域 calibration，误差由独立标签检查。

#### 可以这样回答

自由解释难稳定转换成过滤分数。

让模型只输出 Yes 或 No，用这两个 token 的 logprob 算一个连续分数，再按语言和数据域在 development set 上分别对 threshold 做 calibration。连续分数能画 calibration curve、按需挪阈值；先写长解释再用正则找词，输出不稳，也没法 calibration。模型分只当开发过滤器，误差靠独立人标和固定评测来查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-llm-clf-logprob)

### DeepMind：评测台怎么按生产软件的标准来设计？

> **回答思路**  
> **背景：** 版本不固定时小幅涨分难以解释。  
> **任务：** 建设可复现可回归的评价流程。  
> **做法与原因：** 保存逐题结果、模型提示 decoding 与 grader 版本。  
> **结果／验证：** 配对证据和稳定复跑支持结论。

#### 可以这样回答

版本不固定时小幅涨分难以解释。

核心是每个分数都能复现、能公平比较：每次评测记下模型、题集、提示模板、decoding 参数和 seed，scorer 版本也固定。小幅涨分要做逐题 paired test。日常跑快速检查、夜间跑全套，保存逐题结果来定位回归。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-eval-harness)

### Gemini pre-training 评测岗：leakage 和记忆怎么分开测？

> **回答思路**  
> **背景：** 内容重叠与分数被抬高是两个问题。  
> **任务：** 分别确认暴露和实际记忆收益。  
> **做法与原因：** 扫描与金丝雀发现线索，变式新题检验影响。  
> **结果／验证：** 翻译和 teacher leakage 不只靠字面扫描排除。

#### 可以这样回答

内容重叠与分数被抬高是两个问题。

分两步测：先查训练内容和评测有没有重叠，再查这种重叠有没有把分数抬高。重叠用 n-gram 扫描和金丝雀字符串查，是否虚高就把题目改数字、改变量名再测一遍。teacher model 间接 leakage n-gram 扫不到，要靠 embedding nearest neighbors 和私有评测。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-canary-leak)

### DeepSeek 会问的 data chemistry：反复用 synthetic data 训练，模型会怎么塌？

> **回答思路**  
> **背景：** 反复自生成会逐渐丢失稀有模式。  
> **任务：** 避免 self-training 缩窄数据分布。  
> **做法与原因：** 保留原始来源与独立验证，跟踪 long-tail 和多样性。  
> **结果／验证：** 平均正确与尾部覆盖均稳定才继续迭代。

#### 可以这样回答

反复自生成会逐渐丢失稀有模式。

会先丢掉分布尾部：反复用上一代输出训练下一代，少见情况越来越少，表达越来越像 teacher。应对是每代都保留真人或许可原始数据，只让独立 oracle 验证过的合成进训练，并追踪少见题和表达多样性。答案验证正确，也保证不了风格和覆盖不退化。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-synth-collapse)

### Microsoft Phi：教科书式 synthetic data 为什么有效，局限在哪？

> **回答思路**  
> **背景：** 高信息密度合成可能提高样本效率。  
> **任务：** 解释教科书式数据的收益与限制。  
> **做法与原因：** 固定规模对照，检查 teacher 偏差和 contamination。  
> **结果／验证：** 未见知识及语言覆盖支持，不能只看旧榜单。

#### 可以这样回答

高信息密度合成可能提高样本效率。

Phi 有效是因为提高了每个 token 的信息质量：Phi-1 用过滤代码加合成教材，让 1.3B 模型在 HumanEval 上超过更大的模型。局限在规模和 contamination，世界知识和 multilingual 仍需要足够多的许可网页，后续几代 Phi 也都加了数据量；teacher model 和改写带来的考题 leakage，n-gram deduplication 挡不住，要用新题和私有评测检查。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-phi-textbook)

### Cohere / xAI：preference data 怎么采，一致率低了改什么？

> **回答思路**  
> **背景：** preference data 质量取决于比较标准。  
> **任务：** 稳定收集 current policy 的有效标签。  
> **做法与原因：** 定义评价维度、tie 和弃权条件，让 annotators 先标一小批并核对标准。  
> **结果／验证：** 分歧原因可解释，独立选择质量提高。

#### 可以这样回答

preference data 质量取决于比较标准。

preference data 的质量主要看 annotation guidelines：先写清比较哪些维度、什么算 tie，再让当前模型生成待比较的回答。一致率 $\kappa$ 低时，先查题目、标准和示例是否含糊，改完再采；分歧来自标准本身时，加 annotator 也压不下去。能执行验证的任务优先用 rule-based reward，人只判断自动检查不了的维度。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-pref-collect)

### Cohere / Harvey：没有 gold labels、专家很贵，evaluation set 怎么造？

> **回答思路**  
> **背景：** 没有 gold labels 且专家预算有限。  
> **任务：** 建立可扩展但有 calibration 依据的评价。  
> **做法与原因：** 由专家明确 rubric，并说明 ambiguous cases 如何判断，自动检查可验证部分。  
> **结果／验证：** 独立专家抽查支持 judge，未知不强行打分。

#### 可以这样回答

没有 gold labels 且专家预算有限。

先按任务能不能自动判分来分配专家时间。能执行、有标准答案的做成自动评测，人只抽查；专家写评分标准、标 edge cases，再用少量样本 对 model scores 做 calibration。未经 calibration 的 LLM judge 只能辅助开发，生产日志也不能直接当 evaluation set。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-eval-no-gold)

### Cognition：榜涨了，用户说更差，数据侧先查哪几层？

> **回答思路**  
> **背景：** 公开榜涨分却不改善实际工作。  
> **任务：** 找到 benchmark 与产品失败的断点。  
> **做法与原因：** 依次查 contamination、judge、题目质量和分布。  
> **结果／验证：** 真实任务复测改善才接受数据干预。

#### 可以这样回答

公开榜涨分却不改善实际工作。

先诊断断在哪，再动数据。我会按顺序查四层：training set 有没有 leakage 评测题，scorer 是不是偏爱某种文风，基准题和测试本身有没有错，榜单任务和用户的实际工作差多远。没找到原因就加数据，很可能只是把榜单继续往上推。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-bench-vs-user)

### OpenAI / Cohere / Mistral：Prompt、RAG、fine-tuning，数据岗怎么站队？

> **回答思路**  
> **背景：** 知识更新、行为改变和私有检索需要不同办法。  
> **任务：** 选择最合适的能力载体。  
> **做法与原因：** 根据时效、许可与任务缺口比较 prompt、检索和训练。  
> **结果／验证：** 任务收益、权限隔离与维护成本一起检查。

#### 可以这样回答

知识更新、行为改变和私有检索需要不同办法。

依次问三个问题：知识经常变，或来源不允许进基础模型，就用带权限的 RAG 或工具；要改回答格式、工具习惯和拒答行为，做 SFT / RL；许可的世界知识属于 pre-training 或 continued PT。租户私有文件走带租户键的检索，不写进权重。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-prompt-rag-ft)

### Mistral：fine-tuning 之后旧能力掉了，数据怎么保住已有能力？

> **回答思路**  
> **背景：** 新任务 fine-tuning 可能覆盖已有能力。  
> **任务：** 保住旧任务同时学习新行为。  
> **做法与原因：** 做 regression data replay，并通过受控实验调整 data mix。  
> **结果／验证：** 新旧任务同时评，KL 或 LoRA 不当无遗忘保证。

#### 可以这样回答

新任务 fine-tuning 可能覆盖已有能力。

通过 replay 旧任务数据来保住已有能力。SFT 数据里留着通用指令、multilingual、安全和 tool calls 这些旧任务，每轮同时评新旧能力，旧能力退步超过阈值就减新任务权重或停训。KL 约束和 LoRA 只能让遗忘变慢，代替不了 replay。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-forget-sft)

### Perplexity：线上评测记什么、抽什么、怎么 A/B？

> **回答思路**  
> **背景：** 线上结果受流量、版本和用户行为混杂。  
> **任务：** 验证产品收益并发现失败类型。  
> **做法与原因：** 控制 A/B 变量，分层抽查合法记录。  
> **结果／验证：** 正确、安全、延迟分开报，反馈用于训练前需要授权。

#### 可以这样回答

线上结果受流量、版本和用户行为混杂。

线上评测用来发现失败类型、验证产品收益和成本。记录版本、延迟和工具行为是否合法，按失败类型分层抽查；A/B 尽量只换权重，正确率、安全和延迟分开报。用户原文进训练要有明确授权，补数据就用许可研究集复现失败，或者做验证过的合成。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-online-eval)

### Anthropic 作业：样本轴 double descent，对 data mix 意味着什么？

> **回答思路**  
> **背景：** 样本增加不保证误差单调下降。  
> **任务：** 避免凭条数判断 mix 价值。  
> **做法与原因：** 相同预算比较 data mix 和学习曲线。  
> **结果／验证：** 固定评价支持收益，非单调现象不代替 ablation study。

#### 可以这样回答

样本增加不保证误差单调下降。

意味着增加样本不保证评测一直变好：在插值区附近，测试误差可能先升再降，同类数据翻倍也可能变差。所以调 data mix 时，在相同计算预算下对比新旧 data mix 在固定 evaluation set 上的表现，同时看目标任务和旧能力。double descent 只是提醒结果可能非单调，比例还是由 ablation study 来定。

[原题及技术备查](http://127.0.0.1:3001/?book=apple-interview&section=research&question=dt-sample-descent)

