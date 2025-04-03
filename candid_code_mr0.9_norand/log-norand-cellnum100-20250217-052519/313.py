# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASELINE_COHERENCE_SCORE = 1
INITIAL_FITNESS_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a coherence score for each cache entry, an evolutionary fitness score, a dynamic filter status, and a synchronization vector for tracking access patterns.
coherence_scores = {}
fitness_scores = {}
dynamic_filter_status = {}
synchronization_vector = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined coherence and fitness scores, while also considering the dynamic filter status and synchronization vector to ensure balanced eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = coherence_scores[key] + fitness_scores[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the coherence score of the accessed entry is increased, its fitness score is recalculated using an evolutionary algorithm, the dynamic filter status is updated to reflect recent access, and the synchronization vector is adjusted to capture the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    coherence_scores[key] += 1
    fitness_scores[key] = coherence_scores[key] * 2  # Example evolutionary algorithm
    dynamic_filter_status[key] = True
    synchronization_vector[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its coherence score to a baseline value, assigns an initial fitness score based on evolutionary principles, sets the dynamic filter status to active, and updates the synchronization vector to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    coherence_scores[key] = BASELINE_COHERENCE_SCORE
    fitness_scores[key] = INITIAL_FITNESS_SCORE
    dynamic_filter_status[key] = True
    synchronization_vector[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the coherence and fitness scores of remaining entries to reflect the new cache state, updates the dynamic filter to remove the evicted entry, and adjusts the synchronization vector to maintain accurate access pattern tracking.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del coherence_scores[evicted_key]
    del fitness_scores[evicted_key]
    del dynamic_filter_status[evicted_key]
    del synchronization_vector[evicted_key]
    
    for key in cache_snapshot.cache:
        coherence_scores[key] = max(BASELINE_COHERENCE_SCORE, coherence_scores[key] - 1)
        fitness_scores[key] = coherence_scores[key] * 2  # Example evolutionary algorithm
        synchronization_vector[key] = cache_snapshot.access_count