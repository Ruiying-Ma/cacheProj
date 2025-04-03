# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
BASE_PRIORITY = 1.0
SCALING_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue for cache entries, a latency buffer to track access times, and an adaptive scaling factor to adjust priorities based on access patterns.
priority_queue = []  # Min-heap based on priority
latency_buffer = defaultdict(int)  # Maps object keys to their last access time
priority_map = {}  # Maps object keys to their current priority

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority in the queue, factoring in the latency buffer to ensure that recently accessed items are less likely to be evicted.
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
    Upon a cache hit, the policy increases the priority of the accessed entry in the queue and updates the latency buffer to reflect the current access time, adjusting the adaptive scaling factor to prioritize frequently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    latency_buffer[obj.key] = current_time
    priority_map[obj.key] += SCALING_FACTOR
    heapq.heappush(priority_queue, (priority_map[obj.key], obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it a base priority in the queue, initializes its latency buffer entry, and recalibrates the adaptive scaling factor to accommodate the new entry's access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_time = cache_snapshot.access_count
    latency_buffer[obj.key] = current_time
    priority_map[obj.key] = BASE_PRIORITY
    heapq.heappush(priority_queue, (priority_map[obj.key], obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the victim's metadata from the queue and latency buffer, and recalculates the adaptive scaling factor to redistribute priorities among the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in latency_buffer:
        del latency_buffer[evicted_obj.key]
    if evicted_obj.key in priority_map:
        del priority_map[evicted_obj.key]
    # Recalculate scaling factor if needed (not implemented here as it's a constant)