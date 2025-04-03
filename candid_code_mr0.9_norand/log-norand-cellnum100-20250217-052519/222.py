# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_FUTURE_ACCESS_PROB = 0.4
WEIGHT_RESOURCE_USAGE_COST = 0.3
WEIGHT_LATENCY_MEASUREMENT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and resource usage cost for each cached object. It also keeps a probabilistic model to predict future access patterns and latency measurements for each object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'resource_usage_cost': {},
    'latency_measurement': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the least predicted future access probability, highest resource usage cost, and longest latency measurement. It uses a weighted scoring system to balance these factors and select the optimal candidate for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        future_access_prob = 1 / (1 + metadata['predicted_future_access_time'][key])
        resource_usage_cost = metadata['resource_usage_cost'][key]
        latency_measurement = metadata['latency_measurement'][key]
        
        score = (WEIGHT_FUTURE_ACCESS_PROB * future_access_prob +
                 WEIGHT_RESOURCE_USAGE_COST * resource_usage_cost +
                 WEIGHT_LATENCY_MEASUREMENT * latency_measurement)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time for the object. It also refines the probabilistic model using the new access data and adjusts the predicted future access time accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1 / metadata['access_frequency'][key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, last access time, and resource usage cost. It also updates the probabilistic model to include the new object and estimates its initial predicted future access time and latency measurement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1
    metadata['resource_usage_cost'][key] = obj.size
    metadata['latency_measurement'][key] = 1  # Initial latency measurement

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object. It then recalibrates the probabilistic model to account for the removal and adjusts the resource optimization parameters to reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['predicted_future_access_time'][evicted_key]
    del metadata['resource_usage_cost'][evicted_key]
    del metadata['latency_measurement'][evicted_key]