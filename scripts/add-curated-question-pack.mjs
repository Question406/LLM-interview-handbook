import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const handbookPath = resolve("content/handbooks/llm-interview-v2.json");
const handbook = JSON.parse(readFileSync(handbookPath, "utf8"));

const sources = {
  dpo: { href: "https://arxiv.org/abs/2305.18290", label: "DPO 原论文" },
  onlinePreference: { href: "https://arxiv.org/abs/2312.11456", label: "Iterative Preference Learning" },
  grpo: { href: "https://arxiv.org/abs/2402.03300", label: "DeepSeekMath / GRPO" },
  grpoCalibration: { href: "https://arxiv.org/abs/2508.11800", label: "GRPO calibration analysis" },
  rewardBench: { href: "https://arxiv.org/abs/2403.13787", label: "RewardBench" },
  agentGuide: { href: "https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/", label: "OpenAI Agent guide" },
  webArena: { href: "https://arxiv.org/abs/2307.13854", label: "WebArena" },
  osWorld: { href: "https://arxiv.org/abs/2404.07972", label: "OSWorld" },
  mcp: { href: "https://modelcontextprotocol.io/specification/2025-06-18", label: "MCP specification" },
  toolUse: { href: "https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use", label: "Tool-use schema guide" },
  deepSeekV3: { href: "https://arxiv.org/abs/2412.19437", label: "DeepSeek-V3 / MTP" },
  streamingLlm: { href: "https://arxiv.org/abs/2309.17453", label: "StreamingLLM / attention sinks" },
  flashAttention: { href: "https://arxiv.org/abs/2205.14135", label: "FlashAttention" },
  nccl: { href: "https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html", label: "NCCL communicator guide" },
  calibration: { href: "https://arxiv.org/abs/1706.04599", label: "Calibration paper" },
  hfSampling: { href: "https://huggingface.co/docs/transformers/main/en/generation_strategies", label: "Generation strategies" },
  taotianInterview: { href: "https://www.nowcoder.com/discuss/909920471301226496", label: "2026 淘天 Agent 面经" },
  meituanInterview: { href: "https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0", label: "2025 美团大模型面经" },
};

const answer = (body, links) => `<div class="full-answer"><div class="mini-title">完整答案</div>${body}<div class="sources"><div class="mini-title">延伸阅读</div>${links.map(({ href, label }) => `<a href="${href}" target="_blank" rel="noreferrer">${label}</a>`).join("")}</div></div>`;

