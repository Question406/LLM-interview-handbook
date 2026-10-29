---
id: sd-training-platform
section: ml
order: 23
level: A
title: 训练与模型发布平台：数据、作业、产物和回滚
quick: 假设团队说“把昨天表现最好的模型上线”，但昨天的数据、代码和 checkpoint 都有多个版本。平台首先要能唯一确定这次模型从哪里来。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Google：Rules of Machine Learning
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: primary
  - title: Google SRE Book：Service Level Objectives
    url: 'https://sre.google/sre-book/service-level-objectives/'
    type: primary
---

## 题目描述

设计团队共用的模型训练与发布平台，支持定时训练、失败恢复、实验比较和线上灰度。输入是不可变数据快照、训练代码与配置；输出是可追溯模型版本及发布记录。手册练习要求多租户资源配额和重启恢复，不要求支持所有分布式训练框架。请给出产物、checkpoint 和部署状态之间的区别。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设团队说“把昨天表现最好的模型上线”，但昨天的数据、代码和 checkpoint 都有多个版本。
>
> **做法与原因：** 我会记录数据版本、训练配置、代码与产物，管理作业恢复，再让评估通过的固定产物进入发布。
>
> **检查与取舍：** 验证从失败 checkpoint 恢复、重复提交作业与回滚的过程。

## 可以这样回答

假设团队说“把昨天表现最好的模型上线”，但昨天的数据、代码和 checkpoint 都有多个版本。平台首先要能唯一确定这次模型从哪里来。

我会记录数据版本、训练配置、代码与产物，管理作业恢复，再让评估通过的固定产物进入发布。在线版本、灰度结果与回滚目标都要可追踪。

验证从失败 checkpoint 恢复、重复提交作业与回滚的过程。训练完成只是一个阶段，不能直接等同于可发布。

## 技术备查

## 参考答案与设计讨论

把数据快照、代码、配置和模型产物绑定为一次可重现运行，再用注册、验证、灰度和回滚连接训练与服务。

![训练与模型发布平台：数据、作业、产物和回滚：核心数据流](/system-design/training-platform.svg)

图展示核心数据流；权限、状态和故障恢复以正文约定为准。

### 一次训练必须可追溯

运行记录绑定数据与标签版本、代码提交、配置、环境、随机种子和资源。种子不足以保证任意硬件与分布式环境逐位一致，应说明可重现的容差与范围。产物写入完成且校验通过后才注册为可使用版本。

### 调度与 checkpoint

作业进入有配额的队列，调度训练 worker，checkpoint 保存参数、优化器及所需数据位置。训练中断从已提交的完整 checkpoint 恢复，不读取尚未提交的半份文件。多 worker 恢复还要确认分片和样本进度约定。

### 从注册到线上

模型注册记录离线验证、特征 schema 与兼容性；发布创建不可变部署版本，先影子或小流量，再观察业务与系统指标。保留可回退模型与特征契约，状态迁移无法逆转时需要前向修复计划。

### 例子与关联

训练 A 已输出权重但未通过验证，不应自动替换线上模型 B；同一次运行重复注册也不应产生两个互相矛盾的“正式版本”。上线后某地区特征缺失，先停止扩量并回退兼容版本。延伸阅读[评测平台](?book=us-tech&section=design&question=design-eval-platform)。

