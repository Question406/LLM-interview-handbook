#!/usr/bin/env python3
"""Add Alibaba LLM talent-program interview section into llm-interview-v2."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDBOOK = ROOT / "content/handbooks/llm-interview-v2.json"
CHUNK_DIR = ROOT / "public/content/llm-interview-v2"
TEST = ROOT / "tests/content.test.mjs"


def answer(
    quick: str,
    full: str,
    followups: list[tuple[str, str]] | None = None,
    sources: list[tuple[str, str]] | None = None,
) -> str:
    parts = [
        f'<div class="quick"><div class="mini-title">30 秒回答</div><p>{quick}</p></div>',
        f'<div class="full-answer"><div class="mini-title">完整答案</div>{full}</div>',
    ]
    if followups:
        items = "".join(
            f'<details class="followup"><summary>{q}</summary><div class="follow-answer"><p>{a}</p></div></details>'
            for q, a in followups
        )
        parts.append(f'<div class="followups"><div class="mini-title">常见追问与答案</div>{items}</div>')
    if sources:
        links = "".join(
            f'<a href="{href}" target="_blank" rel="noopener noreferrer">↗ {label}</a>'
            for label, href in sources
        )
        parts.append(f'<div class="sources"><div class="mini-title">原始材料</div>{links}</div>')
    return "\n          ".join(parts)


SRC = {
    "taotian_agent_campus": ("淘天大模型 Agent 校招面经", "https://www.nowcoder.com/discuss/911218249889480704"),
    "taotian_agent_social": ("淘天 Agent 社招一面", "https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f"),
    "intl_algo": ("阿里国际大模型算法一面", "https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850"),
    "flash_agent": ("淘宝闪购 Agent 算法一面", "https://www.nowcoder.com/discuss/879393838081597440"),
    "taotian_prod": ("淘天 Agent 开发技术面", "https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda"),
    "ali_freq": ("阿里系 2025-26 算法高频整理", "https://www.nowcoder.com/discuss/848942791164981248"),
    "ai_oa": ("阿里 AI 研发 0325 笔试", "https://www.nowcoder.com/discuss/866741961221292032"),
    "ai_app_mcp": ("阿里 AI 应用开发面经 MCP", "https://www.nowcoder.com/discuss/877584799056023552"),
    "gspo": ("Qwen GSPO paper", "https://arxiv.org/abs/2507.18071"),
    "gspo_blog": ("Qwen GSPO blog", "https://qwenlm.github.io/blog/gspo/"),
}


QUESTIONS: list[dict] = []


def add(
    qid: str,
    level: str,
    title: str,
    quick: str,
    full: str,
    tags: list[str],
    *,
    real: bool = False,
    followups: list[tuple[str, str]] | None = None,
    sources: list[tuple[str, str]] | None = None,
    search_extra: str = "",
) -> None:
    html = answer(quick, full, followups, sources)
    searchable = " ".join(
        [
            title,
            quick,
            re.sub(r"<[^>]+>", " ", full),
            " ".join(tags),
            " ".join(a for _, a in (followups or [])),
            search_extra,
        ]
    )
    searchable = re.sub(r"\s+", " ", searchable).strip().lower()
    QUESTIONS.append(
        {
            "meta": {
                "id": qid,
                "level": level,
                "sectionId": "alibaba",
                "title": title,
                "quick": quick,
                "tags": tags,
                "isRealInterview": real,
                "searchText": searchable,
                "answerPath": "/content/llm-interview-v2/alibaba.json",
            },
            "html": html,
        }
    )


# --- Overview ---
add(
    "ali-prep-map",
    "S",
    "阿里 LLM 人才计划：应该按哪三条主线准备？",
    "算法主线 DPO→GRPO→DAPO/Dr.GRPO→GSPO；Agent 主线 Tool/MCP/Skill/Memory/RAG + credit assignment；系统主线 RoPE/GQA、ZeRO、KV Cache 与推理。淘天面经会把这三线串在同一轮里问。",
    """<p>阿里 LLM 人才相关岗位（通义 / 淘天 / 国际 / 闪购 Agent）公开面经高度一致，可按三条主线准备：</p>
<div class="table-wrap"><table><thead><tr><th>主线</th><th>必会节点</th><th>典型追问</th></tr></thead><tbody>
<tr><td>Post-Training</td><td>SFT 数据与 mask → preference/DPO → on-policy GRPO → DAPO/GSPO</td><td>为何不用继续 SFT？Advantages / KL / credit 怎么做？</td></tr>
<tr><td>Agent</td><td>规划、工具调度、MCP/Skill、Memory、RAG、Eval、Guardrail</td><td>双十一流量、幻觉拦截、多模态扩展</td></tr>
<tr><td>系统</td><td>RoPE、GQA、LoRA、ZeRO、显存手算、推理优化</td><td>白板推导与工程 trade-off</td></tr>
</tbody></table></div>
<p>准备方式：每条线准备一棵「定义 → 原理 → 项目落点 → 失败模式 → 验证」追问树，而不是背名词。</p>""",
    ["Alibaba", "备考地图", "Qwen"],
    sources=[SRC["taotian_agent_campus"], SRC["taotian_agent_social"], SRC["gspo"], SRC["gspo_blog"]],
)

# --- Post-Training / GRPO ---
add(
    "ali-grpo-vs-sft",
    "S",
    "阿里国际算法面：为什么选 GRPO 而不是继续 SFT / 蒸馏？",
    "SFT 适合教格式与示范轨迹；蒸馏适合逼近 teacher 分布；GRPO 适合有可验证/可打分目标、需要探索与相对优势更新时。选型看信号类型，不是谁更新。",
    """<p>公开阿里国际大模型算法面常开场就问技术选型：</p>
