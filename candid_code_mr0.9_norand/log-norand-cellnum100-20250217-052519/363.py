# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
PREDICTIVE_SCORE_WEIGHT = 0.5
LATENT_VARIABLE_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, a predictive score based on historical access patterns, and a latent variable representing the object's importance derived from heuristic evaluation.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predictive_score': {},
    'latent_variable': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object, which combines the inverse of access frequency, the time since last access, the predictive score, and the latent variable. The object with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 1)
        last_access = metadata['last_access_time'].get(key, cache_snapshot.access_count)
        predictive_score = metadata['predictive_score'].get(key, 0)
        latent_variable = metadata['latent_variable'].get(key, 0)
        
        time_since_last_access = cache_snapshot.access_count - last_access
        composite_score = (1 / access_freq) + time_since_last_access + (PREDICTIVE_SCORE_WEIGHT * predictive_score) + (LATENT_VARIABLE_WEIGHT * latent_variable)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access time is updated to the current time, the predictive score is adjusted based on recent access patterns, and the latent variable is recalculated using heuristic evaluation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = calculate_predictive_score(key)
    metadata['latent_variable'][key] = calculate_latent_variable(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the last access time is set to the current time, the predictive score is generated based on initial access patterns, and the latent variable is estimated using heuristic evaluation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['predictive_score'][key] = calculate_predictive_score(key)
    metadata['latent_variable'][key] = calculate_latent_variable(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalculates the predictive scores and latent variables for the remaining objects to ensure they reflect the current cache state and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predictive_score']:
        del metadata['predictive_score'][evicted_key]
    if evicted_key in metadata['latent_variable']:
        del metadata['latent_variable'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['predictive_score'][key] = calculate_predictive_score(key)
        metadata['latent_variable'][key] = calculate_latent_variable(key)

def calculate_predictive_score(key):
    '''
    This function calculates the predictive score for a given object key.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `predictive_score`: The predictive score of the object.
    '''
    # Placeholder for actual predictive score calculation logic
    return 0

def calculate_latent_variable(key):
    '''
    This function calculates the latent variable for a given object key.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `latent_variable`: The latent variable of the object.
    '''
    # Placeholder for actual latent variable calculation logic
    return 0