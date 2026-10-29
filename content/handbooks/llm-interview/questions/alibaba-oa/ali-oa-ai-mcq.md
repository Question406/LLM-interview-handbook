---
id: ali-oa-ai-mcq
section: alibaba-oa
order: 8
level: A
title: 阿里 AI 研发笔试选择：Teacher forcing、GQA、ReAct、MCP 会怎么挖？
quick: >-
  Teacher forcing 是训练喂金标前缀、推理喂模型自己的输出，所以有 exposure bias。GQA 让一组 Q 头共享 KV，压 KV
  头数换显存和带宽。ReAct 是思考和工具调用逐步交错；MCP 的 tool 是可能有副作用的可调用动作，resource 是只读的上下文。
tags:
  - Alibaba
  - OA
  - 选择题
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: 'https://www.nowcoder.com/discuss/866741961221292032'
    type: candidate-first-hand
---

这套选择题挖的坑很集中：Teacher forcing 考训推不一致，GQA 考省下来的到底是什么，ReAct 考「交错」，MCP 考有没有副作用。我会用做项目时的理解去选，框架官网的标题不用背。

题目来自阿里 AI 研发 2026.03.25 的笔试选择题，约 20 题，一半是 AI。公开出现过的考点有：teacher forcing 的训练与推理差异；MHA/MQA/GQA；LangChain vs LangGraph；ReAct action / observation separation；单 Agent vs multi-agent；长期记忆；tool 参数排错；多任务混合 RL；prompt injection；MCP tool vs resource。下面四节都按「可能的题干和选项 → 选哪个、为什么 → 落到阿里的场景 → 追问」来讲。

## Teacher forcing

autoregressive 训练时，下一步的条件是金标前缀，模型刚才自己生成的 token 不参与。时刻 $t$ 的输入是 $y_{<t}^{\star}$，损失是 $-\log p_\theta(y_t^{\star}\mid y_{<t}^{\star})$。推理时没有金标，只能把 $\hat y_{t-1}$ 喂回去。这个训推不一致叫 exposure bias：训练时从来没见过自己的错误前缀，一错就偏。

| | 训练（Teacher forcing） | 推理 |
| --- | --- | --- |
| 前缀 | 金标 $y^{\star}$ | 模型自己的 $\hat y$ |
| 并行 | 可并行计算全序列 cross entropy loss（CE） | 必须逐步 decoding |
| 风险 | 学得快，exposure bias | 误差累积 |

Scheduled sampling 按一定概率把金标换成模型输出，是一种折中，默认并不这么做。DPO / RL 阶段用的是模型自己 sampling 的轨迹，本身就在补这块偏差。

一道可能的题是「关于 Teacher forcing，下列哪一项正确？」

- A. 训练和推理都把模型上一步输出作为下一步条件，所以不存在 exposure bias
- B. 训练时下一步条件是金标前缀，推理时是模型自己的前缀，因此存在 exposure bias
- C. Teacher forcing 只用于编码器，decoding 器必须 scheduled sampling
- D. 只要加了 KL 正则，Teacher forcing 的训推差异就会消失

选 B。A 把训练说成了 autoregressive sampling 轨迹（rollout），那是推理或 on-policy RL 的做法。C 无中生有。D 里的 KL 约束的是策略别离参考太远，「训练喂金标、推理喂自己」这条结构差异它消不掉。

落到阿里的场景，Qwen 对话 SFT 用 Teacher forcing 并行打 CE，throughput 高；线上 decoding 是 autoregressive 的，用户一说口语化，模型要是在训练里没见过类似前缀就会飘。淘天客服如果只做 SFT，要靠 decoding 约束和检索把输出拉回来；真要补 exposure bias，就用 on-policy sampling 再做 RL。笔试里出现「为什么推理比训练胡话多」，先答这一条，再答 decoding 温度。多轮客服还有一层：训练时历史轮次也是金标，推理时上一轮可能已经答偏，后面几轮会沿着错的历史走，这是跨 turn 的 exposure bias。

**为什么不干脆全程不用 Teacher forcing？**
逐步训练太慢，梯度也不稳定。Free-running 训练和推理一致，但难收敛。

**teacher forcing 下的 token acc 能当评测指标吗？**
会虚高，要以生成指标为准。

