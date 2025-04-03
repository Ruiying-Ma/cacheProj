# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_UNPERSUADEDNESS_LEVEL = 1
DEFAULT_CHILDLIER_SCORE = 1
DEFAULT_COTTAGE_FACTOR = 1
DEFAULT_HYDROFRANKLINITE_INDEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including 'childlier_score' which represents the frequency of access by younger processes, 'unpersuadedness_level' indicating resistance to eviction, 'cottage_factor' representing spatial locality, and 'hydrofranklinite_index' which measures the energy efficiency of keeping the object in the cache.
metadata = {
    'childlier_score': {},
    'unpersuadedness_level': {},
    'cottage_factor': {},
    'hydrofranklinite_index': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of 'childlier_score', 'unpersuadedness_level', 'cottage_factor', and 'hydrofranklinite_index'. Objects with lower scores are considered less beneficial to retain.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (metadata['childlier_score'][key] +
                          metadata['unpersuadedness_level'][key] +
                          metadata['cottage_factor'][key] +
                          metadata['hydrofranklinite_index'][key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the 'childlier_score' is incremented to reflect increased access by younger processes, 'unpersuadedness_level' is slightly increased to show resistance to eviction, 'cottage_factor' is adjusted based on spatial locality changes, and 'hydrofranklinite_index' is recalculated to reflect current energy efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['childlier_score'][key] += 1
    metadata['unpersuadedness_level'][key] += 1
    metadata['cottage_factor'][key] += 1
    metadata['hydrofranklinite_index'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, 'childlier_score' is initialized based on the accessing process's age, 'unpersuadedness_level' starts at a default value, 'cottage_factor' is set according to initial spatial locality, and 'hydrofranklinite_index' is calculated based on initial energy efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['childlier_score'][key] = DEFAULT_CHILDLIER_SCORE
    metadata['unpersuadedness_level'][key] = DEFAULT_UNPERSUADEDNESS_LEVEL
    metadata['cottage_factor'][key] = DEFAULT_COTTAGE_FACTOR
    metadata['hydrofranklinite_index'][key] = DEFAULT_HYDROFRANKLINITE_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy recalculates 'childlier_score' for remaining objects to reflect changes in access patterns, 'unpersuadedness_level' is adjusted for remaining objects to reflect their new resistance levels, 'cottage_factor' is updated to reflect new spatial locality, and 'hydrofranklinite_index' is recalculated to ensure optimal energy efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['childlier_score']:
        del metadata['childlier_score'][evicted_key]
    if evicted_key in metadata['unpersuadedness_level']:
        del metadata['unpersuadedness_level'][evicted_key]
    if evicted_key in metadata['cottage_factor']:
        del metadata['cottage_factor'][evicted_key]
    if evicted_key in metadata['hydrofranklinite_index']:
        del metadata['hydrofranklinite_index'][evicted_key]

    for key in cache_snapshot.cache.keys():
        metadata['childlier_score'][key] += 1
        metadata['unpersuadedness_level'][key] += 1
        metadata['cottage_factor'][key] += 1
        metadata['hydrofranklinite_index'][key] += 1