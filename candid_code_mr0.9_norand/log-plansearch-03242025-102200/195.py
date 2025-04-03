# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue for insertion order, an LRU queue for access order, a ghost queue for recently evicted objects, and a saturate counter for each object to track its access frequency up to a predefined limit.
fifo_queue = deque()
lru_queue = deque()
ghost_queue = deque()
saturate_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the FIFO queue, ensuring the oldest inserted object is evicted first. If the object has a high saturate counter value, it is moved to the ghost queue instead of being completely discarded.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue[0]
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object is moved to the front of the LRU queue, and its saturate counter is incremented if it hasn't reached the predefined limit. The FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in lru_queue:
        lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)
    if saturate_counter[obj.key] < SATURATE_LIMIT:
        saturate_counter[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to the back of the FIFO queue and the front of the LRU queue with its saturate counter initialized to zero. If the cache is full, the oldest object in the FIFO queue is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    if cache_snapshot.size + obj.size > cache_snapshot.capacity:
        evicted_key = evict(cache_snapshot, obj)
        if evicted_key:
            evicted_obj = cache_snapshot.cache[evicted_key]
            update_after_evict(cache_snapshot, obj, evicted_obj)
    
    fifo_queue.append(obj.key)
    lru_queue.appendleft(obj.key)
    saturate_counter[obj.key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, it is added to the ghost queue if its saturate counter is high, otherwise, it is discarded. The FIFO queue is updated by removing the evicted object, and the LRU queue is updated if the object was present.
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
        lru_queue.remove(evicted_key)
    
    if saturate_counter[evicted_key] >= SATURATE_LIMIT:
        ghost_queue.append(evicted_key)
    del saturate_counter[evicted_key]