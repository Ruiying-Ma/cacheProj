# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a recency list, a hit counter for each cache entry, and a global access history log that records the sequence of accesses.
recency_list = deque()  # To maintain the recency list
hit_counter = defaultdict(int)  # To maintain the hit counter for each cache entry
access_history_log = []  # To maintain the global access history log

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the least recently used (LRU) and the least frequently used (LFU) entries, giving priority to entries with the lowest hit count and oldest access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_hits = float('inf')
    oldest_key = None

    for key in recency_list:
        if hit_counter[key] < min_hits:
            min_hits = hit_counter[key]
            oldest_key = key
        elif hit_counter[key] == min_hits:
            oldest_key = key

    candid_obj_key = oldest_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the recency list to move the accessed entry to the most recent position, increments the hit counter for the entry, and appends the access to the global access history log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in recency_list:
        recency_list.remove(obj.key)
    recency_list.append(obj.key)
    hit_counter[obj.key] += 1
    access_history_log.append(('hit', obj.key, cache_snapshot.access_count))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds the object to the recency list as the most recent entry, initializes its hit counter to one, and records the insertion in the global access history log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    recency_list.append(obj.key)
    hit_counter[obj.key] = 1
    access_history_log.append(('insert', obj.key, cache_snapshot.access_count))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the entry from the recency list, deletes its hit counter, and updates the global access history log to reflect the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in recency_list:
        recency_list.remove(evicted_obj.key)
    if evicted_obj.key in hit_counter:
        del hit_counter[evicted_obj.key]
    access_history_log.append(('evict', evicted_obj.key, cache_snapshot.access_count))