const entries = [
  {
    sectionId: "posttrain", id: "pt-dpo-to-grpo", level: "S", isRealInterview: true,
    title: "DPO 后模型分布变尖，还能直接接 GRPO 吗？",
    quick: "可以，但先确认当前 policy 还有足够 rollout diversity。若同题采样几乎相同，组内 reward 方差接近 0，GRPO 的相对优势会失去信号；应先恢复可控探索并监控能力漂移。",
    tags: ["DPO", "GRPO", "真实面经"],
    answerHtml: answer(`<p>可以把它看成一个合理的 warm start：DPO 先把策略带到较好的偏好区域，GRPO 再用当前策略的在线采样继续探索。但“DPO 一定让熵变低”并不成立；真正要检查的是同一 prompt 的候选是否还存在有效差异。</p><ul><li><b>先看信号：</b>组内 reward std、unique response rate、pass@k、token entropy 和 chosen/rejected margin。若一组全对或全错，relative advantage 近似为 0。</li><li><b>再恢复探索：</b>适度调高 rollout temperature/top-p，使用熵约束或更保守的学习率；必要时混入 SFT/DPO replay，避免格式和通用能力漂移。</li><li><b>别忘了 reference：</b>以 DPO checkpoint 为锚更偏局部改进；以更早的 SFT 为锚会给探索更大空间，也会带来更强优化张力。</li></ul><p>不能只看训练 reward，要同时看组内方差、长度和独立 held-out eval。</p>`, [sources.taotianInterview, sources.dpo, sources.grpo]),
  },
  {
    sectionId: "posttrain", id: "pt-rloo-vs-grpo", level: "A", isRealInterview: false,
    title: "RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？",
    quick: "两者都用同 prompt 的多条 rollout 降方差。RLOO 给每条样本用“其余样本 reward 的均值”作 leave-one-out baseline；GRPO 常用组均值并再按组标准差归一化，后者会改变 advantage 的尺度与统计性质。",
    tags: ["RLOO", "GRPO", "RL"],
    answerHtml: answer(`<p>两者的共同点是：不训练 learned value model，而是让同 prompt 的多次采样彼此充当 baseline。差别在 baseline 是否包含当前样本、以及是否再做 group-std normalization。</p><ul><li><b>RLOO：</b>对第 i 条 rollout，用其余 G−1 条 reward 的平均值作 baseline。这样当前 reward 不会“抵消自己”，是 REINFORCE baseline 的直接构造。</li><li><b>GRPO：</b>通常先用组均值中心化，再在实现中按组标准差缩放。它适合可验证、组内有明确相对好坏的任务，但全对/全错会没有相对信号。</li><li><b>追问点：</b>标准差归一化不是纯数值技巧；它会改变不同题目的权重，对随机结果上的 calibration 也可能有影响。要说明具体实现，而不是把所有“无 critic RL”混为一谈。</li></ul>`, [sources.grpo, sources.grpoCalibration]),
  },
  {
    sectionId: "posttrain", id: "pt-online-preference-loop", level: "S", isRealInterview: false,
    title: "为什么 Offline DPO 做到后面常要引入 Online Preference Loop？",
    quick: "固定偏好数据只覆盖旧策略会生成的区域。policy 变强后会走出 dataset support，离线 pair 的边际信息下降；在线循环通过“当前策略采样→标注/打分→更新”持续补齐新分布，但也把 reward hacking 和标注质量带回系统。",
    tags: ["DPO", "Online RLHF", "Data"],
    answerHtml: answer(`<p>Offline DPO 稳定又便宜，但它只能比较数据集已有的回答。模型更新后会把概率质量推向未被标注的新区域；此时继续重复旧 pair，既可能没有信息，也可能把数据中的长度/风格偏差放大。</p><ol><li>用当前或近期 policy 为同一 prompt 采样多个候选；</li><li>用人工、RM 或 verifier 生成带置信度的偏好；</li><li>以严格版本化的 policy、prompt、labeler 记录数据，再做受 KL/质量门控的更新；</li><li>保留固定 held-out human eval，检查 online reward 是否与真正质量一起提升。</li></ol><p>关键风险是“自己的 judge 给自己打分”。因此 online loop 需要独立审计集、对抗样本和数据去重，而不只是更频繁地训练。</p>`, [sources.onlinePreference, sources.dpo]),
  },
  {
    sectionId: "data", id: "data-annotator-agreement", level: "S", isRealInterview: false,
    title: "偏好标注者分歧很大时，应该删数据、投票，还是保留不确定性？",
    quick: "先分辨分歧来自任务本身、rubric、标注者能力还是界面/位置偏差。简单多数投票会丢掉不确定性；更稳妥的是记录重复标注、pair confidence 和分层一致性，并把低一致性样本用于诊断或软标签。",
    tags: ["Preference Data", "Annotation", "Quality"],
    answerHtml: answer(`<p>分歧不是自动等于“脏数据”。它可能暴露任务描述模糊、正确答案不唯一，或某一维度（安全、简洁、事实性）没有被 rubric 明确约束。</p><ul><li><b>先测量：</b>在同一批锚点上做重复标注，按任务/语言/难度/标注者分层看 agreement，而不是只报一个总准确率。</li><li><b>再处理：</b>高置信一致样本可作强监督；低置信但有价值的边界样本可保留为软偏好、降低权重，或进入人工 adjudication。</li><li><b>最后闭环：</b>回看判别依据，补充 rubric 和反例；若不同标注者代表不同产品偏好，应先明确产品目标，而不是让模型平均所有人。</li></ul>`, [sources.rewardBench]),
  },
  {
    sectionId: "data", id: "data-reward-calibration", level: "S", isRealInterview: false,
    title: "Reward Model / Judge 的 rank accuracy 高，为什么还要看 calibration？",
    quick: "排序对不等于分数可信。accuracy 只问“谁更高”，calibration 还问“0.9 的置信度是否真的约有 90% 正确”；一旦分数被用于阈值、拒答、采样或 RL，错误尺度会直接改变决策。",
    tags: ["Reward Model", "Calibration", "Eval"],
    answerHtml: answer(`<p>如果 judge 只用于每对二选一，排序正确率很重要；但工程里它常被用于筛选阈值、best-of-N、数据权重或作为 RL reward。此时分数尺度错误会造成过度过滤、过度优化或风险判断失真。</p><ul><li><b>看 reliability：</b>按预测置信度分桶，比较预测概率与真实偏好频率；同时报告 Brier / log loss，而非只报 accuracy。</li><li><b>看 OOD：</b>按长度、语言、领域、格式、对抗样本和 policy 版本切片；高分回答要抽样人工审计。</li><li><b>再决定用途：</b>可用 temperature / isotonic 等做后校准，但校准集必须独立；若 reward 只在训练分布可靠，就不应把它当无边界的 RL oracle。</li></ul>`, [sources.rewardBench, sources.calibration]),
  },
  {
    sectionId: "agent", id: "agent-schema-contract", level: "S", isRealInterview: false,
    title: "一个可供 Agent 稳定调用的 Tool Schema，除了参数类型还必须写什么？",
    quick: "Tool schema 是执行契约，不只是 JSON 字段。至少应明确何时调用、必填约束、单位/枚举、权限和副作用、幂等语义、可恢复错误与结构化返回；服务端必须验证，不能只相信模型输出。",
    tags: ["Tool Use", "Schema", "Agent"],
    answerHtml: answer(`<p>模型会把 tool description 当作行动空间的一部分。一个只写了字段类型的 schema，往往会导致“JSON 合法但业务错误”的调用。</p><ul><li><b>输入：</b>字段含义、单位、枚举、默认值、互斥/依赖约束，以及哪些信息禁止模型自行猜测。</li><li><b>执行：</b>read/write 副作用、权限范围、是否可重试、idempotency key 和异步任务状态。</li><li><b>输出：</b>machine-readable success/error code、可呈现摘要、下一步可行动信息，而非让模型解析一大段模糊 prose。</li></ul><p>服务端应做 schema 与业务规则验证；让 LLM 自己“遵守格式”只是一层 UX 辅助，不是安全边界。</p>`, [sources.toolUse, sources.mcp]),
  },
  {
    sectionId: "agent", id: "agent-tool-permissions", level: "S", isRealInterview: false,
    title: "为什么 Tool 权限不能只写在 System Prompt？怎样做最小权限？",
    quick: "Prompt 是行为引导，不是访问控制。真正的边界必须在工具服务端：按用户、会话、资源和动作签发最小 capability，并把高风险动作做显式确认、审计和幂等保护。",
    tags: ["Security", "Tool Use", "Permissions"],
    answerHtml: answer(`<p>一旦 Agent 能读写外部系统，模型、网页内容、检索结果和 tool result 都可能带来不可信指令。System prompt 可以降低误用率，却无法阻止越权请求到达 API。</p><ul><li><b>最小 capability：</b>令牌只允许当前用户、当前资源、当前动作和短 TTL；读、写、删除、转账等权限分离。</li><li><b>强制确认：</b>对外发信、删除、权限变更等高影响动作，在执行点要求可理解的确认，不让模型替用户静默决定。</li><li><b>可审计执行：</b>保存结构化 actor、resource、policy decision、request id 和最终状态；所有返回内容都按不可信数据处理。</li></ul>`, [sources.agentGuide, sources.mcp]),
  },
  {
    sectionId: "agentrl", id: "arl-environment-reset", level: "S", isRealInterview: false,
    title: "Agent RL 里的 Environment Reset 为什么比普通文本 RL 更难？",
    quick: "网页、数据库、文件和外部 API 都是有状态的。若 reset 不彻底，后一个 episode 会看到前一个轨迹留下的订单、缓存或权限，reward 和 observation 被污染，训练与 eval 都不再可比较。",
    tags: ["Agent RL", "Environment", "Reproducibility"],
    answerHtml: answer(`<p>文本 completion 通常可近似成独立样本；Agent episode 会改变环境。reset 是定义 MDP 初始状态分布的一部分，而不是测试基础设施细节。</p><ul><li><b>隔离状态：</b>为每个 episode 建独立账号/目录/数据库 snapshot，或能原子恢复到相同初始状态。</li><li><b>控制随机性：</b>记录 seed、任务版本、工具版本、网络 mock 与 observation 截止时间；但不要误以为“完全 deterministic”就等于真实。</li><li><b>处理副作用：</b>写操作必须 cleanup 或回滚；不可逆的外部行为应使用 sandbox 或 human gate。</li></ul><p>否则模型可能学会利用上一个 episode 遗留的捷径，offline reward 很高但部署立即失效。</p>`, [sources.webArena, sources.osWorld]),
  },
  {
    sectionId: "agentrl", id: "arl-offpolicy-reuse", level: "S", isRealInterview: false,
    title: "旧 Agent Trajectory 能不能反复拿来训练？什么时候会变成 Off-Policy 问题？",
    quick: "可以复用作 SFT、replay 或离线评估，但若把旧 policy、旧工具/网页状态下的轨迹当 current-policy policy-gradient 数据，就出现分布偏移。重要性权重会高方差，裁剪虽稳定却引入 bias。",
    tags: ["Agent RL", "Off-Policy", "Replay"],
    answerHtml: answer(`<p>只要行为 policy 与待优化 policy 不同，且你想估计 current policy 的回报梯度，就需要面对 off-policy correction。Agent 任务里偏移更大：policy 变了、检索索引变了、网页变了、工具版本也可能变了。</p><ul><li><b>先记录 behavior：</b>完整 policy/version、采样参数、action log-prob、环境版本和 reward 规则；没有 support 信息就很难做可靠 correction。</li><li><b>明确用途：</b>旧成功轨迹做 SFT/replay 通常合理；做严格 on-policy RL 更新时应限制 freshness 或采用有理论边界的 correction。</li><li><b>监控覆盖：</b>importance ratio 分布、有效样本量、被裁剪比例和按 trajectory length 的 return；这些比“replay buffer 很大”更重要。</li></ul>`, [sources.webArena, sources.grpo]),
  },
  {
    sectionId: "arch", id: "arch-mtp", level: "A", isRealInterview: false,
    title: "Multi-Token Prediction（MTP）训练目标能带来什么？为什么不等于“每次 decode 多吐几个 token”？",
    quick: "MTP 让模型在训练时预测多个未来 token，可增强序列表征；若把额外头作为 speculative draft，还需要 target verification 和足够 acceptance rate，才能在不改变目标分布的前提下获得实际加速。",
    tags: ["MTP", "Speculative Decoding", "Architecture"],
    answerHtml: answer(`<p>标准 next-token loss 只直接监督 t+1。MTP 增加多个未来位置的预测目标，让 hidden state 被要求携带更长程的可预测信息；其价值首先是训练信号，不是魔法式地改变 autoregressive 语义。</p><ul><li><b>训练：</b>定义每个预测头对应的 offset、loss 权重与 teacher forcing 边界，避免 future label 泄漏到主干输入。</li><li><b>推理：</b>draft 一次提出多个 token，target model 并行验证；被拒绝部分仍按 target 修正，因此目标分布由验证规则保证。</li><li><b>系统收益：</b>取决于 draft 成本、acceptance rate、KV/调度开销。若候选质量差，反而只增加工作量。</li></ul>`, [sources.deepSeekV3, sources.flashAttention]),
  },
  {
    sectionId: "arch", id: "arch-attention-sinks", level: "A", isRealInterview: false,
    title: "Attention Sink 是什么？滑动窗口长上下文为什么不能简单删除最早 token？",
    quick: "有些模型会持续给开头少数 token 分配注意力质量，即使它们语义信息很少。直接裁掉这些“锚点”可能让 softmax 分布失稳；streaming 方案常保留少量 sink token 再滑动近期窗口。",
    tags: ["Long Context", "Attention", "KV Cache"],
    answerHtml: answer(`<p>在无限流式输入中，KV cache 不能无限增长。朴素 FIFO eviction 看似合理，却可能突然损坏模型习惯使用的注意力锚点。Attention sink 指的正是这类长期吸收注意力质量的位置。</p><ul><li><b>现象：</b>首 token/特殊 token 即使语义贡献小，也可能反复得到较高 attention mass。</li><li><b>工程策略：</b>保留固定数量的初始 sink token，加上最近窗口；若用专门 sink，需要与训练/位置编码策略匹配。</li><li><b>别过度泛化：</b>是否存在、保留多少、是否影响任务质量都要做长流 eval；它不是所有模型都同样有效的通用定律。</li></ul>`, [sources.streamingLlm]),
  },
  {
    sectionId: "systems", id: "sys-online-softmax", level: "S", isRealInterview: true,
    title: "FlashAttention 的 Online Softmax 怎么在分块后仍保持精确？",
    quick: "每一行维护当前最大值 m 和归一化和 l。读到新 block 后更新 m′=max(m,m_block)，并把旧分子/分母按 exp(m−m′) 重标定，再累加新 block；因此无需 materialize 全部 attention matrix。",
    tags: ["FlashAttention", "Softmax", "真实面经"],
    answerHtml: answer(`<p>普通 attention 的瓶颈不仅是 FLOPs，还在于把 N×N score/probability 写回 HBM。FlashAttention 把 Q/K/V 分块，尽量在片上 SRAM 内完成计算，并通过 online softmax 合并每个 block 的结果。</p><ol><li>对已处理 block 保存行最大值 <b>m</b>、归一化和 <b>l</b> 与累积输出；</li><li>新 block 的最大值为 m<sub>b</sub>，令 m′=max(m,m<sub>b</sub>)；</li><li>把旧累计量乘 exp(m−m′)，新 block 按 exp(score−m′) 计算后再相加；</li><li>最后用累计分子除以 l，得到与整行 softmax 等价的精确结果。</li></ol><p>FlashAttention 不是近似 attention；核心是减少 HBM I/O，而非改变数学目标。</p>`, [sources.meituanInterview, sources.flashAttention]),
  },
  {
    sectionId: "systems", id: "sys-rl-memory", level: "S", isRealInterview: true,
    title: "7B 模型做 GRPO，显存主要花在哪里？怎么优化？",
    quick: "GRPO 虽去掉 Critic，却不等于“显存只剩一个 7B”。训练侧仍有 policy/reference/optimizer/activation，rollout 侧还有多条长序列与 KV；应先按训练、rollout、通信三类峰值拆账，再选 ZeRO、checkpoint、长度/G、colocation 或 disaggregation。",
    tags: ["GRPO", "Memory", "真实面经"],
    answerHtml: answer(`<p>先拒绝背一个固定 GB 数。峰值取决于精度、optimizer、ZeRO stage、sequence length、group size、并行策略，以及训练与 rollout 是否 colocate。</p><ul><li><b>训练侧：</b>policy 参数、gradient、optimizer states、activation 和临时通信 buffer；reference 可冻结但仍要参与 KL/log-prob 计算。</li><li><b>rollout 侧：</b>每个 prompt 的 G 条长 completion 都会占用 KV cache 与采样 buffer。GRPO 省掉 critic，并没有消除 group rollout 的乘数。</li><li><b>优化顺序：</b>先缩无效长尾、控制 group size/并发；再用 activation checkpoint、ZeRO/FSDP、合适的 TP/PP；最后根据集群拓扑决定 colocate、异步 weight sync 或 rollout/训练解耦。</li></ul><p>要把“训练 OOM”和“serving KV OOM”分开，它们的最佳解不同。</p>`, [sources.meituanInterview, sources.grpo]),
  },
  {
    sectionId: "systems", id: "sys-distributed-hang", level: "S", isRealInterview: false,
    title: "分布式训练卡住没有报错，怎样判断是 NCCL 问题还是代码路径不一致？",
    quick: "Collective 要求所有 rank 以相同顺序、相同 shape 参与。某个 rank 提前异常、数据耗尽、条件分支跳过通信，就会让其他 rank 看起来像“卡在 NCCL”；先定位最早发生分歧的 rank 和 collective。",
    tags: ["NCCL", "Distributed Training", "Debugging"],
    answerHtml: answer(`<p>“NCCL hang”是现象，不一定是网络故障。最常见的可复现原因是 rank divergence。</p><ol><li>为每个 collective 记录 rank、step、操作类型、tensor shape、sequence number 和前后的关键状态；</li><li>检查 dataloader 长度、OOM/exception、条件分支、gradient accumulation、unused parameter 和 checkpoint restore 是否在所有 rank 一致；</li><li>用 watchdog/timeout 获取堆栈，比较最早停止前进的 rank，而不是只盯最后超时的 rank；</li><li>确认代码路径一致后，再排查 communicator、网卡、拓扑与驱动版本。</li></ol><p>barrier 可以帮助缩小范围，但在错误位置额外插 barrier 也可能掩盖或制造死锁，不能当根治方案。</p>`, [sources.nccl]),
  },
  {
    sectionId: "fundamentals", id: "fund-calibration", level: "S", isRealInterview: false,
    title: "模型 Accuracy 很高但 Calibration 很差，产品决策会出什么问题？",
    quick: "准确率只计对错，不检查置信度是否可信。若 0.9 置信度的样本实际只对 0.6，基于阈值的拒答、人工转交、风险控制和 best-of-N 都会系统性误判；应结合 reliability、Brier/log loss 与业务成本选阈值。",
    tags: ["Calibration", "ML", "Decision"],
    answerHtml: answer(`<p>Calibration 问的是“模型说 80% 时，长期来看是否真的约 80% 正确”。两个模型 accuracy 相同，过度自信的那个在高风险自动化里通常更危险。</p><ul><li><b>测量：</b>reliability diagram、ECE（注意分桶敏感）、Brier score 和 NLL；按领域、难度、语言和时间切片。</li><li><b>决策：</b>阈值应由错误成本决定。例如高风险写操作需要更高置信度，还可能需要独立 verifier；不能把 0.5 当通用边界。</li><li><b>修复：</b>温度缩放等后校准可改善概率解释，但不能补回 OOD 知识；校准数据必须独立且持续更新。</li></ul>`, [sources.calibration]),
  },
  {
    sectionId: "coding", id: "code-sampling", level: "S", isRealInterview: false,
    title: "手写 Temperature + Top-p Sampling：顺序、数值稳定性和边界怎么处理？",
    quick: "先按 temperature 缩放 logits，再做稳定 softmax；Top-p 应按概率从高到低累积，保留最小的累计质量不少于 p 的 token 集合后重新归一化并采样。要处理 T→0、p 边界、NaN/Inf 和至少保留一个 token。",
    tags: ["Coding", "Sampling", "Inference"],
    answerHtml: answer(`<p>这题考的不只是会调 API，而是能说清“在什么分布上裁剪”。一个稳健实现应做到：</p><ol><li>对 logits 除以 T；T=0 或极小时显式走 argmax，避免数值爆炸；</li><li>减去最大 logit 后计算 softmax，并检查 NaN/Inf；</li><li>按概率降序排序，计算 cumulative probability，保留使累计质量首次达到 p 的最小前缀（至少一个 token）；</li><li>把被滤掉的 token mask 后重新归一化，再用随机数从 categorical 分布采样。</li></ol><p>追问：repetition penalty、min-p、top-k 与 temperature 的先后顺序必须由实现定义并测试；不同顺序会得到不同分布。</p>`, [sources.hfSampling]),
  },
];

