# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_RECENCY = 0
INITIAL_STATE = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, predicted future access patterns, and a hierarchical state machine representing different states of cache lines. It also includes adaptive learning parameters to adjust predictions over time.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'recency': {},           # key -> recency (last access time)
    'state': {},             # key -> state in hierarchical state machine
    'predicted_access': {}   # key -> predicted future access
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating the hierarchical state machine to identify cache lines in the least favorable state, considering both low predicted future access and low recent access frequency. It uses adaptive learning to refine these decisions over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate score based on state, predicted future access, and recency
        state = metadata['state'].get(key, INITIAL_STATE)
        predicted_access = metadata['predicted_access'].get(key, 0)
        recency = metadata['recency'].get(key, 0)
        
        # Lower score means higher chance of eviction
        score = state + predicted_access - recency
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency metadata for the accessed cache line. It also adjusts the hierarchical state machine to reflect the improved state of the cache line and updates the predictive model based on the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, INITIAL_ACCESS_FREQUENCY) + 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['state'][key] = min(metadata['state'].get(key, INITIAL_STATE) + 1, 10)  # Example state increment
    metadata['predicted_access'][key] = metadata['access_frequency'][key]  # Simple prediction model

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with default values, sets its state in the hierarchical state machine to the initial state, and updates the predictive model to account for the new object in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = INITIAL_ACCESS_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['state'][key] = INITIAL_STATE
    metadata['predicted_access'][key] = INITIAL_ACCESS_FREQUENCY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted cache line, updates the hierarchical state machine to reflect the removal, and adjusts the predictive model to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['state']:
        del metadata['state'][evicted_key]
    if evicted_key in metadata['predicted_access']:
        del metadata['predicted_access'][evicted_key]