<ul>
<li><b>继续 SFT：</b>有高质量示范、格式/工具协议要稳定、需要快速对齐行为分布时优先。局限是缺乏探索，容易模仿 teacher 的平均行为，难突破上限。</li>
<li><b>蒸馏：</b>有强 teacher、希望小模型逼近其输出分布；仍是监督学习，突破 teacher 上限更难。</li>
<li><b>GRPO：</b>同 prompt 多样本、组内相对优势，适合数学/代码/可验证任务，或有明确 reward/verifier 的 Agent 场景；能做 on-policy 探索。</li>
</ul>
<p>面试回答要点：先说任务奖励是否可验证、数据是否成对 preference、是否需要探索；再落到你项目里为何选这条线。</p>""",
    ["Alibaba", "GRPO", "SFT"],
    real=True,
    followups=[
        (
            "什么时候三者可以串行？",
            "常见流水线是 SFT 打底 → DPO/偏好对齐 → on-policy GRPO 做 reasoning/工具成功率；蒸馏可穿插在压缩或部署模型阶段。",
        )
    ],
    sources=[SRC["intl_algo"]],
)

add(
    "ali-grpo-loss",
    "S",
    "阿里算法面：请写出 GRPO Loss，并解释每一项",
    "GRPO 用组内相对 advantage 的 clipped surrogate，再加相对参考策略的 KL。核心项是 ρ_t（重要性比）、A_t（组内标准化优势）、clip、以及 β·KL。",
    """<p>可按 PPO 风格写出（面试白板够用）：</p>
<p><code>L = -E[ min(ρ_t A_t, clip(ρ_t, 1-ε, 1+ε) A_t) ] + β · KL(π || π_ref)</code></p>
<p>其中 <code>ρ_t = π_θ(y_t|x,y_&lt;t) / π_old(y_t|x,y_&lt;t)</code>。</p>
<ol>
<li><b>ρ_t：</b>当前策略相对采样策略的概率比，衡量更新幅度。</li>
<li><b>A_t：</b>GRPO 通常用同组样本 reward 做相对标准化得到优势，决定更新方向与强度。</li>
<li><b>clip：</b>限制单步更新，防止策略崩溃；min 取更保守一侧。</li>
<li><b>β KL：</b>约束别偏离 SFT/参考策略太远，抑制 reward hacking 与语言崩坏。</li>
</ol>
<p>回答时强调：GRPO 的“相对”发生在 group 内，不依赖单独 critic/value model，是相对 PPO 的工程简化。</p>""",
    ["Alibaba", "GRPO", "真题"],
    real=True,
    followups=[
        ("ε 一般取多少？", "常见从 0.1–0.2 起步；过大更新不稳，过小学习慢。应结合 KL、reward 方差与崩坏率调。"),
        ("为什么要 π_ref？", "防止策略为刷高 reward 偏离自然语言/可用分布；也是对齐阶段的安全锚点。"),
    ],
    sources=[SRC["intl_algo"]],
)

add(
    "ali-grpo-advantage",
    "S",
    "GRPO 的 Advantage 怎么算？为什么不能直接用 raw reward？",
    "同 prompt 采一组样本，用组内 reward 均值/方差做相对标准化得到 A。直接用 raw reward 尺度不稳、同组不可比，且难区分“都还行”和“明显更好”。",
    """<p>典型做法：对同一 <code>x</code> 采样 G 条输出，得到奖励 <code>r_1…r_G</code>，令</p>
<p><code>A_i = (r_i - mean(r)) / (std(r) + ε)</code></p>
<p>（细节实现会有 baseline、length 归一、token 广播等变体。）</p>
<p>不用 raw reward 的原因：</p>
<ul>
<li>不同 prompt 难度不同，绝对分不可比；</li>
<li>reward 尺度漂移会让更新过猛或过弱；</li>
<li>相对优势更贴近“在当前组里谁更好”，方差通常更可控。</li>
</ul>
<p>若 group 内全对或全错，A≈0，学习信号消失——这正是 DAPO 等改进要处理的 failure mode。</p>""",
    ["Alibaba", "GRPO", "Advantage"],
    real=True,
    sources=[SRC["intl_algo"]],
)

add(
    "ali-importance-sampling",
    "A",
    "GRPO/PPO 为何需要重要性采样？新旧策略差很大时还有用吗？",
    "因为用旧策略采样的轨迹估计新策略目标，需要 ρ 校正。差太大时 ρ 方差爆炸、clip 频繁触发，估计质量变差，应更频繁同步采样策略或缩小更新。",
    """<p>On-policy 方法实际几乎总是“近似 on-policy”：用 <code>π_old</code> rollout，用 <code>π_θ</code> 更新。重要性比把贡献校正回当前策略。</p>
<p>当新旧策略差很大：</p>
<ul>
<li>ρ 极端值增多，方差上升；</li>
<li>clip 大量生效，有效更新变少；</li>
<li>估计偏差/方差同时恶化，训练不稳。</li>
</ul>
<p>工程应对：缩短 sync 间隔、减小学习率/clip 范围、监控 KL 与 ρ 分布、必要时重采样。</p>""",
    ["Alibaba", "GRPO", "PPO"],
    real=True,
    sources=[SRC["intl_algo"]],
)

add(
    "ali-grpo-kl-vs-ppo",
    "A",
    "GRPO 的 KL 和 PPO 的 KL 是一模一样的吗？",
    "目标都是约束 π 靠近参考/旧策略，但实现细节常不同：参考对象（π_ref vs π_old）、估计位置（token/sequence）、是否进 loss 或做 early-stop，面试要说清你用的实现。",
    """<p>相似点：都用 KL 防止更新过猛或奖励劫持。</p>
