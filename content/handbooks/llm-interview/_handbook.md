---
schemaVersion: 1
id: llm-interview-v2
slug: llm-interview
title: LLM / Post-Training / Agent
shortTitle: LLM 面试手册
edition: V2
audience: 中国大陆头部科技公司 · 2027 校招
description: >-
  重点覆盖 Post-Training 算法与数据、Reasoning RL、Agent / Skill / Harness、Agent RL，并含阿里
  LLM 人才计划公开真题与校招笔试 / 研发面；同时系统补齐架构、系统、数学、RAG 与手撕代码。美国 OpenAI / Anthropic /
  Google / Meta / NVIDIA 等公开真题见独立手册「美国 Tech 真题」。
sections:
  - id: posttrain
    title: 01 · Post-Training 核心算法
    description: SFT、RLHF、PPO、GAE、DPO、GRPO、DAPO、GSPO、CISPO、SAPO、DPPO、SimKO、GFPO、ProRL、OPD / OPSD、Routing Replay、TIS、正向/反向 KL 与 reasoning RL
  - id: data
    title: 02 · Post-Training Data / Reward / Eval
    description: SFT 数据、Preference 数据、RLVR、Verifier、Reward hacking、熵塌诊断与修复顺序
  - id: agent
    title: 03 · Agent / Skill / Memory / Context
    description: Harness、Tool、MCP、Skill routing、Memory、Context Engineering 与安全
  - id: agentrl
    title: 04 · Agent Data / Agent RL
    description: >-
      Trajectory、Action granularity、Credit Assignment、GiGPO、过程奖励选型、Multi-Agent、Eval 与 failure
      recovery
  - id: arch
    title: 05 · LLM Architecture
    description: Transformer、Attention、RoPE、GQA、MoE、MLA、LoRA、Tokenizer 与 sizing
  - id: systems
    title: 06 · Training & Inference Systems
    description: Parallelism、ZeRO/FSDP、FlashAttention、vLLM、veRL / slime / AReaL / TRL / Unsloth、batch invariance 与 RL Infra
  - id: fundamentals
    title: 07 · 数学 / ML / RL / RAG 八股
    description: 熵 / 交叉熵 / KL 推导、正向/反向 KL、JS、$k_1/k_2/k_3$、Importance Sampling、Actor-Critic vs 纯 Critic、Policy Gradient、GAE 递推、Optimizer、Retrieval 与 LLM Eval
  - id: coding
    title: 08 · Coding / Whiteboard
    description: Attention、RoPE、GQA、MoE、采样、KV Cache、交叉熵、Tool 调用与传统手撕
  - id: rl-coding
    title: 09 · RL / Post-Training Coding
    description: logprob gather、SFT 训练、DPO、PPO clip、GAE、GRPO / GSPO 手写，以及 TRL / verl / Miles 的 loss 代码路径
  - id: computer-use
    title: 10 · Computer-use / Agent Eval
    description: 可执行 Oracle、可复现 benchmark、GUI 失败归因与安全评测
  - id: multimodal
    title: 11 · Multimodal / VLM Agent
    description: GUI grounding、截图坐标、视觉 Web 评测与文档理解
  - id: mcp-security
    title: 12 · MCP / Agent Security
    description: OAuth 授权、工具信任、递归采样与安全 Elicitation
  - id: swe-agent
    title: 13 · SWE Agent / Reliable Delivery
    description: Issue-to-patch 评测、Sandbox、Trace、Patch 验证与生产质量
  - id: alibaba
    title: 14 · 阿里 LLM 人才计划真题
    description: >-
      面向通义 / 淘天 / 国际 / Agent
      的公开校招与实习面经：Post-Training（DPO/GRPO/GSPO）、Agent（Skill/Memory/RAG/MCP）、生产护栏与系统高频。
  - id: companies
    title: 15 · 公司与原始材料索引
    description: 阿里/Qwen、字节 Seed、腾讯混元、百度 AIDU、智谱、Moonshot、MiniMax、蚂蚁、美团、拼多多、京东、快手、小红书、百川、阶跃、商汤、DeepSeek、高德
  - id: alibaba-oa
    title: 16 · 阿里校招笔试与研发面
    description: >-
      近年淘天 / 国际 / AI 研发公开笔试编程真题与选择题，以及校招技术面高频手撕、Java / Redis / MQ / MySQL
      与系统设计。LLM 人才计划算法题仍看第 14 章。
---
