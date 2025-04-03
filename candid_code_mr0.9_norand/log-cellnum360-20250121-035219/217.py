# Import anything you need below
import time

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.2
LAST_ACCESS_WEIGHT = 0.3
PREDICTED_ACCESS_WEIGHT = 0.3
LOAD_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, load on the system, and context tags for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'context_tags': {},
    'load': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that considers low predicted future access time, low access frequency, high load on the system, and context irrelevance.
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
        predicted_future_access_time = metadata['predicted_future_access_time'].get(key, float('inf'))
        context_tags = metadata['context_tags'].get(key, set())
        
        score = (FREQUENCY_WEIGHT * access_frequency +
                 LAST_ACCESS_WEIGHT * (cache_snapshot.access_count - last_access_time) +
                 PREDICTED_ACCESS_WEIGHT * predicted_future_access_time +
                 LOAD_WEIGHT * metadata['load'])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and adjusts the predicted future access time based on recent patterns. It also updates the context tags to reflect the current usage scenario.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust predicted future access time based on recent patterns (simple heuristic)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10
    # Update context tags (dummy implementation)
    metadata['context_tags'][key] = {'current_usage'}

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, predicts the future access time based on initial context, and tags the object with relevant context information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10
    metadata['context_tags'][key] = {'initial_context'}

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the load on the system, adjusts the predicted future access times for remaining objects, and updates the context tags to reflect the new cache state.
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
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['context_tags']:
        del metadata['context_tags'][evicted_key]
    
    # Recalculate load on the system (dummy implementation)
    metadata['load'] = sum(obj.size for obj in cache_snapshot.cache.values()) / cache_snapshot.capacity
    # Adjust predicted future access times for remaining objects (simple heuristic)
    for key in cache_snapshot.cache:
        metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10
    # Update context tags to reflect the new cache state (dummy implementation)
    for key in cache_snapshot.cache:
        metadata['context_tags'][key] = {'updated_context'}