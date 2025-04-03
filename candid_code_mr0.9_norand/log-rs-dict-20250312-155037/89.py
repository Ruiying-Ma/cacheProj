# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a 'spectral score' for each cache entry, which is a composite score derived from access frequency, recency, and a pseudo-random factor. Additionally, it keeps track of the total number of accesses and the time since the last access for each entry.
spectral_scores = {}
access_frequencies = {}
last_access_times = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest spectral score. If multiple entries have the same score, it uses the pseudo-random factor to break ties, ensuring a balanced eviction strategy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = spectral_scores[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
        elif score == min_score:
            # Use pseudo-random factor to break ties
            if key < candid_obj_key:
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the spectral score of the accessed entry is incremented based on a weighted combination of its frequency and recency. The time since the last access is reset, and the total number of accesses is updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] += 1
    last_access_times[key] = cache_snapshot.access_count
    
    frequency_score = FREQUENCY_WEIGHT * access_frequencies[key]
    recency_score = RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[key])
    spectral_scores[key] = frequency_score + recency_score

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial spectral score based on a pseudo-random factor and sets the time since the last access to zero. The total number of accesses is initialized to one.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequencies[key] = 1
    last_access_times[key] = cache_snapshot.access_count
    
    # Pseudo-random factor based on key
    pseudo_random_factor = sum(ord(char) for char in key) % 100
    spectral_scores[key] = pseudo_random_factor

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates the spectral scores of remaining entries to ensure they reflect the current cache state. The total number of accesses and time since last access for each remaining entry are adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del spectral_scores[evicted_key]
    del access_frequencies[evicted_key]
    del last_access_times[evicted_key]
    
    for key in cache_snapshot.cache:
        frequency_score = FREQUENCY_WEIGHT * access_frequencies[key]
        recency_score = RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[key])
        spectral_scores[key] = frequency_score + recency_score