**它和「标签泄漏」怎么区分？**
泄漏是特征里看见了答案；Teacher forcing 是合法地看见金标前缀，两者别混。

## GQA

attention 里 Query 头数 $H$ 和 KV 头数 $H_{kv}$ 可以不相等。MHA 是 $H_{kv}=H$，每个 Q 头独占一套 KV；MQA 是 $H_{kv}=1$，所有 Q 头共享一份 KV；GQA 把 $H$ 个 Q 头分成 $H_{kv}$ 组，组内共享 KV，$1 \lt H_{kv} \lt H$。它省的是 decoding 时 KV cache 的显存和带宽，Q 的表达力本身没动。

| | MHA | GQA | MQA |
| --- | --- | --- | --- |
| $H_{kv}$ | $H$ | $H/g$ | $1$ |
| KV 体积 | 最大 | 折中 | 最小 |
| 质量 | 通常最好 | 接近 MHA | 更易掉点 |
| 适用 | 小模型、训练 | 7B 以上推理默认 | 极致 throughput |

长上下文时 KV 按 $\text{layers} \times H_{kv} \times T \times d_{\text{head}}$ 增长，GQA 把 $H_{kv}$ 除以组大小，decoding 就吃得消了。训练阶段每步仍要算全量 QK，所以「GQA 让训练 FLOPs 降一个数量级」是错误选项，省下来的是推理时反复读取的 KV 缓存。MLA 是另一条路（低秩吸收），笔试没出现就别主动搅进去。RoPE 作用在每个头的旋转上，和 GQA 正交：分组共享 KV 以后，同一组的 Q 头仍然可以有不同的旋转后查询。

一道可能的题是「Grouped Query Attention（GQA）的主要收益是什么？」

- A. 增加 Query 头数，从而提高训练拟合能力
- B. 把 KV 头数降到少于 Q 头，降低 KV cache 带宽和显存，同时尽量保住质量
- C. 让所有头共享同一份 Q，从而减小激活
- D. 用分组卷积替换 attention，去掉 softmax

选 B。A 说反了，Q 头数通常不变。C 共享的是 KV，Q 没有共享。D 是另一类架构，和 GQA 无关。可以这样说：「KV 头从 $H$ 降到 $H_{kv}$ 再降到 $1$，省的是 KV 带宽，Q 的表达力不受影响。」

落到阿里的场景，Qwen 系列推理默认用 GQA 或类似的分组 KV，否则 32K 上下文的缓存会先把卡撑满。淘天客服要带长订单历史，KV 带宽直接决定 QPS。训练时仍可以按 MHA 的思路理解 attention，但上线必须报 $H_{kv}$。有人把 GQA 说成「减少计算量」，这不精确：训练时 FLOPs 降得有限，瓶颈在 decoding 时读 KV。批量服务时还要乘上 batch，热销会场的并发对话会把 KV 再放大一截，所以容量规划按「并发 × 平均长度 × $H_{kv}$」来估，光看参数量不够。

**组数怎么选？**
常见 $H_{kv}=8$ 或 $H/4$，用针探测试看质量掉多少。

**GQA 和量化谁先做？**
先 GQA，再做 KV 量化，收益可以叠加。

**MQA 为什么少用在大模型上？**
共享过度，长程依赖更容易糊。

**GQA 会不会改变训练的并行切分？**
会。KV 头变少以后，张量并行要按 $H_{kv}$ 能整除来切，不能再假设 KV 头数等于 Q 头数。

## ReAct

ReAct 把轨迹写成交错的 Thought / Action / Observation，一步一步往前走；先想好完整计划、再一次性调完所有工具，不算 ReAct。Thought 写当前还缺什么，Action 按 schema 调工具，Observation 写回真实的返回，然后进入下一轮 Thought。选错了工具或参数，必须靠 Observation 纠偏，禁止在 Thought 里假装成功。

| | 纯 chain of thought（CoT） | 先计划后执行 | ReAct |
| --- | --- | --- | --- |
| 工具 | 无 | 计划阶段一次性列完 | 逐步交错 |
| 纠错 | 只能改文字 | 计划错了后面全错 | 每步看 Observation |
| 风险 | hallucination 事实 | hallucination 计划 | 步数变长、要防死循环 |

