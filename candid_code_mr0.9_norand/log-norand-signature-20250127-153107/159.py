# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
INITIAL_BAYESIAN_PROBABILITY = 0.5
INITIAL_INFORMATION_BOTTLENECK_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a genetic representation of cache objects, Bayesian probabilities of access patterns, and an information bottleneck score for each object. Additionally, it tracks cross-entropy loss to measure prediction accuracy.
genetic_representation = {}
bayesian_probabilities = {}
information_bottleneck_scores = {}
cross_entropy_loss = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest combined score of Bayesian probability and information bottleneck value, adjusted by the cross-entropy loss to prioritize objects with less predictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        bayesian_prob = bayesian_probabilities.get(key, INITIAL_BAYESIAN_PROBABILITY)
        info_bottleneck = information_bottleneck_scores.get(key, INITIAL_INFORMATION_BOTTLENECK_SCORE)
        score = bayesian_prob + info_bottleneck + cross_entropy_loss
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the genetic representation of the accessed object is updated to reflect recent access patterns, Bayesian probabilities are recalculated, and the information bottleneck score is adjusted. The cross-entropy loss is updated to reflect the accuracy of the access prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Update genetic representation
    genetic_representation[key] = cache_snapshot.access_count
    
    # Recalculate Bayesian probabilities
    bayesian_probabilities[key] = (bayesian_probabilities.get(key, INITIAL_BAYESIAN_PROBABILITY) + 1) / 2
    
    # Adjust information bottleneck score
    information_bottleneck_scores[key] = 1 / (1 + math.exp(-bayesian_probabilities[key]))
    
    # Update cross-entropy loss
    cross_entropy_loss = -sum(bayesian_probabilities[key] * math.log(bayesian_probabilities[key]) for key in cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its genetic representation is initialized, Bayesian probabilities are set based on initial access patterns, and an initial information bottleneck score is assigned. The cross-entropy loss is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Initialize genetic representation
    genetic_representation[key] = cache_snapshot.access_count
    
    # Set initial Bayesian probabilities
    bayesian_probabilities[key] = INITIAL_BAYESIAN_PROBABILITY
    
    # Assign initial information bottleneck score
    information_bottleneck_scores[key] = INITIAL_INFORMATION_BOTTLENECK_SCORE
    
    # Update cross-entropy loss
    cross_entropy_loss = -sum(bayesian_probabilities[key] * math.log(bayesian_probabilities[key]) for key in cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the genetic representation is removed, Bayesian probabilities are recalculated for the remaining objects, and the information bottleneck scores are adjusted. The cross-entropy loss is updated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove genetic representation
    if evicted_key in genetic_representation:
        del genetic_representation[evicted_key]
    
    # Remove Bayesian probabilities
    if evicted_key in bayesian_probabilities:
        del bayesian_probabilities[evicted_key]
    
    # Remove information bottleneck score
    if evicted_key in information_bottleneck_scores:
        del information_bottleneck_scores[evicted_key]
    
    # Recalculate Bayesian probabilities for remaining objects
    for key in cache_snapshot.cache:
        bayesian_probabilities[key] = (bayesian_probabilities.get(key, INITIAL_BAYESIAN_PROBABILITY) + 1) / 2
    
    # Adjust information bottleneck scores for remaining objects
    for key in cache_snapshot.cache:
        information_bottleneck_scores[key] = 1 / (1 + math.exp(-bayesian_probabilities[key]))
    
    # Update cross-entropy loss
    cross_entropy_loss = -sum(bayesian_probabilities[key] * math.log(bayesian_probabilities[key]) for key in cache_snapshot.cache)