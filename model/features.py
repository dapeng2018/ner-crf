# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import re

class StartsWithUppercaseFeature(object):
    def __init__(self):
        pass
    
    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["swu=%d" % (int(token.word[:1].istitle()))])
        return result

class TokenLengthFeature(object):
    def __init__(self, max_length=30):
        self.max_length = max_length

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["l=%d" % (min(len(token.word), self.max_length))])
        return result

class ContainsDigitsFeature(object):    
    def __init__(self):
        self.regexpContainsDigits = re.compile(r'[0-9]+')

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["cD=%d" % (int(self.regexpContainsDigits.search(token.word) is not None))])
        return result
    
class ContainsPunctuationFeature(object):
    def __init__(self):
        self.regexpContainsPunctuation = re.compile(r'[\.\,\:\;\(\)\[\]\?\!]+')

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["cP=%d" % (int(self.regexpContainsPunctuation.search(token.word) is not None))])
        return result

class OnlyDigitsFeature(object):
    def __init__(self):
        self.regexpContainsOnlyDigits = re.compile(r'^[0-9]+$')

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["oD=%d" % (int(self.regexpContainsOnlyDigits.search(token.word) is not None))])
        return result

class OnlyPunctuationFeature(object):
    def __init__(self):
        self.regexpContainsOnlyPunctuation = re.compile(r'^[\.\,\:\;\(\)\[\]\?\!]+$')

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["oP=%d" % (int(self.regexpContainsOnlyPunctuation.search(token.word) is not None))])
        return result

class W2VClusterFeature(object):
    def __init__(self, w2v_clusters):
        self.w2v_clusters = w2v_clusters

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["w2v=%d" % (self.token_to_cluster(token))])
        return result
    
    def token_to_cluster(self, token):
        return self.w2v_clusters.get_cluster_of(token.word, -1)

class BrownClusterFeature(object):
    def __init__(self, brown_clusters):
        self.brown_clusters = brown_clusters

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["bc=%d" % (self.token_to_cluster(token))])
        return result
    
    def token_to_cluster(self, token):
        return self.brown_clusters.get_cluster_of(token.word, -1)

class BrownClusterBitsFeature(object):
    def __init__(self, brown_clusters):
        self.brown_clusters = brown_clusters

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["bcb=%s" % (self.token_to_bitchain(token)[0:7])])
        return result
    
    def token_to_bitchain(self, token):
        return self.brown_clusters.get_bitchain_of(token.word, "")

class GazetteerFeature(object):
    def __init__(self, gazetteer):
        self.gazetteer = gazetteer
    
    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["g=%d" % (int(self.is_in_gazetteer(token)))])
        return result
    
    def is_in_gazetteer(self, token):
        return self.gazetteer.contains(token.word)

class WordPatternFeature(object):
    def __init__(self):
        self.max_length = 15
        self.max_length_char = "~"
        
        self.normalization = [
            (r"[A-ZÄÖÜ]", "A"),
            (r"[a-zäöüß]", "a"),
            (r"[0-9]", "9"),
            (r"[\.\!\?\,\;]", "."),
            (r"[\(\)\[\]\{\}]", "("),
            (r"[^Aa9\.\(]", "#")
        ]
        
        # note: we do not map numers to 9+, e.g. years will still be 9999
        self.mappings = [
            (r"[A]{2,}", "A+"),
            (r"[a]{2,}", "a+"),
            (r"[\.]{2,}", ".+"),
            (r"[\(]{2,}", "(+"),
            (r"[#]{2,}", "#+")
        ]

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["wp=%s" % (self.token_to_wordpattern(token))])
        return result
    
    def token_to_wordpattern(self, token):
        normalized = token.word
        for from_regex, to_str in self.normalization:
            normalized = re.sub(from_regex, to_str, normalized)
        
        wp = normalized
        for from_regex, to_str in self.mappings:
            wp = re.sub(from_regex, to_str, wp)
        
        if len(wp) > self.max_length:
            wp = wp[0:self.max_length] + self.max_length_char
        
        return wp

class UnigramRankFeature(object):
    def __init__(self, unigrams):
        self.unigrams = unigrams

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            result.append(["ng1=%d" % (self.token_to_rank(token))])
        return result
    
    def token_to_rank(self, token):
        return self.unigrams.get_rank_of(token.word, -1)

class PrefixFeature(object):
    def __init__(self):
        pass

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            prefix = re.sub(r"[^a-zA-ZäöüÄÖÜß\.\,\!\?]", "#", token.word[0:3])
            result.append(["pf=%s" % (prefix)])
        return result

class SuffixFeature(object):
    def __init__(self):
        pass

    def convert_window(self, window):
        result = []
        for token in window.tokens:
            suffix = re.sub(r"[^a-zA-ZäöüÄÖÜß\.\,\!\?]", "#", token.word[-3:])
            result.append(["sf=%s" % (suffix)])
        return result

class POSTagFeature(object):
    def __init__(self, pos_tagger):
        self.pos_tagger = pos_tagger

    def convert_window(self, window):
        pos_tags = self.stanford_pos_tag(window)
        result = []
        for i, token in enumerate(window.tokens):
            word, pos_tag = pos_tags[i][0], pos_tags[i][1]
            result.append(["pos=%s" % (pos_tag)])
        return result
    
    def stanford_pos_tag(self, window):
        return self.pos_tagger.tag([token.word for token in window.tokens])

class LDATopicFeature(object):
    def __init__(self, lda_wrapper, window_left_size, window_right_size, prob_threshold=0.2):
        self.lda_wrapper = lda_wrapper
        self.window_left_size = window_left_size
        self.window_right_size = window_right_size
        self.prob_threshold = prob_threshold

    def convert_window(self, window):
        result = []
        for i, token in enumerate(window.tokens):
            token_features = []
            window_start = max(0, i - self.window_left_size)
            window_end = min(len(window.tokens), i + self.window_right_size + 1)
            window_tokens = window.tokens[window_start:window_end]
            text = " ".join([token.word for token in window_tokens])
            topics = self.get_topics(text)
            for (topic_idx, prob) in topics:
                if prob > self.prob_threshold:
                    token_features.append("lda_%d=%s" % (topic_idx, "1"))
            result.append(token_features)
        return result
    
    def get_topics(self, text):
        return self.lda_wrapper.get_topics(text)
