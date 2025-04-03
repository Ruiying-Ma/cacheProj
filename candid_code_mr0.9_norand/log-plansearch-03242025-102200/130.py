# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate access frequency, a FIFO queue to track insertion order, an LFU queue to track access frequency, and an LRU queue to track recency of access.
fifo_queue = deque()  # FIFO queue to track insertion order
lfu_queue = defaultdict(int)  # LFU queue to track access frequency
lru_queue = deque()  # LRU queue to track recency of access
count_bloom_filter = defaultdict(int)  # Count Bloom Filter to approximate access frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the FIFO queue for the oldest item. If multiple items have the same age, it then checks the LFU queue to find the least frequently used among them. If there is still a tie, it finally checks the LRU queue to find the least recently used item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Step 1: Check FIFO queue for the oldest item
    oldest_key = fifo_queue[0]
    oldest_items = [oldest_key]
    oldest_age = cache_snapshot.access_count - count_bloom_filter[oldest_key]

    for key in fifo_queue:
        age = cache_snapshot.access_count - count_bloom_filter[key]
        if age > oldest_age:
            oldest_items = [key]
            oldest_age = age
        elif age == oldest_age:
            oldest_items.append(key)

    # Step 2: Check LFU queue for the least frequently used among the oldest items
    if len(oldest_items) > 1:
        min_freq = min(lfu_queue[key] for key in oldest_items)
        least_frequent_items = [key for key in oldest_items if lfu_queue[key] == min_freq]
    else:
        least_frequent_items = oldest_items

    # Step 3: Check LRU queue for the least recently used among the least frequently used items
    if len(least_frequent_items) > 1:
        for key in lru_queue:
            if key in least_frequent_items:
                candid_obj_key = key
                break
    else:
        candid_obj_key = least_frequent_items[0]

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Count Bloom Filter is updated to increment the access frequency of the object. The object is moved to the front of the LRU queue to mark it as recently used. The LFU queue is updated to reflect the new frequency count.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    count_bloom_filter[key] += 1
    lfu_queue[key] += 1

    if key in lru_queue:
        lru_queue.remove(key)
    lru_queue.appendleft(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Count Bloom Filter is updated to initialize the access frequency. The object is added to the back of the FIFO queue, the LFU queue is updated to include the new object with its initial frequency, and the object is added to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    count_bloom_filter[key] = 1
    fifo_queue.append(key)
    lfu_queue[key] = 1
    lru_queue.appendleft(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the Count Bloom Filter is updated to remove the object's frequency count. The object is removed from the FIFO queue, the LFU queue is updated to remove the object, and the object is removed from the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    del count_bloom_filter[key]
    fifo_queue.remove(key)
    del lfu_queue[key]
    lru_queue.remove(key)