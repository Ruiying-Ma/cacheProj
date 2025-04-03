# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1
LOAD_BALANCE_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a load balance factor for different cache regions, a queue for tracking recent accesses, and a consistency map to ensure data coherence across cache levels.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
load_balance_factor = LOAD_BALANCE_FACTOR
access_queue = deque()
consistency_map = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest priority score, adjusted by the load balance factor to ensure even distribution across cache regions. The queue is consulted to break ties by choosing the least recently accessed entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key in cache_snapshot.cache:
        adjusted_priority = priority_scores[key] * load_balance_factor
        if adjusted_priority < min_priority:
            min_priority = adjusted_priority
            candid_obj_key = key
        elif adjusted_priority == min_priority:
            # Break ties using the access queue (LRU)
            if access_queue.index(key) > access_queue.index(candid_obj_key):
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is incremented, the load balance factor is adjusted to reflect the current access pattern, the entry is moved to the front of the queue, and the consistency map is checked for any necessary updates.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] += 1
    # Adjust load balance factor (example: based on hit ratio)
    load_balance_factor = (cache_snapshot.hit_count + 1) / (cache_snapshot.access_count + 1)
    # Move to front of the queue
    if obj.key in access_queue:
        access_queue.remove(obj.key)
    access_queue.appendleft(obj.key)
    # Check consistency map (example: no-op for simplicity)
    consistency_map[obj.key] = obj

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its priority score is initialized based on its expected access frequency, the load balance factor is recalculated to accommodate the new entry, the object is added to the front of the queue, and the consistency map is updated to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] = INITIAL_PRIORITY_SCORE
    # Recalculate load balance factor (example: based on cache size)
    load_balance_factor = cache_snapshot.size / cache_snapshot.capacity
    # Add to front of the queue
    access_queue.appendleft(obj.key)
    # Update consistency map
    consistency_map[obj.key] = obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the priority scores of remaining entries are recalibrated, the load balance factor is adjusted to reflect the reduced cache size, the evicted entry is removed from the queue, and the consistency map is updated to remove references to the evicted data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalibrate priority scores (example: reduce all by a factor)
    for key in priority_scores:
        priority_scores[key] = max(1, priority_scores[key] - 1)
    # Adjust load balance factor (example: based on cache size)
    load_balance_factor = cache_snapshot.size / cache_snapshot.capacity
    # Remove evicted entry from the queue
    if evicted_obj.key in access_queue:
        access_queue.remove(evicted_obj.key)
    # Update consistency map
    if evicted_obj.key in consistency_map:
        del consistency_map[evicted_obj.key]