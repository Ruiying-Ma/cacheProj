# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PREDICTIVE_INDEX_DECAY = 0.9
LATENT_VARIABLE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive index for each cache entry, latent variables representing access patterns, temporal access timestamps, and load distribution metrics across cache entries.
metadata = {
    'predictive_index': {},  # {key: predictive_index}
    'latent_variables': {},  # {key: latent_variable}
    'timestamps': {},        # {key: timestamp}
    'load_distribution': {}  # {key: load}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the predictive index to forecast future access likelihood, considering latent variables to identify less critical entries, and evaluating temporal patterns to deprioritize stale data. Dynamic load balancing ensures even distribution of cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_index = metadata['predictive_index'].get(key, 0)
        latent_variable = metadata['latent_variables'].get(key, 0)
        timestamp = metadata['timestamps'].get(key, 0)
        load = metadata['load_distribution'].get(key, 0)
        
        # Calculate the score for eviction
        score = predictive_index + latent_variable + (cache_snapshot.access_count - timestamp) + load
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the predictive index to reflect the increased likelihood of future access, adjusts latent variables to capture the latest access pattern, and refreshes the temporal access timestamp. Load distribution metrics are recalibrated to account for the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_index'][key] = metadata['predictive_index'].get(key, 0) * PREDICTIVE_INDEX_DECAY + 1
    metadata['latent_variables'][key] = metadata['latent_variables'].get(key, 0) * LATENT_VARIABLE_DECAY + 1
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['load_distribution'][key] = metadata['load_distribution'].get(key, 0) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the predictive index, latent variables, and temporal access timestamp for the new entry. Load distribution metrics are updated to include the new object, ensuring balanced cache utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['predictive_index'][key] = 1
    metadata['latent_variables'][key] = 1
    metadata['timestamps'][key] = cache_snapshot.access_count
    metadata['load_distribution'][key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry, recalibrates the predictive index and latent variables for remaining entries, and updates load distribution metrics to reflect the removal, maintaining balanced cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['predictive_index']:
        del metadata['predictive_index'][evicted_key]
    if evicted_key in metadata['latent_variables']:
        del metadata['latent_variables'][evicted_key]
    if evicted_key in metadata['timestamps']:
        del metadata['timestamps'][evicted_key]
    if evicted_key in metadata['load_distribution']:
        del metadata['load_distribution'][evicted_key]
    
    # Recalibrate the predictive index and latent variables for remaining entries
    for key in metadata['predictive_index']:
        metadata['predictive_index'][key] *= PREDICTIVE_INDEX_DECAY
        metadata['latent_variables'][key] *= LATENT_VARIABLE_DECAY