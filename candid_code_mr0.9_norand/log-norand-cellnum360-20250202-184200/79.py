# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
INITIAL_PREDICTED_FUTURE_ACCESS_TIME = 10  # Initial predicted future access time

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and coherence state for each cache entry.
metadata = collections.defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_time': 0,
    'predicted_future_access_time': INITIAL_PREDICTED_FUTURE_ACCESS_TIME,
    'coherence_state': 'invalid'
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a dynamic scoring system that considers the least frequently accessed, longest time since last access, and the predicted future access time. Entries with lower scores are evicted first.
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
        score = (meta['access_frequency'] + 
                 (cache_snapshot.access_count - meta['last_access_time']) + 
                 meta['predicted_future_access_time'])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, updates the last access time to the current time, and recalculates the predicted future access time based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = cache_snapshot.access_count
    meta['predicted_future_access_time'] = (meta['predicted_future_access_time'] + 
                                            (cache_snapshot.access_count - meta['last_access_time'])) // 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, and estimates the predicted future access time based on initial access patterns. The coherence state is set to valid.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'predicted_future_access_time': INITIAL_PREDICTED_FUTURE_ACCESS_TIME,
        'coherence_state': 'valid'
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and adjusts the dynamic scoring thresholds to better predict future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]