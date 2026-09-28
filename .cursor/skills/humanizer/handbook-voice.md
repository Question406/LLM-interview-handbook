# Interview Atlas voice (for humanizer)

When rewriting handbook questions under `content/handbooks/`, match this voice instead of generic “clean blog” English.

## Voice

- Chinese-first interview notes: direct, technical, slightly oral (“我会这么选…”, “错法：…”).
- Prefer concrete mechanisms, formulas, and failure modes over staging or pep talk.
- Short sentences OK; one-line closers that only restate the prior paragraph are not.
- Keep bilingual terms as they appear (`Temperature` / 温度, GRPO, LoRA). Do not flatten into English-only.

## Must preserve

- YAML frontmatter (all keys/values), including `quick`, `title`, `id`, `sources`
- Math: `$...$`, `$$...$$`
- Inline codes / backticks / question cross-links (`id`, `[[id]]`, full titles)
- Code fences and HTML in `format: legacy-html` bodies
- Technical contrasts that correct a real interview misconception (e.g. temperature vs entropy bonus) — those are content, not AI staging

## Must cut or soften

- Empty not-X-but-Y when the negative half invents a strawman
- Dramatic one-line closers (“说白了：…”, “That is the real win.”) that add no new fact
- Forced rule-of-three lists; decorative **bold** on every noun phrase
- Chatbot leftovers, hedging filler, significance inflation

## Output

File mode: write the final markdown only. Do not invent papers, numbers, or company claims.
