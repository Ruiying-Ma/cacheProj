# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for temporal delta since last access
GAMMA = 0.1  # Weight for predicted next access time
DELTA = 0.1  # Weight for resource usage

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted next access time, and resource usage metrics for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_next_access_time': {},
    'resource_usage': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a score for each object based on a combination of low access frequency, high temporal delta since last access, low predicted next access time, and high resource usage. The object with the lowest score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predicted_next = metadata['predicted_next_access_time'].get(key, math.inf)
        resource_usage = metadata['resource_usage'].get(key, 0)
        
        temporal_delta = cache_snapshot.access_count - last_access
        score = (ALPHA * access_freq) + (BETA * temporal_delta) + (GAMMA * predicted_next) + (DELTA * resource_usage)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the last access time to the current time, recalculates the predicted next access time based on recent access patterns, and adjusts resource usage metrics if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Increment access frequency
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Update last access time
    metadata['last_access_time'][key] = current_time
    
    # Recalculate predicted next access time
    if metadata['access_frequency'][key] > 1:
        last_access = metadata['last_access_time'][key]
        prev_predicted_next = metadata['predicted_next_access_time'][key]
        metadata['predicted_next_access_time'][key] = (prev_predicted_next + (current_time - last_access)) / 2
    else:
        metadata['predicted_next_access_time'][key] = current_time + 1  # Initial prediction
    
    # Adjust resource usage metrics if necessary
    metadata['resource_usage'][key] = obj.size

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the predicted next access time based on initial patterns, and records the initial resource usage metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access time
    metadata['last_access_time'][key] = current_time
    
    # Estimate predicted next access time
    metadata['predicted_next_access_time'][key] = current_time + 1  # Initial prediction
    
    # Record initial resource usage metrics
    metadata['resource_usage'][key] = obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes all associated metadata for the evicted object and may adjust overall resource usage metrics to reflect the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    
    # Remove all associated metadata for the evicted object
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['predicted_next_access_time']:
        del metadata['predicted_next_access_time'][key]
    if key in metadata['resource_usage']:
        del metadata['resource_usage'][key]