# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency of access
GAMMA = 0.2  # Weight for locality score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, recency of access, and a locality score that measures the spatial and temporal locality of the data.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score derived from the inverse of access frequency, recency of access, and the locality score. The entry with the lowest combined score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata[key]['frequency']
        recency = metadata[key]['recency']
        locality = metadata[key]['locality']
        
        score = (ALPHA / freq) + (BETA * (cache_snapshot.access_count - recency)) + (GAMMA * locality)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the recency of access is updated to the current time, and the locality score is adjusted based on the proximity of the current access to previous accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['frequency'] += 1
    metadata[key]['recency'] = cache_snapshot.access_count
    # Adjust locality score based on proximity to previous accesses
    metadata[key]['locality'] = 1 / (cache_snapshot.access_count - metadata[key]['last_access'])
    metadata[key]['last_access'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the recency of access is set to the current time, and the locality score is calculated based on the initial access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'frequency': 1,
        'recency': cache_snapshot.access_count,
        'locality': 1,  # Initial locality score
        'last_access': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted entry is removed from the cache, and the combined scores for remaining entries are recalculated to ensure accurate future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalculate combined scores for remaining entries
    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata[key]['frequency']
        recency = metadata[key]['recency']
        locality = metadata[key]['locality']
        
        metadata[key]['combined_score'] = (ALPHA / freq) + (BETA * (cache_snapshot.access_count - recency)) + (GAMMA * locality)