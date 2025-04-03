# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_EQUILIBRIUM = 0.5
INITIAL_PREDICTIVE_RESONANCE = 0.5
FREQUENCY_INCREMENT = 1
RECENCY_INCREMENT = 1
TEMPORAL_EQUILIBRIUM_ADJUSTMENT = 0.1
PREDICTIVE_RESONANCE_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains an Adaptive Matrix that records access frequencies and recency for each cache entry, a Temporal Equilibrium score that tracks the stability of access patterns over time, and a Predictive Resonance factor that anticipates future accesses based on historical trends.
adaptive_matrix = defaultdict(lambda: {'frequency': 0, 'recency': 0})
temporal_equilibrium = defaultdict(lambda: INITIAL_TEMPORAL_EQUILIBRIUM)
predictive_resonance = defaultdict(lambda: INITIAL_PREDICTIVE_RESONANCE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of Temporal Equilibrium and Predictive Resonance, ensuring that entries with stable and predictable access patterns are retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = temporal_equilibrium[key] + predictive_resonance[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Adaptive Matrix is updated to increase the frequency and recency scores for the accessed entry, while the Temporal Equilibrium score is adjusted to reflect the stability of the access pattern. The Predictive Resonance factor is recalibrated to enhance future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    adaptive_matrix[key]['frequency'] += FREQUENCY_INCREMENT
    adaptive_matrix[key]['recency'] = cache_snapshot.access_count
    
    temporal_equilibrium[key] += TEMPORAL_EQUILIBRIUM_ADJUSTMENT
    predictive_resonance[key] += PREDICTIVE_RESONANCE_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Adaptive Matrix initializes frequency and recency scores for the new entry. The Temporal Equilibrium score is set to a neutral value, and the Predictive Resonance factor is initialized based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    adaptive_matrix[key]['frequency'] = 1
    adaptive_matrix[key]['recency'] = cache_snapshot.access_count
    
    temporal_equilibrium[key] = INITIAL_TEMPORAL_EQUILIBRIUM
    predictive_resonance[key] = INITIAL_PREDICTIVE_RESONANCE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Adaptive Matrix is adjusted to remove the evicted entry's data. The Temporal Equilibrium scores of remaining entries are recalculated to account for the change in cache dynamics, and the Predictive Resonance factors are updated to refine future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in adaptive_matrix:
        del adaptive_matrix[evicted_key]
        del temporal_equilibrium[evicted_key]
        del predictive_resonance[evicted_key]
    
    # Recalculate scores for remaining entries
    for key in cache_snapshot.cache:
        temporal_equilibrium[key] = max(0, temporal_equilibrium[key] - TEMPORAL_EQUILIBRIUM_ADJUSTMENT)
        predictive_resonance[key] = max(0, predictive_resonance[key] - PREDICTIVE_RESONANCE_ADJUSTMENT)