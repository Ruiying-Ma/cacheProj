# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SATURATE_LIMIT = 5
THRESHOLD = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recently accessed' segment and a 'frequently accessed' segment. Each segment uses a clock algorithm for traversal and eviction. Each cache entry has a saturate counter to track access frequency, and an LFU queue is maintained for the 'frequently accessed' segment.
metadata = {
    'recently_accessed': {},
    'frequently_accessed': {},
    'recently_accessed_hand': 0,
    'frequently_accessed_hand': 0,
    'lfu_queue': [],
    'saturate_counters': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict from the 'recently accessed' segment using the clock algorithm. If no suitable victim is found, it then evicts from the 'frequently accessed' segment using the clock algorithm, prioritizing entries with the lowest saturate counter values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while True:
        if metadata['recently_accessed']:
            keys = list(metadata['recently_accessed'].keys())
            key = keys[metadata['recently_accessed_hand'] % len(keys)]
            metadata['recently_accessed_hand'] += 1
            if key in cache_snapshot.cache:
                candid_obj_key = key
                break
        elif metadata['frequently_accessed']:
            keys = list(metadata['frequently_accessed'].keys())
            key = keys[metadata['frequently_accessed_hand'] % len(keys)]
            metadata['frequently_accessed_hand'] += 1
            if key in cache_snapshot.cache:
                candid_obj_key = key
                break
        else:
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the saturate counter for the accessed entry is incremented up to its predefined limit. If the entry is in the 'recently accessed' segment and its counter reaches a threshold, it is moved to the 'frequently accessed' segment and added to the LFU queue. The clock hand is advanced to the next entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in metadata['saturate_counters']:
        metadata['saturate_counters'][key] = min(SATURATE_LIMIT, metadata['saturate_counters'][key] + 1)
    else:
        metadata['saturate_counters'][key] = 1
    
    if key in metadata['recently_accessed']:
        if metadata['saturate_counters'][key] >= THRESHOLD:
            metadata['frequently_accessed'][key] = metadata['recently_accessed'].pop(key)
            metadata['lfu_queue'].append(key)
    
    metadata['recently_accessed_hand'] = (metadata['recently_accessed_hand'] + 1) % len(metadata['recently_accessed'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently accessed' segment with its saturate counter initialized to 1. The clock hand in the 'recently accessed' segment is advanced to the next entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['recently_accessed'][key] = obj
    metadata['saturate_counters'][key] = 1
    metadata['recently_accessed_hand'] = (metadata['recently_accessed_hand'] + 1) % len(metadata['recently_accessed'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the clock hand in the respective segment (either 'recently accessed' or 'frequently accessed') is advanced to the next entry. If the evicted entry was in the 'frequently accessed' segment, it is also removed from the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in metadata['recently_accessed']:
        metadata['recently_accessed'].pop(key)
        metadata['recently_accessed_hand'] = (metadata['recently_accessed_hand'] + 1) % len(metadata['recently_accessed'])
    elif key in metadata['frequently_accessed']:
        metadata['frequently_accessed'].pop(key)
        metadata['lfu_queue'].remove(key)
        metadata['frequently_accessed_hand'] = (metadata['frequently_accessed_hand'] + 1) % len(metadata['frequently_accessed'])
    
    if key in metadata['saturate_counters']:
        metadata['saturate_counters'].pop(key)