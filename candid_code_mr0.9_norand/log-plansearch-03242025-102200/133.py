# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 10

# Put the metadata specifically maintained by the policy below. The policy maintains three queues: FIFO, LFU, and LRU. Each cache entry has a saturate counter associated with it, which increments on access but stops increasing beyond a predefined limit.
fifo_queue = deque()
lfu_queue = defaultdict(list)
lru_queue = deque()
saturate_counters = defaultdict(int)
access_frequencies = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the FIFO queue for the oldest entry. If there is a tie, it checks the LFU queue for the least frequently used entry among the oldest. If there is still a tie, it checks the LRU queue for the least recently used entry among the least frequently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if fifo_queue:
        oldest_key = fifo_queue[0]
        min_freq = access_frequencies[oldest_key]
        lfu_candidates = [oldest_key]
        
        for key in fifo_queue:
            if access_frequencies[key] < min_freq:
                min_freq = access_frequencies[key]
                lfu_candidates = [key]
            elif access_frequencies[key] == min_freq:
                lfu_candidates.append(key)
        
        if len(lfu_candidates) == 1:
            candid_obj_key = lfu_candidates[0]
        else:
            for key in lru_queue:
                if key in lfu_candidates:
                    candid_obj_key = key
                    break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    On a cache hit, the policy increments the saturate counter for the accessed entry (up to its limit), moves the entry to the back of the FIFO queue, updates its position in the LFU queue based on the new frequency, and moves it to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if saturate_counters[key] < SATURATE_LIMIT:
        saturate_counters[key] += 1
    
    fifo_queue.remove(key)
    fifo_queue.append(key)
    
    access_frequencies[key] += 1
    lfu_queue[access_frequencies[key] - 1].remove(key)
    lfu_queue[access_frequencies[key]].append(key)
    
    lru_queue.remove(key)
    lru_queue.appendleft(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the entry to the back of the FIFO queue, inserts it into the LFU queue with an initial frequency of 1, and places it at the front of the LRU queue. The saturate counter is initialized to 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    access_frequencies[key] = 1
    lfu_queue[1].append(key)
    lru_queue.appendleft(key)
    saturate_counters[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from the FIFO, LFU, and LRU queues. It also resets the saturate counter associated with the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    fifo_queue.remove(key)
    lfu_queue[access_frequencies[key]].remove(key)
    lru_queue.remove(key)
    del saturate_counters[key]
    del access_frequencies[key]