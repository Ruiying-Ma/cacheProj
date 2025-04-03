# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import numpy as np

# Put tunable constant parameters below
LATENT_DIM = 10  # Dimension of the latent factor matrix
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_HIERARCHY_LEVEL = 1
INITIAL_DYNAMIC_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a latent factor matrix for each cache object, a predictive score for future accesses, a multi-level hierarchy of object importance, and dynamic weights for each factor based on recent access patterns.
latent_factors = {}
predictive_scores = {}
hierarchy_levels = {}
dynamic_weights = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object using its latent factors, predictive score, hierarchical level, and dynamic weights. The object with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        latent_factor = latent_factors[key]
        predictive_score = predictive_scores[key]
        hierarchy_level = hierarchy_levels[key]
        dynamic_weight = dynamic_weights[key]
        
        composite_score = np.dot(latent_factor, dynamic_weight) + predictive_score + hierarchy_level
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the latent factor matrix to reflect the new access pattern, recalculates the predictive score based on recent accesses, adjusts the object's hierarchical level if necessary, and updates the dynamic weights to prioritize similar future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    latent_factors[key] += 1  # Update latent factors to reflect new access pattern
    predictive_scores[key] = cache_snapshot.access_count  # Recalculate predictive score
    hierarchy_levels[key] += 1  # Adjust hierarchical level if necessary
    dynamic_weights[key] += 1  # Update dynamic weights to prioritize similar future accesses

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its latent factors, assigns an initial predictive score, places it at an appropriate level in the hierarchy based on initial importance, and sets initial dynamic weights based on the current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    latent_factors[key] = np.ones(LATENT_DIM)  # Initialize latent factors
    predictive_scores[key] = INITIAL_PREDICTIVE_SCORE  # Assign initial predictive score
    hierarchy_levels[key] = INITIAL_HIERARCHY_LEVEL  # Place at an appropriate level in the hierarchy
    dynamic_weights[key] = np.ones(LATENT_DIM) * INITIAL_DYNAMIC_WEIGHT  # Set initial dynamic weights

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy rebalances the latent factor matrix to account for the removed object, updates the predictive scores of remaining objects, adjusts the hierarchical levels if needed, and recalibrates the dynamic weights to maintain optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del latent_factors[evicted_key]
    del predictive_scores[evicted_key]
    del hierarchy_levels[evicted_key]
    del dynamic_weights[evicted_key]
    
    # Rebalance latent factor matrix, update predictive scores, adjust hierarchical levels, and recalibrate dynamic weights
    for key in cache_snapshot.cache.keys():
        latent_factors[key] -= 1
        predictive_scores[key] = cache_snapshot.access_count
        hierarchy_levels[key] -= 1
        dynamic_weights[key] -= 1