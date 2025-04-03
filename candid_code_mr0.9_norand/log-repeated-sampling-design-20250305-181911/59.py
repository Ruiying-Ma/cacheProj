# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_DYNAMIC_THRESHOLD = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a hit counter for each cache entry, a timestamp of the last access for each entry, and a dynamic threshold that adapts based on overall cache behavior.
hit_counters = {}
last_access_timestamps = {}
dynamic_threshold = INITIAL_DYNAMIC_THRESHOLD

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on entries that have hit counters below the dynamic threshold. Among these, the entry with the oldest timestamp is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if hit_counters[key] < dynamic_threshold:
            if last_access_timestamps[key] < oldest_timestamp:
                oldest_timestamp = last_access_timestamps[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the hit counter for the corresponding entry is incremented by one, and the last access timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    hit_counters[obj.key] += 1
    last_access_timestamps[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    When a new object is inserted into the cache, it is assigned a hit counter of zero and a current timestamp. The dynamic threshold is recalculated based on the average hit counters and access patterns of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    hit_counters[obj.key] = 0
    last_access_timestamps[obj.key] = cache_snapshot.access_count
    recalculate_dynamic_threshold(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the dynamic threshold is adjusted if necessary to ensure a balance between frequently and infrequently accessed items, promoting better cache performance and adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del hit_counters[evicted_obj.key]
    del last_access_timestamps[evicted_obj.key]
    recalculate_dynamic_threshold(cache_snapshot)

def recalculate_dynamic_threshold(cache_snapshot):
    '''
    Recalculate the dynamic threshold based on the average hit counters and access patterns of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
    - Return: `None`
    '''
    if len(hit_counters) == 0:
        return
    
    average_hits = sum(hit_counters.values()) / len(hit_counters)
    global dynamic_threshold
    dynamic_threshold = max(1, int(average_hits))