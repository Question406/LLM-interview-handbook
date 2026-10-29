---
id: us-mm-prep
section: overview
order: 9
level: S
title: 美国 Tech LLM team：多模态轮怎么准备（编码、token 预算、评测）
quick: >-
  多模态轮先练视觉 token 怎样进入序列、mask 怎样写，再核算高分辨率图像占用的上下文和
  KV。设计与评测要说明区域引用、图文冲突、缺失模态和有害图输入如何处理；基础 attention 练习照常保留，地图见 `us-prep-map`。
tags:
  - US Tech
  - Multimodal
  - 备考
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: 'https://arxiv.org/abs/2312.11805'
    type: primary
  - title: Introducing Apple Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Learning Transferable Visual Models From Natural Language Supervision
    url: 'https://arxiv.org/abs/2103.00020'
    type: primary
---

多模态准备可以接在 RE 六周计划上，重点补编码、视觉 token 预算和证据评测。比如序列里插入图像 patch 后，仍要写对 attention 和 mask，还要算出它占了多少上下文、回答引用哪个区域。Google Gemini、Apple Intelligence、OpenAI 图文和 Meta Llama 视觉方向都会涉及这些问题。六周总表见 `us-llm-re-prep`；Scientist / Applied 差异见 `us-research-vs-applied`。

## 先写清编码和序列形状

闭卷要能写：图 $H\times W$、补丁 $P$，大约 $N_p=(H/P)\times(W/P)$ 个视觉 token，投影到 $D$，和文本拼成 `[B, T_{\mathrm{text}}+T_{\mathrm{vis}}, D]`。损失只在文本位置；视觉位置当 prefix，类似 tool 观察不要进 policy gradient，见 `align-agent-rl`。连接器（MLP / 交叉注意 / Perceiver）面试能讲一个权衡即可：交叉注意省序列长度，拼 token 实现简单、预算直白。

常见误区是：把视觉长度算进 causal mask 却在 softmax 轴上搞错；高分辨率 anyres 把 $N_p$ 乘成数倍还不说 KV；视频按 30 fps 进大模型。打包混模态时 padding 和位置编码（图像用 2D、文本用 1D）要分开讲，不要一句 RoPE 打天下。手写 MHA 仍可能出现，见 `apple-mha-code`；多模态岗只是追问「这段 key 来自补丁怎么办」。

CLIP 只解决检索对齐空间，不能保证生成答案有证据支持。生成要引用区域，见 `design-mm-assistant`。端侧还要讲谁在设备上跑编码器，见 Apple 公开叙述。

## 再核算预算并建立评测

一张 1024 边长、$P=14$ 的图就是几千 token，对话历史会被挤掉。准备时用数字说话：先分类查询要不要图，再粗分辨率定位、裁剪定位框对应的区域，屏走 OCR + 区域。延迟不齐：没到的模态不当证据，见 `design-multimodal-prod`。语音岗把 TTFA 和打断单独练，见 `design-voice-agent`。

Serving：视觉 encoder 是 prefill 侧的瓶颈，和 chat serving 的 首个 token 的等待时间（TTFT） 叠在一起，见 `design-chat-serving`。前缀缓存对「同一张图多轮问」有效，图一换就必须失效。别只会说 paged attention；要说视觉段的 KV 占多少页。

安全：截图越狱、图上的字绕过文本过滤，见 `align-mm-harm`。准备一个「图当不可信输入」的答法，和工具输出注入同构。

acceptance checks 拆：证据支持（框 / 页能否支撑这句话）、正确、hallucination（物体是否存在）、模态缺失拒答、图文冲突、延迟随分辨率变化、有害图通道。不要用 BLEU。检索岗加 ACL 与像素泄漏，见 `design-mm-rag`。人工集覆盖：只有语音、只有图、弱网、打断。

公司倾斜：Google 追长上下文 + 多模态融合；Apple 追端侧、隐私、voice 可说长度；OpenAI 可能把视觉放进 debug「多一种 token 类型」；Amazon 追企业扫描件 检索增强生成（RAG）。论文精读仍以 `us-llm-paper-stack` 六篇打底，多模态加 Gemini 报告里「接口与评测」那几页，不要开二十篇综述。

两周压缩：一周写清 $N_p$ 和 mask，做一道引用框设计；一周做评测表和一条有害图通道。没有 GPU 就把 shape 和预算公式写对，不要装训过原生万卡 VLM。

工作日清单：今天写了哪一个视觉 shape；今天算了哪一张图的 $N_p$；今天画了缺失模态 / 图文冲突的拒答。三天只读论文不写 shape 就停。产出检查：能闭卷写「文本损失、视觉 mask」；能拒绝「整张 4K 进上下文」；能讲截图越狱为什么文本过滤器看不见。行为面用真实权衡（端侧 vs 云、引用 vs 延迟）。

Onsite 设计题先问：图是否必须、引用要不要框、数据能否出设备、p95。这些约束会决定图像处理路径、上下文预算和部署位置。编码轮若给了 packed 序列，先数视觉段长度再写 mask。和 `google-gemini-mm` 对照读接口，不要背参数量。

和六周计划的关系：第 1-2 周 debug 照旧；第 5 周设计把 RAG 换成带框引用的图文助手或 `design-mm-rag`。NVIDIA 岗视觉 encoder 可以讲成 kernel throughput，但仍要会算 $N_p$。不要用「我读过 LLaVA」替代 shape。

## 追问

**没做过视觉训练能面吗？**
能。把序列契约、预算、证据支持和安全讲成可交接系统，比背模型名有用。
**要不要刷 MM 公开榜？**
公开集一定脏。要能讲污染和私有切片，见 `align-eval-contam`。
**和纯文本六周冲突吗？**
不冲突。砍的是第三篇 VLM 综述，不是 KV cache。
**Agent 看屏算多模态还是 agent？**
两者都要。屏的 token 走本题；沙箱确认走 `us-agent-prep`。
**视频怎么算 token？**
先定 fps 和分辨率，再乘 $N_p$。面试先拒绝默认 30 fps，再说关键帧。
**POPE / VQA 够不够当 acceptance checks？**
不够。要加证据支持、冲突、缺失模态、有害图通道和延迟。
