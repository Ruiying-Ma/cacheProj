# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
AMPHECLEXSIS_WEIGHT = 0.5
MADRIER_WEIGHT = 0.3
FOSSIL_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains four metadata attributes for each cache entry: Ampheclexis (access frequency), Madrier (time since last access), Fossil (age of the entry), and Bielding (priority score based on a combination of the other three attributes).
metadata = {}

def calculate_bielding(ampheclexis, madrier, fossil):
    return (AMPHECLEXSIS_WEIGHT * ampheclexis) + (MADRIER_WEIGHT * madrier) + (FOSSIL_WEIGHT * fossil)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest Bielding score, which is calculated using a weighted formula that considers Ampheclexis, Madrier, and Fossil. Entries with lower access frequency, longer time since last access, and older age are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_bielding = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        ampheclexis, madrier, fossil, bielding = metadata[key]
        if bielding < lowest_bielding:
            lowest_bielding = bielding
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, Ampheclexis is incremented, Madrier is reset to zero, Fossil remains unchanged, and Bielding is recalculated to reflect the updated Ampheclexis and Madrier values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    ampheclexis, madrier, fossil, _ = metadata[key]
    ampheclexis += 1
    madrier = 0
    bielding = calculate_bielding(ampheclexis, madrier, fossil)
    metadata[key] = (ampheclexis, madrier, fossil, bielding)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, Ampheclexis is initialized to one, Madrier is set to zero, Fossil is set to the current time, and Bielding is calculated based on the initial values of Ampheclexis, Madrier, and Fossil.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    ampheclexis = 1
    madrier = 0
    fossil = cache_snapshot.access_count
    bielding = calculate_bielding(ampheclexis, madrier, fossil)
    metadata[key] = (ampheclexis, madrier, fossil, bielding)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted entry is removed from the cache. The remaining entries' Bielding scores are recalculated to ensure the eviction policy remains accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        ampheclexis, madrier, fossil, _ = metadata[key]
        madrier += 1
        bielding = calculate_bielding(ampheclexis, madrier, fossil)
        metadata[key] = (ampheclexis, madrier, fossil, bielding)