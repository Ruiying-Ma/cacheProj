# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains an LRU queue to track the order of access for cache entries, a frequency counter for each entry to track how often each entry is accessed, and a timestamp for each entry to track the time of the last access.
lru_queue = deque()
frequency_counter = defaultdict(int)
timestamps = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying the least frequently used entries. Among these, it selects the least recently used entry based on the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_freq = min(frequency_counter.values())
    lru_candidates = [key for key in lru_queue if frequency_counter[key] == min_freq]
    
    for key in lru_queue:
        if key in lru_candidates:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the LRU queue to move the accessed entry to the front, increments the frequency counter for the entry, and updates the timestamp to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)
    frequency_counter[obj.key] += 1
    timestamps[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the entry to the front of the LRU queue, initializes its frequency counter to 1, and sets its timestamp to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    lru_queue.appendleft(obj.key)
    frequency_counter[obj.key] = 1
    timestamps[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from the LRU queue, deletes its frequency counter, and clears its timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    lru_queue.remove(evicted_obj.key)
    del frequency_counter[evicted_obj.key]
    del timestamps[evicted_obj.key]