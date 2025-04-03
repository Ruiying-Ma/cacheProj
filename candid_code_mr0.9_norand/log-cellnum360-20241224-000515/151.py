# Import anything you need below
import heapq
import time

# Put tunable constant parameters below
INITIAL_PRIORITY = 1.0
LOAD_FACTOR_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue where each cache entry is associated with a priority score. This score is dynamically adjusted based on temporal access patterns, load balancing metrics, and event detection signals. Additionally, a timestamp of the last access and a load factor indicating the current system load are stored for each entry.
priority_queue = []  # Min-heap based on priority score
metadata = {}  # Maps obj.key to (priority_score, last_access_time, load_factor)

def calculate_priority_score(recency, load_factor):
    return RECENCY_WEIGHT * recency + LOAD_FACTOR_WEIGHT * load_factor

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by choosing the entry with the lowest priority score from the priority queue. The priority score is influenced by how recently and frequently an entry is accessed, the current system load, and any detected events that may affect cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        priority, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased based on the recency of access and the current load factor. The last access timestamp is updated to the current time, and the load factor is recalibrated if necessary based on system load changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    recency = current_time - metadata[obj.key][1]
    new_priority = calculate_priority_score(recency, load_factor)
    metadata[obj.key] = (new_priority, current_time, load_factor)
    heapq.heappush(priority_queue, (new_priority, obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the current load factor and any relevant events detected. The last access timestamp is set to the current time, and the load factor is updated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    initial_priority = calculate_priority_score(0, load_factor)
    metadata[obj.key] = (initial_priority, current_time, load_factor)
    heapq.heappush(priority_queue, (initial_priority, obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority scores of remaining entries in the priority queue to ensure balance. The load factor is adjusted to account for the reduced cache size, and any event signals are re-evaluated to update their influence on priority scoring.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    for key in cache_snapshot.cache:
        if key in metadata:
            recency = cache_snapshot.access_count - metadata[key][1]
            new_priority = calculate_priority_score(recency, load_factor)
            metadata[key] = (new_priority, metadata[key][1], load_factor)
            heapq.heappush(priority_queue, (new_priority, key))