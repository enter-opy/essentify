import numpy as np
import pandas as pd
import json

class Collection:
    def __init__(self):
        self.results = pd.read_json('results/results.json').transpose()
        self.embeddings = pd.read_json('results/embeddings.json').transpose()
        with open('results/activations.json', 'r') as f:
            self.activations = json.load(f)


    def sort_by_style(self, style):
        results = self.results.copy()
        
        style_ranks = [row[style] for row in self.activations.values()]

        results['style rank'] = style_ranks
        results = results.sort_values(by='style rank', ascending=False)
        results.drop('style rank', axis=1)

        return results


    def filter_by_tempo(self, results, tempo):
        results['distance'] = abs(results['tempo'] - tempo)
        results = results[results['distance'] < 10]
        results = results.drop('distance', axis=1)

        return results


    def filter_instrumentals(self, results, require_instrumentals):
        instrumentals = results[results['instrumental'] == 'Instrumental']
        voices = results[results['instrumental'] == 'Voice']

        results = instrumentals if require_instrumentals else voices

        return results


    def filter_by_danceability(self, results, danceability):
        min_danceability, max_danceability = danceability
        min_danceability /= 100
        max_danceability /= 100

        results = results[results['danceability confidence'] >= min_danceability]
        results = results[results['danceability confidence'] <= max_danceability]

        return results


    def filter_by_arousal_and_valence(self, results, arousal, valence):
        min_arousal, max_arousal = arousal
        min_valence, max_valence = valence
        
        if min_arousal > 0:
            results = results[results['arousal'] >= min_arousal]
        if max_arousal < 9:
            results = results[results['arousal'] <= max_arousal]
        if max_arousal > 0:
            results = results[results['valence'] >= min_valence]
        if max_valence < 9:
            results = results[results['valence'] <= max_valence]

        return results


    def filter_by_key_and_scale(self, results, key, scale):
        if key != 'All':
            results = results[results['key (edma)'] == key]

        if scale != 'All':
            results = results[results['scale (edma)'] == scale.lower()]

        return results


    def search_similar_tracks(self, filename, embedding_model):
        results = self.embeddings.copy()
        curr_embedding = results[embedding_model + '_embeddings'][filename]

        similarities = []

        for i, index in enumerate(results.index):
            similarity = np.dot(results[embedding_model + '_embeddings'][index], curr_embedding)
            similarity /= (np.linalg.norm(results[embedding_model + '_embeddings'][index]) * np.linalg.norm(curr_embedding))
            similarity = similarity.tolist()
            similarities.append(similarity)

        results['similarity'] = similarities
        results = results.sort_values(by='similarity', ascending=False)
        results = results.drop('similarity', axis=1)

        return results



