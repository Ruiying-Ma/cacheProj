# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_COUNTER_LIMIT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate access frequency, an LFU queue to track the least frequently used objects, an LRU queue to track the least recently used objects, and a saturate counter for each object to avoid aging issues.
count_bloom_filter = defaultdict(int)
lfu_queue = deque()
lru_queue = deque()
saturate_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the LFU queue for the least frequently used object. If there are ties, it then checks the LRU queue to select the least recently used object among them.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = float('inf')
    lfu_candidates = []
    
    for key in lfu_queue:
        if count_bloom_filter[key] < min_freq:
            min_freq = count_bloom_filter[key]
            lfu_candidates = [key]
        elif count_bloom_filter[key] == min_freq:
            lfu_candidates.append(key)
    
    if lfu_candidates:
        for key in lru_queue:
            if key in lfu_candidates:
                candid_obj_key = key
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the saturate counter for the object (if it hasn't reached its upper limit), updates the Count Bloom Filter to reflect the increased access frequency, moves the object to the front of the LRU queue, and adjusts its position in the LFU queue if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    
    if saturate_counter[key] < SATURATE_COUNTER_LIMIT:
        saturate_counter[key] += 1
    
    count_bloom_filter[key] += 1
    
    if key in lru_queue:
        lru_queue.remove(key)
    lru_queue.appendleft(key)
    
    if key in lfu_queue:
        lfu_queue.remove(key)
    lfu_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its saturate counter, updates the Count Bloom Filter with an initial frequency, places the object at the front of the LRU queue, and inserts it into the LFU queue based on its initial frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    
    saturate_counter[key] = 1
    count_bloom_filter[key] = 1
    
    lru_queue.appendleft(key)
    lfu_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes the object from both the LFU and LRU queues, and updates the Count Bloom Filter to reflect the removal, ensuring the metadata remains consistent.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    
    if key in lru_queue:
        lru_queue.remove(key)
    if key in lfu_queue:
        lfu_queue.remove(key)
    
    if key in count_bloom_filter:
        del count_bloom_filter[key]
    if key in saturate_counter:
        del saturate_counter[key]