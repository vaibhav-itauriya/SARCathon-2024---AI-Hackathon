import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
import faiss
import re
import nltk
from nltk.corpus import stopwords
from spellchecker import SpellChecker

class FAQSearch:
    def __init__(self, faq_file, embedding_file='embeddings.npy'):
        # Initialize the spell checker
        self.spell = SpellChecker()
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

        # Load the language model
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.faqs = self.load_faqs(faq_file)
        self.questions = [faq['question'] for faq in self.faqs]
        self.answers = [faq['answer'] for faq in self.faqs]
        
        # Preprocess questions
        self.processed_questions = [self.preprocess_text(q) for q in self.questions]

        # Load or compute embeddings
        if os.path.exists(embedding_file):
            self.question_embeddings = np.load(embedding_file)
        else:
            self.question_embeddings = self.model.encode(self.processed_questions, convert_to_tensor=False)
            np.save(embedding_file, self.question_embeddings)
        
        # Build FAISS index
        self.index = self.build_faiss_index(self.question_embeddings)
        
    def load_faqs(self, faq_file):
        with open(faq_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            faqs = []
            for category in data.values():
                faqs.extend(category)
            return faqs

    def preprocess_text(self, text):
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove stop words
        tokens = text.split()
        tokens = [word for word in tokens if word not in self.stop_words]
        return ' '.join(tokens)

    def correct_spelling(self, query):
        corrected_query = []
        for word in query.split():
            corrected_word = self.spell.correction(word)
            corrected_query.append(corrected_word)
        return ' '.join(corrected_query)

    def build_faiss_index(self, embeddings):
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index

    def get_suggestions(self, query):
        suggestions = process.extract(query, self.questions, limit=5)
        return [match[0] for match in suggestions if match[1] > 50]

    def search(self, query, top_k=5):
        # Correct spelling
        query = self.correct_spelling(query)
        # Preprocess query
        processed_query = self.preprocess_text(query)

        # Fuzzy Matching
        fuzzy_matches = process.extract(processed_query, self.processed_questions, limit=top_k)
        fuzzy_results = []
        for match, score in fuzzy_matches:
            if score > 60:
                index = self.processed_questions.index(match)
                fuzzy_results.append({
                    'question': self.questions[index],
                    'answer': self.answers[index],
                    'score': score / 100  # Normalize score to [0,1]
                })

        # Semantic Search using FAISS
        query_embedding = self.model.encode([processed_query], convert_to_tensor=False)
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        semantic_results = []
        for i, idx in enumerate(indices[0]):
            score = 1 - (distances[0][i] / 4)  # Normalize distances
            if score > 0.5:
                semantic_results.append({
                    'question': self.questions[idx],
                    'answer': self.answers[idx],
                    'score': score
                })

        # Combine and sort results
        combined_results = {item['question']: item for item in fuzzy_results + semantic_results}
        sorted_results = sorted(combined_results.values(), key=lambda x: x['score'], reverse=True)

        return sorted_results[:top_k]