<p>常见差异：</p>
<ul>
<li><b>参考谁：</b>对齐阶段常用冻结 SFT 作 <code>π_ref</code>；PPO 实现里也常见相对 <code>π_old</code> 的近似 KL。</li>
<li><b>怎么估：</b>token-level 平均 KL、序列级 KL、或近似 KL；系数 β 调度也不同。</li>
<li><b>作用方式：</b>有的进 loss，有的做 target/阈值 early stop。</li>
</ul>
<p>阿里面经喜欢追：你监控哪些指标（KL、entropy、reward、崩坏率）来判断 KL 项是否过强/过弱。</p>""",
    ["Alibaba", "GRPO", "PPO"],
    real=True,
    sources=[SRC["intl_algo"]],
)

add(
    "ali-credit-token",
    "S",
    "序列级最终奖励，在 GRPO 里如何分配到每个 token？",
    "最常见是把序列 advantage 广播到所有生成 token；更细可做 step/action 边界对齐、过程奖励或 critic。粗广播能训但方差大，关键错误步与废话会被同等强化。",
    """<p>公开阿里算法面常问 credit assignment：</p>
<ol>
<li><b>序列广播：</b>整条 response 一个 R / A，每个 token 共享。实现简单，适合短 reasoning；长轨迹噪声大。</li>
<li><b>动作边界对齐：</b>Agent 多工具调用时，按 tool-call / turn 切段，只在 decision token 上优化。</li>
<li><b>过程奖励 / 验证器：</b>中间步骤可打分时用 denser signal。</li>
<li><b>Critic/TD：</b>需要 value 时再引入（GRPO 常刻意避免）。</li>
</ol>
<p>回答模板：先承认默认广播的局限 → 说明你任务长度与是否有 verifier → 给出可落地的更细 credit 方案。</p>""",
    ["Alibaba", "GRPO", "Credit"],
    real=True,
    followups=[
        (
            "Agent 多轮工具调用还有什么挑战？",
            "状态非平稳、工具失败重试、部分可观测、长 horizon credit、以及环境 reset/幂等。只靠 final success 往往不够。",
        )
    ],
    sources=[SRC["intl_algo"], SRC["taotian_agent_social"]],
)

add(
    "ali-multineg-then-grpo",
    "S",
    "淘天面经：单正多负 DPO 后，能否再接 GRPO？分类场景为何 DPO 常更稳？",
    "多负 DPO 主要学“正优于各负”，不保证学全负样本两两排序。DPO 压尖后可接 GRPO 做 on-policy 探索，但要防分布过尖导致采样退化。分类/偏好清晰时 DPO 往往更稳、更省。",
    """<p>淘天 Agent 公开面经原题方向：</p>
<ul>
<li><b>多负 DPO：</b>目标是拉高 chosen、压低各 rejected；并不自动得到 rejected 之间的精细序。若要序，需要更完整的 ranking/listwise 目标或额外约束。</li>
<li><b>接续 GRPO：</b>可以，用来在可验证奖励上恢复探索；但若 DPO 后 entropy 过低，group 样本多样性不足，A 信号变弱，需要调温度/约束或回退数据。</li>
<li><b>分类场景：</b>标签边界清晰、偏好噪声低时，DPO 这类离线偏好目标通常比 on-policy RL 更稳、成本更低；GRPO 更吃 verifier 与采样质量。</li>
</ul>""",
    ["Alibaba", "DPO", "GRPO"],
    real=True,
    sources=[SRC["taotian_agent_social"]],
)

add(
    "ali-reward-hacking",
    "A",
    "Reward hacking 是什么？训练指标里怎么发现？",
    "模型钻奖励模型/规则空子，指标上涨但真实质量下降。看 KL 异常、长度膨胀、模板刷分、人工抽检 divergence、多 RM 分歧。",
    """<p>典型现象：RM score ↑ 但人工偏好/下游任务 ↓；输出变长、套话、格式刷分；对已知 RM 弱点过拟合。</p>
<p>监控与缓解：</p>
<ul>
<li>同时看 task success、人工抽检、安全性，不只看 RM；</li>
<li>KL/entropy 约束与长度惩罚；</li>
<li>多奖励集成、定期换/重训 RM；</li>
<li>可验证任务尽量用 rule/verifier 代替纯 RM。</li>
</ul>""",
    ["Alibaba", "RLHF", "Reward"],
    real=True,
    sources=[SRC["intl_algo"]],
)

add(
    "ali-dapo-allcorrect",
    "A",
    "Group 里样本全对或全错时 GRPO 会怎样？DAPO 怎么处理？",
    "组内无相对差异 → advantage≈0，梯度信号消失。DAPO 等通过动态采样、非对称裁剪、或过滤无效 group 等机制保证仍有有效更新。",
    """<p>这是 reasoning RL 的经典 failure mode：难题全错、简单题全对，相对优势学不到东西。</p>
<p>回答结构：</p>
<ol>
<li>先解释 GRPO 依赖组内相对差异；</li>
<li>指出全对/全错导致 A 塌缩；</li>
<li>引出 DAPO/Dr.GRPO 等对采样、裁剪、标准化的修正；</li>
<li>落到实践：按难度 curriculum、保证 group 多样性、监控空 group 比例。</li>
</ol>
<p>阿里方向额外建议熟悉 Qwen <b>GSPO</b>：序列级重要性比与裁剪视角，和 token-level GRPO 对照着讲。</p>""",
    ["Alibaba", "DAPO", "GSPO"],
    real=True,
    sources=[SRC["intl_algo"], SRC["gspo"]],
)

# --- Taotian Agent campus ---
add(
    "ali-attention-math",
    "S",
    "淘天校招：Transformer Attention 的本质是什么？（数学角度）",
    "用 query 去匹配 keys 得到权重，再对 values 加权求和，是内容寻址的软检索/软组合。softmax(QKᵀ/√d)V。",
    """<p>把每个位置的表示投影为 Q/K/V：Q 表示“我要找什么”，K 表示“我能被怎样匹配”，V 表示“我提供什么内容”。缩放点积注意力输出是 values 的凸组合，本质是基于内容的软查找。</p>
