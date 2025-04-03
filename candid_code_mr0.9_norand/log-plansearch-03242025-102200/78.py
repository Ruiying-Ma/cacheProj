# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque

# Put tunable constant parameters below
DECAY_THRESHOLD = 5
INITIAL_DECAY_VALUE = 10
DECAY_DECREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains three main structures: a FIFO queue to track the order of insertion, an LRU queue to track the usage frequency, and a decay factor for each cache entry to periodically decrease its value over time.
fifo_queue = deque()
lru_queue = deque()
decay_values = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the FIFO queue to identify the oldest entry. If the oldest entry has a decay value below a certain threshold, it is evicted. If not, the policy then checks the LRU queue to find the least recently used entry with the lowest decay value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while fifo_queue:
        oldest_key = fifo_queue[0]
        if decay_values[oldest_key] < DECAY_THRESHOLD:
            candid_obj_key = oldest_key
            break
        fifo_queue.popleft()
    
    if candid_obj_key is None:
        min_decay = float('inf')
        for key in lru_queue:
            if decay_values[key] < min_decay:
                min_decay = decay_values[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the LRU queue to move the accessed entry to the most recently used position. The decay value of the accessed entry is reset or increased to reflect its recent use.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)
    decay_values[obj.key] = INITIAL_DECAY_VALUE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the object to the end of the FIFO queue and the most recently used position of the LRU queue. The decay value for the new object is initialized to a default starting value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    lru_queue.appendleft(obj.key)
    decay_values[obj.key] = INITIAL_DECAY_VALUE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy removes the entry from both the FIFO and LRU queues. The decay values of all remaining entries are periodically decreased to ensure that older entries do not dominate the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in fifo_queue:
        fifo_queue.remove(evicted_obj.key)
    if evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)
    if evicted_obj.key in decay_values:
        del decay_values[evicted_obj.key]
    
    for key in decay_values:
        decay_values[key] = max(0, decay_values[key] - DECAY_DECREMENT)