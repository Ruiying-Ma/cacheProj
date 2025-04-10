# Import anything you need below
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.25
WEIGHT_LAST_ACCESS_TIME = 0.25
WEIGHT_PREDICTED_FUTURE_ACCESS_TIME = 0.25
WEIGHT_PREFETCHING_SUCCESS_RATE = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and prefetching success rate for each cache entry.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, low predicted future access time, and low prefetching success rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (WEIGHT_ACCESS_FREQUENCY * (1 / meta['access_frequency']) +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - meta['last_access_time']) +
                 WEIGHT_PREDICTED_FUTURE_ACCESS_TIME * meta['predicted_future_access_time'] +
                 WEIGHT_PREFETCHING_SUCCESS_RATE * (1 - meta['prefetching_success_rate']))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, updates the last access time to the current time, and adjusts the predicted future access time based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = cache_snapshot.access_count
    # Adjust predicted future access time based on recent access patterns
    meta['predicted_future_access_time'] = (meta['predicted_future_access_time'] + (cache_snapshot.access_count - meta['last_access_time'])) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the predicted future access time based on similar objects, and initializes the prefetching success rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'predicted_future_access_time': estimate_predicted_future_access_time(obj),
        'prefetching_success_rate': 0.5  # Initial guess
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the weighted scores for remaining entries, adjusts the prefetching strategy based on the success rate, and updates the overall cache state to optimize for future latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalculate weighted scores for remaining entries
    for key, meta in metadata.items():
        meta['weighted_score'] = (WEIGHT_ACCESS_FREQUENCY * (1 / meta['access_frequency']) +
                                  WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - meta['last_access_time']) +
                                  WEIGHT_PREDICTED_FUTURE_ACCESS_TIME * meta['predicted_future_access_time'] +
                                  WEIGHT_PREFETCHING_SUCCESS_RATE * (1 - meta['prefetching_success_rate']))
    
    # Adjust prefetching strategy based on the success rate
    for key, meta in metadata.items():
        if meta['prefetching_success_rate'] < 0.5:
            meta['prefetching_success_rate'] *= 1.1  # Increase prefetching success rate
        else:
            meta['prefetching_success_rate'] *= 0.9  # Decrease prefetching success rate

def estimate_predicted_future_access_time(obj):
    '''
    Estimate the predicted future access time based on similar objects.
    - Args:
        - `obj`: The object for which to estimate the predicted future access time.
    - Return:
        - `predicted_future_access_time`: The estimated predicted future access time.
    '''
    # For simplicity, we return a constant value. In a real implementation, this could be based on historical data.
    return 100