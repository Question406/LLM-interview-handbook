# Content system

Each handbook lives in `content/handbooks/` as a versioned JSON document. The UI reads the registry in `content/registry.ts`, so presentation code stays independent from handbook copy.

Small handbooks can keep `answerHtml` inline. Large handbooks should use `answerPath`; the legacy importer automatically writes one lazy-loaded answer chunk per module under `public/content/`. This keeps the initial page fast even as the library grows.

To add a handbook:

1. Copy `content/handbooks/example.json` and give it a unique `id` and `slug`.
2. Add sections and questions. `answerHtml` accepts paragraphs, lists, tables, code, links, and the existing pre-rendered formula SVG markup.
3. Import the file and add it to the exported `handbooks` array in `content/registry.ts`.

The legacy single-file handbook can be re-imported with:

```sh
npm run import:legacy -- ../llm_interview_handbook_v2.html
```

Question IDs must stay stable because review progress and deep links are keyed by `handbook-id/question-id`.
