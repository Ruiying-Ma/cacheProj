# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a clock hand pointer, an LFU queue with saturate counters, an LRU queue, and a mapping of cache entries to their respective counters and positions in the queues.
clock_hand = 0
lfu_queue = defaultdict(deque)  # Maps frequency to a deque of objects with that frequency
lru_queue = deque()  # Stores objects in the order of their recent usage
object_metadata = {}  # Maps object key to (frequency, lru_position)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the LFU queue for the least frequently used item. If there are ties, it uses the LRU queue to select the least recently used item among them. The clock hand is then advanced to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    global clock_hand

    # Find the minimum frequency in the LFU queue
    min_freq = min(lfu_queue.keys())
    # Get the least recently used object among those with the minimum frequency
    for key in lru_queue:
        if object_metadata[key][0] == min_freq:
            candid_obj_key = key
            break

    # Advance the clock hand
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the saturate counter for the accessed item, updates its position in the LFU queue to reflect its new frequency, and moves it to the front of the LRU queue to mark it as recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    freq, _ = object_metadata[key]

    # Increment the frequency
    new_freq = freq + 1
    object_metadata[key] = (new_freq, 0)

    # Update LFU queue
    lfu_queue[freq].remove(key)
    if not lfu_queue[freq]:
        del lfu_queue[freq]
    lfu_queue[new_freq].append(key)

    # Update LRU queue
    lru_queue.remove(key)
    lru_queue.appendleft(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its saturate counter to 1, places it in the LFU queue based on its frequency, and adds it to the front of the LRU queue. The clock hand is then advanced to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    global clock_hand

    key = obj.key
    # Initialize the saturate counter to 1
    object_metadata[key] = (1, 0)

    # Place in LFU queue
    lfu_queue[1].append(key)

    # Add to the front of the LRU queue
    lru_queue.appendleft(key)

    # Advance the clock hand
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the victim's metadata from both the LFU and LRU queues, adjusts the clock hand to point to the next valid entry, and ensures the mapping of cache entries is updated to reflect the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global clock_hand

    evicted_key = evicted_obj.key
    freq, _ = object_metadata[evicted_key]

    # Remove from LFU queue
    lfu_queue[freq].remove(evicted_key)
    if not lfu_queue[freq]:
        del lfu_queue[freq]

    # Remove from LRU queue
    lru_queue.remove(evicted_key)

    # Remove from metadata
    del object_metadata[evicted_key]

    # Adjust the clock hand to point to the next valid entry
    clock_hand = (clock_hand + 1) % len(cache_snapshot.cache)