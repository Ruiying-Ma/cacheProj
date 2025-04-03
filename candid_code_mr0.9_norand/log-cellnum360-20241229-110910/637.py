# Import anything you need below
import numpy as np

# Put tunable constant parameters below
HARMONIC_SCORE_INCREMENT = 1.0
NEURAL_CALIBRATION_ADJUSTMENT = 0.1
SYNERGISTIC_STRENGTHENING = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a harmonic score for each cache entry, a neural calibration vector that adjusts based on access patterns, and a synergistic matrix that records interactions between cache entries.
harmonic_scores = {}
neural_calibration_vector = {}
synergistic_matrix = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest harmonic score, adjusted by the neural calibration vector, and cross-referenced with the synergistic matrix to minimize disruption to frequently accessed pairs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = harmonic_scores[key] - neural_calibration_vector.get(key, 0)
        for other_key in cache_snapshot.cache:
            if other_key != key:
                adjusted_score += synergistic_matrix.get((key, other_key), 0)
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the harmonic score of the accessed entry is increased, the neural calibration vector is adjusted to reflect the current access pattern, and the synergistic matrix is updated to strengthen the relationship between the accessed entry and its neighbors.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    harmonic_scores[key] = harmonic_scores.get(key, 0) + HARMONIC_SCORE_INCREMENT
    neural_calibration_vector[key] = neural_calibration_vector.get(key, 0) + NEURAL_CALIBRATION_ADJUSTMENT
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            synergistic_matrix[(key, other_key)] = synergistic_matrix.get((key, other_key), 0) + SYNERGISTIC_STRENGTHENING

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the harmonic score is initialized based on the neural calibration vector's current state, and the synergistic matrix is updated to include potential interactions with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    harmonic_scores[key] = neural_calibration_vector.get(key, 0)
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            synergistic_matrix[(key, other_key)] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the harmonic scores of remaining entries are recalibrated, the neural calibration vector is adjusted to account for the change in cache composition, and the synergistic matrix is pruned to remove references to the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in harmonic_scores:
        del harmonic_scores[evicted_key]
    if evicted_key in neural_calibration_vector:
        del neural_calibration_vector[evicted_key]
    
    keys_to_remove = [key for key in synergistic_matrix if evicted_key in key]
    for key in keys_to_remove:
        del synergistic_matrix[key]
    
    for key in cache_snapshot.cache:
        harmonic_scores[key] = max(0, harmonic_scores[key] - NEURAL_CALIBRATION_ADJUSTMENT)