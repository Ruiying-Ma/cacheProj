# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import heapq

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue where each cache entry is associated with a priority score. It also tracks the recency of access for each entry using a timestamp.
priority_queue = []  # This will be a min-heap based on (priority_score, timestamp, obj_key)
priority_scores = {}  # Maps obj_key to its priority score
timestamps = {}  # Maps obj_key to its last access timestamp

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score from the priority queue. If there are multiple entries with the same priority score, the least recently accessed entry is chosen.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        priority_score, timestamp, obj_key = heapq.heappop(priority_queue)
        if obj_key in cache_snapshot.cache:
            candid_obj_key = obj_key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, and its timestamp is updated to the current time to reflect its recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    priority_scores[obj_key] += 1
    timestamps[obj_key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (priority_scores[obj_key], timestamps[obj_key], obj_key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it an initial priority score and sets its timestamp to the current time. The new entry is then added to the priority queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    priority_scores[obj_key] = INITIAL_PRIORITY_SCORE
    timestamps[obj_key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (priority_scores[obj_key], timestamps[obj_key], obj_key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy removes the entry from the priority queue and updates any necessary internal structures to maintain the integrity of the priority queue and recency tracking.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_obj_key = evicted_obj.key
    if evicted_obj_key in priority_scores:
        del priority_scores[evicted_obj_key]
    if evicted_obj_key in timestamps:
        del timestamps[evicted_obj_key]
    # No need to remove from priority_queue explicitly as it will be ignored in future evictions