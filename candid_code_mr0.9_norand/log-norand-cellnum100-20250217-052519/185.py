# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
FAIRNESS_WEIGHT = 0.5
PREDICTIVE_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, a predictive score based on historical access patterns, and a fairness score to ensure diverse access patterns are considered.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'recency': {},           # {obj.key: last_access_time}
    'predictive_score': {},  # {obj.key: predictive_score}
    'fairness_score': {}     # {obj.key: fairness_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the predictive score and fairness score, prioritizing objects with low predictive scores and adjusting for cognitive biases to ensure fair representation of different access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (PREDICTIVE_WEIGHT * metadata['predictive_score'][key] +
                          FAIRNESS_WEIGHT * metadata['fairness_score'][key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency of the accessed object are updated, the predictive score is recalculated based on the latest access pattern, and the fairness score is adjusted to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = 1 / metadata['access_frequency'][key]
    metadata['fairness_score'][key] = cache_snapshot.access_count - metadata['recency'][key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency, assigns an initial predictive score based on similar objects, and sets a baseline fairness score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = 1
    metadata['fairness_score'][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the predictive and fairness scores for the remaining objects to ensure the eviction decision aligns with the overall access patterns and fairness considerations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]
    if evicted_key in metadata['fairness_score']:
        del metadata['fairness_score'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] = 1 / metadata['access_frequency'][key]
        metadata['fairness_score'][key] = cache_snapshot.access_count - metadata['recency'][key]