# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.25
RECENCY_WEIGHT = 0.25
SIZE_WEIGHT = 0.25
TYPE_WEIGHT = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency (Collarman), access recency (Spavined), object size (Graphite), and object type (Stegocephalian).
collarman = {}
spavined = {}
graphite = {}
stegocephalian = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score based on the metadata. Objects with low access frequency, old access recency, large size, and less critical type are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = collarman[key]
        recency = cache_snapshot.access_count - spavined[key]
        size = graphite[key]
        type_priority = stegocephalian[key]
        
        score = (FREQUENCY_WEIGHT * frequency +
                 RECENCY_WEIGHT * recency +
                 SIZE_WEIGHT * size +
                 TYPE_WEIGHT * type_priority)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency (Collarman) is incremented, access recency (Spavined) is updated to the current time, object size (Graphite) remains unchanged, and object type (Stegocephalian) is re-evaluated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    collarman[key] += 1
    spavined[key] = cache_snapshot.access_count
    # Assuming object type re-evaluation is not necessary for this example

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency (Collarman) is initialized to 1, access recency (Spavined) is set to the current time, object size (Graphite) is recorded, and object type (Stegocephalian) is classified.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    collarman[key] = 1
    spavined[key] = cache_snapshot.access_count
    graphite[key] = obj.size
    stegocephalian[key] = classify_object_type(obj)  # Assuming a function classify_object_type exists

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the metadata for access frequency (Collarman), access recency (Spavined), object size (Graphite), and object type (Stegocephalian) are removed for the evicted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    del collarman[key]
    del spavined[key]
    del graphite[key]
    del stegocephalian[key]

def classify_object_type(obj):
    '''
    Dummy function to classify object type. Replace with actual classification logic.
    '''
    return 1  # Assuming all objects have the same type priority for this example