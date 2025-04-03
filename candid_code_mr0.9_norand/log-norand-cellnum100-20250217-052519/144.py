# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
TIME_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted latency for future accesses, and a dynamic priority score for each cache entry.
metadata = {}

def calculate_priority_score(access_frequency, predicted_latency, last_access_time, current_time):
    return (FREQUENCY_WEIGHT * access_frequency) - (LATENCY_WEIGHT * predicted_latency) + (TIME_WEIGHT * (current_time - last_access_time))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest dynamic priority score, which is calculated based on a combination of low access frequency, high predicted latency, and long time since last access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        priority_score = calculate_priority_score(meta['access_frequency'], meta['predicted_latency'], meta['last_access_time'], current_time)
        if priority_score < lowest_priority_score:
            lowest_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and recalculates the predicted latency and dynamic priority score based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = current_time
    meta['predicted_latency'] = 1 / meta['access_frequency']  # Example: simple inverse of frequency
    meta['priority_score'] = calculate_priority_score(meta['access_frequency'], meta['predicted_latency'], meta['last_access_time'], current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the initial predicted latency based on object characteristics, and computes the initial dynamic priority score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_time': current_time,
        'predicted_latency': 1,  # Example: initial latency
        'priority_score': calculate_priority_score(1, 1, current_time, current_time)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry and may adjust the predicted latency model and dynamic priority scoring mechanism based on the overall cache performance and recent eviction patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]