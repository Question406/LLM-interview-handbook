---
id: agent-skill-security
section: agent
order: 10
level: S
title: 第三方 Skill 有哪些安全风险？
quick: "第三方 Skill 可能包含恶意指令、脚本和外部引用，带来提示注入、任意代码执行、敏感数据外传与供应链风险。执行程序必须限制文件、网络、秘密和工具权限，不能只让模型自行判断安全。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>第三方 Skill 可能包含恶意指令、脚本和外部引用，带来提示注入、任意代码执行、敏感数据外传与供应链风险。执行程序必须限制文件、网络、秘密和工具权限，不能只让模型自行判断安全。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><ul><li><b>Instruction injection：</b>Skill 文本要求忽略用户/系统规则。</li><li><b>Code execution：</b>脚本读取 filesystem、执行 shell。</li><li><b>Data exfiltration：</b>上传 secrets、repo、用户数据。</li><li><b>Dependency/supply-chain：</b>后续版本加入恶意脚本或依赖。</li><li><b>Over-permission：</b>Skill 本只需读文件，却拿到网络+写权限。</li></ul><p>用权限清单明确允许访问的文件、网络、秘密和工具，再配合沙箱、网络策略、秘密隔离与资源上限。固定版本，或核对哈希与签名；更新时检查改动。</p><p>运行程序应把 Skill 指令视为待检查内容。即使它要求上传 ~/.ssh/id_rsa，执行器也必须拒绝。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和恶意 MCP server 攻击面有什么不同？</summary><div class="follow-answer"><p>Skill 主要提供操作指令和代码包；MCP server 还会在运行时返回观测结果，并执行外部操作。两者都可能提示注入，但数据来源和执行权限边界不同。</p></div></details><details class="followup"><summary>安装前静态分析够吗？</summary><div class="follow-answer"><p>不够。实际执行行为、网络请求、环境变量和依赖更新，可能绕过静态检查，仍需要运行时沙箱与审计日志。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>
