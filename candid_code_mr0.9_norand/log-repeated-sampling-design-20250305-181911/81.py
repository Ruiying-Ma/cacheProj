# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a two-dimensional grid where each cell contains an object and the number of accesses, as well as a timestamp of the last access. The grid represents a heatmap of access frequency and recency.
heatmap = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by finding the cell with the lowest access count and the oldest timestamp if there are ties in access count. It aims to remove the least frequently and least recently used object based on the heatmap.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_access_count = float('inf')
    oldest_timestamp = float('inf')
    
    for key, (access_count, last_access_time) in heatmap.items():
        if access_count < min_access_count or (access_count == min_access_count and last_access_time < oldest_timestamp):
            min_access_count = access_count
            oldest_timestamp = last_access_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access count for the corresponding cell is incremented by one, and the timestamp is updated to the current time to reflect recency of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    if obj.key in heatmap:
        access_count, _ = heatmap[obj.key]
        heatmap[obj.key] = (access_count + 1, cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, a new cell is added to the grid with an initial access count of one and the current timestamp to denote the time of insertion and the first access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    heatmap[obj.key] = (1, cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the corresponding cell is removed from the grid, and the grid is adjusted to reflect the removal, ensuring the overall structure remains consistent.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in heatmap:
        del heatmap[evicted_obj.key]