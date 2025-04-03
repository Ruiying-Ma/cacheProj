# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency in the priority score
BETA = 0.3   # Weight for last access time in the priority score
GAMMA = 0.2  # Weight for predicted future access time in the priority score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and resource usage patterns. It also keeps a dynamic priority score for each cache entry based on these factors.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of each object
    'last_access_time': {},  # Dictionary to store last access time of each object
    'predicted_future_access_time': {},  # Dictionary to store predicted future access time of each object
    'priority_score': {}  # Dictionary to store dynamic priority score of each object
}

def calculate_priority_score(key):
    '''
    Calculate the priority score for a given object key.
    '''
    freq = metadata['access_frequency'].get(key, 0)
    last_time = metadata['last_access_time'].get(key, 0)
    future_time = metadata['predicted_future_access_time'].get(key, float('inf'))
    
    # Composite score calculation
    score = (ALPHA * freq) + (BETA * (1 / (last_time + 1))) + (GAMMA * (1 / (future_time + 1)))
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which includes the inverse of predicted future access time, access frequency, and resource usage. The entry with the lowest score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_priority_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the last access time and increments the access frequency for the accessed entry. It also recalculates the predicted future access time and adjusts the dynamic priority score accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update metadata
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = current_time
    # For simplicity, we assume future access time is a function of current access frequency
    metadata['predicted_future_access_time'][key] = current_time + (1 / (metadata['access_frequency'][key] + 1))
    metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, predicts the future access time based on historical data, and calculates the initial dynamic priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = current_time
    metadata['predicted_future_access_time'][key] = current_time + 1  # Initial prediction
    metadata['priority_score'][key] = calculate_priority_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy rebalances the resource usage patterns and updates the load forecasting model to improve future predictions. It also adjusts the dynamic priority scores of remaining entries to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['priority_score']:
        del metadata['priority_score'][evicted_key]
    
    # Rebalance resource usage patterns and update priority scores
    for key in cache_snapshot.cache:
        metadata['priority_score'][key] = calculate_priority_score(key)