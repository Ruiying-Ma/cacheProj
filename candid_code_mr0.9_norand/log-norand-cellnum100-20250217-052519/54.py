# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
INITIAL_RESPONSE_TIME = 1.0
INITIAL_ACCESS_PROBABILITY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a probabilistic forecast model using a Markov chain to predict future access patterns, response time profiles for each cached object, and a cache optimization score that combines these factors.
markov_chain = collections.defaultdict(lambda: collections.defaultdict(float))
response_time_profile = {}
cache_optimization_score = {}

def calculate_cache_optimization_score(obj):
    # Example calculation combining access probability and response time
    access_probability = markov_chain[obj.key].get('access_probability', INITIAL_ACCESS_PROBABILITY)
    response_time = response_time_profile.get(obj.key, INITIAL_RESPONSE_TIME)
    return access_probability / response_time

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest cache optimization score, which is calculated based on the predicted future access probability and the response time profile.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = cache_optimization_score.get(key, calculate_cache_optimization_score(cached_obj))
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the Markov chain to reflect the transition to the accessed object, adjusts the response time profile based on the current access time, and recalculates the cache optimization score for the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Update Markov chain
    for key in cache_snapshot.cache:
        if key != obj.key:
            markov_chain[key][obj.key] += 1
    
    # Adjust response time profile
    response_time_profile[obj.key] = cache_snapshot.access_count
    
    # Recalculate cache optimization score
    cache_optimization_score[obj.key] = calculate_cache_optimization_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Markov chain state, sets an initial response time profile based on the insertion time, and calculates an initial cache optimization score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize Markov chain state
    markov_chain[obj.key] = collections.defaultdict(float)
    
    # Set initial response time profile
    response_time_profile[obj.key] = cache_snapshot.access_count
    
    # Calculate initial cache optimization score
    cache_optimization_score[obj.key] = calculate_cache_optimization_score(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes its Markov chain state, clears its response time profile, and recalculates the cache optimization scores for the remaining objects to ensure they reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove Markov chain state
    if evicted_obj.key in markov_chain:
        del markov_chain[evicted_obj.key]
    
    # Clear response time profile
    if evicted_obj.key in response_time_profile:
        del response_time_profile[evicted_obj.key]
    
    # Recalculate cache optimization scores for remaining objects
    for key, cached_obj in cache_snapshot.cache.items():
        cache_optimization_score[key] = calculate_cache_optimization_score(cached_obj)