# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PATTERN_HISTORY_SIZE = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a circular buffer to track the order of cache accesses, a counter for each cache line to record access frequency, and a pattern history table to capture recent access patterns.
circular_buffer = []
access_frequency = {}
pattern_history_table = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the lowest access frequency within the circular buffer, while also considering the data locality by checking the pattern history table for recent access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = float('inf')
    for key in circular_buffer:
        if access_frequency[key] < min_freq:
            min_freq = access_frequency[key]
            candid_obj_key = key
        elif access_frequency[key] == min_freq:
            if key not in pattern_history_table or len(pattern_history_table[key]) < PATTERN_HISTORY_SIZE:
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency counter for the accessed cache line, updates the circular buffer to move the accessed line to the most recent position, and records the access pattern in the pattern history table.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    circular_buffer.remove(key)
    circular_buffer.append(key)
    if key not in pattern_history_table:
        pattern_history_table[key] = []
    pattern_history_table[key].append(cache_snapshot.access_count)
    if len(pattern_history_table[key]) > PATTERN_HISTORY_SIZE:
        pattern_history_table[key].pop(0)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency counter to one, places it at the most recent position in the circular buffer, and updates the pattern history table to reflect the new access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    circular_buffer.append(key)
    if key not in pattern_history_table:
        pattern_history_table[key] = []
    pattern_history_table[key].append(cache_snapshot.access_count)
    if len(pattern_history_table[key]) > PATTERN_HISTORY_SIZE:
        pattern_history_table[key].pop(0)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy resets the access frequency counter of the evicted cache line, removes it from the circular buffer, and updates the pattern history table to remove the evicted line's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    del access_frequency[key]
    circular_buffer.remove(key)
    if key in pattern_history_table:
        del pattern_history_table[key]