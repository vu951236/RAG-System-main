import math

def compute_tf(tokens):
    if not tokens: return {}
    counts = {}
    for word in tokens:
        counts[word] = counts.get(word, 0) + 1
    
    tf_log = {}
    for word, count in counts.items():
        tf_log[word] = 1 + math.log10(count)
    return tf_log

def compute_idf(all_documents_tokens):
    n_docs = len(all_documents_tokens)
    if n_docs == 0: return {}

    idf_dict = {}
    for doc in all_documents_tokens:
        for word in set(doc):
            idf_dict[word] = idf_dict.get(word, 0) + 1
    
    for word, count in idf_dict.items():
        # Sử dụng log10(N/count)
        idf_dict[word] = math.log10(n_docs / count)
    return idf_dict

def calculate_cosine_similarity(query_tf, doc_tf, idf_dict):
    words = set(query_tf.keys()) & set(doc_tf.keys())
    if not words: return 0
    
    dot_product = 0
    mag1 = 0
    mag2 = sum((v * idf_dict.get(k, 0))**2 for k, v in doc_tf.items())
    
    for q_word, q_tf_val in query_tf.items():
        idf = idf_dict.get(q_word, 0)
        v1 = q_tf_val * idf
        mag1 += v1 ** 2
        if q_word in doc_tf:
            v2 = doc_tf[q_word] * idf
            dot_product += v1 * v2
    
    mag1 = math.sqrt(mag1)
    mag2 = math.sqrt(mag2)
    
    return dot_product / (mag1 * mag2) if (mag1 * mag2) > 0 else 0