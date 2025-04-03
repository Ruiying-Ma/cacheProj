# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a circular queue for round robin scheduling, a priority level for each cache entry to handle priority inversion, access latency records for each entry to balance latency, and a resource allocation score to manage cache space distribution.
priority_levels = defaultdict(lambda: DEFAULT_PRIORITY)
access_latency = defaultdict(int)
round_robin_queue = deque()
resource_allocation_scores = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by first checking for entries with the lowest priority level, then among those, it chooses the entry with the highest access latency. If there's a tie, it uses round robin scheduling to select the next entry in the queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = min(priority_levels[obj_key] for obj_key in cache_snapshot.cache)
    candidates = [obj_key for obj_key in cache_snapshot.cache if priority_levels[obj_key] == min_priority]
    
    if candidates:
        max_latency = max(access_latency[obj_key] for obj_key in candidates)
        candidates = [obj_key for obj_key in candidates if access_latency[obj_key] == max_latency]
    
    if candidates:
        for obj_key in round_robin_queue:
            if obj_key in candidates:
                candid_obj_key = obj_key
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority level of the accessed entry, updates its access latency to reflect the current access time, and adjusts its position in the round robin queue to the end to ensure fair scheduling.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_levels[obj.key] += 1
    access_latency[obj.key] = cache_snapshot.access_count
    if obj.key in round_robin_queue:
        round_robin_queue.remove(obj.key)
    round_robin_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it a default priority level, records its initial access latency as zero, and places it at the end of the round robin queue to await its turn for potential eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_levels[obj.key] = DEFAULT_PRIORITY
    access_latency[obj.key] = 0
    round_robin_queue.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the resource allocation scores for remaining entries to ensure balanced cache space distribution, and updates the round robin queue to remove the evicted entry and maintain scheduling order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in round_robin_queue:
        round_robin_queue.remove(evicted_obj.key)
    
    # Recalibrate resource allocation scores
    total_size = sum(o.size for o in cache_snapshot.cache.values())
    for obj_key in cache_snapshot.cache:
        resource_allocation_scores[obj_key] = cache_snapshot.cache[obj_key].size / total_size