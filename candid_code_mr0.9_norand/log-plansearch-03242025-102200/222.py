# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 10
FIFO_QUEUE_SIZE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a FIFO queue for recently inserted objects and a main cache for frequently accessed objects. It also uses a Count Bloom Filter to approximate access frequency and a saturate counter for each object to track access counts up to a predefined limit.
fifo_queue = deque()
main_cache = {}
saturate_counter = defaultdict(int)
count_bloom_filter = set()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the FIFO queue for eviction candidates. If the FIFO queue is empty, it then looks at the main cache and evicts the object with the lowest saturate counter value. If there are ties, it uses the FIFO order within the main cache segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        candid_obj_key = fifo_queue.popleft().key
    else:
        min_counter = float('inf')
        for key, cached_obj in main_cache.items():
            if saturate_counter[key] < min_counter:
                min_counter = saturate_counter[key]
                candid_obj_key = key
            elif saturate_counter[key] == min_counter:
                if cached_obj in main_cache:
                    candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the saturate counter for the accessed object up to its predefined limit. It also updates the Count Bloom Filter to reflect the increased access frequency. If the object is in the FIFO queue, it is moved to the main cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if saturate_counter[obj.key] < SATURATE_LIMIT:
        saturate_counter[obj.key] += 1
    count_bloom_filter.add(obj.key)
    if obj in fifo_queue:
        fifo_queue.remove(obj)
        main_cache[obj.key] = obj

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the FIFO queue and initializes its saturate counter. The Count Bloom Filter is updated to reflect the new object's presence. If the FIFO queue is full, the oldest object is moved to the main cache or evicted if the main cache is also full.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj)
    saturate_counter[obj.key] = 0
    count_bloom_filter.add(obj.key)
    if len(fifo_queue) > FIFO_QUEUE_SIZE:
        oldest_obj = fifo_queue.popleft()
        if cache_snapshot.size + oldest_obj.size <= cache_snapshot.capacity:
            main_cache[oldest_obj.key] = oldest_obj
        else:
            evict(cache_snapshot, oldest_obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes its entry from the Count Bloom Filter and resets its saturate counter. If the evicted object was in the FIFO queue, the next oldest object in the FIFO queue is promoted to the main cache if space allows.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter.discard(evicted_obj.key)
    saturate_counter[evicted_obj.key] = 0
    if evicted_obj in fifo_queue:
        fifo_queue.remove(evicted_obj)
        if fifo_queue and cache_snapshot.size + fifo_queue[0].size <= cache_snapshot.capacity:
            oldest_obj = fifo_queue.popleft()
            main_cache[oldest_obj.key] = oldest_obj