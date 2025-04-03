# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASE_MAGNETISM = 1.0
MAGNETISM_INCREMENT = 0.1
DECAY_FACTOR = 0.99

# Put the metadata specifically maintained by the policy below. Maintains a record of each cache entry's 'magnetism' score and the total number of accesses and time-based 'entropy' per entry.
metadata = {
    'magnetism': {},  # key -> magnetism score
    'entropy': {}     # key -> last access time
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest magnetism score modified by a decaying entropy factor, which emphasizes recency along with frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        magnetism = metadata['magnetism'].get(key, BASE_MAGNETISM)
        entropy = metadata['entropy'].get(key, cache_snapshot.access_count)
        score = magnetism * (DECAY_FACTOR ** (cache_snapshot.access_count - entropy))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the entry's magnetism score is increased by a small constant, and its entropy is updated to reflect the current time, giving a slight preference to recently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['magnetism'][key] = metadata['magnetism'].get(key, BASE_MAGNETISM) + MAGNETISM_INCREMENT
    metadata['entropy'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new item, it is initialized with a base magnetism score and entropy set to the current time, ensuring that new entries start with a baseline advantage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['magnetism'][key] = BASE_MAGNETISM
    metadata['entropy'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Once an entry is evicted, entropy and magnetism scores of all other entries are decayed slightly to re-balance their relative standings and emphasize remaining useful entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['magnetism']:
        del metadata['magnetism'][evicted_key]
    if evicted_key in metadata['entropy']:
        del metadata['entropy'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['magnetism'][key] *= DECAY_FACTOR
        metadata['entropy'][key] = cache_snapshot.access_count