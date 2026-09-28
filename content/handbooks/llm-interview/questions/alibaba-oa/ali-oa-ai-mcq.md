---
id: ali-oa-ai-mcq
section: alibaba-oa
order: 8
level: A
title: 阿里 AI 研发笔试选择：Teacher forcing、GQA、ReAct、MCP 会怎么挖？
quick: >-
  Teacher forcing 是训练喂真值、推理喂自己的输出。GQA 是压 KV 头数换带宽。ReAct 是推理-行动交错。MCP 的 tool 是可调用动作，resource 是可读上下文。
tags:
  - Alibaba
  - OA
  - 选择题
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

## 真题记录

- 公司 / 场次：阿里 AI 研发 2026.03.25 选择（约 20 题，一半 AI）
- 公开出现过：teacher forcing 训推差异；MHA/MQA/GQA；LangChain vs LangGraph；ReAct 边界；单 Agent vs multi-agent；长期记忆；tool 参数排错；多任务混合 RL；提示词注入；MCP tool vs resource。

这类题我靠项目口吻选，不背框架官网标题。下面四条按「可选题干 + 正确口径」展开。

## Teacher forcing

自回归训练时，下一步的条件不是模型刚才吐出的 token，而是金标前缀。时刻 $t$ 的输入是 $y_{<t}^{\star}$，损失是 $-\log p_\theta(y_t^{\star}\mid y_{<t}^{\star})$。推理时没有金标，只能把 $\hat y_{t-1}$ 喂回去。这条训推不一致叫 exposure bias：训练从未见过自己的错误前缀，一错就偏。

| | 训练（Teacher forcing） | 推理 |
| --- | --- | --- |
| 前缀 | 金标 $y^{\star}$ | 模型自己的 $\hat y$ |
| 并行 | 可并行算全序列 CE | 必须逐步解码 |
| 风险 | 学得快，暴露偏差 | 误差累积 |

Scheduled sampling 以概率把金标换成模型输出，是折中，不是默认。DPO / RL 阶段用自己采样的轨迹，本身就在补这块偏差。

可选题干：关于 Teacher forcing，下列哪一项正确？

- A. 训练和推理都把模型上一步输出作为下一步条件，所以不存在暴露偏差
- B. 训练时下一步条件是金标前缀，推理时是模型自己的前缀，因此存在 exposure bias
- C. Teacher forcing 只用于编码器，解码器必须 scheduled sampling
- D. 只要加了 KL 正则，Teacher forcing 的训推差异就会消失

正确口径：选 B。A 把训练说成了自回归 rollout，那是推理或 on-policy RL。C 无中生有。D 的 KL 约束的是策略别离参考太远，不消灭「训练喂金标、推理喂自己」这条结构差异。

阿里场景：Qwen 对话 SFT 用 Teacher forcing 并行打 CE，吞吐高；线上解码是自回归，用户一说口语化，模型若在训练里没见过类似前缀就会飘。淘天客服若只用 SFT，要靠解码约束和检索把输出拉回；要真补暴露偏差，用 on-policy 采样再 RL。笔试如果出现「为什么推理比训练胡话多」，先答这条，再答解码温度。多轮客服还有另一层：训练时历史轮次也是金标，推理时上一轮可能已经答偏，后面轮会沿着错历史走，这是跨 turn 的暴露偏差。

追问：为什么不全程不用 Teacher forcing？因为逐步训练太慢，梯度还不稳定。Free-running 训练和推理一致但难收敛。评测 teacher forcing 的 token acc 会虚高，要以生成指标为准。和「标签泄漏」怎么区分？泄漏是特征里看见了答案，Teacher forcing 是合法地看见金标前缀，二者不要混。

## GQA

注意力里 Query 头数 $H$ 和 KV 头数 $H_{kv}$ 可以不等。MHA 是 $H_{kv}=H$，每个 Q 头独占一套 KV。MQA 是 $H_{kv}=1$，所有 Q 头共享一份 KV。GQA 把 $H$ 个 Q 头分成 $H_{kv}$ 组，组内共享 KV，$1 \lt H_{kv} \lt H$。省的是解码时 KV cache 的显存和带宽，不是 Q 的表达力本身。

| | MHA | GQA | MQA |
| --- | --- | --- | --- |
| $H_{kv}$ | $H$ | $H/g$ | $1$ |
| KV 体积 | 最大 | 折中 | 最小 |
| 质量 | 通常最好 | 接近 MHA | 更易掉点 |
| 适用 | 小模型、训练 | 7B 以上推理默认 | 极致吞吐 |

长上下文时 KV 按 $\text{layers} \times H_{kv} \times T \times d_{\text{head}}$ 涨。GQA 把 $H_{kv}$ 除掉组大小，解码更吃得消。训练阶段每步仍要算全量 QK，所以「GQA 让训练 FLOPs 降一个数量级」是错选项；省的是推理时反复读取的 KV 缓存。MLA 是另一条路（低秩吸收），笔试没出现就不要主动搅进去。RoPE 作用在每个头的旋转上，和 GQA 正交：分组共享 KV 之后，同一组的 Q 头仍可以有不同旋转后的查询。

可选题干：Grouped Query Attention（GQA）的主要收益是什么？

- A. 增加 Query 头数，从而提高训练拟合能力
- B. 把 KV 头数降到少于 Q 头，降低 KV cache 带宽和显存，同时尽量保住质量
- C. 让所有头共享同一份 Q，从而减小激活
- D. 用分组卷积替换注意力，去掉 softmax

正确口径：选 B。A 说反了，Q 头数通常不变。C 共享的是 KV 不是 Q。D 是另一类架构，不是 GQA。正确说法：「KV 头从 $H$ 降到 $H_{kv}$ 再降到 $1$，省的是 KV 带宽，不是 Q 的表达力。」

