# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
DEFAULT_PREDICTIVE_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior, time of day), and predictive scores derived from real-time monitoring and data interpolation.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predictive_score': {},
    'contextual_tags': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining predictive analytics and contextual tagging to identify the least likely needed data. It prioritizes objects with low predictive scores and infrequent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['predictive_score'][key] * (1 / (metadata['access_frequency'][key] + 1))
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency, last access time, and recalculates the predictive score based on the new access pattern. Contextual tags are also updated to reflect the current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Recalculate predictive score (this is a placeholder, actual calculation may vary)
    metadata['predictive_score'][key] = 1 / (metadata['access_frequency'][key] + 1)
    # Update contextual tags (this is a placeholder, actual update may vary)
    metadata['contextual_tags'][key] = {'time_of_day': time.strftime("%H:%M:%S")}

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default predictive score, current access time, and relevant contextual tags. It also updates the overall cache state to reflect the new addition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = DEFAULT_PREDICTIVE_SCORE
    metadata['contextual_tags'][key] = {'time_of_day': time.strftime("%H:%M:%S")}

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata of the evicted object and recalculates the predictive scores for the remaining objects to ensure the cache adapts to the new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['predictive_score'][evicted_key]
    del metadata['contextual_tags'][evicted_key]
    
    # Recalculate predictive scores for remaining objects (this is a placeholder, actual calculation may vary)
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] = 1 / (metadata['access_frequency'][key] + 1)