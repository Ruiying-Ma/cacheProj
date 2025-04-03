# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
HIGH_FREQUENCY_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a clock hand for cyclic traversal, a ghost queue for recently evicted objects, an LFU queue to track the frequency of accesses, and an LRU queue to track the recency of accesses.
clock_hand = 0
ghost_queue = deque()
lfu_queue = defaultdict(int)
lru_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the clock hand for the least recently used object. If the object has a high frequency of access (LFU), it is given a second chance and moved to the ghost queue. The clock hand then moves to the next object until a suitable victim is found.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand
    candid_obj_key = None
    cache_keys = list(cache_snapshot.cache.keys())
    cache_size = len(cache_keys)
    
    while True:
        current_key = cache_keys[clock_hand]
        if lfu_queue[current_key] > HIGH_FREQUENCY_THRESHOLD:
            ghost_queue.append((current_key, lfu_queue[current_key], cache_snapshot.access_count))
            clock_hand = (clock_hand + 1) % cache_size
        else:
            candid_obj_key = current_key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's position in the LRU queue is updated to the most recent position, and its frequency count in the LFU queue is incremented. The clock hand remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global lru_queue, lfu_queue
    lru_queue.remove(obj.key)
    lru_queue.append(obj.key)
    lfu_queue[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to the LRU queue as the most recent object and its frequency count is initialized in the LFU queue. The clock hand remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global lru_queue, lfu_queue
    lru_queue.append(obj.key)
    lfu_queue[obj.key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the object is added to the ghost queue with its frequency count and recency information. The clock hand moves to the next position in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global clock_hand, ghost_queue, lru_queue, lfu_queue
    ghost_queue.append((evicted_obj.key, lfu_queue[evicted_obj.key], cache_snapshot.access_count))
    lru_queue.remove(evicted_obj.key)
    del lfu_queue[evicted_obj.key]
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)