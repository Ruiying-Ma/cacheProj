# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
BASE_FREQUENCY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency modulator for each cache entry, a circular queue to track the order of entries, a priority eviction metric that combines frequency and recency, and a dynamic cache index that adjusts based on access patterns.
frequency_modulator = defaultdict(lambda: BASE_FREQUENCY)
circular_queue = deque()
priority_eviction_metric = {}
dynamic_cache_index = 0

def calculate_priority_metric(key):
    # Calculate the priority eviction metric based on frequency and recency
    frequency = frequency_modulator[key]
    recency = circular_queue.index(key) if key in circular_queue else float('inf')
    return frequency + recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority eviction metric, which is calculated by combining the frequency modulator and its position in the circular queue, favoring less frequently accessed and older entries.
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
        priority = calculate_priority_metric(key)
        if priority < min_priority:
            min_priority = priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency modulator for the accessed entry is incremented, its position in the circular queue is updated to reflect recency, and the priority eviction metric is recalculated to reflect the increased frequency and updated recency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_modulator[key] += 1
    if key in circular_queue:
        circular_queue.remove(key)
    circular_queue.append(key)
    priority_eviction_metric[key] = calculate_priority_metric(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the frequency modulator is initialized to a base value, the object is added to the end of the circular queue, and the priority eviction metric is set to reflect its initial state, with adjustments made to the dynamic cache index if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_modulator[key] = BASE_FREQUENCY
    circular_queue.append(key)
    priority_eviction_metric[key] = calculate_priority_metric(key)
    # Adjust dynamic cache index if necessary
    dynamic_cache_index = len(circular_queue) // 2

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the circular queue is updated to remove the evicted entry, the dynamic cache index is adjusted to optimize for current access patterns, and the priority eviction metrics of remaining entries are recalculated if needed to maintain accurate eviction priorities.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in circular_queue:
        circular_queue.remove(evicted_key)
    del frequency_modulator[evicted_key]
    del priority_eviction_metric[evicted_key]
    # Adjust dynamic cache index if necessary
    dynamic_cache_index = len(circular_queue) // 2
    # Recalculate priority eviction metrics
    for key in circular_queue:
        priority_eviction_metric[key] = calculate_priority_metric(key)