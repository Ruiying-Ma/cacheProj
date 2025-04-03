# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
LAST_ACCESS_WEIGHT = 0.3
PREDICTED_ACCESS_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, resource usage statistics, and dynamic thresholds for each cache entry.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'predicted_future_access_time': {},  # {obj.key: predicted_future_access_time}
    'dynamic_thresholds': {
        'frequency_threshold': 1,
        'time_threshold': 1,
        'predicted_threshold': 1
    }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by considering a combination of the least frequently accessed, the longest time since last access, and the predicted future access time, while also balancing resource contention and load.
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
    Upon a cache hit, the policy updates the access frequency, last access time, and recalculates the predicted future access time for the accessed entry, while also adjusting dynamic thresholds based on current load and resource usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10  # Example prediction logic
    
    # Adjust dynamic thresholds
    total_accesses = cache_snapshot.access_count
    if total_accesses > 0:
        metadata['dynamic_thresholds']['frequency_threshold'] = sum(metadata['access_frequency'].values()) / len(metadata['access_frequency'])
        metadata['dynamic_thresholds']['time_threshold'] = total_accesses / len(metadata['last_access_time'])
        metadata['dynamic_thresholds']['predicted_threshold'] = sum(metadata['predicted_future_access_time'].values()) / len(metadata['predicted_future_access_time'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the last access time to the current time, predicts its future access time, and adjusts dynamic thresholds to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10  # Example prediction logic
    
    # Adjust dynamic thresholds
    total_accesses = cache_snapshot.access_count
    if total_accesses > 0:
        metadata['dynamic_thresholds']['frequency_threshold'] = sum(metadata['access_frequency'].values()) / len(metadata['access_frequency'])
        metadata['dynamic_thresholds']['time_threshold'] = total_accesses / len(metadata['last_access_time'])
        metadata['dynamic_thresholds']['predicted_threshold'] = sum(metadata['predicted_future_access_time'].values()) / len(metadata['predicted_future_access_time'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates resource usage statistics, updates load balancing metrics, and adjusts dynamic thresholds to reflect the removal of the evicted entry.
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
    
    # Adjust dynamic thresholds
    total_accesses = cache_snapshot.access_count
    if total_accesses > 0:
        if metadata['access_frequency']:
            metadata['dynamic_thresholds']['frequency_threshold'] = sum(metadata['access_frequency'].values()) / len(metadata['access_frequency'])
        if metadata['last_access_time']:
            metadata['dynamic_thresholds']['time_threshold'] = total_accesses / len(metadata['last_access_time'])
        if metadata['predicted_future_access_time']:
            metadata['dynamic_thresholds']['predicted_threshold'] = sum(metadata['predicted_future_access_time'].values()) / len(metadata['predicted_future_access_time'])