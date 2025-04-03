# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQ = 0.25
WEIGHT_LAST_ACCESS = 0.25
WEIGHT_ADJACENCY_SCORE = 0.25
WEIGHT_PREDICTIVE_SCORE = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, adjacency score (based on data adjacency), and a predictive score (based on historical access patterns).
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'adjacency_score': {},   # key -> adjacency score
    'predictive_score': {}   # key -> predictive score
}

def calculate_composite_score(key, current_time):
    access_freq = metadata['access_frequency'].get(key, 1)
    last_access = metadata['last_access_time'].get(key, current_time)
    adjacency = metadata['adjacency_score'].get(key, 0)
    predictive = metadata['predictive_score'].get(key, 0)
    
    score = (WEIGHT_ACCESS_FREQ / access_freq +
             WEIGHT_LAST_ACCESS * (current_time - last_access) +
             WEIGHT_ADJACENCY_SCORE * adjacency +
             WEIGHT_PREDICTIVE_SCORE * predictive)
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the inverse of access frequency, the time since last access, the adjacency score, and the predictive score. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    current_time = cache_snapshot.access_count
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key, current_time)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access time is updated to the current time, the adjacency score is recalculated based on the accessed data's neighbors, and the predictive score is adjusted based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = current_time
    # Recalculate adjacency score and predictive score based on your specific logic
    # For simplicity, we assume they remain the same in this example
    metadata['adjacency_score'][key] = metadata['adjacency_score'].get(key, 0)
    metadata['predictive_score'][key] = metadata['predictive_score'].get(key, 0)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access time is set to the current time, the adjacency score is computed based on the new object's data neighbors, and the predictive score is initialized based on historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = current_time
    # Initialize adjacency score and predictive score based on your specific logic
    metadata['adjacency_score'][key] = 0  # Example initialization
    metadata['predictive_score'][key] = 0  # Example initialization

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted entry is removed from the cache, and the remaining entries' predictive scores are updated to reflect the change in the cache's state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for the evicted entry
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['adjacency_score']:
        del metadata['adjacency_score'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]
    
    # Update predictive scores for remaining entries based on your specific logic
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] = metadata['predictive_score'].get(key, 0)  # Example update