for (const entry of entries) {
  const section = handbook.sections.find((candidate) => candidate.id === entry.sectionId);
  if (!section) throw new Error(`Unknown section: ${entry.sectionId}`);
  const answerPath = section.questions[0]?.answerPath;
  if (!answerPath) throw new Error(`Section has no answer chunk: ${entry.sectionId}`);
  const chunkPath = resolve(`public${answerPath}`);
  const chunk = JSON.parse(readFileSync(chunkPath, "utf8"));
  const metadata = {
    id: entry.id,
    level: entry.level,
    sectionId: entry.sectionId,
    title: entry.title,
    quick: entry.quick,
    tags: entry.tags,
    isRealInterview: entry.isRealInterview,
    searchText: [entry.title, entry.quick, ...entry.tags, entry.answerHtml.replace(/<[^>]+>/g, " ")].join(" ").replace(/\s+/g, " ").trim(),
    answerPath,
  };
  const existingIndex = section.questions.findIndex((question) => question.id === entry.id);
  if (existingIndex === -1) section.questions.push(metadata);
  else section.questions[existingIndex] = metadata;
  chunk[entry.id] = entry.answerHtml;
  writeFileSync(chunkPath, `${JSON.stringify(chunk)}\n`);
}

const allQuestions = handbook.sections.flatMap((section) => section.questions);
const sourceUrls = new Set();
for (const section of handbook.sections) {
  const answerPath = section.questions[0].answerPath;
  const chunk = JSON.parse(readFileSync(resolve(`public${answerPath}`), "utf8"));
  for (const html of Object.values(chunk)) {
    for (const match of html.matchAll(/href="([^"]+)"/gi)) sourceUrls.add(match[1]);
  }
}
handbook.updatedAt = "2026-08-17";
handbook.stats = {
  questions: allQuestions.length,
  mustKnow: allQuestions.filter((question) => question.level === "S").length,
  realInterviews: allQuestions.filter((question) => question.isRealInterview).length,
  sources: sourceUrls.size,
};
writeFileSync(handbookPath, `${JSON.stringify(handbook)}\n`);
console.log(`Question pack applied: ${entries.length} curated questions; handbook now has ${allQuestions.length} questions.`);
