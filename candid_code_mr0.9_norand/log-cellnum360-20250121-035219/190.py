# Import anything you need below
import time

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
PREDICTED_FUTURE_ACCESS_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access timestamps, access frequency, predicted future access time, and resource usage patterns for each cached object.
metadata = {
    'access_timestamps': {},  # {obj.key: last_access_time}
    'access_frequencies': {},  # {obj.key: access_count}
    'predicted_future_access_times': {},  # {obj.key: predicted_future_access_time}
    'resource_usage_patterns': {}  # {obj.key: resource_usage_pattern}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a combination of the least recently used, least frequently used, and the predicted future access time, prioritizing objects with the lowest predicted future access and highest latency impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        recency = cache_snapshot.access_count - metadata['access_timestamps'].get(key, 0)
        frequency = metadata['access_frequencies'].get(key, 0)
        predicted_future_access = metadata['predicted_future_access_times'].get(key, float('inf'))
        
        score = (RECENCY_WEIGHT * recency) + (FREQUENCY_WEIGHT * frequency) + (PREDICTED_FUTURE_ACCESS_WEIGHT * predicted_future_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access timestamp, increments the access frequency, and recalculates the predicted future access time based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_timestamps'][key] = cache_snapshot.access_count
    metadata['access_frequencies'][key] = metadata['access_frequencies'].get(key, 0) + 1
    # Recalculate predicted future access time (this is a placeholder, actual implementation may vary)
    metadata['predicted_future_access_times'][key] = metadata['access_frequencies'][key] * 2  # Example heuristic

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access timestamp, sets the access frequency to one, and estimates the initial predicted future access time using historical data and current resource usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_timestamps'][key] = cache_snapshot.access_count
    metadata['access_frequencies'][key] = 1
    # Estimate initial predicted future access time (this is a placeholder, actual implementation may vary)
    metadata['predicted_future_access_times'][key] = 2  # Example heuristic

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy logs the eviction event, updates resource usage patterns, and adjusts the predictive model to refine future access time predictions for remaining objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Log eviction event (this is a placeholder, actual implementation may vary)
    print(f"Evicted object with key: {evicted_key}")
    
    # Update resource usage patterns (this is a placeholder, actual implementation may vary)
    metadata['resource_usage_patterns'][evicted_key] = metadata['access_frequencies'].get(evicted_key, 0)
    
    # Adjust predictive model (this is a placeholder, actual implementation may vary)
    for key in cache_snapshot.cache:
        metadata['predicted_future_access_times'][key] = metadata['access_frequencies'][key] * 2  # Example heuristic

    # Clean up metadata for evicted object
    if evicted_key in metadata['access_timestamps']:
        del metadata['access_timestamps'][evicted_key]
    if evicted_key in metadata['access_frequencies']:
        del metadata['access_frequencies'][evicted_key]
    if evicted_key in metadata['predicted_future_access_times']:
        del metadata['predicted_future_access_times'][evicted_key]
    if evicted_key in metadata['resource_usage_patterns']:
        del metadata['resource_usage_patterns'][evicted_key]