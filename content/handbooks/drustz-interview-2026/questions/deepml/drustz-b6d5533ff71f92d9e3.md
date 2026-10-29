---
id: drustz-b6d5533ff71f92d9e3
section: deepml
order: 114
level: A
title: Implement TF-IDF (Term Frequency-Inverse Document Frequency)
quick: Deep-ML 练习 · Implement TF-IDF (Term Frequency-Inverse Document Frequency)
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/60_implement-tf-idf-term-frequency-inverse-document-f/description.md
    type: primary
---
### description.md

## Task: Implement TF-IDF (Term Frequency-Inverse Document Frequency)

Your task is to implement a function that computes the TF-IDF scores for a query against a given corpus of documents.

### Function Signature

Write a function `compute_tf_idf(corpus, query)` that takes the following inputs:

- `corpus`: A list of documents, where each document is a list of words.
- `query`: A list of words for which you want to compute the TF-IDF scores.

### Output

The function should return a list of lists containing the TF-IDF scores for the query words in each document, rounded to five decimal places.

### Important Considerations

1. **Handling Division by Zero:**  
   When implementing the Inverse Document Frequency (IDF) calculation, you must account for cases where a term does not appear in any document (`df = 0`). This can lead to division by zero in the standard IDF formula. Add smoothing (e.g., adding 1 to both numerator and denominator) to avoid such errors.

2. **Empty Corpus:**  
   Ensure your implementation gracefully handles the case of an empty corpus. If no documents are provided, your function should either raise an appropriate error or return an empty result. This will ensure the program remains robust and predictable.

3. **Edge Cases:**  
   - Query terms not present in the corpus.  
   - Documents with no words.  
   - Extremely large or small values for term frequencies or document frequencies.

By addressing these considerations, your implementation will be robust and handle real-world scenarios effectively.


### example.json

```json
{
  "input": "corpus = [\n    [\"the\", \"cat\", \"sat\", \"on\", \"the\", \"mat\"],\n    [\"the\", \"dog\", \"chased\", \"the\", \"cat\"],\n    [\"the\", \"bird\", \"flew\", \"over\", \"the\", \"mat\"]\n]\nquery = [\"cat\"]\n\nprint(compute_tf_idf(corpus, query))",
  "output": "[[0.21461], [0.25754], [0.0]]",
  "reasoning": "The TF-IDF scores for the word \"cat\" in each document are computed and rounded to five decimal places."
}
```




### learn.md

# Understanding TF-IDF (Term Frequency-Inverse Document Frequency)

TF-IDF is a numerical statistic that reflects how important a word is in a document relative to a collection (or corpus). It is widely used in information retrieval, text mining, and natural language processing tasks.

## Mathematical Formulation

TF-IDF is the product of two key statistics: **Term Frequency (TF)** and **Inverse Document Frequency (IDF)**.

### 1. Term Frequency (TF)

The term frequency is defined as:

$TF(t, d) = \frac{\text{Number of times term } t \text{ appears in document } d}{\text{Total number of terms in document } d}$

- $t$: A specific term (word).
- $d$: A specific document in the corpus.

### 2. Inverse Document Frequency (IDF)

To account for how common or rare a term is across all documents in the corpus, we calculate:

$IDF(t) = \log\Bigl(\frac{N + 1}{\text{df}(t) + 1}\Bigr) + 1$

Where:

- $N$: Total number of documents in the corpus.
- $\text{df}(t)$: Number of documents containing the term $t$.
- Adding $+1$ inside the fraction prevents division by zero if a term never appears.
- Adding $+1$ outside the log ensures IDF remains nonzero.

### 3. TF-IDF

Combining TF and IDF:

$TFIDF(t, d) = TF(t, d) \times IDF(t)$

## Implementation Steps

1. **Compute TF**  
   For each document, count how often each term appears and divide by the document’s total word count.

2. **Compute IDF**  
   For each term, calculate its document frequency across all documents and apply the IDF formula.

3. **Calculate TF-IDF**  
   For every term in every document, multiply the term’s TF by its IDF.

4. **Normalization (Optional)**  
   Normalize TF-IDF vectors (e.g., using $L2$ norm) if comparing documents in a vector space model.

## Example Calculation

Suppose we have a small corpus of 3 documents:

- **Doc1**: "The cat sat on the mat"  
- **Doc2**: "The dog chased the cat"  
- **Doc3**: "The bird flew over the mat"

We want to calculate the TF-IDF for the word **"cat"** in **Doc1**.

### Step 1: Compute $TF("cat", \text{Doc1})$

$TF("cat", \text{Doc1}) = \frac{1}{6} \approx 0.1667$

- "cat" appears once.
- Total words in Doc1 (counting each occurrence of “the”) = 6.

### Step 2: Compute $IDF("cat")$

