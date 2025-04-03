# Import anything you need below
import numpy as np

# Put tunable constant parameters below
INITIAL_PROBABILISTIC_SCORE = 1.0
ADAPTATION_COEFFICIENT = 0.1
SCORE_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a probabilistic score for each cache entry, a historical access pattern matrix, and a real-time adaptation coefficient. The score is influenced by access frequency, recency, and predicted future access patterns.
probabilistic_scores = {}
access_pattern_matrix = {}
adaptation_coefficient = ADAPTATION_COEFFICIENT

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry, combining its probabilistic score and strategic foresight from the access pattern matrix. The entry with the lowest composite score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        probabilistic_score = probabilistic_scores.get(key, INITIAL_PROBABILISTIC_SCORE)
        access_pattern_score = access_pattern_matrix.get(key, 0)
        composite_score = probabilistic_score + adaptation_coefficient * access_pattern_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the probabilistic score of the accessed entry is increased based on its recency and frequency. The access pattern matrix is updated to reflect the latest access, and the adaptation coefficient is adjusted to fine-tune future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    probabilistic_scores[key] = probabilistic_scores.get(key, INITIAL_PROBABILISTIC_SCORE) + 1
    access_pattern_matrix[key] = cache_snapshot.access_count
    global adaptation_coefficient
    adaptation_coefficient *= SCORE_DECAY_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its probabilistic score based on initial access predictions. The access pattern matrix is updated to include the new entry, and the adaptation coefficient is recalibrated to account for the new entry's potential impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    probabilistic_scores[key] = INITIAL_PROBABILISTIC_SCORE
    access_pattern_matrix[key] = cache_snapshot.access_count
    global adaptation_coefficient
    adaptation_coefficient *= SCORE_DECAY_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the adaptation coefficient to reflect the change in cache composition. The access pattern matrix is adjusted to remove the evicted entry, and the probabilistic scores of remaining entries are slightly adjusted to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in probabilistic_scores:
        del probabilistic_scores[evicted_key]
    if evicted_key in access_pattern_matrix:
        del access_pattern_matrix[evicted_key]
    
    global adaptation_coefficient
    adaptation_coefficient *= SCORE_DECAY_FACTOR
    
    for key in probabilistic_scores:
        probabilistic_scores[key] *= SCORE_DECAY_FACTOR