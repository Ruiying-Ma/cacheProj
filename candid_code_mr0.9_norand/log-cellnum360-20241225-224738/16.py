# Import anything you need below
import heapq

# Put tunable constant parameters below
HEURISTIC_SCORE_BASE = 100
LOAD_FACTOR_INCREMENT = 0.1
LOAD_FACTOR_DECREMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue for cache entries based on a heuristic score, a load factor indicating current cache pressure, and a priority inversion flag for each entry to temporarily boost low-priority items.
priority_queue = []  # Min-heap based on heuristic score
load_factor = 0.0
metadata = {}  # Maps obj.key to (heuristic_score, priority_inversion_flag)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest heuristic score from the priority queue, considering the load factor to decide if immediate eviction is necessary or if load shedding can be applied to delay eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        score, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the heuristic score of the accessed entry is recalculated to reflect its increased importance, and the priority inversion flag is checked to determine if it should be reset, while the load factor is slightly decreased to reflect reduced pressure.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if obj.key in metadata:
        heuristic_score, priority_inversion_flag = metadata[obj.key]
        heuristic_score -= 1  # Increase importance by decreasing score
        if priority_inversion_flag:
            priority_inversion_flag = False
        metadata[obj.key] = (heuristic_score, priority_inversion_flag)
        heapq.heappush(priority_queue, (heuristic_score, obj.key))
    
    global load_factor
    load_factor = max(0.0, load_factor - LOAD_FACTOR_DECREMENT)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the heuristic score is initialized based on initial access patterns, the load factor is increased to reflect added pressure, and the priority inversion flag is set to false.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    heuristic_score = HEURISTIC_SCORE_BASE
    priority_inversion_flag = False
    metadata[obj.key] = (heuristic_score, priority_inversion_flag)
    heapq.heappush(priority_queue, (heuristic_score, obj.key))
    
    global load_factor
    load_factor += LOAD_FACTOR_INCREMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the load factor is decreased to reflect reduced pressure, and the priority queue is rebalanced to ensure the next eviction candidate is accurately prioritized, while the priority inversion flag of remaining entries is evaluated for potential adjustment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    global load_factor
    load_factor = max(0.0, load_factor - LOAD_FACTOR_DECREMENT)
    
    # Rebalance the priority queue
    heapq.heapify(priority_queue)