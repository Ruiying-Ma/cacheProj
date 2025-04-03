# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
DECAY_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue for insertion order, an LRU queue for access order, a ghost queue for recently evicted objects, and a decay counter for each object to periodically decrease its value.
fifo_queue = deque()
lru_queue = deque()
ghost_queue = deque()
decay_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the FIFO queue for the oldest entry. If the oldest entry has a decay value below a certain threshold, it is evicted. Otherwise, the policy checks the LRU queue for the least recently used entry with a decay value below the threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Check FIFO queue first
    while fifo_queue:
        oldest_key = fifo_queue[0]
        if decay_counter[oldest_key] < DECAY_THRESHOLD:
            candid_obj_key = oldest_key
            break
        else:
            fifo_queue.popleft()
    
    # If no suitable candidate found in FIFO, check LRU queue
    if candid_obj_key is None:
        while lru_queue:
            lru_key = lru_queue[0]
            if decay_counter[lru_key] < DECAY_THRESHOLD:
                candid_obj_key = lru_key
                break
            else:
                lru_queue.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the LRU queue to move the accessed object to the most recently used position and resets its decay counter. The FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    if obj_key in lru_queue:
        lru_queue.remove(obj_key)
    lru_queue.append(obj_key)
    decay_counter[obj_key] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds it to the end of the FIFO queue, the front of the LRU queue, and initializes its decay counter. If the cache is full, the policy evicts an object first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    # If cache is full, evict an object first
    if cache_snapshot.size + obj.size > cache_snapshot.capacity:
        evicted_key = evict(cache_snapshot, obj)
        if evicted_key:
            evicted_obj = cache_snapshot.cache[evicted_key]
            update_after_evict(cache_snapshot, obj, evicted_obj)
    
    # Add the new object to the FIFO and LRU queues
    fifo_queue.append(obj_key)
    lru_queue.appendleft(obj_key)
    decay_counter[obj_key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes it from both the FIFO and LRU queues and adds it to the ghost queue. The decay counter for the evicted object is reset if it re-enters the cache from the ghost queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    if evicted_key in lru_queue:
        lru_queue.remove(evicted_key)
    ghost_queue.append(evicted_key)
    decay_counter[evicted_key] = 0