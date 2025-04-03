# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_RECENCY = 0
INITIAL_SILKINESS = 1.0
INITIAL_SUBLINGUAL = 1.0
INITIAL_SUBMEMBRANACEOUS = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a 'silkiness' score which is a composite measure of smoothness in access patterns. It also tracks sublingual and submembranaceous scores representing deeper contextual relevance and structural importance respectively.
metadata = {
    'access_frequency': {},
    'recency': {},
    'silkiness': {},
    'sublingual': {},
    'submembranaceous': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of silkiness, sublingual, and submembranaceous metrics. If scores are tied, the least recently used item is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    min_recency = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (metadata['silkiness'][key] + 
                          metadata['sublingual'][key] + 
                          metadata['submembranaceous'][key])
        if combined_score < min_combined_score or (combined_score == min_combined_score and metadata['recency'][key] < min_recency):
            min_combined_score = combined_score
            min_recency = metadata['recency'][key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency are updated. The silkiness score is recalculated to reflect the smoothness of access patterns. Sublingual and submembranaceous scores are adjusted based on the contextual relevance and structural importance of the access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['silkiness'][key] = 1.0 / metadata['access_frequency'][key]
    metadata['sublingual'][key] += 0.1  # Example adjustment
    metadata['submembranaceous'][key] += 0.1  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, initial values for access frequency, recency, silkiness, sublingual, and submembranaceous scores are set. These values are based on initial contextual and structural analysis.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = INITIAL_ACCESS_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['silkiness'][key] = INITIAL_SILKINESS
    metadata['sublingual'][key] = INITIAL_SUBLINGUAL
    metadata['submembranaceous'][key] = INITIAL_SUBMEMBRANACEOUS

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the silkiness, sublingual, and submembranaceous scores for the remaining objects to ensure the cache maintains optimal smoothness, contextual relevance, and structural importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['recency'][evicted_key]
    del metadata['silkiness'][evicted_key]
    del metadata['sublingual'][evicted_key]
    del metadata['submembranaceous'][evicted_key]

    for key in cache_snapshot.cache.keys():
        metadata['silkiness'][key] = 1.0 / metadata['access_frequency'][key]
        metadata['sublingual'][key] += 0.1  # Example adjustment
        metadata['submembranaceous'][key] += 0.1  # Example adjustment