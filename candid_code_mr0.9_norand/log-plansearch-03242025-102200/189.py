# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, OrderedDict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10  # Example size limit for FIFO queue
DECAY_THRESHOLD = 5  # Example threshold for decay counter

# Put the metadata specifically maintained by the policy below. The policy maintains four segments: a FIFO queue for new entries, an LRU queue for frequently accessed entries, a decay counter for each entry to periodically reduce its value, and a segmentation flag to distinguish between single-access and multi-access entries.
fifo_queue = deque()
lru_queue = OrderedDict()
decay_counters = {}
segmentation_flags = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates, prioritizing the oldest entry. If the FIFO queue is empty, it then checks the LRU queue, evicting the least recently used entry. Decay counters are used to demote entries from the LRU queue back to the FIFO queue if they have not been accessed recently.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue.popleft()
    else:
        if lru_queue:
            candid_obj_key = next(iter(lru_queue))
            lru_queue.pop(candid_obj_key)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy moves the entry to the LRU queue if it is not already there, resets its decay counter, and updates its position in the LRU queue to reflect recent access. The segmentation flag is set to indicate multi-access status.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in fifo_queue:
        fifo_queue.remove(key)
        lru_queue[key] = obj
    elif key in lru_queue:
        lru_queue.move_to_end(key)
    
    decay_counters[key] = 0
    segmentation_flags[key] = 'multi-access'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the FIFO queue, initializes its decay counter, and sets the segmentation flag to indicate single-access status. If the FIFO queue exceeds its size limit, the oldest entry is moved to the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    decay_counters[key] = 0
    segmentation_flags[key] = 'single-access'
    
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        oldest_key = fifo_queue.popleft()
        lru_queue[oldest_key] = cache_snapshot.cache[oldest_key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy removes it from its respective queue and clears its metadata. If the entry was in the FIFO queue, the next oldest entry is promoted to the LRU queue if necessary. Decay counters for remaining entries are decremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    if evicted_key in lru_queue:
        lru_queue.pop(evicted_key)
    
    if evicted_key in decay_counters:
        del decay_counters[evicted_key]
    if evicted_key in segmentation_flags:
        del segmentation_flags[evicted_key]
    
    for key in list(decay_counters.keys()):
        decay_counters[key] += 1
        if decay_counters[key] >= DECAY_THRESHOLD:
            if key in lru_queue:
                lru_queue.pop(key)
                fifo_queue.append(key)
            decay_counters[key] = 0