<p>面试加分：提到因果掩码、多头并行子空间、以及与 RAG/工具检索在“寻址”思想上的类比（但机制不同）。</p>""",
    ["Alibaba", "Attention", "淘天"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-attention-agent-limit",
    "A",
    "Agent 多轮对话里，Attention 的局限性体现在哪？",
    "上下文长度与噪声、长程依赖被稀释、工具结果与历史混杂导致 distraction、计算/显存随序列平方或线性增长，且无法替代显式状态/记忆系统。",
    """<p>结合 Agent 场景回答：</p>
<ul>
<li>多轮 tool observation 堆积，真正关键证据被冲淡；</li>
<li>需要跨很早之前的约束/用户偏好时，纯 attention 不可靠；</li>
<li>无法天然提供可审计的外部状态、权限与终止条件；</li>
<li>因此要有 Memory/State/Skill/Harness 等系统层补偿。</li>
</ul>""",
    ["Alibaba", "Agent", "Attention"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-sft-then-posttrain",
    "S",
    "SFT 核心流程与数据构建？之后 Post-Training 各自解决什么？",
    "SFT：定任务分布→采/合成指令数据→清洗配比→监督学习。其后 DPO 解决偏好排序；PPO/RLHF 解决复杂主观目标；GRPO 等 RL 解决可验证/探索目标。",
    """<p><b>SFT：</b>定义场景与格式 → 采集/合成 instruction-response → 去重、安全过滤、难度与任务配比 → 设 loss mask → 用离线评测+人工评查看是否真变好。</p>
<p><b>之后：</b></p>
<ul>
<li><b>DPO：</b>成对偏好，学“更好 vs 更差”；</li>
<li><b>RLHF/PPO：</b>RM + 强化学习，拟合更复杂的人类偏好；</li>
<li><b>GRPO 等：</b>可验证奖励或 group 相对优化，强化推理/工具成功率。</li>
</ul>
<p>强调它们不是堆 buzzword，而是针对不同监督信号。</p>""",
    ["Alibaba", "SFT", "Post-Training"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-rag-eval",
    "S",
    "RAG 如何提升生成质量？怎样评估一个 RAG 是否 work？",
    "用检索证据约束生成，降低过时与幻觉。评估要拆开：检索（召回/精确/nDCG）、生成（忠实度/引用正确率）、端到端任务成功率，并做失败归因。",
    """<p>相对“裸生成”，RAG 把外部知识以证据形式注入上下文；与传统检索+模板不同，生成器需在证据上做综合与拒答。</p>
<p>评估分层：</p>
<ol>
<li>检索：Recall@k、Hit、nDCG、路由正确率；</li>
<li>生成： faithfulness、引用可追溯、拒答率；</li>
<li>业务：任务成功、人工满意度、延迟与成本。</li>
</ol>
<p>淘天追问常落到：切分策略、混合检索、rerank、以及“检索错还是生成幻觉”的归因。</p>""",
    ["Alibaba", "RAG", "Eval"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-ppo-dpo-grpo-ask",
    "S",
    "PPO 和 DPO 的主要区别？DPO 注意点？用过 GRPO 吗？",
    "DPO 用偏好对直接优化策略，无显式 RM/RL loop；PPO 先 RM 再 on-policy 优化，表达力强但复杂。DPO 怕噪声偏好与分布过尖；GRPO 用组内相对奖励做 on-policy 更新。",
    """<div class="table-wrap"><table><thead><tr><th></th><th>DPO</th><th>PPO/RLHF</th><th>GRPO</th></tr></thead><tbody>
<tr><td>数据</td><td>preference pairs</td><td>偏好→RM + rollout</td><td>同题多样本 + reward/verifier</td></tr>
<tr><td>复杂度</td><td>低</td><td>高（四模型）</td><td>中（无 critic，要采样）</td></tr>
<tr><td>风险</td><td>噪声敏感、缺探索</td><td>RM hacking、不稳</td><td>空 group、credit 粗</td></tr>
</tbody></table></div>
<p>DPO 注意：数据质量、β、length bias、是否真提升 chosen 有用性而不只是压 rejected。</p>""",
    ["Alibaba", "DPO", "GRPO"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-modular-agent-plan",
    "A",
    "Modular Agent 如何实现多步规划？工具链路调度与 fallback 怎么设计？",
    "规划器产出步骤/子目标，执行器按状态机调用工具；每步有输入输出契约、超时重试、幂等与降级。fallback：换工具、缩任务、澄清用户、转人工。",
    """<p>工业界回答要落到控制面：</p>
<ul>
<li><b>规划：</b>Plan-and-Execute / ReAct；关键业务可用确定性工作流包住 LLM 规划。</li>
<li><b>调度：</b>工具白名单、并行/串行依赖、参数 schema 校验。</li>
<li><b>fallback：</b>瞬时错误重试；逻辑错误换策略；超预算终止；高风险 Human-in-the-loop。</li>
<li><b>可观测：</b>trace、tool 指纹、重复调用检测防死循环。</li>
</ul>""",
    ["Alibaba", "Agent", "Harness"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-agent-eval-dims",
    "S",
    "Agent 评估体系有哪些维度？如何衡量 planning vs hallucination？",
    "任务成功率、步数/成本、工具正确率、规划遵从、幻觉/忠实度、安全越权率、澄清率。Planning 看子目标分解与依赖；幻觉看无证据断言与错误 tool 参数。",
    """<p>建议把指标拆开，避免只看最终 success：</p>
