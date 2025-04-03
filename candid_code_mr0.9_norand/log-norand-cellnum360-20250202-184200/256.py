# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
FUTURE_ACCESS_PREDICTION_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and state preservation markers for each cached object.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'state_preservation_marker': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining least frequently used (LFU) and least recently used (LRU) metrics, while also considering the predicted future access time. Objects with the lowest combined score and no state preservation markers are chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        if metadata['state_preservation_marker'].get(key, False):
            continue
        
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        future_access = metadata['predicted_future_access_time'].get(key, math.inf)
        
        score = access_freq + (cache_snapshot.access_count - last_access) + FUTURE_ACCESS_PREDICTION_WEIGHT * future_access
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency is incremented, the last access time is updated to the current time, and the predicted future access time is recalculated based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = predict_future_access_time(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, predicts the future access time based on initial patterns, and sets state preservation markers if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = predict_future_access_time(key)
    metadata['state_preservation_marker'][key] = False

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted object and recalibrates the predictive model to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][key]
    if key in metadata['state_preservation_marker']:
        del metadata['state_preservation_marker'][key]

def predict_future_access_time(key):
    '''
    This function predicts the future access time for a given object key based on recent access patterns.
    - Args:
        - `key`: The key of the object for which to predict future access time.
    - Return:
        - `predicted_time`: The predicted future access time.
    '''
    # For simplicity, we assume a basic prediction model where future access time is inversely proportional to access frequency.
    access_freq = metadata['access_frequency'].get(key, 1)
    return 1 / access_freq