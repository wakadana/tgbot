from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentFilter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 2),
            stop_words=None,  # Можно подключить стоп-слова для ru/en при необходимости
        )

    def filter_by_interests(self, items: List[Dict], interests: List[str], threshold: float = 0.2) -> List[Dict]:
        if not items:
            return []
        if not interests:
            # Если интересов нет — вернем top-N без фильтрации
            return items[:20]

        texts = [f"{it.get('title','')} {it.get('summary','')}".strip() for it in items]
        # Совмещаем интересы в один запрос для получения единого вектора
        interest_query = "; ".join(interests)

        corpus = texts + [interest_query]
        tfidf = self.vectorizer.fit_transform(corpus)

        news_vectors = tfidf[:-1]
        interest_vector = tfidf[-1]

        sims = cosine_similarity(news_vectors, interest_vector)
        # sims: (n_news, 1)
        scored = []
        for idx, item in enumerate(items):
            score = float(sims[idx][0])
            if score >= threshold:
                enriched = dict(item)
                enriched["relevance_score"] = score
                scored.append(enriched)

        scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return scored[:50]