<ul>
<li><b>Outcome：</b>任务完成、业务 KPI；</li>
<li><b>Process：</b>平均工具轮次、无效调用、循环率；</li>
<li><b>Planning：</b>计划可执行性、关键步骤覆盖、是否过早结束；</li>
<li><b>Hallucination：</b>无依据事实、伪造引用、与工具结果矛盾；</li>
<li><b>Safety：</b>越权、不可逆操作未确认。</li>
</ul>
<p>最好有固定评测集 + trace 回归，而不是每次人工聊天感觉。</p>""",
    ["Alibaba", "Agent", "Eval"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-qwen-finetune-loss",
    "A",
    "微调 Qwen 时，训练阶段和 Loss 如何选择？",
    "先定目标：指令遵循用 SFT（只对 assistant/action token 计 loss）；偏好用 DPO；可验证目标用 GRPO。阶段不要跳，数据与 mask 必须匹配部署协议。",
    """<p>淘天校招原题常见追问：</p>
<ul>
<li>为何先 SFT 再对齐：先学会格式/工具协议，再优化偏好或成功率；</li>
<li>Loss mask：user/tool response 通常不进 policy loss；</li>
<li>LoRA vs 全参：数据少/多任务隔离用 LoRA；要大幅改行为再考虑更大更新；</li>
<li>用 Qwen 系列时关注其 chat template、tool schema 与官方 post-train 实践（含 GSPO）。</li>
</ul>""",
    ["Alibaba", "Qwen", "SFT"],
    real=True,
    sources=[SRC["taotian_agent_campus"], SRC["gspo"]],
)

add(
    "ali-prompt-optimize",
    "B",
    "Prompt 自动推荐/压缩可用哪些策略？",
    "模板分层、示例检索、embedding 聚类选示范、摘要压缩、关键槽位结构化；效果要用任务指标验证，不只看更短。",
    """<p>常见路线：</p>
<ul>
<li>按意图路由到短模板；</li>
<li>用 embedding 检索相似成功 case 作 few-shot；</li>
<li>长历史摘要 + 结构化 state，避免全文拼接；</li>
<li>对工具说明做裁剪，只暴露当前任务相关 tools。</li>
</ul>""",
    ["Alibaba", "Prompt", "Context"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

add(
    "ali-latency-3tools",
    "S",
    "场景题：Agent 链路含 3 个工具且高频请求，延迟如何优化？",
    "并行可并行的工具、缓存高频路径、意图分流到轻量模板、缩小 prompt/工具集、投机/小模型草稿、超时降级与限流。先量测再改。",
    """<p>建议按依赖图优化：</p>
<ol>
<li>画清 3 个工具的串并行依赖，能并行就并行；</li>
<li>高频 query 走缓存或固定 workflow，绕开多轮 LLM；</li>
<li>首包分类用小模型，复杂再上大模型；</li>
<li>压缩上下文与 tool schema，减少 prefill；</li>
<li>设 SLA：超时跳过非关键工具或降级 FAQ；</li>
<li>看 p95/p99、工具 RT、LLM RT、排队，避免盲目换更大模型。</li>
</ol>""",
    ["Alibaba", "Agent", "性能"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)

# --- Skill / Memory / MCP ---
add(
    "ali-skill-memory-rag",
    "S",
    "淘天面经：Skill、Memory、RAG 分别解决什么核心问题？",
    "Skill 解决“这类任务怎么做”的程序化经验复用；Memory 解决跨会话状态与个性化；RAG 解决外部知识证据注入。三者别混成一个向量库。",
    """<div class="table-wrap"><table><thead><tr><th>组件</th><th>核心问题</th><th>典型实现</th></tr></thead><tbody>
<tr><td>Skill</td><td>How to do this class of tasks?</td><td>流程+模板+脚本+工具使用规范，按需加载</td></tr>
<tr><td>Memory</td><td>What should persist across turns/sessions?</td><td>短上下文、摘要、画像、向量事件</td></tr>
<tr><td>RAG</td><td>What evidence do I need now?</td><td>检索知识库/文档并引用</td></tr>
</tbody></table></div>
<p>淘天追问重点是边界：把操作手册塞进 RAG ≠ 有 Skill；把所有历史塞进窗口 ≠ 有 Memory 治理。</p>""",
    ["Alibaba", "Skill", "Memory", "RAG"],
    real=True,
    sources=[SRC["taotian_agent_social"]],
)

add(
    "ali-memory-conflict",
    "A",
    "Agent 记忆如何迭代？新旧经验冲突时怎样取舍？",
    "分短/长期：短期窗口+摘要；长期结构化写入要带时间戳/来源/置信度。冲突时按时间、权威来源、用户显式更正优先，并支持遗忘与审计。",
    """<p>可落地策略：</p>
<ul>
<li>写入前做冲突检测（同实体不同值）；</li>
<li>保留 provenance：谁说的、何时、哪次工具结果；</li>
<li>用户更正 &gt; 工具权威数据 &gt; 模型推断；</li>
<li>定期衰减低置信记忆，防记忆污染。</li>
</ul>
<p>闪购等面经还会问长周期对话的分层压缩：近详远略 + 关键事件入库检索。</p>""",
    ["Alibaba", "Memory"],
    real=True,
    sources=[SRC["taotian_agent_social"], SRC["flash_agent"]],
)

add(
    "ali-agent-final-reward",
    "S",
    "Agent RL 只靠最终结果奖励够不够？多步工具轨迹如何 credit？",
    "经常不够。长 horizon 下要过程奖励、关键决策步加权、失败可恢复轨迹，或 action-level 优化，否则成功归因模糊。",
    """<p>淘天原题方向与手册 Agent RL 章一致：final reward 广播方差大。</p>
