---
schemaVersion: 1
id: us-tech-interview
slug: us-tech
title: 美国 Tech / Frontier Lab 真题
shortTitle: 美国 Tech 真题
edition: V1
audience: 美国 frontier lab / Big Tech 的 LLM team · Research Engineer、MLE、训练与推理系统、对齐
description: >-
  面向 LLM 训练 / 推理 / 对齐 / 多模态 / Agent 岗：OpenAI、Anthropic、Google DeepMind、Meta Llama、NVIDIA、
  Apple Foundation Models、Amazon Bedrock/Nova、Microsoft Phi/Copilot、xAI Grok。覆盖 Transformer debug、
  KV、长上下文、MoE、投机解码、视觉 token、工具 RL、FlashDecoding、评测污染与 serving。每题给 30 秒讲法、
  面试答法和追问。只依据公开面经、官方流程和论文，不编造被论坛藏掉的细节。
sections:
  - id: overview
    title: 01 · 备考地图
    description: LLM team 轮次、RE 六周计划、必读论文栈，以及多模态 / Agent 面怎么准备
  - id: openai
    title: 02 · OpenAI
    description: Transformer debug、KV、投机解码、多模态连接、test-time compute、工具循环 RL、FlashDecoding
  - id: anthropic
    title: 03 · Anthropic
    description: Claude vision/PDF、computer-use RL、MCP/工具往返、流式工具、记忆与多模态越狱
  - id: google
    title: 04 · Google / DeepMind
    description: Gemini 多模态 / Agent、ViT/Flamingo/PaLI、TPU decode、视频 token、多模态 SFT
  - id: meta
    title: 05 · Meta
    description: Llama Vision / AnyRes、early fusion、Toolformer、vLLM、代码 agent、语音 token
  - id: nvidia
    title: 06 · NVIDIA
    description: FlashDecoding / FlashInfer、W4A8、KV offload、Medusa/EAGLE、fused MoE、视觉+LLM 同卡
  - id: apple
    title: 07 · Apple
    description: 端侧多模态训练、视觉 token 预算、语音进 LLM、端侧 agent、token 剪枝
  - id: amazon
    title: 08 · Amazon
    description: Nova 多模态、Converse 工具、企业 agent 评测、PDF/图 RAG、LLM rerank
  - id: microsoft
    title: 09 · Microsoft
    description: Phi vision、LLaVA 训练、Copilot agent、Florence、多 agent 失败模式
  - id: xai
    title: 10 · xAI / Tesla
    description: Grok 视觉、搜索 agent、实时语音、tool loop；Tesla 题仅作对照
  - id: coding
    title: 11 · ML Coding 白板
    description: FlashDecoding、paged block table、SWA/ALiBi mask、融合 CE、投机接受、INT8、一步 decode
  - id: systems
    title: 12 · 训练 / 推理系统
    description: KV offload、FlashInfer、radix 前缀树、多模态 prefill、agent 调度、FP8 GEMM、EP dispatch
  - id: design
    title: 13 · ML System Design
    description: 多模态助手、语音/浏览器 agent、agent 评测、多模态 RAG、步数与成本预算
  - id: alignment
    title: 14 · Alignment / Evals
    description: 工具/Agent RL、可验证奖励、多模态危害、思维链泄漏、weak-to-strong、RM 过优化
---
