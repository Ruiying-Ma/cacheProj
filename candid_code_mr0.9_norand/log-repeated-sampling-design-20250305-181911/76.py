# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. Maintains a timestamp for each cache object recording its last access time and a counter that increments every time the object is accessed.
last_access_time = {}
access_counter = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    Chooses the eviction victim based on a combination of the least recently used and the least frequently used strategies, selecting the object with the earliest last access time among those with the lowest access counters.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_access_count = float('inf')
    min_access_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if access_counter[key] < min_access_count:
            min_access_count = access_counter[key]
            min_access_time = last_access_time[key]
            candid_obj_key = key
        elif access_counter[key] == min_access_count:
            if last_access_time[key] < min_access_time:
                min_access_time = last_access_time[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Updates the last access timestamp to the current time and increments the access counter of the hit object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    last_access_time[obj.key] = current_time
    access_counter[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Sets the last access timestamp to the current time and initializes the access counter to 1 for the newly inserted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    last_access_time[obj.key] = current_time
    access_counter[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    No additional updates are required for the metadata after evicting a victim, as its metadata is inherently removed from the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del last_access_time[evicted_obj.key]
    del access_counter[evicted_obj.key]