# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
HIGH_NOVELTY_SCORE = 1000
NOVELTY_DECAY = 0.9
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
NOVELTY_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. Maintains access frequency and recency for each object as well as a novelty score which measures how recently new objects have been introduced.
access_frequency = {}
recency = {}
novelty_score = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    Chooses the eviction victim based on a weighted score combining low access frequency, low recency, and high novelty score ensuring both old and less accessed data get evicted to keep the cache fresh.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (FREQUENCY_WEIGHT * access_frequency[key] +
                 RECENCY_WEIGHT * (cache_snapshot.access_count - recency[key]) -
                 NOVELTY_WEIGHT * novelty_score[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Increases the access frequency and resets the recency to the current time for the accessed object while decreasing its novelty score slightly to reflect its ongoing relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency[key] = cache_snapshot.access_count
    novelty_score[key] *= NOVELTY_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Initializes the access frequency and recency and assigns a high novelty score to the newly inserted object to reflect its recent introduction into the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    novelty_score[key] = HIGH_NOVELTY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Shifts the novelty scores of remaining objects to slightly lower values to recalibrate the novelty spectrum within the cache, balancing between retaining frequently accessed data and introducing new objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in access_frequency:
        del access_frequency[evicted_key]
    if evicted_key in recency:
        del recency[evicted_key]
    if evicted_key in novelty_score:
        del novelty_score[evicted_key]
    
    for key in cache_snapshot.cache:
        novelty_score[key] *= NOVELTY_DECAY