# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate access frequency, a decay factor to periodically reduce frequency counts, an LFU queue to track the least frequently used objects, and an LRU queue to track the least recently used objects.
count_bloom_filter = defaultdict(int)
lfu_queue = deque()
lru_queue = deque()
key_to_lfu_node = {}
key_to_lru_node = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the LFU queue for the least frequently used object. If there is a tie, it then checks the LRU queue to select the least recently used object among those tied in frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if lfu_queue:
        min_freq = count_bloom_filter[lfu_queue[0]]
        candidates = [key for key in lfu_queue if count_bloom_filter[key] == min_freq]
        if candidates:
            candid_obj_key = candidates[0]
            for key in lru_queue:
                if key in candidates:
                    candid_obj_key = key
                    break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access count in the Count Bloom Filter for the object, updates its position in the LFU queue based on the new frequency, and moves the object to the front of the LRU queue to mark it as recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    lfu_queue.remove(obj.key)
    lfu_queue.append(obj.key)
    lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access count in the Count Bloom Filter, places the object in the appropriate position in the LFU queue based on its initial frequency, and adds it to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] = 1
    lfu_queue.append(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes the object's entry from the LFU queue and the LRU queue, and decrements its count in the Count Bloom Filter. The decay process is also applied to all entries in the Count Bloom Filter to ensure older values do not dominate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in count_bloom_filter:
        del count_bloom_filter[evicted_obj.key]
    if evicted_obj.key in lfu_queue:
        lfu_queue.remove(evicted_obj.key)
    if evicted_obj.key in lru_queue:
        lru_queue.remove(evicted_obj.key)
    
    # Apply decay to all entries in the Count Bloom Filter
    for key in count_bloom_filter:
        count_bloom_filter[key] = int(count_bloom_filter[key] * DECAY_FACTOR)