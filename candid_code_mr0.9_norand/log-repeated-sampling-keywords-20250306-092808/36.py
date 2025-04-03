# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
HOT_THRESHOLD = 5
WARM_THRESHOLD = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a queue hierarchy with three levels: hot, warm, and cold. Each cache entry has an access frequency counter and a freshness timestamp.
cold_queue = deque()
warm_queue = deque()
hot_queue = deque()
access_frequency = defaultdict(int)
freshness_timestamp = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evicts the least recently used (LRU) entry from the cold queue first. If the cold queue is empty, it evicts from the warm queue, and finally from the hot queue if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if cold_queue:
        candid_obj_key = cold_queue.popleft()
    elif warm_queue:
        candid_obj_key = warm_queue.popleft()
    elif hot_queue:
        candid_obj_key = hot_queue.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency counter of the entry is incremented, and its freshness timestamp is updated to the current time. The entry is then promoted to a higher queue if its access frequency surpasses a threshold.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    freshness_timestamp[key] = cache_snapshot.access_count

    if access_frequency[key] >= HOT_THRESHOLD:
        if key in warm_queue:
            warm_queue.remove(key)
        elif key in cold_queue:
            cold_queue.remove(key)
        hot_queue.append(key)
    elif access_frequency[key] >= WARM_THRESHOLD:
        if key in cold_queue:
            cold_queue.remove(key)
        warm_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the cold queue with an initial access frequency of 1 and a current freshness timestamp. If the cold queue is full, the LRU entry is evicted to make space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    freshness_timestamp[key] = cache_snapshot.access_count
    cold_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy re-evaluates the thresholds for promoting entries between queues based on the current cache usage and access patterns, ensuring optimal distribution across hot, warm, and cold queues.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in freshness_timestamp:
        del freshness_timestamp[evicted_key]
    if evicted_key in cold_queue:
        cold_queue.remove(evicted_key)
    if evicted_key in warm_queue:
        warm_queue.remove(evicted_key)
    if evicted_key in hot_queue:
        hot_queue.remove(evicted_key)