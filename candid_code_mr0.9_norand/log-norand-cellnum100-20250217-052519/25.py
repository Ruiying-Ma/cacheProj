# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
INITIAL_ENTROPY = 1.0
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_DYNAMIC_SCORE = 1.0
ENTROPY_DECAY = 0.9
PREDICTIVE_SCORE_INCREMENT = 0.1
DYNAMIC_SCORE_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains an entropy score for each cache entry, a predictive model score based on access patterns, a dynamic allocation score reflecting the changing importance of entries, and a weighted score combining these factors.
metadata = {
    'entropy': {},
    'predictive_score': {},
    'dynamic_score': {},
    'weighted_score': {}
}

def calculate_weighted_score(entropy, predictive_score, dynamic_score):
    return entropy + predictive_score + dynamic_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest weighted score, which is a combination of entropy, predictive model score, and dynamic allocation score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_weighted_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        weighted_score = metadata['weighted_score'][key]
        if weighted_score < min_weighted_score:
            min_weighted_score = weighted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the entropy score is recalculated to reflect the reduced uncertainty, the predictive model score is updated based on the latest access pattern, and the dynamic allocation score is adjusted to increase the importance of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy'][key] *= ENTROPY_DECAY
    metadata['predictive_score'][key] += PREDICTIVE_SCORE_INCREMENT
    metadata['dynamic_score'][key] += DYNAMIC_SCORE_INCREMENT
    metadata['weighted_score'][key] = calculate_weighted_score(
        metadata['entropy'][key],
        metadata['predictive_score'][key],
        metadata['dynamic_score'][key]
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the entropy score is initialized based on initial uncertainty, the predictive model score is set using initial access predictions, and the dynamic allocation score is assigned a default value reflecting its initial importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy'][key] = INITIAL_ENTROPY
    metadata['predictive_score'][key] = INITIAL_PREDICTIVE_SCORE
    metadata['dynamic_score'][key] = INITIAL_DYNAMIC_SCORE
    metadata['weighted_score'][key] = calculate_weighted_score(
        metadata['entropy'][key],
        metadata['predictive_score'][key],
        metadata['dynamic_score'][key]
    )

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the weighted scores of remaining entries to ensure they reflect the current state of the cache, and adjusts the dynamic allocation scores to redistribute importance among the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['entropy'][evicted_key]
    del metadata['predictive_score'][evicted_key]
    del metadata['dynamic_score'][evicted_key]
    del metadata['weighted_score'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['dynamic_score'][key] += DYNAMIC_SCORE_INCREMENT
        metadata['weighted_score'][key] = calculate_weighted_score(
            metadata['entropy'][key],
            metadata['predictive_score'][key],
            metadata['dynamic_score'][key]
        )