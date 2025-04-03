# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
AGE_WEIGHT = 1
HIT_COUNT_WEIGHT = 1
QUEUE_DEPTH_WEIGHT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including hit count, queue depth, and age. Additionally, it tracks the overall cache hit rate and maintains a parallel cache for frequently accessed items.
metadata = {}
parallel_cache = {}
total_hits = 0
total_accesses = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that considers the age of the entry, its hit count, and the queue depth. Entries with the lowest score are evicted first. The parallel cache is checked first for potential evictions before the main cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    # Check parallel cache first
    for key, entry in parallel_cache.items():
        age = cache_snapshot.access_count - entry['last_access']
        hit_count = entry['hit_count']
        queue_depth = entry['queue_depth']
        score = (AGE_WEIGHT * age) - (HIT_COUNT_WEIGHT * hit_count) + (QUEUE_DEPTH_WEIGHT * queue_depth)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    # Check main cache if no candidate found in parallel cache
    if candid_obj_key is None:
        for key, entry in metadata.items():
            age = cache_snapshot.access_count - entry['last_access']
            hit_count = entry['hit_count']
            queue_depth = entry['queue_depth']
            score = (AGE_WEIGHT * age) - (HIT_COUNT_WEIGHT * hit_count) + (QUEUE_DEPTH_WEIGHT * queue_depth)
            if score < min_score:
                min_score = score
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the hit count for the accessed entry is incremented, its age is reset, and the queue depth is updated to reflect its new position. The overall cache hit rate is recalculated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global total_hits, total_accesses
    total_hits += 1
    total_accesses += 1
    
    if obj.key in metadata:
        metadata[obj.key]['hit_count'] += 1
        metadata[obj.key]['last_access'] = cache_snapshot.access_count
        metadata[obj.key]['queue_depth'] = len(metadata)
    
    if obj.key in parallel_cache:
        parallel_cache[obj.key]['hit_count'] += 1
        parallel_cache[obj.key]['last_access'] = cache_snapshot.access_count
        parallel_cache[obj.key]['queue_depth'] = len(parallel_cache)
    
    # Update overall cache hit rate
    cache_hit_rate = total_hits / total_accesses

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its hit count to 1, sets its age to 0, and places it at the appropriate position in the queue. The overall cache hit rate is updated to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global total_accesses
    total_accesses += 1
    
    metadata[obj.key] = {
        'hit_count': 1,
        'last_access': cache_snapshot.access_count,
        'queue_depth': len(metadata)
    }
    
    # Update overall cache hit rate
    cache_hit_rate = total_hits / total_accesses

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy removes its metadata, adjusts the queue depth for remaining entries, and recalculates the overall cache hit rate. If the evicted entry was in the parallel cache, it is also removed from there.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global total_accesses
    total_accesses += 1
    
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    if evicted_obj.key in parallel_cache:
        del parallel_cache[evicted_obj.key]
    
    # Adjust queue depth for remaining entries
    for key, entry in metadata.items():
        entry['queue_depth'] = len(metadata)
    
    for key, entry in parallel_cache.items():
        entry['queue_depth'] = len(parallel_cache)
    
    # Update overall cache hit rate
    cache_hit_rate = total_hits / total_accesses