---
id: byte-team-agent-security
section: agent
order: 207
level: A
title: 字节实习一面：团队内部 Coding Agent 怎么管权限、命令和敏感信息？
quick: >-
  按人、仓、命令三类授权：默认可读当前 repo，写路径与 shell 走白名单。密钥扫描拦截
  `.env` / 私钥；全量审计谁改了哪次。模型只拿短期会话 token，不持有生产凭据。
tags:
  - ByteDance
  - Security
  - Audit
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如果让你把这个本地 Coding Agent 做成团队内部工具，你会怎么处理权限、安全和审计？比如文件读写、命令执行、敏感信息泄露。”**

这块容易直接答成把安全写进 prompt「请不要泄露」。内部 Coding Agent 一旦共享、能执行命令、能读仓，边界必须在工具服务端和策略引擎。模型会被注入或「忽略以上指令」打穿；审计日志若允许模型写，等于没有审计。这是 Harness 的授权层，见 `byte-harness-engineering`、`agent-tool-permissions`、`agent-prompt-injection`。

## 按人、仓、命令三类授权

身份走 SSO，会话绑定人而不是绑定「这台笔记本」。默认可读当前有 ACL 的 repo；写路径与 shell 走白名单。分层：身份 → 仓库 ACL → 工具策略（禁网络、禁 `sudo`、禁读 `~/.ssh`）→ 输出脱敏。同学 A 在有写权限的 `frontend` 仓可改 `src/**`、跑 `npm test`；同一 Agent 被要求 `cat ~/.ssh/id_rsa` 或把 `.env` 打到外网，策略引擎直接拒并记审计。同学 B 没有该仓 ACL，即使用同一套模型也读不到。

个人本地玩具可以松；一旦能 `git push`、能碰密钥或生产配置，默认拒绝并且可审计。真正的访问控制不在 system prompt。命令白名单按风险分级：只读检索默许，写文件要路径前缀，网络和特权命令要额外审批。Skill 与工具描述里的注入面见 `agent-skill-security`。

## 密钥、输出脱敏、模型不持有生产凭据

密钥扫描拦截 `.env`、私钥、云厂商 AK。命中则拒绝读、拒绝写入上下文、拒绝出现在 Observation。生产部署密钥走独立 secret 服务；会话里如需访问下游，只发一次性、短 TTL、最小权限的只读凭证，用完即废。模型上下文里不应出现长期凭据。

输出脱敏处理工具返回和模型最终回复：订单号可保留后四位，完整身份证、cookie、token 打码。要接受误杀，多打码比漏出密钥可修复。脱敏在执行层做，不要指望模型「注意别输出」。

## 审计日志不可被模型改写

全量记录：谁、哪次会话、读了哪些路径、执行了哪条命令、写了哪个文件、是否被策略拒绝。日志存独立通道，模型没有写权限。这才能事后回答「这个错误 patch 是谁的 Agent 合进去的」，并和回滚策略接上。SSO 过期后会话吊销：已发的短 TTL 凭证失效，进行中的高风险动作停。

失败模式：prompt 防泄露；把模型当防火墙；审计和业务库写在一起被 Agent 编辑。安全策略是默认拒绝，错误 patch 回滚是同一套 Harness，不是两个产品。

## 追问

- **白名单怎么列才不会锁死？** 按仓库语言给默认模板（例如前端允许 `npm test`、禁止 `curl | sh`），再按团队加例外并审计例外使用率。没有例外流程的白名单会被绕开或被废弃。
- **脱敏误杀了合法日志怎么办？** 提供「在审批下查看原文」的通道，而不是让 Agent 自动关闭脱敏。
- **prompt 注入从哪来？** 仓库 README、网页、工具返回都可能带指令。不可信内容进隔离区，不能提升权限，见 `agent-prompt-injection`。
- **和开源 Coding Agent 的差别？** 团队版多了身份、ACL、审计和密钥治理；本地个人工具的「能跑」不等于可共享。
