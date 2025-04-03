# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_CONTEXTUAL_TAGS = 0.2
WEIGHT_RESOURCE_USAGE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior patterns, application type), and resource usage metrics (e.g., memory and CPU usage).
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'contextual_tags': {},
    'resource_usage': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses a weighted scoring system that combines predictive analytics (future access likelihood), contextual inference (importance based on context), and resource allocation (current resource usage) to select the eviction victim. The object with the lowest score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        last_access_time = metadata['last_access_time'].get(key, 0)
        contextual_tags = metadata['contextual_tags'].get(key, 0)
        resource_usage = metadata['resource_usage'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_CONTEXTUAL_TAGS * contextual_tags +
                 WEIGHT_RESOURCE_USAGE * resource_usage)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and re-evaluates the contextual tags and resource usage metrics based on the current context and system state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Re-evaluate contextual tags and resource usage metrics
    metadata['contextual_tags'][key] = evaluate_contextual_tags(obj)
    metadata['resource_usage'][key] = evaluate_resource_usage(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns initial contextual tags based on the insertion context, and updates resource usage metrics to reflect the new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = evaluate_contextual_tags(obj)
    metadata['resource_usage'][key] = evaluate_resource_usage(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the resource usage metrics to account for the freed resources, and adjusts the contextual tags and predictive analytics models to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    if evicted_key in metadata['resource_usage']:
        del metadata['resource_usage'][evicted_key]
    
    # Recalculate resource usage metrics
    for key in metadata['resource_usage']:
        metadata['resource_usage'][key] = evaluate_resource_usage(cache_snapshot.cache[key])

def evaluate_contextual_tags(obj):
    # Placeholder function to evaluate contextual tags
    return 1

def evaluate_resource_usage(obj):
    # Placeholder function to evaluate resource usage
    return obj.size