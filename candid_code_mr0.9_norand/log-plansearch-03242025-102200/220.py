# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
FIFO_QUEUE_SIZE_LIMIT = 10
GHOST_QUEUE_SIZE_LIMIT = 10
ACCESS_THRESHOLD = 2

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a FIFO queue for objects accessed only once and a main cache for frequently accessed objects. A Count Bloom Filter tracks the access frequency of each object. A ghost queue records recently evicted objects.

fifo_queue = deque()
main_cache = {}
count_bloom_filter = defaultdict(int)
ghost_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it evicts the least recently used object from the main cache. The evicted object is added to the ghost queue.
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
        # Evict the least recently used object from the main cache
        candid_obj_key = min(main_cache, key=lambda k: main_cache[k].last_access_time)
        del main_cache[candid_obj_key]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Count Bloom Filter is updated to increment the access count of the object. If the object is in the FIFO queue and its access count exceeds a threshold, it is promoted to the main cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    if obj.key in fifo_queue and count_bloom_filter[obj.key] > ACCESS_THRESHOLD:
        fifo_queue.remove(obj.key)
        main_cache[obj.key] = obj

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the FIFO queue. The Count Bloom Filter is updated to initialize the access count of the new object. If the FIFO queue exceeds its size limit, the oldest object is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    count_bloom_filter[obj.key] = 1
    if len(fifo_queue) > FIFO_QUEUE_SIZE_LIMIT:
        evicted_key = fifo_queue.popleft()
        ghost_queue.append(evicted_key)
        if len(ghost_queue) > GHOST_QUEUE_SIZE_LIMIT:
            ghost_queue.popleft()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the Count Bloom Filter is updated to decrement the access count. The evicted object is added to the ghost queue. If the ghost queue exceeds its size limit, the oldest object in the ghost queue is removed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[evicted_obj.key] -= 1
    ghost_queue.append(evicted_obj.key)
    if len(ghost_queue) > GHOST_QUEUE_SIZE_LIMIT:
        ghost_queue.popleft()