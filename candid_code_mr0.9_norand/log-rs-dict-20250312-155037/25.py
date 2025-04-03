# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASE_SOLUBILITY_INDEX = 1
BASE_SHUTTLECOCK_FACTOR = 1
BASE_NEORAMA_SCORE = 1
BASE_BROMODEOXYURIDINE_LEVEL = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including 'solubility_index', 'shuttlecock_factor', 'neorama_score', and 'bromodeoxyuridine_level' for each cache entry. These metrics are derived from the access patterns, frequency, and recency of usage, as well as the computational complexity of the data.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a composite score calculated from the solubility_index, shuttlecock_factor, neorama_score, and bromodeoxyuridine_level. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (metadata[key]['solubility_index'] +
                           metadata[key]['shuttlecock_factor'] +
                           metadata[key]['neorama_score'] +
                           metadata[key]['bromodeoxyuridine_level'])
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the solubility_index is increased to reflect higher access frequency, the shuttlecock_factor is adjusted to account for the recency of access, the neorama_score is recalculated based on the new access pattern, and the bromodeoxyuridine_level is updated to reflect the computational complexity of the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['solubility_index'] += 1
    metadata[key]['shuttlecock_factor'] = cache_snapshot.access_count
    metadata[key]['neorama_score'] = metadata[key]['solubility_index'] / (cache_snapshot.access_count - metadata[key]['shuttlecock_factor'] + 1)
    metadata[key]['bromodeoxyuridine_level'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the solubility_index is initialized to a base value, the shuttlecock_factor is set to reflect the initial recency, the neorama_score is calculated based on initial access patterns, and the bromodeoxyuridine_level is set according to the computational complexity of the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'solubility_index': BASE_SOLUBILITY_INDEX,
        'shuttlecock_factor': cache_snapshot.access_count,
        'neorama_score': BASE_NEORAMA_SCORE,
        'bromodeoxyuridine_level': BASE_BROMODEOXYURIDINE_LEVEL
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the solubility_index, shuttlecock_factor, neorama_score, and bromodeoxyuridine_level of the remaining entries are recalibrated to ensure balanced cache management and to reflect the removal of the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata[key]['solubility_index'] = max(BASE_SOLUBILITY_INDEX, metadata[key]['solubility_index'] - 1)
        metadata[key]['shuttlecock_factor'] = cache_snapshot.access_count
        metadata[key]['neorama_score'] = metadata[key]['solubility_index'] / (cache_snapshot.access_count - metadata[key]['shuttlecock_factor'] + 1)
        metadata[key]['bromodeoxyuridine_level'] = max(BASE_BROMODEOXYURIDINE_LEVEL, metadata[key]['bromodeoxyuridine_level'] - 1)