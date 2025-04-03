# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_RECENCY = 0
INITIAL_CONTEXT_TAGS = {'time_of_day': 0, 'user_behavior': 0}
INITIAL_LATENT_VARIABLES = {'historical_access': 0}
INITIAL_PROBABILISTIC_TREND_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, context tags (e.g., time of day, user behavior patterns), and latent variables inferred from historical data. It also keeps a probabilistic trend score for each cache entry.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining predictive ensembles to forecast future access patterns, context-aware inference to understand the current usage scenario, and latent variable modeling to identify less critical entries. The entry with the lowest probabilistic trend score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    lowest_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata[key]['probabilistic_trend_score']
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency of the accessed entry. It also adjusts the context tags based on the current context and refines the latent variables and probabilistic trend score using the latest access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key]['access_frequency'] += 1
    metadata[key]['recency'] = cache_snapshot.access_count
    metadata[key]['context_tags']['time_of_day'] = time.localtime().tm_hour
    metadata[key]['context_tags']['user_behavior'] += 1
    metadata[key]['latent_variables']['historical_access'] += 1
    metadata[key]['probabilistic_trend_score'] = (
        metadata[key]['access_frequency'] * 0.5 +
        metadata[key]['recency'] * 0.3 +
        metadata[key]['context_tags']['user_behavior'] * 0.2
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, recency, and context tags. It also sets initial latent variables and calculates an initial probabilistic trend score based on similar historical entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key] = {
        'access_frequency': INITIAL_ACCESS_FREQUENCY,
        'recency': cache_snapshot.access_count,
        'context_tags': INITIAL_CONTEXT_TAGS.copy(),
        'latent_variables': INITIAL_LATENT_VARIABLES.copy(),
        'probabilistic_trend_score': INITIAL_PROBABILISTIC_TREND_SCORE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the overall cache context model to reflect the removal. It also recalibrates the latent variable distributions and probabilistic trend analysis to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalibrate latent variables and probabilistic trend analysis
    for key in metadata:
        metadata[key]['latent_variables']['historical_access'] -= 1
        metadata[key]['probabilistic_trend_score'] = (
            metadata[key]['access_frequency'] * 0.5 +
            metadata[key]['recency'] * 0.3 +
            metadata[key]['context_tags']['user_behavior'] * 0.2
        )