# Import anything you need below
import time

# Put tunable constant parameters below
PRIORITY_DECAY_RATE = 0.9
THRESHOLD_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a priority score, last access timestamp, and a dynamic threshold value. The priority score decays over time, and the threshold adapts based on cache load and access patterns.
metadata = {
    'priority_scores': {},  # Maps object keys to their priority scores
    'last_access_times': {},  # Maps object keys to their last access timestamps
    'adaptive_threshold': 1.0  # Initial adaptive threshold
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by comparing the priority scores of cache entries against the adaptive threshold. Entries with scores below the threshold are considered for eviction, with preference given to those with the lowest scores and oldest timestamps.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    oldest_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority_scores'].get(key, 0)
        last_access = metadata['last_access_times'].get(key, 0)
        
        if priority < metadata['adaptive_threshold']:
            if priority < min_priority or (priority == min_priority and last_access < oldest_time):
                min_priority = priority
                oldest_time = last_access
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, and its last access timestamp is updated. The adaptive threshold is recalibrated based on the current load and recent access patterns to ensure optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority_scores'][key] = metadata['priority_scores'].get(key, 0) + 1
    metadata['last_access_times'][key] = cache_snapshot.access_count
    
    # Recalibrate adaptive threshold
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    metadata['adaptive_threshold'] += THRESHOLD_ADJUSTMENT_FACTOR * (load_factor - metadata['adaptive_threshold'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its priority score is initialized based on the current adaptive threshold, and its last access timestamp is set to the current time. The threshold is adjusted to account for the new entry and maintain balance in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority_scores'][key] = metadata['adaptive_threshold']
    metadata['last_access_times'][key] = cache_snapshot.access_count
    
    # Adjust adaptive threshold
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    metadata['adaptive_threshold'] += THRESHOLD_ADJUSTMENT_FACTOR * (load_factor - metadata['adaptive_threshold'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the adaptive threshold is recalibrated to reflect the reduced load, and the priority decay rate is adjusted to ensure that remaining entries are evaluated fairly in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['priority_scores']:
        del metadata['priority_scores'][key]
    if key in metadata['last_access_times']:
        del metadata['last_access_times'][key]
    
    # Recalibrate adaptive threshold
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    metadata['adaptive_threshold'] += THRESHOLD_ADJUSTMENT_FACTOR * (load_factor - metadata['adaptive_threshold'])
    
    # Adjust priority decay rate
    for k in metadata['priority_scores']:
        metadata['priority_scores'][k] *= PRIORITY_DECAY_RATE