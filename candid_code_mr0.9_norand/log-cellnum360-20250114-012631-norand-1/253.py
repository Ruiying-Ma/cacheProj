# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_HEURISTIC_SCORE = 1.0
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_PREDICTED_FUTURE_ACCESS = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and a heuristic score for each cache entry. It also tracks a global quantum alignment factor to synchronize cache operations.
metadata = {}
global_quantum_alignment_factor = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry based on its access frequency, recency, predicted future access, and heuristic score. The entry with the lowest composite score is selected for eviction.
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
        composite_score = (meta['access_frequency'] + 
                           (cache_snapshot.access_count - meta['last_access_timestamp']) + 
                           meta['predicted_future_access'] + 
                           meta['heuristic_score'])
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access timestamp of the hit entry. It also recalculates the predicted future access time and adjusts the heuristic score based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    meta['predicted_future_access'] = (meta['predicted_future_access'] + 
                                       (cache_snapshot.access_count - meta['last_access_timestamp'])) / 2
    meta['heuristic_score'] = meta['access_frequency'] / (cache_snapshot.access_count - meta['last_access_timestamp'] + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, sets the current timestamp as the last access time, predicts its next access time based on initial patterns, and assigns an initial heuristic score. The global quantum alignment factor is also updated to reflect the new state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': INITIAL_ACCESS_FREQUENCY,
        'last_access_timestamp': cache_snapshot.access_count,
        'predicted_future_access': INITIAL_PREDICTED_FUTURE_ACCESS,
        'heuristic_score': INITIAL_HEURISTIC_SCORE
    }
    global global_quantum_alignment_factor
    global_quantum_alignment_factor += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the global quantum alignment factor to ensure synchronization. It also adjusts the heuristic scores of remaining entries to reflect the change in cache composition and updates any predictive models based on the eviction event.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    global global_quantum_alignment_factor
    global_quantum_alignment_factor -= 1
    
    for key, meta in metadata.items():
        meta['heuristic_score'] = meta['access_frequency'] / (cache_snapshot.access_count - meta['last_access_timestamp'] + 1)