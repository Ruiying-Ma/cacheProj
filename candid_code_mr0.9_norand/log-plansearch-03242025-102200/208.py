# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque

# Put tunable constant parameters below
INITIAL_DECAY_COUNTER = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recently accessed' segment and a 'frequently accessed' segment. Each segment uses a clock algorithm for traversal and a decay counter for aging. Additionally, an LRU queue is maintained within each segment to track the least recently used items.
recently_accessed = deque()
frequently_accessed = deque()
decay_counters = {}
clock_hand_recent = 0
clock_hand_frequent = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict from the 'recently accessed' segment using the clock algorithm. If no suitable victim is found, it then attempts to evict from the 'frequently accessed' segment. The decay counters are checked to ensure that older items are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand_recent, clock_hand_frequent
    candid_obj_key = None

    # Try to evict from recently accessed segment
    while recently_accessed:
        key = recently_accessed[clock_hand_recent]
        if decay_counters[key] <= 0:
            candid_obj_key = key
            break
        decay_counters[key] -= 1
        clock_hand_recent = (clock_hand_recent + 1) % len(recently_accessed)

    # If no suitable victim found, try to evict from frequently accessed segment
    if candid_obj_key is None:
        while frequently_accessed:
            key = frequently_accessed[clock_hand_frequent]
            if decay_counters[key] <= 0:
                candid_obj_key = key
                break
            decay_counters[key] -= 1
            clock_hand_frequent = (clock_hand_frequent + 1) % len(frequently_accessed)

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the item's decay counter is reset, and it is moved to the 'frequently accessed' segment if it is not already there. The clock hand is advanced, and the LRU queue is updated to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global clock_hand_frequent
    key = obj.key

    # Reset decay counter
    decay_counters[key] = INITIAL_DECAY_COUNTER

    # Move to frequently accessed segment if not already there
    if key in recently_accessed:
        recently_accessed.remove(key)
        frequently_accessed.append(key)

    # Advance clock hand
    clock_hand_frequent = (clock_hand_frequent + 1) % len(frequently_accessed)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently accessed' segment with an initial decay counter value. The clock hand is advanced, and the LRU queue is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global clock_hand_recent
    key = obj.key

    # Place in recently accessed segment with initial decay counter
    recently_accessed.append(key)
    decay_counters[key] = INITIAL_DECAY_COUNTER

    # Advance clock hand
    clock_hand_recent = (clock_hand_recent + 1) % len(recently_accessed)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the clock hand is advanced, and the decay counters for all items are periodically decremented. The LRU queue is updated to remove the evicted object, and the segments are rebalanced if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand_recent, clock_hand_frequent
    evicted_key = evicted_obj.key

    # Remove evicted object from LRU queue and decay counters
    if evicted_key in recently_accessed:
        recently_accessed.remove(evicted_key)
    if evicted_key in frequently_accessed:
        frequently_accessed.remove(evicted_key)
    if evicted_key in decay_counters:
        del decay_counters[evicted_key]

    # Advance clock hands
    clock_hand_recent = (clock_hand_recent + 1) % len(recently_accessed) if recently_accessed else 0
    clock_hand_frequent = (clock_hand_frequent + 1) % len(frequently_accessed) if frequently_accessed else 0

    # Periodically decrement decay counters
    for key in decay_counters:
        decay_counters[key] -= 1