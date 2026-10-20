# Interview Atlas voice (for humanizer)

When rewriting handbook questions under `content/handbooks/`, match this voice instead of generic “clean blog” English.

## Voice

- Chinese-first explanations for someone learning the topic. Use complete, natural sentences; explain the mechanism and why it works. Avoid compressed interview slogans such as “错法：…” without an explanation.
- Prefer concrete mechanisms, formulas, and failure modes over staging or pep talk.
- Short sentences OK; one-line closers that only restate the prior paragraph are not.
- Keep bilingual terms as they appear (`Temperature` / 温度, GRPO, LoRA). Do not flatten into English-only.

## Must preserve

- YAML frontmatter except `quick`: preserve `title`, `id`, `sources`, dates, tags, status, and all other metadata. Rewrite `quick` so it is understandable on its own; synchronize the duplicate short answer in legacy HTML.
- Math: `$...$`, `$$...$$`
- Inline codes / backticks / question cross-links (`id`, `[[id]]`, full titles)
- Code fences, inline identifiers, and SVG formulas. For `format: legacy-html`, rewrite prose inside text nodes while preserving the existing structure and attributes.
- Technical contrasts that correct a real interview misconception (e.g. temperature vs entropy bonus) — those are content, not AI staging

## Must cut or soften

- Empty not-X-but-Y when the negative half invents a strawman
- Dramatic one-line closers (“说白了：…”, “That is the real win.”) that add no new fact
- Forced rule-of-three lists; decorative **bold** on every noun phrase
- Chatbot leftovers, hedging filler, significance inflation

## Output

File mode: write the final markdown only. Do not invent papers, numbers, or company claims.

For a whole-library request, read every published question and review its short and full answer in context. Keep a per-file progress record so an interruption does not silently leave part of the library unfinished. An answer that already reads naturally can remain unchanged, but must still be reviewed. Do not use a sample-only pass or mechanical substitutions as a substitute for this review.
