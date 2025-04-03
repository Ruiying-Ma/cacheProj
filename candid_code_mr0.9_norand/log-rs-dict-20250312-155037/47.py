# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency in bibliopoly score
BETA = 0.3   # Weight for recency in bibliopoly score
GAMMA = 0.2  # Weight for size in bibliopoly score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a unique 'bibliopoly' score which is a combination of the object's size and its access pattern complexity.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of objects
    'recency': {},           # Dictionary to store recency of access of objects
    'bibliopoly_score': {}   # Dictionary to store bibliopoly score of objects
}

def calculate_bibliopoly_score(obj, cache_snapshot):
    '''
    Calculate the bibliopoly score for an object based on its size, access frequency, and recency.
    '''
    access_freq = metadata['access_frequency'].get(obj.key, 0)
    recency = metadata['recency'].get(obj.key, cache_snapshot.access_count)
    size = obj.size
    score = ALPHA * access_freq + BETA * (cache_snapshot.access_count - recency) + GAMMA * size
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest bibliopoly score, prioritizing objects that are infrequently accessed, less recently accessed, and have simpler access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = calculate_bibliopoly_score(cached_obj, cache_snapshot)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency of the accessed object are updated, and its bibliopoly score is recalculated to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata['access_frequency'][obj.key] = metadata['access_frequency'].get(obj.key, 0) + 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    metadata['bibliopoly_score'][obj.key] = calculate_bibliopoly_score(obj, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its initial access frequency and recency are set, and its bibliopoly score is calculated based on its size and expected access pattern complexity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata['access_frequency'][obj.key] = 1
    metadata['recency'][obj.key] = cache_snapshot.access_count
    metadata['bibliopoly_score'][obj.key] = calculate_bibliopoly_score(obj, cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the bibliopoly scores of remaining objects to ensure the eviction decision remains optimal, and updates the overall cache metadata to reflect the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata of evicted object
    if evicted_obj.key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_obj.key]
    if evicted_obj.key in metadata['recency']:
        del metadata['recency'][evicted_obj.key]
    if evicted_obj.key in metadata['bibliopoly_score']:
        del metadata['bibliopoly_score'][evicted_obj.key]
    
    # Recalculate bibliopoly scores for remaining objects
    for key, cached_obj in cache_snapshot.cache.items():
        metadata['bibliopoly_score'][key] = calculate_bibliopoly_score(cached_obj, cache_snapshot)