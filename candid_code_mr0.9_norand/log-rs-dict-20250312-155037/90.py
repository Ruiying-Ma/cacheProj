# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict

# Put tunable constant parameters below
FLATULENCE_DECREASE_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a unique 'flatulence' score that increases with each access. It also tracks interosseal connections, representing the relationship between cached items.
access_frequency = defaultdict(int)
recency = defaultdict(int)
flatulence_score = defaultdict(int)
interosseal_connections = defaultdict(lambda: defaultdict(int))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined score of access frequency, recency, and flatulence. Items with weak interosseal connections are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (access_frequency[key] + 
                          (cache_snapshot.access_count - recency[key]) + 
                          flatulence_score[key])
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
        elif combined_score == min_score:
            # Prioritize weak interosseal connections
            if interosseal_connections[key][obj.key] < interosseal_connections[candid_obj_key][obj.key]:
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency of the item are updated. The flatulence score is incremented, and interosseal connections are strengthened with related items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency[key] = cache_snapshot.access_count
    flatulence_score[key] += 1
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            interosseal_connections[key][other_key] += 1
            interosseal_connections[other_key][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its initial access frequency and recency are set. The flatulence score starts at zero, and interosseal connections are established based on related items in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency[key] = cache_snapshot.access_count
    flatulence_score[key] = 0
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            interosseal_connections[key][other_key] = 1
            interosseal_connections[other_key][key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the metadata of remaining items is adjusted to reflect the removal. Interosseal connections are recalculated, and the flatulence scores of related items are slightly decreased.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of evicted object
    del access_frequency[evicted_key]
    del recency[evicted_key]
    del flatulence_score[evicted_key]
    del interosseal_connections[evicted_key]
    
    for other_key in cache_snapshot.cache:
        if evicted_key in interosseal_connections[other_key]:
            del interosseal_connections[other_key][evicted_key]
        flatulence_score[other_key] *= FLATULENCE_DECREASE_FACTOR