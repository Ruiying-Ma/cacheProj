# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
CONSISTENCY_WEIGHT = 1.0
ACCESS_FREQ_WEIGHT = 1.0
LAST_ACCESS_WEIGHT = 1.0
WRITE_COUNT_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, write count, and a consistency score derived from read-write patterns.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a composite score that considers low access frequency, older last access timestamp, high write count, and low consistency score to minimize write amplification and maintain data consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (ACCESS_FREQ_WEIGHT / (meta['access_frequency'] + 1) +
                 LAST_ACCESS_WEIGHT * (cache_snapshot.access_count - meta['last_access_timestamp']) +
                 WRITE_COUNT_WEIGHT * meta['write_count'] +
                 CONSISTENCY_WEIGHT * (1 - meta['consistency_score']))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access timestamp to the current time, and recalculates the consistency score based on recent read-write patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    # Recalculate consistency score based on some read-write pattern logic
    meta['consistency_score'] = calculate_consistency_score(meta)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, initializes the write count to 0, and calculates an initial consistency score based on the object's expected read-write pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'write_count': 0,
        'consistency_score': calculate_initial_consistency_score(obj)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the overall cache consistency score and read throughput metrics to ensure optimal performance and adjusts internal thresholds for future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    # Recalculate overall cache consistency score and read throughput metrics
    recalculate_cache_metrics(cache_snapshot)

def calculate_consistency_score(meta):
    # Placeholder for actual consistency score calculation logic
    return 1.0

def calculate_initial_consistency_score(obj):
    # Placeholder for initial consistency score calculation logic
    return 1.0

def recalculate_cache_metrics(cache_snapshot):
    # Placeholder for recalculating cache metrics logic
    pass