<p>实践组合：</p>
<ul>
<li>任务成功 + 成本/步数惩罚；</li>
<li>关键 tool 参数正确性过程分；</li>
<li>对 irreversible action 单独约束；</li>
<li>用评测集区分“偶然成功”与“稳健策略”。</li>
</ul>""",
    ["Alibaba", "Agent RL", "Credit"],
    real=True,
    sources=[SRC["taotian_agent_social"]],
)

add(
    "ali-score-vs-agent",
    "A",
    "单次 LLM 打分算不算 Agent？和多轮工具 Agent 的核心区别？",
    "单次打分更像一次性推理/判别；Agent 强调多步决策、与环境交互、状态更新与终止条件。差别在控制回路，不在是否调用了一次模型。",
    """<p>可用定义对齐面试官：</p>
<ul>
<li><b>单次打分：</b>无环境反馈闭环，或只有一次 forward；</li>
<li><b>Agent：</b>observe→act→observe 循环，工具/用户/环境改变 state。</li>
</ul>
<p>不要把“用了 LLM”等同于 Agent；要讲清状态、动作空间、停止条件与责任边界。</p>""",
    ["Alibaba", "Agent"],
    real=True,
    sources=[SRC["taotian_agent_social"]],
)

add(
    "ali-mcp-vs-fc",
    "S",
    "MCP 和 Function Calling 的区别？为何生产不能只靠 FC？",
    "FC 是模型生成结构化调用的接口形态；MCP 是工具/资源/提示的标准化连接协议，便于跨客户端复用、鉴权与治理。生产需要协议层，而不是每个业务手写一份工具描述。",
    """<p>FC：应用把 tools schema 塞进请求，模型返回调用；执行仍在宿主。</p>
<p>MCP：把能力抽象为可发现的 tools/resources，统一 schema、权限、传输（stdio/HTTP/SSE 等），让多个 Agent/模型复用。</p>
<p>只靠 FC 的问题：工具描述分裂、权限难管、日志不统一、难以跨团队复用。大厂更在意协议层与业务层解耦。</p>""",
    ["Alibaba", "MCP", "Tool"],
    real=True,
    sources=[SRC["ai_app_mcp"]],
)

# --- Production Agent ---
add(
    "ali-double11-scale",
    "S",
    "淘天场景：把 Agent Demo 改造成支撑“双十一”级流量，最大挑战是什么？",
    "不是换更大模型，而是：限流与降级、缓存高频路径、异步化与削峰、状态外置、可观测与熔断、成本预算。先保证正确的关键路径可降级存活。",
    """<p>架构挑战可按层答：</p>
<ol>
<li><b>流量：</b>网关限流、队列削峰、关键/非关键分流；</li>
<li><b>算力：</b>小模型/模板兜底，大模型只服务复杂单；</li>
<li><b>状态：</b>会话与记忆外置，避免单机亲和；</li>
<li><b>依赖：</b>工具超时、舱壁隔离、缓存商品/订单热点；</li>
<li><b>发布：</b>灰度、熔断、回滚、审计。</li>
</ol>
<p>面试官听的是：你懂电商大流量下 AI 系统的工程约束。</p>""",
    ["Alibaba", "Agent", "高并发"],
    real=True,
    sources=[SRC["taotian_prod"]],
)

add(
    "ali-framework-choice",
    "A",
    "Agent 编排选 LangChain 类开源还是自研？",
    "PoC 可用开源加速；生产看可控性、可观测、权限与性能。核心业务链路往往自研状态机/图编排，开源作外围。关键是 trade-off，不是站队。",
    """<p>对比维度：开发速度、可调试性、版本锁定、性能开销、安全合规、团队熟悉度。</p>
<p>淘天/闪购面经共同点：能说清“为何选/为何不选”，并承认企业内数据不出域、私有化约束。</p>""",
    ["Alibaba", "Agent", "架构"],
    real=True,
    sources=[SRC["taotian_prod"], SRC["flash_agent"]],
)

add(
    "ali-guardrail",
    "S",
    "如何控制 Agent 自主性边界？Safety Guardrail 怎么设计？",
    "规则引擎管硬约束，LLM 管柔推理；工具分级（只读/可逆/不可逆）；不可逆前人工确认；输出过滤与策略引擎双闸门。",
    """<p>退换货等明确规则场景：优先规则/工作流，LLM 负责理解与填槽，不负责改规则。</p>
<p>Guardrail 分层：输入安全 → 工具权限 → 执行确认 → 输出合规检查 → 审计。自主性随风险升高而降低。</p>""",
    ["Alibaba", "Safety", "Agent"],
    real=True,
    sources=[SRC["taotian_prod"], SRC["flash_agent"]],
)

add(
    "ali-hallucination-intercept",
    "A",
    "幻觉或不合规内容，工程上如何在生成前后拦截？",
    "前：检索强制、工具结果优先、拒答策略；中：schema/规则校验；后：事实核对、敏感词/合规模型、引用存在性检查。关键路径可双模型复核。",
    """<p>可落地机制：</p>
<ul>
<li>生成前：必须先查知识库/订单系统，禁止空上下文臆造；</li>
<li>生成中：结构化输出与工具参数校验失败则重试；</li>
<li>生成后：NLI/规则核对、敏感分类、人工抽检队列；</li>
<li>高风险域：默认检索增强 + 拒答，而不是强行回答。</li>
</ul>""",
    ["Alibaba", "Hallucination", "安全"],
    real=True,
    sources=[SRC["taotian_prod"]],
)

add(
    "ali-multimodal-arch",
    "B",
    "为 Agent 增加“以图找同款”，后端要做哪些改造？",
    "增加视觉理解/特征服务、图搜索引、多模态检索链路、权限与审核、以及 Agent 工具 schema；编排上新增“图→候选→确认”状态，并评估延迟与成本。",
    """<p>改造清单：</p>
