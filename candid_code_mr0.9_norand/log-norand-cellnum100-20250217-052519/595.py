# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
LFU_WEIGHT = 0.4
LRU_WEIGHT = 0.4
PREDICTED_ACCESS_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and context tags (e.g., user behavior, application type). It also tracks system load and cache hit/miss rates in real-time.
metadata = {
    'access_frequency': {},  # {key: frequency}
    'last_access_time': {},  # {key: last_access_time}
    'predicted_future_access_time': {},  # {key: predicted_future_access_time}
    'context_tags': {},  # {key: context_tags}
    'system_load': 0,  # system load metric
    'hit_rate': 0,  # cache hit rate
    'miss_rate': 0,  # cache miss rate
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining least frequently used, least recently used, and least likely to be accessed soon (based on predictive analytics). It also considers the current system load to balance performance.
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
        
        score = (LFU_WEIGHT * frequency) + (LRU_WEIGHT * (cache_snapshot.access_count - last_access)) + (PREDICTED_ACCESS_WEIGHT * predicted_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and refines the predicted future access time using real-time analytics. It also updates the context tags based on the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10  # Example prediction logic
    metadata['context_tags'][key] = 'updated_context'  # Example context update

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the last access time to the current time, and predicts its future access time. It also assigns context tags based on the insertion context and updates system load metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10  # Example prediction logic
    metadata['context_tags'][key] = 'initial_context'  # Example context assignment
    metadata['system_load'] = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the system load and cache hit/miss rates. It also refines the predictive model using the eviction data and updates the context tags to improve future predictions.
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
    if key in metadata['context_tags']:
        del metadata['context_tags'][key]
    
    metadata['system_load'] = cache_snapshot.size / cache_snapshot.capacity
    metadata['hit_rate'] = cache_snapshot.hit_count / cache_snapshot.access_count
    metadata['miss_rate'] = cache_snapshot.miss_count / cache_snapshot.access_count