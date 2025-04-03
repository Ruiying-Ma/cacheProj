# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
TIME_WINDOWS = [5, 10, 15]  # Example time windows in minutes

# Put the metadata specifically maintained by the policy below. The policy maintains a 'heatmap' that tracks access frequencies in specific time windows for each cache entry, and an 'age' indicator which tracks the length of time each entry has been in the cache. The heatmap is a list of access counts for rolling time windows (e.g., last 5 minutes, last 10 minutes), and age is a simple counter.
metadata = {
    'heatmaps': {},  # key: obj.key, value: list of access counts for each time window
    'ages': {}       # key: obj.key, value: age counter
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses to evict the cache entry that has the lowest 'heat' in the most recent time window, adjusted based on its age. An entry with low access frequency in the recent window and higher age is preferred for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_heat = float('inf')
    max_age = -1

    for key, cached_obj in cache_snapshot.cache.items():
        heat = metadata['heatmaps'][key][0]  # Most recent time window heat
        age = metadata['ages'][key]
        if heat < min_heat or (heat == min_heat and age > max_age):
            min_heat = heat
            max_age = age
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    When a cache hit occurs, the heatmap for the accessed entry updates its relevant time window frequency by incrementing the count. The age indicator for this entry is reset or reduced to reflect its recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['heatmaps'][key][0] += 1  # Increment the most recent time window count
    metadata['ages'][key] = 0  # Reset age to 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon insertion of a new object, a new heatmap with zero counts for all time windows and an age counter starting at zero is created for the entry. The heatmaps of other entries are adjusted to ensure proper shifting of their time windows.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['heatmaps'][key] = [0] * len(TIME_WINDOWS)  # Initialize heatmap with zeros
    metadata['ages'][key] = 0  # Initialize age to 0

    # Increment age for all other entries
    for k in metadata['ages']:
        if k != key:
            metadata['ages'][k] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the heatmap and age counter of the evicted entry are removed from the metadata store. Remaining entries' metadata is re-evaluated to account for their adjusted positions in terms of their age ranking.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['heatmaps'][evicted_key]
    del metadata['ages'][evicted_key]

    # Increment age for all remaining entries
    for k in metadata['ages']:
        metadata['ages'][k] += 1