# -*- coding: utf-8 -*-
from text_utils import *
import re

class IntersectionFinder:
    valid_token_pat = re.compile(u'\A[a-zA-Z]+\Z')

    def __init__(self, threshold=2):
        # This dictionary stores the transition data for each token
        self.token_graph = {}
        self.threshold = threshold
        self.next_index = 0

    def add_text_to_graph(self, text):
        text_index = self.next_index
        self.next_index += 1
        prepared_text = normalize_text(text)
        raw_tokens, _ = word_tokenize(prepared_text)
        tokens = [fix_strange_quote_chars(t) for t in raw_tokens]
        
        last_token = None

        # Replace by set
        for t in tokens:
            if t not in self.token_graph:
                self.token_graph[t] = {}

            if last_token is not None:
                
                if t not in self.token_graph[last_token]:
                    self.token_graph[last_token][t] = set([text_index])
                else:
                    self.token_graph[last_token][t].add(text_index)

                last_token = t
            else:
                last_token = t
        return text_index
    
    def find_intersection_key_points_data(self, tokens):
        len_tokens = len(tokens)
        # texts_complying is a set for each token index. Representes text indexes that contain the current token transition
        # texts_complying is a set for each token index. Its the intersection between the elements of the previous array. This
        # way, whe can keep track when a text citation ends for one of the texts on the dataset but still complies for another text
        texts_complying_intersection = [{}]*len_tokens 

        prev_token = None
        prev_intersection = {}

        key_points = []

        for i, t in enumerate(tokens):
            prev_i = max(0, i-1)
            if prev_token is None:
                prev_token = t
                prev_intersection = {}
                continue

            if prev_token not in self.token_graph: # There are no more texts complying with the sequence. Add a key point
                if len(texts_complying_intersection[prev_i]) != 0:
                    key_points.append({'index': prev_i, 'texts_complying': prev_intersection})

                prev_token = t
                prev_intersection = {}
                continue

            if t in self.token_graph[prev_token]:
                texts_indexes = self.token_graph[prev_token][t]
                new_common_indexes = texts_indexes.intersection(prev_intersection)
                
                if len(new_common_indexes) != 0:
                    texts_complying_intersection[i] = new_common_indexes
                else:
                    texts_complying_intersection[i] = texts_indexes
                if len(new_common_indexes) == 0 and len(texts_complying_intersection[prev_i]) != 0: # There are no more texts complying with the sequence. Add a key point
                    key_points.append({'index': prev_i, 'texts_complying': prev_intersection})

                prev_token = t
                prev_intersection = texts_complying_intersection[i]

            else:
                if len(texts_complying_intersection[prev_i]) != 0:
                    key_points.append({'index': prev_i, 'texts_complying': prev_intersection})

                prev_token = t
                prev_intersection = []

        if prev_intersection != []:
            key_points.append({'index': len(tokens)-1, 'texts_complying': prev_intersection})
        return {
            'key_points': key_points,
            'texts_complying_intersection': texts_complying_intersection
        }

    def key_point_data_to_intersections(self, original_text, spans, key_point_data):
        key_points = key_point_data['key_points']
        texts_complying_intersection = key_point_data['texts_complying_intersection']
        intersections = []
        for kp in key_points:
            first_one = None
            last_one = None
            num_tokens = 0
            for index in range(kp['index'] + 1): # iterate the commom indexes until now
                ind = kp['index'] - index
                common_ind = texts_complying_intersection[ind]

                first_one = spans[ind]
                num_tokens += 1
                if kp['texts_complying'].issubset(common_ind):
                    if last_one is None:
                        last_one = spans[ind]
                else:
                    break
            
            if num_tokens >= self.threshold:
                start = first_one[0]
                end = last_one[1]
                intersections.append({'text': original_text[start:end+1], 
                'sources_indexes': kp['texts_complying'],
                'start': start, 
                'end': end
                })
        return intersections
    
    def get_intersections(self, text):
        prepared_text = normalize_text(text)
        raw_tokens, raw_spans = word_tokenize(prepared_text)
        raw_tokens[:] = [fix_strange_quote_chars(t) for t in raw_tokens]

        valid_tokens_and_spans = [(t, raw_spans[i]) for i, t in enumerate(raw_tokens) if IntersectionFinder.valid_token_pat.match(t)]
        tokens = [t for [t, s] in valid_tokens_and_spans]
        spans = [s for [t, s] in valid_tokens_and_spans]

        key_point_data = self.find_intersection_key_points_data(tokens)
        intersections = self.key_point_data_to_intersections(text, spans, key_point_data)
        return intersections