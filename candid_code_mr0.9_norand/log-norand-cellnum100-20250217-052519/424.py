# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_FAILURE_RATE = 0.2
WEIGHT_LOAD_DISTRIBUTION = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted failure rates, and load distribution across cache layers.
metadata = {
    'access_frequency': {},  # key -> access frequency
    'last_access_time': {},  # key -> last access time
    'predicted_failure_rate': {},  # key -> predicted failure rate
    'load_distribution': {}  # key -> load distribution
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, high predicted failure rate, and current load on the cache layer.
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
        predicted_failure_rate = metadata['predicted_failure_rate'].get(key, 0)
        load_distribution = metadata['load_distribution'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * (1 / (access_frequency + 1)) +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_FAILURE_RATE * predicted_failure_rate +
                 WEIGHT_LOAD_DISTRIBUTION * load_distribution)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and last access time for the accessed object, and adjusts the load distribution to reflect the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Adjust load distribution if necessary (not specified how, so we assume no change)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access time, updates the predicted failure rate based on object characteristics, and recalculates the load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_failure_rate'][key] = 1 / (obj.size + 1)  # Example heuristic
    metadata['load_distribution'][key] = obj.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes its metadata, recalculates the load distribution, and adjusts the predicted failure rates for remaining objects if necessary.
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
    if evicted_key in metadata['predicted_failure_rate']:
        del metadata['predicted_failure_rate'][evicted_key]
    if evicted_key in metadata['load_distribution']:
        del metadata['load_distribution'][evicted_key]
    
    # Recalculate load distribution for remaining objects
    total_size = sum(obj.size for obj in cache_snapshot.cache.values())
    for key in cache_snapshot.cache:
        metadata['load_distribution'][key] = cache_snapshot.cache[key].size / total_size