阿里场景：Qwen 系列推理默认 GQA / 类似分组 KV，否则 32K 上下文的缓存先把卡撑满。淘天客服要带长订单历史，KV 带宽直接决定 QPS。训练仍可按 MHA 思路理解注意力，但上线必须报 $H_{kv}$。有人把 GQA 说成「减少计算量」不精确：训练时 FLOPs 降得有限，瓶颈在解码读 KV。批量服务时还要乘 batch，热销会场的并发对话会把 KV 再放大一截，所以容量规划按「并发 × 平均长度 × $H_{kv}$」估，别只看参数量。

追问：组数怎么选？常见 $H_{kv}=8$ 或 $H/4$，用针探看质量掉多少。和量化谁先做？先 GQA 再 KV 量化，收益叠加。MQA 为什么少用在大模型？共享过度，长程依赖更容易糊。GQA 会不会改变训练并行切分？会，KV 头变少后，张量并行要按 $H_{kv}$ 可整除来切，不能再假设头数等于 Q 头。

## ReAct

ReAct 把轨迹写成交错的 Thought / Action / Observation，不是「先想完整计划再一次性调完所有工具」。Thought 写当前缺口，Action 按 schema 调工具，Observation 写回真实返回，再进入下一轮 Thought。选错工具或参数时，必须用 Observation 纠偏，禁止在 Thought 里假装成功。

| | 纯 CoT | 先计划后执行 | ReAct |
| --- | --- | --- | --- |
| 工具 | 无 | 计划阶段一次性列完 | 逐步交错 |
| 纠错 | 只能改文字 | 计划错了后面全错 | 每步看 Observation |
| 风险 | 幻觉事实 | 幻觉计划 | 步数变长、要防死循环 |

LangChain 偏链式组件拼装；LangGraph 偏有状态图、循环和分支。笔试若问「哪个更适合带重试的 Agent」，选图 / 状态机，不要选一条线性 chain。ReAct 是推理模式，不是某个库的商标。

可选题干：下列哪一项最符合 ReAct？

- A. 模型先输出完整计划，再按计划并行调用全部工具，最后一次性总结
- B. 思考文本与 tool call 交替进行，每一步以工具返回作为下一轮观察
- C. 只允许调用一次工具，否则就算 prompt 注入
- D. ReAct 等于把检索结果全部塞进系统提示，不再调用工具

正确口径：选 B。A 是 plan-then-act，失败不能中途改工具。C、D 都不是 ReAct 定义。边界：Thought 里不要编造 Observation；工具超时是执行失败，和选错工具要分开处理。

阿里场景：淘天客服查物流：Thought「缺运单号」→ 调订单工具 → Observation 得到运单 → 再调物流工具。若先写「我要同时查优惠券、库存、物流」再一把梭，一个工具失败整段作废。多工具时不要把全量 schema 塞进 prompt，按意图检索或分级披露，这是字节和淘天都会追的工程细节。

追问：和 function calling 什么关系？function calling 是 Action 的接口形态，ReAct 是交错策略。如何防死循环？最大步数、重复 Action 检测、同一错误两次则换策略。单 Agent 和 multi-agent：能单步工具解决就不要上多 Agent，多 Agent 用来拆角色和权限，不是默认更强。

## MCP

MCP（Model Context Protocol）把模型可接触的外部世界分成稳定类型。**Tool** 是可调用动作，有输入 schema、可能有副作用（发邮件、改订单、写库）。**Resource** 是可拉取的只读材料（文件、工单快照、配置）。**Prompt** 是可复用的提示模板。生产还要鉴权、超时、审计、schema 校验。Tool 返回失败是 Observation，不是让模型自己「脑补成功」。

| | Tool | Resource | Prompt 模板 |
| --- | --- | --- | --- |
| 方向 | 模型 → 世界（可能写入） | 世界 → 模型（只读） | 填槽后当上下文 |
| 副作用 | 有 | 无 | 无 |
| 安全 | 要授权、确认、幂等 | 要 ACL、脱敏 | 要防注入 |
| 例子 | `refund_order` | `order://123/snapshot` | 「客服话术 / 退款」 |

提示词注入是用户或工具返回里夹带「忽略系统提示」之类指令。防御：工具返回当数据不当指令、敏感 Tool 二次确认、权限最小化。MCP 只统一接口，不自动解决注入。

可选题干：在 MCP 里，tool 与 resource 的本质区别是？

- A. tool 只能读数据库，resource 才能发写请求
- B. tool 是可能有副作用的可调用动作，resource 是可拉取的只读上下文
- C. 二者只是名字不同，协议层完全等价
- D. resource 必须是 HTTP，tool 必须是 gRPC

正确口径：选 B。A 说反了。C 忽略了副作用和鉴权模型。D 把传输和语义绑死，协议不这样规定。落地还要：超时、schema 校验、幂等键、审计日志。参数排错题的口径是「先对照 schema 和 Observation，不要改业务故事去迁就坏参数」。

阿里场景：退款 Agent：读订单快照用 resource，发起退款用 tool，并且 tool 要登录态和金额校验。长期记忆不要塞进每次 resource 全量：热数据检索，冷数据归档。多任务混合 RL 若出现在选项里，记住「不同任务的 reward 要归一化或分桶，不能直接加」，和 MCP 是另一条题，不要混进 tool/resource。

追问：tool 要不要对用户展示参数？资金类要。resource 变了怎么通知模型？靠订阅或下次拉取，不要假设上下文永远新鲜。MCP 和普通 function calling 差在哪？MCP 标准化了发现、鉴权、资源与提示，不只是一个 JSON schema。
