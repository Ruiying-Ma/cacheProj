# Import anything you need below
import time

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1
INITIAL_PRIORITY = 1
INITIAL_FREQUENCY = 1
INITIAL_LATENCY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a synchronized timestamp of the last access, a frequency count of accesses, and a latency estimate for retrieval.
cache_metadata = {
    'priority': {},  # Maps obj.key to its priority score
    'timestamp': {},  # Maps obj.key to its last access timestamp
    'frequency': {},  # Maps obj.key to its access frequency count
    'latency': {}  # Maps obj.key to its latency estimate
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry based on its priority, recency of access, frequency of access, and latency. The entry with the lowest score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = cache_metadata['priority'].get(key, INITIAL_PRIORITY)
        timestamp = cache_metadata['timestamp'].get(key, 0)
        frequency = cache_metadata['frequency'].get(key, INITIAL_FREQUENCY)
        latency = cache_metadata['latency'].get(key, INITIAL_LATENCY)
        
        # Calculate composite score
        score = (priority / (1 + frequency)) + (cache_snapshot.access_count - timestamp) + latency
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score is increased, the timestamp is updated to the current time, the frequency count is incremented, and the latency estimate is adjusted based on recent retrieval time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['priority'][key] = cache_metadata['priority'].get(key, INITIAL_PRIORITY) + PRIORITY_INCREMENT
    cache_metadata['timestamp'][key] = cache_snapshot.access_count
    cache_metadata['frequency'][key] = cache_metadata['frequency'].get(key, INITIAL_FREQUENCY) + 1
    # Adjust latency estimate (for simplicity, we assume a constant adjustment)
    cache_metadata['latency'][key] = cache_metadata['latency'].get(key, INITIAL_LATENCY) * 0.9

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the priority score is initialized based on the object's importance, the timestamp is set to the current time, the frequency count starts at one, and the latency is estimated based on initial retrieval time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['priority'][key] = INITIAL_PRIORITY
    cache_metadata['timestamp'][key] = cache_snapshot.access_count
    cache_metadata['frequency'][key] = INITIAL_FREQUENCY
    cache_metadata['latency'][key] = INITIAL_LATENCY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the priority arbitration mechanism to ensure balanced distribution, synchronizes timestamps across remaining entries, adjusts frequency distribution to reflect the change, and recalculates latency management parameters.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata of evicted object
    cache_metadata['priority'].pop(evicted_key, None)
    cache_metadata['timestamp'].pop(evicted_key, None)
    cache_metadata['frequency'].pop(evicted_key, None)
    cache_metadata['latency'].pop(evicted_key, None)
    
    # Recalibrate priority arbitration mechanism
    # For simplicity, we assume recalibration involves normalizing priorities
    total_priority = sum(cache_metadata['priority'].values())
    if total_priority > 0:
        for key in cache_metadata['priority']:
            cache_metadata['priority'][key] /= total_priority
    
    # Synchronize timestamps
    current_time = cache_snapshot.access_count
    for key in cache_metadata['timestamp']:
        cache_metadata['timestamp'][key] = current_time
    
    # Adjust frequency distribution
    max_frequency = max(cache_metadata['frequency'].values(), default=1)
    for key in cache_metadata['frequency']:
        cache_metadata['frequency'][key] /= max_frequency
    
    # Recalculate latency management parameters
    # For simplicity, we assume a constant adjustment
    for key in cache_metadata['latency']:
        cache_metadata['latency'][key] *= 1.1