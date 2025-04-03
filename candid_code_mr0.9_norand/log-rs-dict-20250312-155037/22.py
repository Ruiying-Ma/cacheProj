# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
NEURAL_ACTIVITY_DEFAULT = 1
CHELEM_DEFAULT = 1
CENANTHY_DEFAULT = 1
CARTILAGE_DEFAULT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including neural activity scores, chelem scores, cenanthy scores, and cartilage scores for each cache entry. Neural activity scores represent the frequency and recency of access, chelem scores represent the importance of the data, cenanthy scores represent the connectivity of the data to other entries, and cartilage scores represent the structural integrity of the cache entry.
metadata = {
    'neural_activity': {},
    'chelem': {},
    'cenanthy': {},
    'cartilage': {}
}

def composite_score(key):
    return (metadata['neural_activity'][key] + 
            metadata['chelem'][key] + 
            metadata['cenanthy'][key] + 
            metadata['cartilage'][key])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a composite score derived from the neural activity, chelem, cenanthy, and cartilage scores. The entry with the lowest composite score is selected for eviction, ensuring a balance between recency, importance, connectivity, and structural integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the neural activity score is increased to reflect the recent access, the chelem score is adjusted based on the importance of the access, the cenanthy score is updated to reflect any changes in connectivity, and the cartilage score is checked and maintained to ensure structural integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['neural_activity'][key] += 1
    metadata['chelem'][key] += 1
    metadata['cenanthy'][key] += 1
    metadata['cartilage'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, initial neural activity, chelem, cenanthy, and cartilage scores are assigned based on the object's characteristics. The scores are set to default values that will be adjusted as the object is accessed and interacts with other cache entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['neural_activity'][key] = NEURAL_ACTIVITY_DEFAULT
    metadata['chelem'][key] = CHELEM_DEFAULT
    metadata['cenanthy'][key] = CENANTHY_DEFAULT
    metadata['cartilage'][key] = CARTILAGE_DEFAULT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the composite scores for remaining entries to ensure balance and updates the neural activity, chelem, cenanthy, and cartilage scores to reflect the new cache state. This ensures that the cache adapts dynamically to changes in its contents.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['neural_activity'][evicted_key]
    del metadata['chelem'][evicted_key]
    del metadata['cenanthy'][evicted_key]
    del metadata['cartilage'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['neural_activity'][key] += 1
        metadata['chelem'][key] += 1
        metadata['cenanthy'][key] += 1
        metadata['cartilage'][key] += 1