---
id: drustz-3d4206b40ae62cafa4
section: deepml
order: 11
level: A
title: BM25 Ranking
quick: Deep-ML 练习 · BM25 Ranking
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/90_bm25-ranking/description.md
    type: primary
---
### description.md

Implement the BM25 ranking function to calculate document scores for a query in an information retrieval context. BM25 is an advanced variation of TF-IDF that incorporates term frequency saturation, document length normalization, and a configurable penalty for document length effects.


### example.json

```json
{
  "input": "corpus = [['the', 'cat', 'sat'], ['the', 'dog', 'ran'], ['the', 'bird', 'flew']], query = ['the', 'cat']",
  "output": "[0.693, 0., 0. ]",
  "reasoning": "BM25 calculates scores for each document in the corpus by evaluating how well the query terms match each document while considering term frequency saturation and document length normalization."
}
```




### learn.md

## **BM25**

BM25 (Best Match 25) is used in information retrieval for search relevance. Similar to TF-IDF, it reflects the importance of a word in a document within a collection or corpus. However, BM25 improves upon TF-IDF by addressing key limitations.

### Limitations of TF-IDF Addressed by BM25

1. **Saturation**: In TF-IDF, having a term multiple times in a document skews the term frequency, making the document overly relevant. BM25 mitigates this by using:  
   $$ \text{TF-adjusted} = \frac{\text{TF}}{\text{TF} + k_1} $$  

2. **Document Length Normalization**: BM25 accounts for document length by normalizing term frequencies using:  
   $$ \text{Normalized Length} = 1 - b + b \times \frac{\text{Doc Len}}{\text{Average Doc Len}} $$  

3. **Amplifying Parameter**: The $b$ parameter controls the influence of document length normalization. Higher $b$ values amplify the effect.

### Final BM25 Formula

The BM25 score for a term is given by:  
$$ \text{BM25} = \text{IDF} \times \frac{\text{TF} \times (k_1 + 1)} {\text{TF} + k_1 \times (1 - b + b \times \frac{\text{dl}}{\text{adl}})} $$  

Where:  
- $ \text{TF} $: Term frequency in the document.  
- $ \text{IDF} $: Inverse document frequency, calculated as $ \log(\frac{N + 1}{\text{df} + 1}) $.  
- $ N $: Total number of documents.  
- $ \text{df} $: Number of documents containing the term.  
- $ \text{dl} $: Document length.  
- $ \text{adl} $: Average document length.  
- $ k_1 $: Saturation parameter.  
- $ b $: Normalization parameter.

### Implementation Steps

1. Compute document length ($ dl $) and average document length ($ adl $).  
2. Calculate term frequencies ($ TF $) using the BM25 formula.  
3. Compute inverse document frequencies ($ IDF $) for each term.  
4. Calculate BM25 scores for each document.

### Applications

BM25 is widely used in:  
- Search Engines  
- Recommendation Systems  
- Natural Language Processing (NLP)  

Understanding BM25 enables the creation of robust systems for search and ranking tasks.


### meta.json

```json
{
  "id": "90",
  "title": "BM25 Ranking ",
  "difficulty": "medium",
  "category": "NLP",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/saitiger",
      "name": "Sai Tiger Raina"
    }
  ]
}
```




### solution.py

```python
import numpy as np
from collections import Counter


def calculate_bm25_scores(corpus, query, k1=1.5, b=0.75):
    if not corpus or not query:
        raise ValueError("Corpus and query cannot be empty")

    doc_lengths = [len(doc) for doc in corpus]
    avg_doc_length = np.mean(doc_lengths)
    doc_term_counts = [Counter(doc) for doc in corpus]
    doc_freqs = Counter()
    for doc in corpus:
        doc_freqs.update(set(doc))

    scores = np.zeros(len(corpus))
    N = len(corpus)

    for term in query:
        df = doc_freqs.get(term, 0) + 1
        idf = np.log((N + 1) / df)

        for idx, term_counts in enumerate(doc_term_counts):
            if term not in term_counts:
                continue

            tf = term_counts[term]
            doc_len_norm = 1 - b + b * (doc_lengths[idx] / avg_doc_length)
            term_score = (tf * (k1 + 1)) / (tf + k1 * doc_len_norm)
            scores[idx] += idf * term_score

    return np.round(scores, 3)
```




### starter_code.py

```python
import numpy as np
from collections import Counter


def calculate_bm25_scores(corpus, query, k1=1.5, b=0.75):
    # Your code here
    pass
    return np.round(scores, 3)
```




### tests.json

```json
[
  {
    "test": "print(calculate_bm25_scores([['the', 'cat', 'sat'], ['the', 'dog', 'ran'], ['the', 'bird', 'flew']], ['the', 'cat']))",
    "expected_output": "[0.693, 0., 0. ]"
  },
  {
    "test": "print(calculate_bm25_scores([['the'] * 10, ['the']], ['the']))",
    "expected_output": "[0,0]"
  },
  {
    "test": "print(calculate_bm25_scores([['term'] * 10, ['the'] * 2], ['term'], k1=1.0))",
    "expected_output": "[.705, 0]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/90_bm25-ranking/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/90_bm25-ranking/description.md)。Deep-ML：Educational Use Only License。
