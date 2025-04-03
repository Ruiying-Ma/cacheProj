# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
NEURALGIAC_INITIAL = 50
NEURALGIAC_DECREASE = 5
HYPSOBATHYMETRIC_INITIAL = 10
HYPSOBATHYMETRIC_INCREASE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, temporal access patterns, and spatial locality of cache objects. It also tracks neuralgiac scores representing the 'pain' or cost of eviction, and hypsobathymetric scores indicating the depth of access patterns over time.
metadata = {
    'access_frequency': {},
    'temporal_access_pattern': {},
    'spatial_locality': {},
    'neuralgiac_score': {},
    'hypsobathymetric_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest neuralgiac score and the highest hypsobathymetric score, prioritizing objects that are least painful to evict and have shallow access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_neuralgiac_score = float('inf')
    max_hypsobathymetric_score = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        neuralgiac_score = metadata['neuralgiac_score'][key]
        hypsobathymetric_score = metadata['hypsobathymetric_score'][key]
        
        if neuralgiac_score < min_neuralgiac_score or (neuralgiac_score == min_neuralgiac_score and hypsobathymetric_score > max_hypsobathymetric_score):
            min_neuralgiac_score = neuralgiac_score
            max_hypsobathymetric_score = hypsobathymetric_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increases the access frequency and adjusts the temporal access pattern to reflect recent usage. The neuralgiac score is decreased slightly to indicate reduced eviction cost, and the hypsobathymetric score is updated to reflect deeper access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['temporal_access_pattern'][key] = cache_snapshot.access_count
    metadata['neuralgiac_score'][key] = max(0, metadata['neuralgiac_score'][key] - NEURALGIAC_DECREASE)
    metadata['hypsobathymetric_score'][key] += HYPSOBATHYMETRIC_INCREASE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and sets initial temporal and spatial locality patterns. The neuralgiac score is set to a moderate level, and the hypsobathymetric score is initialized to reflect shallow access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['temporal_access_pattern'][key] = cache_snapshot.access_count
    metadata['spatial_locality'][key] = obj.size
    metadata['neuralgiac_score'][key] = NEURALGIAC_INITIAL
    metadata['hypsobathymetric_score'][key] = HYPSOBATHYMETRIC_INITIAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the neuralgiac scores of remaining objects to reflect the reduced overall 'pain' in the cache. The hypsobathymetric scores are adjusted to account for the removal of the evicted object's access patterns, and access frequencies are normalized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['temporal_access_pattern'][evicted_key]
    del metadata['spatial_locality'][evicted_key]
    del metadata['neuralgiac_score'][evicted_key]
    del metadata['hypsobathymetric_score'][evicted_key]
    
    total_access_frequency = sum(metadata['access_frequency'].values())
    for key in metadata['access_frequency']:
        metadata['neuralgiac_score'][key] = max(0, metadata['neuralgiac_score'][key] - NEURALGIAC_DECREASE)
        metadata['hypsobathymetric_score'][key] = max(0, metadata['hypsobathymetric_score'][key] - HYPSOBATHYMETRIC_INCREASE)
        metadata['access_frequency'][key] = metadata['access_frequency'][key] / total_access_frequency