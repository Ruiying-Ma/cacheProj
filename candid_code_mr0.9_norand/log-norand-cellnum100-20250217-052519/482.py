# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for LFU
BETA = 0.5   # Weight for LRU

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and resource usage metrics for each cache entry.
metadata = {
    'access_frequency': {},  # key -> frequency
    'last_access_time': {},  # key -> last access timestamp
    'predicted_future_access_time': {},  # key -> predicted future access time
    'resource_usage': {}  # key -> resource usage metrics
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining least frequently used (LFU) and least recently used (LRU) strategies, while also considering predicted future access times and resource usage to ensure optimal load balancing and resource optimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predicted_future_access = metadata['predicted_future_access_time'].get(key, float('inf'))
        resource_usage = metadata['resource_usage'].get(key, 0)
        
        # Calculate the combined score
        score = (ALPHA * frequency) + (BETA * (cache_snapshot.access_count - last_access)) + predicted_future_access + resource_usage
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, refreshes the last access timestamp, and recalculates the predicted future access time based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Recalculate predicted future access time (simple heuristic)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + (metadata['access_frequency'][key] * 10)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the current timestamp as the last access time, and estimates the initial predicted future access time using temporal access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Initial predicted future access time (simple heuristic)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10
    metadata['resource_usage'][key] = obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates resource usage metrics and adjusts the predicted future access times for remaining entries to maintain optimal load balancing and resource optimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['resource_usage']:
        del metadata['resource_usage'][evicted_key]
    
    # Recalculate resource usage metrics for remaining entries
    for key in cache_snapshot.cache:
        metadata['resource_usage'][key] = cache_snapshot.cache[key].size
        # Adjust predicted future access times (simple heuristic)
        metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + (metadata['access_frequency'][key] * 10)