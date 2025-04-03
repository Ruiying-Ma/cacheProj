# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_THRESHOLD_SCORE = 1.0
CALIBRATION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and an adaptive threshold score for each cache entry. It also keeps a system calibration factor to adjust predictions based on real-time system performance.
metadata = {}
system_calibration_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the predicted future access time, access frequency, and the adaptive threshold score. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (meta['predicted_future_access_time'] * system_calibration_factor) / (meta['access_frequency'] * meta['adaptive_threshold_score'])
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the last access time and increments the access frequency for the accessed entry. It also recalculates the predicted future access time using the updated access pattern and adjusts the adaptive threshold score based on the system calibration factor.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    meta = metadata[key]
    
    meta['last_access_time'] = current_time
    meta['access_frequency'] += 1
    meta['predicted_future_access_time'] = current_time + (1 / meta['access_frequency'])
    meta['adaptive_threshold_score'] *= (1 + CALIBRATION_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, predicts the future access time based on initial patterns, and assigns an initial adaptive threshold score. The system calibration factor is also updated to reflect the new cache state.
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
        'predicted_future_access_time': current_time + 1,
        'adaptive_threshold_score': INITIAL_THRESHOLD_SCORE
    }
    
    global system_calibration_factor
    system_calibration_factor = 1 + (CALIBRATION_FACTOR * len(cache_snapshot.cache) / cache_snapshot.capacity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the system calibration factor to account for the change in cache composition. It also adjusts the adaptive threshold scores of remaining entries to ensure optimal future predictions and evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    global system_calibration_factor
    system_calibration_factor = 1 + (CALIBRATION_FACTOR * len(cache_snapshot.cache) / cache_snapshot.capacity)
    
    for key, meta in metadata.items():
        meta['adaptive_threshold_score'] *= (1 - CALIBRATION_FACTOR)