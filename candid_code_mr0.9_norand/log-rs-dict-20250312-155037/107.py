# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
SPICE_LEVEL_INCREMENT = 1
BASELINE_PUBLIC_INTEREST = 10
INITIAL_SPICE_LEVEL = 5
INITIAL_LUCK_FACTOR = 5
INITIAL_ACTIVITY_PATTERN = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a 'spice level' score for each cache entry, inspired by Zanthoxylum (a spicy plant). It also keeps track of 'public interest' levels, akin to Semipublic, and a 'luck factor' derived from Penney's game. Additionally, it records 'activity patterns' similar to Desmodactyli's unique movements.
spice_levels = {}
public_interests = {}
luck_factors = {}
activity_patterns = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of spice level, public interest, luck factor, and activity patterns. Entries with the least engagement and lowest scores across these metrics are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (spice_levels[key] + public_interests[key] + luck_factors[key] + activity_patterns[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the spice level of the accessed entry is increased slightly, public interest is boosted, luck factor is recalculated based on recent access patterns, and activity patterns are updated to reflect the latest access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    spice_levels[key] += SPICE_LEVEL_INCREMENT
    public_interests[key] += 1
    luck_factors[key] = (luck_factors[key] + cache_snapshot.access_count) % 100
    activity_patterns[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, the policy assigns initial spice level based on the object's type, sets a baseline public interest, initializes luck factor randomly, and starts tracking activity patterns from the moment of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    spice_levels[key] = INITIAL_SPICE_LEVEL
    public_interests[key] = BASELINE_PUBLIC_INTEREST
    luck_factors[key] = INITIAL_LUCK_FACTOR
    activity_patterns[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy redistributes the spice level among remaining entries, adjusts public interest levels to reflect the removal, recalculates luck factors to account for the change, and updates activity patterns to ensure smooth transitions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    remaining_keys = cache_snapshot.cache.keys()
    
    # Redistribute spice levels
    total_spice = sum(spice_levels[key] for key in remaining_keys)
    for key in remaining_keys:
        spice_levels[key] = total_spice // len(remaining_keys)
    
    # Adjust public interest levels
    total_interest = sum(public_interests[key] for key in remaining_keys)
    for key in remaining_keys:
        public_interests[key] = total_interest // len(remaining_keys)
    
    # Recalculate luck factors
    for key in remaining_keys:
        luck_factors[key] = (luck_factors[key] + cache_snapshot.access_count) % 100
    
    # Update activity patterns
    for key in remaining_keys:
        activity_patterns[key] = cache_snapshot.access_count