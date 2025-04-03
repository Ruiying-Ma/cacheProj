# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_SEQUENTIAL_ACCESS = 0.1
WEIGHT_LOAD_DISTRIBUTION = 0.1
WEIGHT_CONTEXTUAL_RELEVANCE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, sequential access patterns, load distribution metrics, and contextual information about the data being cached.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'sequential_access': {},  # {obj.key: sequential_access_score}
    'load_distribution': {},  # {obj.key: load_score}
    'contextual_relevance': {}  # {obj.key: relevance_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that considers low access frequency, old last access time, lack of sequential access patterns, high load on specific cache segments, and low relevance of contextual information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        last_access_time = metadata['last_access_time'].get(key, 0)
        sequential_access = metadata['sequential_access'].get(key, 0)
        load_distribution = metadata['load_distribution'].get(key, 0)
        contextual_relevance = metadata['contextual_relevance'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_SEQUENTIAL_ACCESS * sequential_access +
                 WEIGHT_LOAD_DISTRIBUTION * load_distribution +
                 WEIGHT_CONTEXTUAL_RELEVANCE * contextual_relevance)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, adjusts sequential access patterns if applicable, rebalances load metrics, and updates contextual information based on the current access context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust sequential access patterns, load metrics, and contextual information as needed
    # For simplicity, we assume these are updated in a straightforward manner
    metadata['sequential_access'][key] = 1  # Example update
    metadata['load_distribution'][key] = 1  # Example update
    metadata['contextual_relevance'][key] = 1  # Example update

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, checks for and records any sequential access patterns, updates load distribution metrics to reflect the new insertion, and stores initial contextual information about the object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['sequential_access'][key] = 1  # Example initialization
    metadata['load_distribution'][key] = 1  # Example initialization
    metadata['contextual_relevance'][key] = 1  # Example initialization

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata, recalculates load distribution metrics to account for the removal, and adjusts any sequential access patterns and contextual information that may be affected by the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['sequential_access']:
        del metadata['sequential_access'][key]
    if key in metadata['load_distribution']:
        del metadata['load_distribution'][key]
    if key in metadata['contextual_relevance']:
        del metadata['contextual_relevance'][key]
    # Recalculate load distribution metrics and adjust sequential access patterns as needed
    # For simplicity, we assume these are updated in a straightforward manner