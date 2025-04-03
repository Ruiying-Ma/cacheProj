# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic index to track the position in the cache, a frequency counter for each item to optimize access based on usage, and a queue to manage the order of items. The queue is rotated periodically to ensure rapid access to frequently used items.
cyclic_index = 0
frequency_counter = defaultdict(int)
access_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the item at the current cyclic index, but it prioritizes items with the lowest frequency count. If multiple items have the same frequency, the oldest item in the queue is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = float('inf')
    min_freq_keys = []

    # Find the minimum frequency among the items
    for key in cache_snapshot.cache:
        freq = frequency_counter[key]
        if freq < min_freq:
            min_freq = freq
            min_freq_keys = [key]
        elif freq == min_freq:
            min_freq_keys.append(key)

    # If multiple items have the same frequency, evict the oldest in the queue
    for key in access_queue:
        if key in min_freq_keys:
            candid_obj_key = key
            break

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed item is incremented, and the item is moved to the front of the queue to ensure rapid access. The cyclic index is advanced to the next position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] += 1
    access_queue.remove(obj.key)
    access_queue.appendleft(obj.key)
    global cyclic_index
    cyclic_index = (cyclic_index + 1) % len(cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the cyclic index is updated to point to the next position, the frequency counter for the new item is initialized to one, and the item is added to the front of the queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] = 1
    access_queue.appendleft(obj.key)
    global cyclic_index
    cyclic_index = (cyclic_index + 1) % len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an item, the cyclic index is adjusted to point to the next item in the cache, the frequency counter for the evicted item is removed, and the queue is rotated to bring less frequently accessed items closer to the front.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del frequency_counter[evicted_obj.key]
    access_queue.remove(evicted_obj.key)
    access_queue.rotate(-1)
    global cyclic_index
    cyclic_index = (cyclic_index + 1) % len(cache_snapshot.cache)