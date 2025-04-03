# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASE_JOY = 1
INITIAL_WORSHIP = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'joy' score for each cache entry, a 'flute' score representing access frequency, a 'worship' score indicating the importance of the entry, and a 'septerium' score representing the age of the entry.
joy_scores = {}
flute_scores = {}
worship_scores = {}
septerium_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score using the 'joy', 'flute', 'worship', and 'septerium' scores. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (joy_scores[key] + flute_scores[key] + worship_scores[key] + (cache_snapshot.access_count - septerium_scores[key]))
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the 'joy' score is incremented, the 'flute' score is increased to reflect higher access frequency, the 'worship' score is adjusted based on the importance of the access, and the 'septerium' score is reset to reflect the entry's renewed relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    joy_scores[key] += 1
    flute_scores[key] += 1
    worship_scores[key] += 1  # Adjust based on importance, here we increment by 1 for simplicity
    septerium_scores[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the 'joy' score is initialized to a base value, the 'flute' score starts at zero, the 'worship' score is set based on initial importance, and the 'septerium' score is set to the current time to track the age of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    joy_scores[key] = BASE_JOY
    flute_scores[key] = 0
    worship_scores[key] = INITIAL_WORSHIP
    septerium_scores[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the composite scores for remaining entries to ensure accurate ranking, and adjusts the 'joy', 'flute', 'worship', and 'septerium' scores to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del joy_scores[evicted_key]
    del flute_scores[evicted_key]
    del worship_scores[evicted_key]
    del septerium_scores[evicted_key]
    
    # Recalculate composite scores for remaining entries
    for key in cache_snapshot.cache.keys():
        joy_scores[key] = joy_scores[key]  # No change
        flute_scores[key] = flute_scores[key]  # No change
        worship_scores[key] = worship_scores[key]  # No change
        septerium_scores[key] = septerium_scores[key]  # No change