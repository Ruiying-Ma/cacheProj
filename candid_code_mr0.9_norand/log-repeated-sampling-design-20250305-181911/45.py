# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1.0
INITIAL_BOOST = 0.5
NORMALIZATION_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a list of objects' access patterns and a priority score for each object, which is influenced by access frequency, recency, and an unpredictability measure. Each access pattern is represented as a string of recent accesses and is used to dynamically adjust an object's priority score.
priority_scores = {}
access_patterns = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest priority score. If multiple objects have the same low priority score, it selects the one with the least predictable access pattern, breaking ties by the least recently used if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    least_predictable = float('inf')
    least_recent = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_scores.get(key, DEFAULT_PRIORITY)
        pattern = access_patterns.get(key, "")
        unpredictability = len(set(pattern))  # Simple unpredictability measure
        last_access = int(pattern[-1]) if pattern else float('inf')

        if (priority < min_priority or
            (priority == min_priority and unpredictability < least_predictable) or
            (priority == min_priority and unpredictability == least_predictable and last_access < least_recent)):
            min_priority = priority
            least_predictable = unpredictability
            least_recent = last_access
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's priority score is incremented based on its frequency and recency of access. The access pattern string is updated by appending the current access time, and a recalibration of the unpredictability measure is performed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    priority_scores[key] = priority_scores.get(key, DEFAULT_PRIORITY) + 1
    access_patterns[key] = access_patterns.get(key, "") + str(cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score to a default base value and begins tracking its access pattern. The priority score is then adjusted according to an initial boost to account for freshness.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    priority_scores[key] = DEFAULT_PRIORITY + INITIAL_BOOST
    access_patterns[key] = str(cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After an eviction occurs, the priority scores of remaining objects are normalized to prevent saturation and recalibrated to maintain a balanced distribution. The access patterns of the remaining objects are also reviewed to ensure consistency in unpredictability measurement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
    if evicted_key in access_patterns:
        del access_patterns[evicted_key]

    for key in priority_scores:
        priority_scores[key] *= NORMALIZATION_FACTOR