# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_RELEVANCE_SCORE = 10
RELEVANCE_INCREMENT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, which includes a relevance score, usage count, and last access timestamp. Each entry also has a 'neighbor' reference pointing to another cache entry, forming a linked network.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest relevance score. If multiple entries have the same relevance score, it picks the one with the lowest usage count. If a tie persists, it evicts the oldest entry based on the last access timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_relevance = float('inf')
    min_usage = float('inf')
    oldest_timestamp = float('inf')
    
    for key, cache_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        if (meta['relevance_score'] < min_relevance or
            (meta['relevance_score'] == min_relevance and meta['usage_count'] < min_usage) or
            (meta['relevance_score'] == min_relevance and meta['usage_count'] == min_usage and meta['last_access'] < oldest_timestamp)):
            min_relevance = meta['relevance_score']
            min_usage = meta['usage_count']
            oldest_timestamp = meta['last_access']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the relevance score of the accessed entry is increased by a predetermined amount, the usage count is incremented by one, and the last access timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    meta = metadata[obj.key]
    meta['relevance_score'] += RELEVANCE_INCREMENT
    meta['usage_count'] += 1
    meta['last_access'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, the policy sets an initial relevance score, initializes the usage count to one, sets the current time as the last access timestamp, and assigns a 'neighbor' reference to an existing entry in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if cache_snapshot.cache:
        neighbor_key = next(iter(cache_snapshot.cache))
    else:
        neighbor_key = None
    
    metadata[obj.key] = {
        'relevance_score': INITIAL_RELEVANCE_SCORE,
        'usage_count': 1,
        'last_access': cache_snapshot.access_count,
        'neighbor': neighbor_key
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy reassigns the 'neighbor' reference of the remaining entries that were pointing to the evicted entry, ensuring the network remains intact. It also recalculates relevance scores for a subset of entries based on their new network positions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    for key, meta in metadata.items():
        if meta['neighbor'] == evicted_key:
            meta['neighbor'] = next(iter(cache_snapshot.cache)) if cache_snapshot.cache else None
    
    del metadata[evicted_key]