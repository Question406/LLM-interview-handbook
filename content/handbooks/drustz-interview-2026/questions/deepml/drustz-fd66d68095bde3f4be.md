---
id: drustz-fd66d68095bde3f4be
section: deepml
order: 64
level: A
title: Evaluate Translation Quality with METEOR Score
quick: Deep-ML 练习 · Evaluate Translation Quality with METEOR Score
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/110_evaluate-translation-quality-with-meteor-score/description.md
    type: primary
---
### description.md

Develop a function to compute the METEOR score for evaluating machine translation quality. Given a reference translation and a candidate translation, calculate the score based on unigram matches, precision, recall, F-mean, and a penalty for word order fragmentation.


### example.json

```json
{
  "input": "meteor_score('Rain falls gently from the sky', 'Gentle rain drops from the sky')",
  "output": "0.625",
  "reasoning": "The function identifies 4 unigram matches ('rain', 'gently'/'gentle', 'from', 'sky'), computes precision (4/6) and recall (4/5), calculates an F-mean, and then apply a small penalty for two chunks."
}
```




### learn.md

METEOR(Metric for Evaluation of Translation with Explicit ORdering) is a metric generally used for 
machine translation and evaluating the text output of generative AI models. METEOR build was introduced to address 
the limitations in earlier metrics like BLEU.

## Key Characteristics
- Considers semantic similarity beyond exact word matching
- Accounts for word order and translation variations
- Provides more human-aligned translation assessment

# Implementation 
1. **Tokenization**

2. **Frequency of matching words** : Matching needs to be exact

3. **Calculate Precision, Recall and F-mean**
```text
   F_mean = (Precision * Recall) / 
   (alpha * Precision + (1 - alpha) * Recall)
```

   - alpha typically set to 0.9
   - Balances precision and recall

4. **Fragmentation Penalty**

```text
Chunks = Count of contiguous matched word sequences
Penalty = gamma * (Chunks / Matches)^β
```



   - beta controls penalty weight (typically 3)
   - gamma limits maximum penalty (typically 0.5)

5. **Final METEOR Score**

```text
METEOR = F_mean * (1 - Penalty)
```



   - Ranges from 0 (no match) to 1 (perfect match)

**__Note__** : The [paper](https://aclanthology.org/W05-0909/) that introduced the metric doesn't have the parameters (alpha,β, and gamma) as tunable parameters, but implementation in other libraries like NLTK offers this flexibility.

# Example 

- Reference: "The quick brown fox jumps over the lazy dog"
- Candidate: "A quick brown fox jumps over a lazy dog"

### 1. Tokenization
- Reference Tokens: ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog']
- Candidate Tokens: ['a', 'quick', 'brown', 'fox', 'jumps', 'over', 'a', 'lazy', 'dog']

### 2. Unigram Matching
- Matching tokens: ['quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog']
- Matches: 7

### 3. Unigram Precision and Recall Calculation
- Precision = Matches / Candidate Length = 7 / 9 ~ 0.778

- Recall = Matches / Reference Length = 7 / 9 ~ 0.778

### 4. F-mean Calculation (alpha = 0.9)
```text
F_mean = (Precision * Recall) / 
(alpha * Precision + (1 - alpha) * Recall)
       = (0.778 * 0.778) / (0.9 * 0.778 + (1 - 0.9) * 0.778)
       = 0.606 / (0.7 + 0.078)
       = 0.606 / 0.778
       ≈ 0.779
```



### 5. Chunk Calculation
- Contiguous matched sequences:
  1. ['quick', 'brown', 'fox']
  2. ['jumps', 'over']
  3. ['lazy', 'dog']
- Number of Chunks: 3
- Total Number of Unigram Matches: 7

### 6. Penalty Calculation (betta = 3, gamma = 0.5)
```text
Penalty = gamma * 
(Number of Chunks / Total Number of Unigram Matches)^betta
        = 0.5 * (3 / 7)^3
        = 0.5 * (0.429)^3
        ≈ 0.039
```



### 7. Final METEOR Score
```text
METEOR = F_mean * (1 - Penalty)
       = 0.779 * (1 - 0.039)
       = 0.779 * 0.961
       ≈ 0.749
```




### meta.json

```json
{
  "id": "110",
  "title": "Evaluate Translation Quality with METEOR Score",
  "difficulty": "medium",
  "category": "NLP",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/saitiger",
      "name": "saitiger"
    }
  ]
}
```




### solution.py

```text
"import numpy as np
from collections import Counter

def meteor_score(reference, candidate, alpha=0.9, beta=3, gamma=0.5):
    if not reference or not candidate:
        raise ValueError("Reference and candidate cannot be empty")
    
    # Tokenize and count
    ref_tokens = reference.lower().split()
    cand_tokens = candidate.lower().split()

    # Counter for unigram for reference and candidate 
    ref_counts = Counter(ref_tokens) 
    cand_counts = Counter(cand_tokens)
    
    # Calculate matches
    num_matches = sum((ref_counts & cand_counts).values()) # Number of matching words in candidate and reference 
    ref_len = len(ref_tokens)
    cand_len = len(cand_tokens)  

    # Unigram Precision and Recall 
    precision = num_matches / cand_len if cand_len > 0 else 0 # Avoiding Division by zero
    recall = num_matches / ref_len if ref_len > 0 else 0 # Avoiding Division by zero 
    
    if num_matches == 0:
        return 0.0
    
    fmean = (precision * recall) / (alpha * precision + (1 - alpha) * recall)

    # Chunk calculation 
    matched_positions = []
    ref_positions = {}  # Store positions of words in reference
    used_positions = set()  # Track already used indices

    # Populate reference positions for word alignment tracking
    for i, word in enumerate(ref_tokens):
        ref_positions.setdefault(word, []).append(i)

    # Determine the sequence of matched positions in reference
    for word in cand_tokens:
        if word in ref_positions:
            for pos in ref_positions[word]:
                if pos not in used_positions:
                    matched_positions.append(pos)
                    used_positions.add(pos)
                    break  # Ensure each match is used only once

    # Count chunks by detecting breaks in position sequence
    num_chunks = 1 if matched_positions else 0
    for i in range(1, len(matched_positions)):
        if matched_positions[i] != matched_positions[i - 1] + 1:
            num_chunks += 1  # Break in sequence → new chunk

    # Fragmentation penalty
    penalty = gamma * ((num_chunks / num_matches) ** beta) if num_matches > 0 else 0
    
    # Final score
    return round(fmean * (1 - penalty), 3) # Rounding to 3 Decimal places
```




### starter_code.py

```python
import numpy as np
from collections import Counter


def meteor_score(reference, candidate, alpha=0.9, beta=3, gamma=0.5):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "print(round(meteor_score('The dog barks at the moon', 'The dog barks at the moon'),3))",
    "expected_output": "0.998"
  },
  {
    "test": "print(round(meteor_score('Rain falls gently from the sky', 'Gentle rain drops from the sky'),3))",
    "expected_output": "0.625"
  },
  {
    "test": "print(round(meteor_score('The sun shines brightly', 'Clouds cover the sky'),3))",
    "expected_output": "0.125"
  },
  {
    "test": "print(round(meteor_score('Birds sing in the trees', 'Birds in the trees sing'),3))",
    "expected_output": "0.892"
  }
]
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/110_evaluate-translation-quality-with-meteor-score/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/110_evaluate-translation-quality-with-meteor-score/description.md)。Deep-ML：Educational Use Only License。
