# Import anything you need below
import heapq
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_PRIORITY = 1
PRIORITY_INCREMENT = 1
PREDICTIVE_THRESHOLD = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a priority queue for cache items, a latency buffer to track access times, a predictive threshold for future access prediction, and a hybrid allocation map to balance between frequently and infrequently accessed items.
priority_queue = []  # Min-heap based on priority and latency
latency_buffer = {}  # Maps object keys to their last access time
hybrid_allocation_map = defaultdict(lambda: INITIAL_PRIORITY)  # Maps object keys to their priority
access_frequency = defaultdict(int)  # Maps object keys to their access frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking the predictive threshold to identify items unlikely to be accessed soon, then shuffles priorities based on recent access patterns, and finally selects the item with the lowest priority and highest latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Shuffle priorities based on recent access patterns
    for key in cache_snapshot.cache:
        if key in latency_buffer:
            latency = cache_snapshot.access_count - latency_buffer[key]
            priority = hybrid_allocation_map[key]
            heapq.heappush(priority_queue, (priority, latency, key))
    
    # Select the item with the lowest priority and highest latency
    while priority_queue:
        priority, latency, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the priority of the accessed item by increasing its priority score, adjusts the latency buffer to reflect the current access time, and recalibrates the predictive threshold based on the updated access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Increase priority score
    hybrid_allocation_map[key] += PRIORITY_INCREMENT
    # Update latency buffer
    latency_buffer[key] = cache_snapshot.access_count
    # Update access frequency
    access_frequency[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority based on the hybrid allocation map, updates the latency buffer with the current time, and adjusts the predictive threshold to accommodate the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Assign initial priority
    hybrid_allocation_map[key] = INITIAL_PRIORITY
    # Update latency buffer
    latency_buffer[key] = cache_snapshot.access_count
    # Initialize access frequency
    access_frequency[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the hybrid allocation map to ensure optimal distribution between frequently and infrequently accessed items, updates the latency buffer to remove the evicted item's data, and recalibrates the predictive threshold to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove evicted item's data from latency buffer
    if evicted_key in latency_buffer:
        del latency_buffer[evicted_key]
    # Remove evicted item's data from hybrid allocation map
    if evicted_key in hybrid_allocation_map:
        del hybrid_allocation_map[evicted_key]
    # Remove evicted item's data from access frequency
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]