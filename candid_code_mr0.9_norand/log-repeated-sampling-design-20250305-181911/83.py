# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
THRESHOLD = 5  # Example threshold for usage frequency score

# Put the metadata specifically maintained by the policy below. The policy maintains a usage frequency score and a 'refresh count' for each object in the cache. The refresh count tracks how often an object's score has been reset due to refreshing intervals.
usage_frequency = {}
refresh_count = {}
last_access_time = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts the object with the lowest cumulative score of usage frequency and refresh count. In case of a tie, the least recently used among them is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    min_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = usage_frequency[key] + refresh_count[key]
        access_time = last_access_time[key]
        
        if score < min_score or (score == min_score and access_time < min_time):
            min_score = score
            min_time = access_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the usage frequency score of the object is incremented by one. If the score exceeds a predefined threshold, it is reset to zero and the refresh count is incremented by one.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    usage_frequency[key] += 1
    if usage_frequency[key] > THRESHOLD:
        usage_frequency[key] = 0
        refresh_count[key] += 1
    last_access_time[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Immediately after inserting a new object, it is assigned a usage frequency score of one and a refresh count of zero. All other objects remain unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    usage_frequency[key] = 1
    refresh_count[key] = 0
    last_access_time[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After an object is evicted, its metadata is removed. No other objects' metadata is altered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in usage_frequency:
        del usage_frequency[key]
    if key in refresh_count:
        del refresh_count[key]
    if key in last_access_time:
        del last_access_time[key]