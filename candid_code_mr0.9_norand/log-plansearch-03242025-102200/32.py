# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
RECENT_SEGMENT_SIZE_RATIO = 0.5  # Ratio of the cache capacity allocated to the 'recent' segment

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'frequent' segment and a 'recent' segment. Each segment uses a clock hand to traverse its entries cyclically. Each entry in the cache has a reference bit and a segment identifier.
metadata = {
    'recent': {},
    'frequent': {},
    'recent_hand': 0,
    'frequent_hand': 0,
    'recent_keys': [],
    'frequent_keys': []
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict from the 'recent' segment using the clock algorithm. If no suitable victim is found, it then attempts to evict from the 'frequent' segment using the clock algorithm. The clock hand moves cyclically through the entries, evicting the first entry with a reference bit of 0.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    recent_keys = metadata['recent_keys']
    frequent_keys = metadata['frequent_keys']
    
    # Try to evict from the 'recent' segment
    while True:
        if len(recent_keys) == 0:
            break
        hand = metadata['recent_hand']
        key = recent_keys[hand]
        if metadata['recent'][key]['ref_bit'] == 0:
            candid_obj_key = key
            break
        else:
            metadata['recent'][key]['ref_bit'] = 0
            metadata['recent_hand'] = (hand + 1) % len(recent_keys)
    
    # If no suitable victim found in 'recent', try to evict from 'frequent'
    if candid_obj_key is None:
        while True:
            if len(frequent_keys) == 0:
                break
            hand = metadata['frequent_hand']
            key = frequent_keys[hand]
            if metadata['frequent'][key]['ref_bit'] == 0:
                candid_obj_key = key
                break
            else:
                metadata['frequent'][key]['ref_bit'] = 0
                metadata['frequent_hand'] = (hand + 1) % len(frequent_keys)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the reference bit of the accessed entry is set to 1. If the entry is in the 'recent' segment and is accessed again, it is promoted to the 'frequent' segment. The clock hand position remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in metadata['recent']:
        metadata['recent'][key]['ref_bit'] = 1
        # Promote to 'frequent' segment
        metadata['frequent'][key] = metadata['recent'].pop(key)
        metadata['frequent_keys'].append(key)
        metadata['recent_keys'].remove(key)
    elif key in metadata['frequent']:
        metadata['frequent'][key]['ref_bit'] = 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the object is placed in the 'recent' segment with its reference bit set to 1. The clock hand in the 'recent' segment advances to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['recent'][key] = {'ref_bit': 1}
    metadata['recent_keys'].append(key)
    metadata['recent_hand'] = (metadata['recent_hand'] + 1) % len(metadata['recent_keys'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the clock hand in the corresponding segment advances to the next position. If the evicted entry was in the 'frequent' segment, no further action is taken. If it was in the 'recent' segment, the policy checks if the 'frequent' segment needs rebalancing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['recent']:
        metadata['recent_keys'].remove(key)
        del metadata['recent'][key]
        metadata['recent_hand'] = metadata['recent_hand'] % len(metadata['recent_keys']) if metadata['recent_keys'] else 0
        # Check if 'frequent' segment needs rebalancing
        if len(metadata['frequent_keys']) > len(metadata['recent_keys']) * (1 / RECENT_SEGMENT_SIZE_RATIO - 1):
            # Move one item from 'frequent' to 'recent'
            hand = metadata['frequent_hand']
            move_key = metadata['frequent_keys'][hand]
            metadata['recent'][move_key] = metadata['frequent'].pop(move_key)
            metadata['recent_keys'].append(move_key)
            metadata['frequent_keys'].remove(move_key)
            metadata['frequent_hand'] = metadata['frequent_hand'] % len(metadata['frequent_keys']) if metadata['frequent_keys'] else 0
    elif key in metadata['frequent']:
        metadata['frequent_keys'].remove(key)
        del metadata['frequent'][key]
        metadata['frequent_hand'] = metadata['frequent_hand'] % len(metadata['frequent_keys']) if metadata['frequent_keys'] else 0