LangChain 偏链式组件拼装，LangGraph 偏有状态的图、循环和分支。笔试问「哪个更适合带重试的 Agent」，选图 / 状态机，一条线性 chain 不合适。ReAct 是一种推理模式，跟哪个库的商标无关。

一道可能的题是「下列哪一项最符合 ReAct？」

- A. 模型先输出完整计划，再按计划并行调用全部工具，最后一次性总结
- B. 思考文本与工具调用交替进行，每一步以工具返回作为下一轮观察
- C. 只允许调用一次工具，否则就算 prompt 注入
- D. ReAct 等于把检索结果全部塞进系统提示，不再调用工具

选 B。A 是 plan-then-act，失败了不能中途改工具。C、D 都不符合 ReAct 的定义。Action / observation separation 上，Thought 里不要编造 Observation；工具超时属于执行失败，和选错工具要分开处理。

落到阿里的场景，淘天客服查物流是这样走的：Thought「缺运单号」→ 调订单工具 → Observation 拿到运单 → 再调物流工具。如果一开始就写「我要同时查优惠券、库存、物流」然后一把梭，一个工具失败整段作废。工具多的时候别把全量 schema 塞进 prompt，按意图检索或分级披露，这是字节和淘天都会追的工程细节。

**ReAct 和 function calling 是什么关系？**
function calling 是 Action 的接口形态，ReAct 是交错的策略。

**怎么防死循环？**
设最大步数、检测重复的 Action，同一个错误出现两次就换策略。

**单 Agent 还是 multi-agent？**
单步工具能解决的就别上多 Agent。多 Agent 用来拆角色和权限，默认并不更强。

## MCP

MCP（Model Context Protocol）把模型能接触的外部世界分成几种稳定的类型。**Tool** 是可调用的动作，有输入 schema，可能有副作用（发邮件、改订单、写库）。**Resource** 是可以拉取的只读材料（文件、工单快照、配置）。**Prompt** 是可复用的提示模板。生产上还要做鉴权、超时、审计和 schema 校验。Tool 返回失败就是一条 Observation，模型不能自己「脑补成功」。

| | Tool | Resource | Prompt 模板 |
| --- | --- | --- | --- |
| 方向 | 模型 → 世界（可能写入） | 世界 → 模型（只读） | 填槽后当上下文 |
| 副作用 | 有 | 无 | 无 |
| 安全 | 要授权、确认、幂等 | 要 ACL、脱敏 | 要防注入 |
| 例子 | `refund_order` | `order://123/snapshot` | 「客服话术 / 退款」 |

prompt injection 是用户输入或工具返回里夹带「忽略系统提示」之类的指令。防御办法是把工具返回当数据、不当指令，敏感 Tool 二次确认，权限最小化。MCP 只统一了接口，注入问题它不会自动解决。

一道可能的题是「在 MCP 里，tool 与 resource 的本质区别是？」

- A. tool 只能读数据库，resource 才能发写请求
- B. tool 是可能有副作用的可调用动作，resource 是可拉取的只读上下文
- C. 二者只是名字不同，协议层完全等价
- D. resource 必须是 HTTP，tool 必须是 gRPC

选 B。A 说反了。C 忽略了副作用和鉴权模型。D 把传输方式和语义绑死了，协议并没有这样规定。落地还要考虑超时、schema 校验、idempotency key 和审计日志。遇到参数排错题，先对照 schema 和 Observation，别改业务故事去迁就坏参数。

落到阿里的场景，以退款 Agent 为例：读订单快照用 resource，发起退款用 tool，而且 tool 要校验登录态和金额。长期记忆别每次都全量塞进 resource，热数据走检索，冷数据归档。多任务混合 RL 如果出现在选项里，记住不同任务的 reward 要 normalization 或分桶，不能直接相加；这是另一道题，别和 tool/resource 混在一起。

**tool 的参数要不要展示给用户？**
资金类的要。

**resource 变了怎么通知模型？**
靠订阅或者下次拉取，别假设上下文永远是新的。

**MCP 和普通 function calling 差在哪？**
MCP standardization 了发现、鉴权、资源和提示，一个 JSON schema 覆盖不了这些。
