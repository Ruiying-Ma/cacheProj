# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
DEFAULT_QUANTUM_LATENCY = 1.0
INITIAL_ENTROPY_SCORE = 1.0
INITIAL_HEURISTIC_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including predictive entropy scores for each cache entry, quantum latency metrics, temporal access patterns, and heuristic feedback scores.
metadata = {
    'entropy_scores': {},  # Predictive entropy scores for each cache entry
    'quantum_latency': {},  # Quantum latency metrics for each cache entry
    'temporal_patterns': {},  # Temporal access patterns for each cache entry
    'heuristic_scores': {}  # Heuristic feedback scores for each cache entry
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, combining predictive entropy, quantum latency, and temporal signal analysis. The entry with the highest composite score, indicating the least likelihood of future access and highest cost of retention, is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_composite_score = -math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy_score = metadata['entropy_scores'].get(key, INITIAL_ENTROPY_SCORE)
        quantum_latency = metadata['quantum_latency'].get(key, DEFAULT_QUANTUM_LATENCY)
        temporal_pattern = metadata['temporal_patterns'].get(key, 0)
        heuristic_score = metadata['heuristic_scores'].get(key, INITIAL_HEURISTIC_SCORE)
        
        composite_score = entropy_score + quantum_latency + temporal_pattern + heuristic_score
        
        if composite_score > max_composite_score:
            max_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive entropy score to reflect the reduced uncertainty of future accesses, adjusts the quantum latency metric to account for the recent access, and recalibrates the temporal signal analysis to capture the latest access pattern. The heuristic feedback score is also updated to refine future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy_scores'][key] = max(0, metadata['entropy_scores'].get(key, INITIAL_ENTROPY_SCORE) - 0.1)
    metadata['quantum_latency'][key] = DEFAULT_QUANTUM_LATENCY
    metadata['temporal_patterns'][key] = cache_snapshot.access_count
    metadata['heuristic_scores'][key] = metadata['heuristic_scores'].get(key, INITIAL_HEURISTIC_SCORE) + 0.1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the predictive entropy score based on initial access patterns, sets the quantum latency metric to a default low value, and begins tracking temporal signals from the moment of insertion. The heuristic feedback loop is primed with initial values to start learning from subsequent accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy_scores'][key] = INITIAL_ENTROPY_SCORE
    metadata['quantum_latency'][key] = DEFAULT_QUANTUM_LATENCY
    metadata['temporal_patterns'][key] = cache_snapshot.access_count
    metadata['heuristic_scores'][key] = INITIAL_HEURISTIC_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the predictive entropy scores for remaining entries to account for the changed cache state, updates quantum latency metrics to reflect the reduced cache load, and adjusts temporal signal patterns to remove the evicted entry's influence. The heuristic feedback loop is also updated to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['entropy_scores']:
        del metadata['entropy_scores'][evicted_key]
    if evicted_key in metadata['quantum_latency']:
        del metadata['quantum_latency'][evicted_key]
    if evicted_key in metadata['temporal_patterns']:
        del metadata['temporal_patterns'][evicted_key]
    if evicted_key in metadata['heuristic_scores']:
        del metadata['heuristic_scores'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['entropy_scores'][key] = max(0, metadata['entropy_scores'].get(key, INITIAL_ENTROPY_SCORE) - 0.05)
        metadata['quantum_latency'][key] = max(0, metadata['quantum_latency'].get(key, DEFAULT_QUANTUM_LATENCY) - 0.05)
        metadata['temporal_patterns'][key] = cache_snapshot.access_count
        metadata['heuristic_scores'][key] = metadata['heuristic_scores'].get(key, INITIAL_HEURISTIC_SCORE) + 0.05