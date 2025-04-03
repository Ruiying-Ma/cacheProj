# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
DYNAMIC_ALLOCATION_FACTOR_INITIAL = 1.0
LOAD_RECALIBRATION_THRESHOLD = 100
PRIORITY_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a dynamic allocation factor, a load recalibration counter, and a sequential alignment index. The priority score is a composite value derived from access frequency, recency, and a dynamic allocation factor that adjusts based on system load. The load recalibration counter tracks the number of cache hits and misses to adjust the dynamic allocation factor. The sequential alignment index records the order of access to optimize sequential data patterns.
priority_scores = defaultdict(float)
dynamic_allocation_factor = DYNAMIC_ALLOCATION_FACTOR_INITIAL
load_recalibration_counter = 0
sequential_alignment_index = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest priority score. In case of a tie, it considers the sequential alignment index to favor retaining entries that are part of a detected sequential access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if priority_scores[key] < min_priority:
            min_priority = priority_scores[key]
            candid_obj_key = key
        elif priority_scores[key] == min_priority:
            # Use sequential alignment index to break ties
            if sequential_alignment_index.index(key) < sequential_alignment_index.index(candid_obj_key):
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased based on its current score and the dynamic allocation factor. The load recalibration counter is incremented to reflect the hit, and the sequential alignment index is updated to reflect the latest access order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global load_recalibration_counter
    
    # Increase priority score
    priority_scores[obj.key] += PRIORITY_INCREMENT * dynamic_allocation_factor
    
    # Increment load recalibration counter
    load_recalibration_counter += 1
    
    # Update sequential alignment index
    if obj.key in sequential_alignment_index:
        sequential_alignment_index.remove(obj.key)
    sequential_alignment_index.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score based on the dynamic allocation factor and current system load. The load recalibration counter is checked to determine if a recalibration of the dynamic allocation factor is needed. The sequential alignment index is updated to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global dynamic_allocation_factor, load_recalibration_counter
    
    # Initialize priority score
    priority_scores[obj.key] = dynamic_allocation_factor
    
    # Check if recalibration is needed
    if load_recalibration_counter >= LOAD_RECALIBRATION_THRESHOLD:
        dynamic_allocation_factor = (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))
        load_recalibration_counter = 0
    
    # Update sequential alignment index
    sequential_alignment_index.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the dynamic allocation factor if the load recalibration counter indicates a significant change in cache performance. The sequential alignment index is adjusted to remove the evicted entry, and the priority scores of remaining entries are recalculated if necessary to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global dynamic_allocation_factor, load_recalibration_counter
    
    # Remove evicted entry from sequential alignment index
    if evicted_obj.key in sequential_alignment_index:
        sequential_alignment_index.remove(evicted_obj.key)
    
    # Recalibrate dynamic allocation factor if needed
    if load_recalibration_counter >= LOAD_RECALIBRATION_THRESHOLD:
        dynamic_allocation_factor = (cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count))
        load_recalibration_counter = 0
    
    # Recalculate priority scores if necessary
    for key in cache_snapshot.cache:
        priority_scores[key] *= dynamic_allocation_factor