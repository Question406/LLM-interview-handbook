---
id: agent-skill-security
section: agent
order: 10
level: S
title: 第三方 Skill 有哪些安全风险？
quick: >-
  Skill 可包含 instructions、scripts、external references，因此同时有 prompt
  injection、任意代码执行、secret exfiltration 与 supply-chain update 风险；安全边界必须在
  runtime，不是让模型“自觉”。
tags:
  - Skill
  - Security
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Skill 可包含 instructions、scripts、external references，因此同时有 prompt injection、任意代码执行、secret exfiltration 与 supply-chain update 风险；安全边界必须在 runtime，不是让模型“自觉”。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><ul><li><b>Instruction injection：</b>Skill 文本要求忽略用户/系统规则。</li><li><b>Code execution：</b>脚本读取 filesystem、执行 shell。</li><li><b>Data exfiltration：</b>上传 secrets、repo、用户数据。</li><li><b>Dependency/supply-chain：</b>后续版本加入恶意脚本或依赖。</li><li><b>Over-permission：</b>Skill 本只需读文件，却拿到网络+写权限。</li></ul><p>建议 permission manifest（filesystem/network/secrets/tools）、sandbox、network policy、secret isolation、resource limit、version pin/hash/signature、update diff review。</p><p>Runtime 还应把“Skill instruction”视为 untrusted content：即使 Skill 说必须上传 ~/.ssh/id_rsa，executor 也必须拒绝。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和恶意 MCP server 攻击面有什么不同？</summary><div class="follow-answer"><p>Skill 更偏程序性 instruction/code package；MCP server 还拥有运行时返回 observation 和外部 side-effect capability。两者都可能 prompt inject，但 trust boundary 不同。</p></div></details><details class="followup"><summary>安装前静态分析够吗？</summary><div class="follow-answer"><p>不够。动态行为、网络调用、环境变量、依赖更新都可能绕过静态规则，需要 runtime sandbox 与 audit log。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>
