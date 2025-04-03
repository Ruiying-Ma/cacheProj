# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate access frequency, an LFU queue to track the least frequently used objects, and an LRU queue to track the least recently used objects.
count_bloom_filter = defaultdict(int)
lfu_queue = defaultdict(deque)
lru_queue = deque()

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
    for freq in sorted(lfu_queue.keys()):
        if lfu_queue[freq]:
            for key in lru_queue:
                if key in lfu_queue[freq]:
                    candid_obj_key = key
                    break
            if candid_obj_key:
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access count in the Count Bloom Filter, updates the position of the object in the LFU queue based on the new frequency, and moves the object to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    count_bloom_filter[key] += 1
    freq = count_bloom_filter[key]
    
    # Update LFU queue
    lfu_queue[freq - 1].remove(key)
    if not lfu_queue[freq - 1]:
        del lfu_queue[freq - 1]
    lfu_queue[freq].append(key)
    
    # Update LRU queue
    lru_queue.remove(key)
    lru_queue.appendleft(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access count in the Count Bloom Filter, places the object in the appropriate position in the LFU queue based on its initial frequency, and adds the object to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    count_bloom_filter[key] = 1
    
    # Update LFU queue
    lfu_queue[1].append(key)
    
    # Update LRU queue
    lru_queue.appendleft(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the object's entry from the LFU queue and the LRU queue, and decrements the access count in the Count Bloom Filter if applicable.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    freq = count_bloom_filter[key]
    
    # Update LFU queue
    lfu_queue[freq].remove(key)
    if not lfu_queue[freq]:
        del lfu_queue[freq]
    
    # Update LRU queue
    lru_queue.remove(key)
    
    # Update Count Bloom Filter
    del count_bloom_filter[key]