# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
MAX_RECENCY_SCORE = 1000  # Maximum value for recency score

# Put the metadata specifically maintained by the policy below. The policy maintains an access counter and a recency score for each cache entry. The access counter tracks the number of times an item has been accessed, while the recency score is a decay-based metric that reduces over time if the item is not accessed.
access_counter = {}
recency_score = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combined score, which is calculated by dividing the access counter by the recency score. The entry with the lowest combined score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = access_counter[key] / recency_score[key]
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access counter for the entry is incremented, and the recency score is refreshed to its maximum value to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_counter[key] += 1
    recency_score[key] = MAX_RECENCY_SCORE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, its access counter is initialized to 1, and the recency score is set to its maximum value to indicate it is the most recently accessed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_counter[key] = 1
    recency_score[key] = MAX_RECENCY_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy does not need to update the metadata of remaining entries, but any global metadata such as the average recency score may be recalculated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in access_counter:
        del access_counter[evicted_key]
    if evicted_key in recency_score:
        del recency_score[evicted_key]