---
id: agent-skill-security
section: agent
order: 10
level: S
title: 第三方 Skill 有哪些安全风险？
quick: "第三方 Skill 可能带来提示注入、任意代码执行、敏感数据外传、供应链和权限过大的风险。执行程序要用权限清单、沙箱、网络和秘密隔离限制它，并固定版本、核对哈希与签名，模型自己判断安全靠不住。"
tags:
  - Skill
  - Security
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>第三方 Skill 可能带来提示注入、任意代码执行、敏感数据外传、供应链和权限过大的风险。执行程序要用权限清单、沙箱、网络和秘密隔离限制它，并固定版本、核对哈希与签名，模型自己判断安全靠不住。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>第三方 Skill 我会当成一份不可信的指令加一包不可信的代码来处理，风险主要出在五个地方。文本层面，Skill 里可以写指令注入（instruction injection），要求模型忽略用户和系统规则；代码层面，附带的脚本能读文件系统、执行 shell；数据层面，它可能把 secrets、代码仓库或用户数据上传出去；供应链层面，今天审过的版本没问题，后续版本却可能加进恶意脚本或依赖；权限层面，一个本来只需要读文件的 Skill，却拿到了网络和写权限。</p><p>所以防线要放在执行程序上。先用权限清单写明它能访问哪些文件、网络、秘密和工具，再配合沙箱、网络策略、秘密隔离和资源上限。版本要固定，或者核对哈希与签名，更新时检查改了什么。</p><p>运行程序应该把 Skill 里的指令当成待检查的内容。比如 Skill 要求上传 ~/.ssh/id_rsa，就算模型照做了，执行器也必须拒绝。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和恶意 MCP server 攻击面有什么不同？</summary><div class="follow-answer"><p>差别在数据来源和执行权限的边界。Skill 主要提供操作指令和代码包；MCP server 还会在运行时返回观测结果，并执行外部操作。两者都可能带提示注入。</p></div></details><details class="followup"><summary>安装前静态分析够吗？</summary><div class="follow-answer"><p>不够。实际执行时的行为、网络请求、环境变量和依赖更新都可能绕过静态检查，所以还需要运行时沙箱和审计日志。</p></div></details></div>

<div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>
