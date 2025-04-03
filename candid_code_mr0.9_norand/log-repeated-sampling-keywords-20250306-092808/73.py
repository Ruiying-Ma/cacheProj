# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_TIME = 1.0
WEIGHT_FREQ = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a timestamp for each cache entry, a frequency counter for access, and a combined score derived from both the timestamp and frequency.
metadata = {
    'timestamps': {},  # key -> last access time
    'frequencies': {},  # key -> access frequency
    'scores': {}  # key -> combined score
}

def calculate_score(current_time, last_access_time, frequency):
    time_since_last_access = current_time - last_access_time
    return WEIGHT_TIME * time_since_last_access - WEIGHT_FREQ * frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score, which is calculated as a weighted sum of the time since last access and the frequency of access. This ensures that both infrequently accessed and old entries are considered for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        score = calculate_score(current_time, metadata['timestamps'][key], metadata['frequencies'][key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp to the current time and increments the frequency counter. The combined score is recalculated using the updated timestamp and frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    metadata['timestamps'][key] = current_time
    metadata['frequencies'][key] += 1
    metadata['scores'][key] = calculate_score(current_time, metadata['timestamps'][key], metadata['frequencies'][key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy sets the initial timestamp to the current time and initializes the frequency counter to one. The combined score is calculated based on these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    metadata['timestamps'][key] = current_time
    metadata['frequencies'][key] = 1
    metadata['scores'][key] = calculate_score(current_time, metadata['timestamps'][key], metadata['frequencies'][key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the metadata associated with the evicted entry, ensuring that the cache metadata remains consistent and up-to-date.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    del metadata['timestamps'][evicted_key]
    del metadata['frequencies'][evicted_key]
    del metadata['scores'][evicted_key]