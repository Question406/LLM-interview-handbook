# 编程题面完整性复核：2026-10-27

## 范围与方法

扫描所有题本的已发布编程源题，共 603 份文件；汇编手册对同一源题的引用不重复算，两个 LeetCode 题本中的独立源文件分别计数。系统设计和纯概念题不要求伪装成编程接口。

全量检查独立题面是否可提取、接口/输入与输出小节、具体示例、starter、参考实现和测试的语法。对密集 ML/训练题与多接口题进一步复核字段语义、loss/reduction、预处理隔离、默认交付与扩展范围。静态检查不能替代语义判断；“有标题或字数够长”不构成完整性证明。

| 题本 | 编程源题数 |
| --- | --- |
| apple-interview | 8 |
| data-team-interview | 53 |
| leetcode-150 | 150 |
| leetcode-75 | 75 |
| llm-interview | 102 |
| ml-101 | 13 |
| us-startup | 6 |
| us-tech | 196 |

## 修订结果

75 份题面已修订：19 份补充实际任务/字段/公式/状态/返回值，另 56 份拆清接口与示例小节。修订卡统一添加「题面补全 2026-10-27」，可以在网页题库搜索。

重点修订包括：分类训练、soft preference BCE、position-bias audit、DPO、response logprob、GAE 的 episode 假设、KL 方向与 reduction、GRPO aggregation、MoE 路由、Paged KV 初态、scikit-learn pipeline、noisy annotators、BCE 指标及 attention inputs。

## 验证

- 603 份练习经 practice loader 成功提取题面、starter、reference 和 tests；Python reference/tests 均可解析。
- 19 道实质修订题的参考实现和默认测试在本地环境全部执行通过，包括分类一步更新与完整 position-bias 三行例子。
- 比较本轮前后，603 道题的首个 Python 参考实现 block 未改变；两张题的测试增加了手算结果检查。
- 新增构建检查：示例必须单列小节、示例前必须说明接口或输入规则、示例必须包含具体输入与预期结果；加入相应 regression tests。
- 编程 statement 仍在解题思路之前；新增示例采用 text fences，不会被 runner 误当作 Python implementation。

## 本轮修订清单

