# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_ACCESS_LATENCY = 0
INITIAL_TEMPORAL_PATTERN = 0
INITIAL_STOCHASTIC_PARAM = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access latency history, a predictive score for each cache entry, temporal access patterns, and stochastic model parameters for access prediction.
metadata = {
    'access_latency': collections.defaultdict(lambda: INITIAL_ACCESS_LATENCY),
    'predictive_score': collections.defaultdict(lambda: INITIAL_PREDICTIVE_SCORE),
    'temporal_pattern': collections.defaultdict(lambda: INITIAL_TEMPORAL_PATTERN),
    'stochastic_param': collections.defaultdict(lambda: INITIAL_STOCHASTIC_PARAM)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest predictive score and the highest access latency, adjusted by temporal access patterns and stochastic model predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    max_latency = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['predictive_score'][key]
        latency = metadata['access_latency'][key]
        temporal_pattern = metadata['temporal_pattern'][key]
        stochastic_param = metadata['stochastic_param'][key]
        
        # Combine the factors to determine the eviction candidate
        combined_score = score - latency + temporal_pattern + stochastic_param
        
        if combined_score < min_score or (combined_score == min_score and latency > max_latency):
            min_score = combined_score
            max_latency = latency
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access latency history, recalculates the predictive score, adjusts the temporal access pattern, and refines the stochastic model parameters for the accessed entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access latency history
    metadata['access_latency'][key] = current_time - metadata['access_latency'][key]
    
    # Recalculate predictive score
    metadata['predictive_score'][key] = 1 / (1 + metadata['access_latency'][key])
    
    # Adjust temporal access pattern
    metadata['temporal_pattern'][key] += 1
    
    # Refine stochastic model parameters
    metadata['stochastic_param'][key] = (metadata['stochastic_param'][key] + metadata['predictive_score'][key]) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access latency history, sets an initial predictive score, establishes a baseline temporal access pattern, and initializes stochastic model parameters for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access latency history
    metadata['access_latency'][key] = current_time
    
    # Set initial predictive score
    metadata['predictive_score'][key] = INITIAL_PREDICTIVE_SCORE
    
    # Establish baseline temporal access pattern
    metadata['temporal_pattern'][key] = INITIAL_TEMPORAL_PATTERN
    
    # Initialize stochastic model parameters
    metadata['stochastic_param'][key] = INITIAL_STOCHASTIC_PARAM

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry and recalibrates the predictive scores, temporal patterns, and stochastic model parameters for the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata associated with the evicted entry
    del metadata['access_latency'][evicted_key]
    del metadata['predictive_score'][evicted_key]
    del metadata['temporal_pattern'][evicted_key]
    del metadata['stochastic_param'][evicted_key]
    
    # Recalibrate the predictive scores, temporal patterns, and stochastic model parameters for the remaining entries
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] = 1 / (1 + metadata['access_latency'][key])
        metadata['temporal_pattern'][key] += 1
        metadata['stochastic_param'][key] = (metadata['stochastic_param'][key] + metadata['predictive_score'][key]) / 2