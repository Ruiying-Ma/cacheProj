# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a chronological list of access timestamps for each block, a counter for the number of times each block has been accessed, and a list of access intervals representing the time difference between consecutive accesses for each block.
access_timestamps = {}
access_counters = {}
access_intervals = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts the block with the highest average access interval. If there's a tie, it will evict the one with the oldest last access timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_avg_interval = -1
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if access_counters[key] > 1:
            avg_interval = sum(access_intervals[key]) / (access_counters[key] - 1)
        else:
            avg_interval = float('inf')
        
        last_access_time = access_timestamps[key][-1]
        
        if (avg_interval > max_avg_interval) or (avg_interval == max_avg_interval and last_access_time < oldest_timestamp):
            max_avg_interval = avg_interval
            oldest_timestamp = last_access_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the current time in the access timestamps list, increments the access counter for the block, and updates the access intervals list by adding the time difference between the current and previous access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    if key in access_timestamps:
        last_access_time = access_timestamps[key][-1]
        access_timestamps[key].append(current_time)
        access_counters[key] += 1
        access_intervals[key].append(current_time - last_access_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access timestamps with the current time, sets the access counter to one, and starts the access intervals list as empty.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    access_timestamps[key] = [current_time]
    access_counters[key] = 1
    access_intervals[key] = []

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a block, the policy removes all metadata associated with that block, including access timestamps, access counter, and access intervals.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    
    if key in access_timestamps:
        del access_timestamps[key]
    if key in access_counters:
        del access_counters[key]
    if key in access_intervals:
        del access_intervals[key]