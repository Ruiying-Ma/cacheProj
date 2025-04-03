# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10
LFU_QUEUE_SIZE_LIMIT = 20
SATURATE_COUNTER_LIMIT = 5
FIFO_TO_LFU_THRESHOLD = 3

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a FIFO queue for newly inserted objects, an LFU queue for frequently accessed objects, and a saturate counter for each object to track access frequency up to a predefined limit.
fifo_queue = deque()
lfu_queue = deque()
saturate_counters = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it then checks the LFU queue and evicts the least frequently used object. If both queues are empty, it evicts the object with the lowest saturate counter value.
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
    elif lfu_queue:
        # Find the least frequently used object in LFU queue
        min_freq = min(saturate_counters[key] for key in lfu_queue)
        for key in lfu_queue:
            if saturate_counters[key] == min_freq:
                candid_obj_key = key
                lfu_queue.remove(key)
                break
    else:
        # Find the object with the lowest saturate counter value
        min_counter = min(saturate_counters.values())
        for key, counter in saturate_counters.items():
            if counter == min_counter:
                candid_obj_key = key
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented if it hasn't reached the upper limit. If the object is in the FIFO queue and its counter exceeds a threshold, it is moved to the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if saturate_counters[key] < SATURATE_COUNTER_LIMIT:
        saturate_counters[key] += 1
    
    if key in fifo_queue and saturate_counters[key] > FIFO_TO_LFU_THRESHOLD:
        fifo_queue.remove(key)
        lfu_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue with its saturate counter initialized to 1. If the FIFO queue exceeds its size limit, the oldest object is moved to the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    saturate_counters[key] = 1
    fifo_queue.append(key)
    
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        oldest_key = fifo_queue.popleft()
        lfu_queue.append(oldest_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy checks the state of the FIFO and LFU queues. If the FIFO queue is below its size limit, it remains unchanged. If the LFU queue is below its size limit, it remains unchanged. The saturate counters of remaining objects are not altered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in saturate_counters:
        del saturate_counters[evicted_key]
    if evicted_key in fifo_queue:
        fifo_queue.remove(evicted_key)
    if evicted_key in lfu_queue:
        lfu_queue.remove(evicted_key)