- "cat" appears in 2 out of 3 documents, so $\text{df}("cat") = 2$.
- $N = 3$.

Using the formula with smoothing and an added constant:

$IDF("cat") = \log\Bigl(\frac{N + 1}{\text{df}("cat") + 1}\Bigr) + 1 = \log\Bigl(\frac{3 + 1}{2 + 1}\Bigr) + 1 = \log\Bigl(\frac{4}{3}\Bigr) + 1 \approx 0.2877 + 1 = 1.2877$

### Step 3: Calculate $TFIDF("cat", \text{Doc1})$

$TFIDF("cat", \text{Doc1}) = TF("cat", \text{Doc1}) \times IDF("cat") = 0.1667 \times 1.2877 \approx 0.2147$

## Applications of TF-IDF

1. **Information Retrieval**  
   TF-IDF is often used in search engines to rank how relevant a document is to a given query.
2. **Text Mining**  
   Helps identify key terms and topics in large volumes of text.
3. **Document Classification**  
   Useful for weighting important words in classification tasks.
4. **Search Engines**  
   Refines document ranking by emphasizing distinctive terms.
5. **Recommendation Systems**  
   Evaluates text-based similarity (e.g., for content-based filtering).

TF-IDF remains a foundational technique in natural language processing, widely used for feature extraction and analysis across numerous text-based applications.


### meta.json

```json
{
  "id": "60",
  "title": "Implement TF-IDF (Term Frequency-Inverse Document Frequency)",
  "difficulty": "medium",
  "category": "NLP",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/Hui-cd",
      "name": "Hui"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def compute_tf_idf(corpus, query):
    """
    Compute TF-IDF scores for a query against a corpus of documents using only NumPy.
    The output TF-IDF scores retain five decimal places.
    """
    vocab = sorted(set(word for document in corpus for word in document).union(query))
    word_to_index = {word: idx for idx, word in enumerate(vocab)}

    tf = np.zeros((len(corpus), len(vocab)))

    for doc_idx, document in enumerate(corpus):
        for word in document:
            word_idx = word_to_index[word]
            tf[doc_idx, word_idx] += 1
        tf[doc_idx, :] /= len(document)

    df = np.count_nonzero(tf > 0, axis=0)

    num_docs = len(corpus)
    idf = np.log((num_docs + 1) / (df + 1)) + 1

    tf_idf = tf * idf

    query_indices = [word_to_index[word] for word in query]
    tf_idf_scores = tf_idf[:, query_indices]

    tf_idf_scores = np.round(tf_idf_scores, 5)

    return tf_idf_scores.tolist()
```




### starter_code.py

```python
import numpy as np


def compute_tf_idf(corpus, query):
    """
    Compute TF-IDF scores for a query against a corpus of documents.

    :param corpus: List of documents, where each document is a list of words
    :param query: List of words in the query
    :return: List of lists containing TF-IDF scores for the query words in each document
    """
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\n\ncorpus = [\n    [\"the\", \"cat\", \"sat\", \"on\", \"the\", \"mat\"],\n    [\"the\", \"dog\", \"chased\", \"the\", \"cat\"],\n    [\"the\", \"bird\", \"flew\", \"over\", \"the\", \"mat\"]\n]\nquery = [\"cat\"]\n\nprint(compute_tf_idf(corpus, query))",
    "expected_output": "[[0.21461], [0.25754], [0.0]]"
  },
  {
    "test": "import numpy as np\n\ncorpus = [\n    [\"the\", \"cat\", \"sat\", \"on\", \"the\", \"mat\"],\n    [\"the\", \"dog\", \"chased\", \"the\", \"cat\"],\n    [\"the\", \"bird\", \"flew\", \"over\", \"the\", \"mat\"]\n]\nquery = [\"cat\", \"mat\"]\n\nprint(compute_tf_idf(corpus, query))",
    "expected_output": "[[0.21461, 0.21461], [0.25754, 0.0], [0.0, 0.21461]]"
  },
  {
    "test": "import numpy as np\n\ncorpus = [\n    [\"this\", \"is\", \"a\", \"sample\"],\n    [\"this\", \"is\", \"another\", \"example\"],\n    [\"yet\", \"another\", \"sample\", \"document\"],\n    [\"one\", \"more\", \"document\", \"for\", \"testing\"]\n]\nquery = [\"sample\", \"document\", \"test\"]\n\nprint(compute_tf_idf(corpus, query))",
    "expected_output": "[[0.37771, 0.0, 0.0], [0.0, 0.0, 0.0], [0.37771, 0.37771, 0.0], [0.0, 0.30217, 0.0]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/60_implement-tf-idf-term-frequency-inverse-document-f/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/60_implement-tf-idf-term-frequency-inverse-document-f/description.md)。Deep-ML：Educational Use Only License。
