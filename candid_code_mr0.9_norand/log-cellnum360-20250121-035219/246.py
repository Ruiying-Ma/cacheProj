# Import anything you need below
import math

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_PREDICTED_FUTURE_ACCESS = 1.0
WEIGHT_HEURISTIC_ERROR_MARGIN = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and a heuristic error margin for each cache entry.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a score for each entry based on a weighted combination of low access frequency, distant predicted future access time, and high heuristic error margin, evicting the entry with the highest score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (WEIGHT_ACCESS_FREQUENCY / meta['access_frequency']) + \
                (WEIGHT_PREDICTED_FUTURE_ACCESS * meta['predicted_future_access_time']) + \
                (WEIGHT_HEURISTIC_ERROR_MARGIN * meta['heuristic_error_margin'])
        
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, updates the last access time to the current time, and adjusts the predicted future access time based on recent access patterns while recalculating the heuristic error margin.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = current_time
    meta['predicted_future_access_time'] = current_time + (current_time - meta['last_access_time']) / meta['access_frequency']
    meta['heuristic_error_margin'] = abs(meta['predicted_future_access_time'] - current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, predicts the future access time based on initial patterns, and sets an initial heuristic error margin.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': current_time,
        'predicted_future_access_time': current_time + 1,  # Initial prediction
        'heuristic_error_margin': 1  # Initial error margin
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the heuristic error margins for the remaining entries to adaptively scale their frequency and prediction accuracy based on the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key, meta in metadata.items():
        meta['heuristic_error_margin'] = abs(meta['predicted_future_access_time'] - cache_snapshot.access_count)