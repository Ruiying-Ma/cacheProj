# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_PREDICTED_FUTURE_ACCESS = 0.2
WEIGHT_CONTEXT_RELEVANCE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and context tags (e.g., user activity, application type).
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access': {},
    'context_tags': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, long time since last access, distant predicted future access, and low relevance of context tags.
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
        predicted_future_access = metadata['predicted_future_access'].get(key, float('inf'))
        context_relevance = metadata['context_tags'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_PREDICTED_FUTURE_ACCESS * predicted_future_access +
                 WEIGHT_CONTEXT_RELEVANCE * context_relevance)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, sets the last access time to the current time, adjusts the predicted future access time based on recent patterns, and re-evaluates the relevance of context tags.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access'][key] = cache_snapshot.access_count + 100  # Example pattern
    metadata['context_tags'][key] = 1  # Example context relevance

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the predicted future access time based on initial patterns, and assigns context tags based on the current environment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access'][key] = cache_snapshot.access_count + 100  # Example pattern
    metadata['context_tags'][key] = 1  # Example context relevance

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted object and rebalances the remaining metadata to ensure optimal latency and resource allocation.
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
    if evicted_key in metadata['predicted_future_access']:
        del metadata['predicted_future_access'][evicted_key]
    if evicted_key in metadata['context_tags']:
        del metadata['context_tags'][evicted_key]