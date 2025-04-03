# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
FREQUENCY_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a timestamp for each cache entry, a frequency counter for each entry, and two queues: a primary queue for frequently accessed items and a secondary queue for less frequently accessed items.
timestamps = {}
frequency_counters = defaultdict(int)
primary_queue = deque()
secondary_queue = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the secondary queue for the least recently used item. If the secondary queue is empty, it then checks the primary queue for the least frequently used item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if secondary_queue:
        # Evict the least recently used item from the secondary queue
        candid_obj_key = secondary_queue.popleft()
    elif primary_queue:
        # Evict the least frequently used item from the primary queue
        candid_obj_key = min(primary_queue, key=lambda k: frequency_counters[k])
        primary_queue.remove(candid_obj_key)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp to the current time and increments the frequency counter of the accessed item. If the item is in the secondary queue and its frequency exceeds a threshold, it is moved to the primary queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    timestamps[key] = cache_snapshot.access_count
    frequency_counters[key] += 1
    
    if key in secondary_queue and frequency_counters[key] > FREQUENCY_THRESHOLD:
        secondary_queue.remove(key)
        primary_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy sets its timestamp to the current time and initializes its frequency counter to one. The new object is placed in the secondary queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    timestamps[key] = cache_snapshot.access_count
    frequency_counters[key] = 1
    secondary_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from its respective queue and deletes its associated timestamp and frequency counter.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in secondary_queue:
        secondary_queue.remove(key)
    if key in primary_queue:
        primary_queue.remove(key)
    if key in timestamps:
        del timestamps[key]
    if key in frequency_counters:
        del frequency_counters[key]