| 题目 | 修订类型 |
| --- | --- |
| [编程：交换 AB／BA 后还原身份，计算 position bias 审计表](../../handbooks/apple-interview/questions/alignment/afm-rm-bias-audit-code.md) | 任务与契约补全 |
| [编程：soft preference BCE，如何区分投票比例与样本权重？](../../handbooks/apple-interview/questions/alignment/afm-rm-soft-target-code.md) | 任务与契约补全 |
| [45 分钟模拟 A：从零完成 PyTorch 分类训练并口述 data pipeline](../../handbooks/apple-interview/questions/mock/afm-mock-screen-a.md) | 任务与契约补全 |
| [Self-Attention Coding：实现 batched causal attention，并处理全 padding 行](../../handbooks/apple-interview/questions/tensor/afm-web-attention-code.md) | 任务与契约补全 |
| [CoderPad：按任务家族做配对 bootstrap，如何避免模板多的家族支配结论？](../../handbooks/data-team-interview/questions/tech-screen/dt-cluster-bootstrap-code.md) | 任务与契约补全 |
| [CoderPad：实现带 reference policy 的 DPO loss，并验证 gradient 方向](../../handbooks/data-team-interview/questions/tech-screen/dt-dpo-batch-code.md) | 任务与契约补全 |
| [Apple MLE 原帖：拿到数据后现场完成预处理、训练、评测与可视化](../../handbooks/data-team-interview/questions/tech-screen/dt-p3a-tabular-full-pipeline.md) | 任务与契约补全 |
| [CoderPad：KenLM / perplexity data quality checks 怎么写，阈值按语言怎么切？](../../handbooks/data-team-interview/questions/tech-screen/dt-ppl-filter-code.md) | 任务与契约补全 |
| [CoderPad：批量计算回答 log probability，EOS 和 padding 怎么对齐？](../../handbooks/data-team-interview/questions/tech-screen/dt-response-logprob-code.md) | 任务与契约补全 |
| [CoderPad：把变长对话组成 SFT batch，截断后还能保住监督信号吗？](../../handbooks/data-team-interview/questions/tech-screen/dt-sft-collate-code.md) | 任务与契约补全 |
| [手写 Beam Search 一步：累计 logprob、flatten top-k、backpointer 父 beam](../../handbooks/llm-interview/questions/coding/code-beam-search.md) | 任务与契约补全 |
| [手写 MoE router（softmax + top-k）和 Switch 风格 aux loss](../../handbooks/llm-interview/questions/coding/code-moe-router-aux-loss.md) | 任务与契约补全 |
| [手写 Paged KV Cache 的 block table 与 copy-on-write（beam / 分支）](../../handbooks/llm-interview/questions/coding/code-paged-kv-cow.md) | 任务与契约补全 |
| [京东零售二面：二叉树中序遍历如何非递归写？](../../handbooks/llm-interview/questions/coding/jd-inorder-iterative.md) | 题面结构拆分 |
| [拼多多应用开发：手写 Attention 时要写出哪些形状和 Mask？](../../handbooks/llm-interview/questions/coding/pdd-attention-handwrite.md) | 题面结构拆分 |
| [拼多多应用开发：如何手写交叉熵，数值上要防什么？](../../handbooks/llm-interview/questions/coding/pdd-ce-handwrite.md) | 题面结构拆分 |
| [阶跃星辰：手撕 top-p 采样，edge cases 怎么处理？](../../handbooks/llm-interview/questions/coding/stepfun-top-p-sampling.md) | 题面结构拆分 |
| [腾讯混元一面：生成所有合法括号组合](../../handbooks/llm-interview/questions/coding/tencent-generate-parens.md) | 题面结构拆分 |
| [腾讯混元一面：手写 Multi-Head Attention 要交代哪些形状？](../../handbooks/llm-interview/questions/coding/tencent-mha-handwrite.md) | 题面结构拆分 |
| [手写 DPO Loss：如何从 token logits 得到 sequence log-prob？](../../handbooks/llm-interview/questions/rl-coding/code-dpo.md) | 题面结构拆分 |
| [verl 里优势在 driver、clip 在 worker，代码怎么接？](../../handbooks/llm-interview/questions/rl-coding/code-fw-verl.md) | 题面结构拆分 |
| [手写 GAE：terminal 和 truncation 怎么处理？](../../handbooks/llm-interview/questions/rl-coding/code-gae.md) | 任务与契约补全 |
| [手写 GRPO group advantage：$\mathrm{std}\approx 0$ 怎么处理？](../../handbooks/llm-interview/questions/rl-coding/code-grpo.md) | 题面结构拆分 |
| [手写 PPO clipped surrogate，并解释 $A$ 的符号](../../handbooks/llm-interview/questions/rl-coding/code-ppo-clip.md) | 题面结构拆分 |
| [手写 PPO / GRPO / GSPO：TRL 和 verl 各改哪一段？](../../handbooks/llm-interview/questions/rl-coding/code-ppo-grpo-gspo.md) | 任务与契约补全 |
| [阶跃星辰：手撕 GRPO 时 loss 和组内优势分别怎么写？](../../handbooks/llm-interview/questions/rl-coding/stepfun-grpo-loss-handwrite.md) | 题面结构拆分 |
| [Anthropic：RL Fundamentals，修一段有 bug 的 GRPO](../../handbooks/us-tech/questions/anthropic/anthropic-grpo-debug.md) | 题面结构拆分 |
| [Anthropic：用 LLM 构造多步工具 Agent](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-agents-coding-llm-tool-use.md) | 题面结构拆分 |
| [Anthropic：同域爬虫：从 BFS 到并发和分布式](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-coding-q1-web-crawler.md) | 题面结构拆分 |
| [Anthropic：分布式众数与中位数：低带宽通信](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-coding-q4-distributed-mode-median.md) | 题面结构拆分 |
| [Anthropic：ML Programming：QKV Attention 与 einsum](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-ml-programming-screen.md) | 题面结构拆分 |
| [Anthropic：文件系统 OA：路径操作与未公开扩展](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-oa-file-systems.md) | 题面结构拆分 |
| [Anthropic：员工管理：打卡、晋升和重叠奖金](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-oa-worker-management.md) | 题面结构拆分 |
| [Anthropic：GRPO 调试与重要性采样比追问](../../handbooks/us-tech/questions/anthropic/p3a-anthropic-rl-fundamentals-grpo-debug.md) | 题面结构拆分 |
| [白板：AdamW 一步更新，m/v、bias correction、decoupled decay](../../handbooks/us-tech/questions/coding/coding-adamw.md) | 任务与契约补全 |
| [白板：BPE 训练一步 merge，词表膨胀；词尾标记写成 endofword 禁止 XML](../../handbooks/us-tech/questions/coding/coding-bpe-merge.md) | 题面结构拆分 |
| [白板：DPO 的梯度写成加权 logprob，权重是什么，什么时候大](../../handbooks/us-tech/questions/coding/coding-dpo-weighted.md) | 题面结构拆分 |
| [白板：融合 linear 和 cross entropy，不要物化 `[B, T, V]` logits](../../handbooks/us-tech/questions/coding/coding-fused-ce.md) | 题面结构拆分 |
| [白板：GRPO 的 token loss 怎么聚合成一个数？三种写法的长度偏置](../../handbooks/us-tech/questions/coding/coding-grpo-loss-agg.md) | 任务与契约补全 |
| [白板：token 级 KL（策略 vs 参考策略），reduction 和 ignore pad](../../handbooks/us-tech/questions/coding/coding-kl-div.md) | 任务与契约补全 |
| [白板：MQA 单 KV head，怎么对 query heads broadcast](../../handbooks/us-tech/questions/coding/coding-mq-attn.md) | 题面结构拆分 |
| [白板：QK RMSNorm 再 RoPE，Qwen / 部分 Llama 变体怎么写](../../handbooks/us-tech/questions/coding/coding-qk-norm.md) | 题面结构拆分 |
| [白板：RoPE 对 q/k 旋转，偶数维成对，decode 的 position](../../handbooks/us-tech/questions/coding/coding-rope.md) | 题面结构拆分 |
| [白板：sliding window 和 causal mask 合成，prefill 与 decode 的 shape](../../handbooks/us-tech/questions/coding/coding-swa-mask.md) | 题面结构拆分 |
| [白板：温度 → top-k → nucleus 的顺序，实现细节](../../handbooks/us-tech/questions/coding/coding-topk-nucleus.md) | 题面结构拆分 |
| [Cursor：投机解码的接受率与残差采样](../../handbooks/us-tech/questions/coding/p3a-cursor-speculative-decoding-acceptance.md) | 题面结构拆分 |
| [Perplexity：过期积分：时间范围与最早过期优先](../../handbooks/us-tech/questions/design/p3a-perplexity-credit-tracker-with-expiring-credits.md) | 题面结构拆分 |
| [Perplexity：历史 KV：时间戳操作与 restore](../../handbooks/us-tech/questions/design/p3a-perplexity-kv-store-with-timestamps-and-restore.md) | 题面结构拆分 |
| [Perplexity：第一处 stop 前截断与流式扩展](../../handbooks/us-tech/questions/design/p3a-perplexity-stop-sequences-before-first-match.md) | 题面结构拆分 |
| [Google：用 JAX 写一层 Transformer，shard、scan、remat 怎么摆](../../handbooks/us-tech/questions/google/google-jax-transformer.md) | 题面结构拆分 |
| [Meta Superintelligence/MLE：Attention 与 Flash/Linear 追问](../../handbooks/us-tech/questions/meta/p3a-meta-attention-implementation-and-follow-ups.md) | 题面结构拆分 |
| [Microsoft AI / Copilot：CSV 初始化的内存 SQL 引擎](../../handbooks/us-tech/questions/microsoft/p3a-microsoft-in-memory-sql-engine.md) | 题面结构拆分 |
| [Microsoft AI / Copilot：日志邮箱解析：显示名、注释与去重](../../handbooks/us-tech/questions/microsoft/p3a-microsoft-parse-emails-state-machine.md) | 题面结构拆分 |
| [NVIDIA：FlashDecoding split-K，和训练用 FlashAttention 差在哪](../../handbooks/us-tech/questions/nvidia/nvidia-flash-decode.md) | 题面结构拆分 |
| [OpenAI：GPU credit，调用乱序也要按时间重放](../../handbooks/us-tech/questions/openai/openai-gpu-credits.md) | 题面结构拆分 |
| [OpenAI：attention 里 softmax 轴和 mask 用 0 会怎样，怎么单测](../../handbooks/us-tech/questions/openai/openai-softmax-bug.md) | 题面结构拆分 |
| [OpenAI：标注员噪声：找出低质量标注并验证改进](../../handbooks/us-tech/questions/openai/p3a-openai-classifier-noisy-annotators.md) | 任务与契约补全 |
| [OpenAI：持久 KV：任意字节编码与 1KB 分文件](../../handbooks/us-tech/questions/openai/p3a-openai-durable-kv-store-serialization.md) | 题面结构拆分 |
| [OpenAI：内存 SQL：建表、插入、投影、筛选和排序](../../handbooks/us-tech/questions/openai/p3a-openai-in-memory-database-sql.md) | 题面结构拆分 |
| [OpenAI：随机求解时间：LLM 推理重启策略](../../handbooks/us-tech/questions/openai/p3a-openai-math-reasoning-stopping-time.md) | 题面结构拆分 |
| [OpenAI：怪兽战斗：基础规则、属性克制与目标策略](../../handbooks/us-tech/questions/openai/p3a-openai-monster-battle-system.md) | 题面结构拆分 |
| [OpenAI：可恢复迭代器：一维、二维和三维](../../handbooks/us-tech/questions/openai/p3a-openai-resumable-iterator.md) | 题面结构拆分 |
| [OpenAI：流式熵：logits 在线累积与数值稳定](../../handbooks/us-tech/questions/openai/p3a-openai-streaming-entropy.md) | 题面结构拆分 |
| [OpenAI：包版本依赖：约束解析与求解](../../handbooks/us-tech/questions/openai/p3a-openai-version-dependency.md) | 题面结构拆分 |
| [Mistral：每日 GPU 余量统计](../../handbooks/us-tech/questions/overview/p3a-mistral-daily-gpu-remaining.md) | 题面结构拆分 |
| [KV Prefix ⑤：链式块哈希、缓存上下文与碰撞防护](../../handbooks/us-tech/questions/systems/kv-prefix-block-hash.md) | 题面结构拆分 |
| [KV Prefix ②：手写 Radix Tree——插入、边分裂与任意前缀命中](../../handbooks/us-tech/questions/systems/kv-prefix-radix.md) | 题面结构拆分 |
| [xAI：一小时电影生成 Agent workflow](../../handbooks/us-tech/questions/xai/p3a-xai-agentic-one-hour-movie-generation.md) | 题面结构拆分 |
| [xAI：分布式 matmul：DP 与 FSDP 模拟](../../handbooks/us-tech/questions/xai/p3a-xai-distributed-matmul-dp-fsdp.md) | 题面结构拆分 |
| [xAI：嵌套 Python 容器 flatten 与 unflatten](../../handbooks/us-tech/questions/xai/p3a-xai-flatten-unflatten-nested-structure.md) | 题面结构拆分 |
| [xAI：有限内存时间窗第 k 大/小](../../handbooks/us-tech/questions/xai/p3a-xai-kth-element-streaming-window.md) | 题面结构拆分 |
| [xAI：图像 Patchify 与 CNN 输入轴转置](../../handbooks/us-tech/questions/xai/p3a-xai-patchify-cnn.md) | 题面结构拆分 |
| [xAI：迭代器 checkpoint：跨进程与嵌套恢复](../../handbooks/us-tech/questions/xai/p3a-xai-resumable-iterator-design.md) | 题面结构拆分 |
| [xAI：Spaces 活跃时长与流式并发 top-K](../../handbooks/us-tech/questions/xai/p3a-xai-twitter-spaces-active-hours.md) | 题面结构拆分 |
| [xAI coding：API rate limiter，多租户公平和突发](../../handbooks/us-tech/questions/xai/xai-rate-limiter.md) | 题面结构拆分 |