<ul>
<li>接入多模态模型或特征提取服务；</li>
<li>商品图索引与相似度检索；</li>
<li>新 tool：image_search_same_item；</li>
<li>链路：上传→检索→重排→商品卡→用户确认；</li>
<li>内容安全与版权审核；</li>
<li>监控：检索空结果率、同款准确率、RT。</li>
</ul>""",
    ["Alibaba", "多模态", "Agent"],
    real=True,
    sources=[SRC["taotian_prod"]],
)

add(
    "ali-hitl-risk",
    "A",
    "闪购面经：Human-in-the-Loop 与高风险异常管控怎么做？",
    "关键 tool 前插入确认；低置信暂停；工具分级+熔断；沙箱与生产隔离；结构化审计。指令里写清 STOP_CONDITION，并在代码层强制执行。",
    """<p>要点：HITL 不能只靠 prompt 自觉，要在编排层强制。</p>
<ul>
<li>只读 / 可逆写入 / 不可逆 三级权限；</li>
<li>连续失败 N 次熔断；</li>
<li>长周期记忆分层压缩，冷启动靠检索关键事件；</li>
<li>承认缺闭环时，用任务成功率做 DPO/PPO 与沙盒 ELO 选优。</li>
</ul>""",
    ["Alibaba", "HITL", "Agent"],
    real=True,
    sources=[SRC["flash_agent"]],
)

add(
    "ali-auc-offline-online",
    "A",
    "AI Coding 压轴：离线 AUC 高、上线暴跌，如何从数据/标签/serving 归因？",
    "优先查 train-serving skew、样本分布偏移、特征泄露、标签口径/延迟、标注噪声、模型与 feature schema 不一致、在线缺失填充与精度差异。",
    """<p>公开闪购面经给的排序思路（可作答模板）：</p>
<ol>
<li>Train-Serving 特征分布偏移；</li>
<li>线上样本分布与训练不一致；</li>
<li>特征泄露导致离线虚高；</li>
<li>标签定义口径不一致；</li>
<li>Label delay；</li>
<li>标注噪声放大；</li>
<li>版本与 schema 未对齐；</li>
<li>在线推理精度/缺失填充策略差异。</li>
</ol>
<p>回答时说明：用日志回放、特征监控、切片评估验证，而不是只猜。</p>""",
    ["Alibaba", "Eval", "AI Coding"],
    real=True,
    sources=[SRC["flash_agent"]],
)

# --- Systems + OA ---
add(
    "ali-arch-hotspots",
    "S",
    "通义/云智能方向：架构与系统高频题该怎么刷？",
    "白板优先：RoPE 相对性与外推、RMSNorm/Pre-Norm、SwiGLU 参数量、GQA 与 KV Cache、LoRA 初始化与 α、ZeRO 显存手算、TP 切分。每题练到能画图讲 trade-off。",
    """<p>据阿里系公开面经统计，高频簇是：</p>
<ul>
<li>位置编码 RoPE（含长上下文外推）；</li>
<li>GQA/MQA 与推理带宽；</li>
<li>LoRA/QLoRA；</li>
<li>ZeRO 1/2/3 与显存构成；</li>
<li>推理：PagedAttention、量化、投机解码。</li>
</ul>
<p>这些题在手册 Architecture / Systems 章已有深卡；本卡作阿里定向刷题清单。</p>""",
    ["Alibaba", "Architecture", "Systems"],
    sources=[SRC["ali_freq"]],
)

add(
    "ali-ai-oa",
    "B",
    "阿里 AI 研发笔试（选择 + 编程 + Prompt）怎么准备？",
    "选择覆盖 Transformer/Agent/MCP + CS 基础；编程仍是算法；Prompt 题要写清角色、提取字段、逐步规则、只输出约定 JSON，并用边界 case 自测。",
    """<p>0325 AI 研发场公开复盘结构：约 20 选择 + 3 编程 + 1 Prompt。</p>
<p>选择侧曾出现：teacher forcing、MHA/MQA/GQA、ReAct、MCP tool vs resource、多 Agent 等。</p>
<p>Prompt 题策略：</p>
<ul>
<li>角色 + 信息抽取默认值；</li>
<li>计费/业务规则逐步写死；</li>
<li>夜间加价等边界单独强调；</li>
<li>强制 JSON schema 输出；</li>
<li>用反例（不足 1km、等候不足 5 分钟）自测。</li>
</ul>
<p>建议同步刷牛客 Prompt 题库。</p>""",
    ["Alibaba", "笔试", "Prompt"],
    real=True,
    sources=[SRC["ai_oa"]],
)

add(
    "ali-coding-islands",
    "B",
    "淘天校招手撕：岛屿数量（思路卡）",
    "网格 DFS/BFS 或并查集：遍历到陆地就淹没整座岛并计数。注意边界与访问标记。",
    """<p>阿里 LLM 岗仍常手撕经典题（岛屿数量、无重复最长子串、平方根等）。</p>
