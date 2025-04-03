# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, and a 'recency score' which is a weighted combination of frequency and recency.
metadata = {}

def calculate_recency_score(frequency, last_access_time, current_time):
    return FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * (current_time - last_access_time)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest recency score, which balances both infrequently accessed and least recently accessed entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_recency_score = float('inf')
    current_time = cache_snapshot.access_count

    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata[key]['frequency']
        last_access = metadata[key]['last_access']
        recency_score = calculate_recency_score(freq, last_access, current_time)
        if recency_score < min_recency_score:
            min_recency_score = recency_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the recency score is recalculated to reflect the increased frequency and recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    metadata[key]['frequency'] += 1
    metadata[key]['last_access'] = current_time
    metadata[key]['recency_score'] = calculate_recency_score(metadata[key]['frequency'], metadata[key]['last_access'], current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access timestamp is set to the current time, and the recency score is calculated based on these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    metadata[key] = {
        'frequency': 1,
        'last_access': current_time,
        'recency_score': calculate_recency_score(1, current_time, current_time)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata for the evicted entry is removed from the cache, and the recency scores of remaining entries are recalculated to ensure they reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]

    current_time = cache_snapshot.access_count
    for key in cache_snapshot.cache:
        metadata[key]['recency_score'] = calculate_recency_score(metadata[key]['frequency'], metadata[key]['last_access'], current_time)