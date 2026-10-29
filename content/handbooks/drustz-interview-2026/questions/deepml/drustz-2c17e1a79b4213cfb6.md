---
id: drustz-2c17e1a79b4213cfb6
section: deepml
order: 158
level: A
title: question.schema.json
quick: Deep-ML 练习 · question.schema.json
companies: []
tags:
  - DrustZ
  - Deep-ML 练习
  - Deep-ML · ML Coding
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/schemas/question.schema.json
    type: primary
---
### question.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Deep-ML Question",
  "type": "object",

  "required": [
    "id",
    "title",
    "description",
    "difficulty",
    "category",
    "starter_code",
    "solution",
    "example",
    "test_cases",
    "learn_section",
    "video",
    "likes",
    "dislikes",
    "contributor"
  ],

  "properties": {
    "id": { "type": "string", "pattern": "^[0-9]+$" },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "difficulty": { "type": "string", "enum": ["easy", "medium", "hard"] },
    "category": { "type": "string" },

    "starter_code": { "type": "string" },
    "solution": { "type": "string" },

    "example": { "type": "object" },
    "test_cases": { "type": "array" },

    "learn_section": { "type": "string" },
    "video": { "type": "string" },
    "likes": { "type": "string" },
    "dislikes": { "type": "string" },
    "contributor": { "type": "array" },

    "marimo_link": { "type": "string" },

    "tinygrad_difficulty": { "type": "string", "enum": ["easy", "medium", "hard"] },
    "tinygrad_starter_code": { "type": "string" },
    "tinygrad_solution": { "type": "string" },
    "tinygrad_test_cases": { "type": "array" },

    "pytorch_difficulty": { "type": "string", "enum": ["easy", "medium", "hard"] },
    "pytorch_starter_code": { "type": "string" },
    "pytorch_solution": { "type": "string" },
    "pytorch_test_cases": { "type": "array" }
  },

  "additionalProperties": false
}
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/schemas/question.schema.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/schemas/question.schema.json)。Deep-ML：Educational Use Only License。