<p>岛屿数量：对每个未访问的 <code>1</code> 启动搜索，将连通块标记为已访问，计数 +1。时间 O(mn)。</p>
<p>面试加分：讨论并查集写法、以及与“连通分量”在图上的对应。</p>""",
    ["Alibaba", "Coding"],
    real=True,
    sources=[SRC["taotian_agent_campus"]],
)


def main() -> None:
    handbook = json.loads(HANDBOOK.read_text())
    # remove previous alibaba section if re-run
    handbook["sections"] = [s for s in handbook["sections"] if s["id"] != "alibaba"]

    section = {
        "id": "alibaba",
        "title": "10 · 阿里 LLM 人才计划真题",
        "description": "面向通义 / 淘天 / 国际 / Agent 的公开校招与实习面经：Post-Training（DPO/GRPO/GSPO）、Agent（Skill/Memory/RAG/MCP）、生产护栏与系统高频。",
        "questions": [q["meta"] for q in QUESTIONS],
    }
    # insert before companies or append then move companies last
    sections = handbook["sections"]
    companies = next(s for s in sections if s["id"] == "companies")
    others = [s for s in sections if s["id"] != "companies"]
    handbook["sections"] = others + [section, companies]

    # refresh company-alibaba pointer
    for s in handbook["sections"]:
        if s["id"] != "companies":
            continue
        for q in s["questions"]:
            if q["id"] != "company-alibaba":
                continue
            q["quick"] = (
                "先刷本手册「10 · 阿里 LLM 人才计划真题」：DPO→GRPO→GSPO、淘天 Agent 校招链、"
                "Skill/Memory/RAG、双十一护栏；再回 Architecture/Systems 补 RoPE/GQA/ZeRO。"
            )
            q["tags"] = ["Alibaba", "Qwen", "真题导航"]
            q["searchText"] = (
                "阿里 / qwen / 淘天：应该重点准备什么？ "
                + q["quick"]
                + " alibaba qwen 淘天 agent grpo gspo skill memory rag mcp"
            ).lower()

    chunk = {q["meta"]["id"]: q["html"] for q in QUESTIONS}
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    (CHUNK_DIR / "alibaba.json").write_text(json.dumps(chunk, ensure_ascii=False) + "\n")

    # update companies chunk for company-alibaba
    companies_chunk_path = CHUNK_DIR / "companies.json"
    companies_chunk = json.loads(companies_chunk_path.read_text())
    companies_chunk["company-alibaba"] = answer(
        "先刷本手册「10 · 阿里 LLM 人才计划真题」：把 DPO→GRPO→DAPO/GSPO、淘天 Agent 链、Skill/Memory/RAG、生产护栏串起来；系统题回 Architecture/Systems 章补齐。",
        """<p><b>算法主线：</b>SFT 数据与 mask → preference/DPO → on-policy reasoning RL → GRPO failure modes → DAPO/Dr.GRPO/<b>GSPO</b>（Qwen 尤相关）。</p>
<p><b>Agent 主线：</b>Tool/MCP/Skill、Memory/RAG 边界、trajectory 与 final-reward credit、评测与 Guardrail、高并发降级。</p>
<p><b>系统主线：</b>RoPE/GQA、LoRA、ZeRO、KV Cache、推理优化。</p>
<p>本手册第 10 章已按公开淘天/国际/闪购面经拆成独立真题卡，建议按章节刷完再回来看本导航卡查漏。</p>""",
        sources=[
            SRC["taotian_agent_campus"],
            SRC["taotian_agent_social"],
            SRC["intl_algo"],
            SRC["flash_agent"],
            SRC["gspo"],
            SRC["gspo_blog"],
        ],
    )
    companies_chunk_path.write_text(json.dumps(companies_chunk, ensure_ascii=False) + "\n")

    all_q = [q for s in handbook["sections"] for q in s["questions"]]
    source_urls = set()
    for html in chunk.values():
        source_urls.update(re.findall(r'href="([^"]+)"', html))
    for html in companies_chunk.values():
        source_urls.update(re.findall(r'href="([^"]+)"', html))
    # also count existing chunk sources lightly via previous stats approach: recount from all chunks
    for path in CHUNK_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        for html in data.values():
            source_urls.update(re.findall(r'href="([^"]+)"', html))

    handbook["stats"] = {
        "questions": len(all_q),
        "mustKnow": sum(1 for q in all_q if q["level"] == "S"),
        "realInterviews": sum(1 for q in all_q if q["isRealInterview"]),
        "sources": len(source_urls),
    }
    handbook["updatedAt"] = "2026-08-17"
    handbook["description"] = (
        "重点覆盖 Post-Training 算法与数据、Reasoning RL、Agent / Skill / Harness、Agent RL，"
        "并含阿里 LLM 人才计划公开真题；同时系统补齐架构、系统、数学、RAG 与手撕代码。"
    )

    HANDBOOK.write_text(json.dumps(handbook, ensure_ascii=False) + "\n")

    # update test expectations
    test_src = TEST.read_text()
    test_src = re.sub(r"assert\.equal\(handbook\.sections\.length, \d+\);", f"assert.equal(handbook.sections.length, {len(handbook['sections'])});", test_src)
    test_src = re.sub(
        r"assert\.equal\(questions\.length, \d+\);",
        f"assert.equal(questions.length, {handbook['stats']['questions']});",
        test_src,
    )
    test_src = re.sub(
        r"assert\.equal\(new Set\(questions\.map\(\(question\) => question\.id\)\)\.size, \d+\);",
        f"assert.equal(new Set(questions.map((question) => question.id)).size, {handbook['stats']['questions']});",
        test_src,
    )
    test_src = re.sub(
        r"assert\.equal\(questions\.filter\(\(question\) => question\.level === \"S\"\)\.length, \d+\);",
        f"assert.equal(questions.filter((question) => question.level === \"S\").length, {handbook['stats']['mustKnow']});",
        test_src,
    )
    test_src = re.sub(
        r"assert\.equal\(questions\.filter\(\(question\) => question\.isRealInterview\)\.length, \d+\);",
        f"assert.equal(questions.filter((question) => question.isRealInterview).length, {handbook['stats']['realInterviews']});",
        test_src,
    )
    TEST.write_text(test_src)

    print(
        json.dumps(
            {
                "added": len(QUESTIONS),
                "sections": len(handbook["sections"]),
                "stats": handbook["stats"],
                "alibaba_ids": [q["meta"]["id"] for q in QUESTIONS],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
