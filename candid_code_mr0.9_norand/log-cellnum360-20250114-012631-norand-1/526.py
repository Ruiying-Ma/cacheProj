# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import hashlib

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
LAST_ACCESS_WEIGHT = 0.3
PREDICTED_ACCESS_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and error correction codes for each cache entry. It also tracks the current load on the system to dynamically balance cache usage.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'error_correction_codes': {},
    'system_load': 0
}

def calculate_error_correction_code(obj):
    return hashlib.md5(obj.key.encode()).hexdigest()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the least frequently accessed, the longest time since last access, and the least likely to be accessed in the near future as predicted by a machine learning model. It also considers the current system load to avoid evicting entries that might be needed soon under high load conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        predicted_access = metadata['predicted_future_access_time'].get(key, float('inf'))
        
        score = (FREQUENCY_WEIGHT * frequency +
                 LAST_ACCESS_WEIGHT * (cache_snapshot.access_count - last_access) +
                 PREDICTED_ACCESS_WEIGHT * predicted_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and last access time for the hit entry. It also refines the predicted future access time using the latest access pattern and updates the error correction codes to ensure data integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Update predicted future access time (dummy implementation)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100
    metadata['error_correction_codes'][key] = calculate_error_correction_code(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency and last access time. It also generates an initial predicted future access time based on current access patterns and calculates the error correction codes for the new entry. The system load is also updated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Initial predicted future access time (dummy implementation)
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 100
    metadata['error_correction_codes'][key] = calculate_error_correction_code(obj)
    # Update system load (dummy implementation)
    metadata['system_load'] = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the metadata associated with the evicted entry. It then recalculates the system load and adjusts the predictive model to improve future eviction decisions. The error correction codes are also updated to ensure the remaining cache entries maintain data integrity.
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
    if key in metadata['error_correction_codes']:
        del metadata['error_correction_codes'][key]
    # Update system load (dummy implementation)
    metadata['system_load'] = cache_snapshot.size / cache_snapshot.capacity