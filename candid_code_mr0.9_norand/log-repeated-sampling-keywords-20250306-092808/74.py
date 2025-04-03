# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PREFETCH_SCORE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache line including access frequency, last access timestamp, prefetch score, and dirty bit status.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score derived from the least access frequency, oldest access timestamp, lowest prefetch score, and clean status (non-dirty).
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (meta['access_frequency'] + 1) * (cache_snapshot.access_count - meta['last_access_timestamp']) * (meta['prefetch_score'] + 1)
        if meta['dirty']:
            score *= 2  # Penalize dirty objects
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the prefetch score is adjusted based on the temporal locality of the access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in metadata:
        metadata[key]['access_frequency'] += 1
        metadata[key]['last_access_timestamp'] = cache_snapshot.access_count
        metadata[key]['prefetch_score'] *= PREFETCH_SCORE_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access timestamp is set to the current time, the prefetch score is calculated based on the likelihood of future accesses, and the dirty bit is set to false.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'prefetch_score': 1.0,  # Initial prefetch score
        'dirty': False
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted line is cleared. If the evicted line was dirty, the write-back policy ensures the data is written to the main memory before clearing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if metadata[evicted_key]['dirty']:
        # Simulate write-back to main memory
        pass
    del metadata[evicted_key]