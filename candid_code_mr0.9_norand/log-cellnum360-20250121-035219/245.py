# Import anything you need below
import time

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.3
FREQUENCY_WEIGHT = 0.2
PREDICTED_ACCESS_WEIGHT = 0.3
RESOURCE_USAGE_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and resource usage patterns. It also tracks data throughput and latency metrics for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'resource_usage': {},
    'latency': {},
    'throughput': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that combines low access frequency, high latency, low predicted future access, and high resource usage. Objects with the lowest scores are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        latency = metadata['latency'].get(key, 0)
        predicted_access = metadata['predicted_future_access_time'].get(key, 0)
        resource_usage = metadata['resource_usage'].get(key, 0)
        
        score = (LATENCY_WEIGHT * latency +
                 FREQUENCY_WEIGHT * (1 / (access_freq + 1)) +
                 PREDICTED_ACCESS_WEIGHT * (1 / (predicted_access + 1)) +
                 RESOURCE_USAGE_WEIGHT * resource_usage)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and adjusts the predicted future access time based on recent access patterns. It also updates the latency and throughput metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = current_time
    metadata['predicted_future_access_time'][key] = current_time + (current_time - metadata['last_access_time'].get(key, current_time))
    # Update latency and throughput metrics as needed
    metadata['latency'][key] = time.time() - metadata['last_access_time'].get(key, time.time())
    metadata['throughput'][key] = metadata['throughput'].get(key, 0) + obj.size

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the last access time to the current time, and estimates the predicted future access time based on initial access patterns. It also starts tracking latency and throughput metrics for the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = current_time
    metadata['predicted_future_access_time'][key] = current_time + 1  # Initial guess
    metadata['latency'][key] = 0  # Initial latency
    metadata['throughput'][key] = obj.size  # Initial throughput

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the resource usage patterns and adjusts the weights for future eviction decisions. It also updates the overall cache performance metrics, including data throughput and latency optimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['resource_usage']:
        del metadata['resource_usage'][evicted_key]
    if evicted_key in metadata['latency']:
        del metadata['latency'][evicted_key]
    if evicted_key in metadata['throughput']:
        del metadata['throughput'][evicted_key]
    
    # Recalculate resource usage patterns and adjust weights if necessary
    # This is a placeholder for more complex logic
    total_size = sum(obj.size for obj in cache_snapshot.cache.values())
    for key in cache_snapshot.cache:
        metadata['resource_usage'][key] = cache_snapshot.cache[key].size / total_size