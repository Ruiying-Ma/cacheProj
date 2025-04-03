# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
ALPHA = 0.1  # Learning rate for temporal difference learning
GAMMA = 0.9  # Discount factor for future rewards

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, a temporal difference error tracker, a genetic representation of cache objects, Bayesian probabilities of access patterns, an information bottleneck score for each object, and cross-entropy loss to measure prediction accuracy.
Q_table = {}
policy_network = {}
temporal_difference_error = {}
genetic_representation = {}
bayesian_probabilities = {}
information_bottleneck_score = {}
cross_entropy_loss = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest combined score of Bayesian probability and information bottleneck value, adjusted by the cross-entropy loss, and then refines the selection using the policy network based on the Q-table values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        bayesian_prob = bayesian_probabilities.get(key, 1.0)
        info_bottleneck = information_bottleneck_score.get(key, 0.0)
        cross_entropy = cross_entropy_loss.get(key, 0.0)
        combined_score = bayesian_prob + info_bottleneck + cross_entropy
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The policy updates the Q-value for the accessed object using temporal difference learning, adjusts the policy network, updates the genetic representation, recalculates Bayesian probabilities, adjusts the information bottleneck score, and updates the cross-entropy loss to reflect the accuracy of the access prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    Q_table[key] = Q_table.get(key, 0) + ALPHA * (1 + GAMMA * max(Q_table.values(), default=0) - Q_table.get(key, 0))
    policy_network[key] = Q_table[key]
    genetic_representation[key] = obj.size
    bayesian_probabilities[key] = bayesian_probabilities.get(key, 1.0) * 0.9
    information_bottleneck_score[key] = -math.log(bayesian_probabilities[key])
    cross_entropy_loss[key] = -math.log(bayesian_probabilities[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The policy updates the Q-table to reflect the new state, adjusts the policy network, initializes the genetic representation, sets Bayesian probabilities based on initial access patterns, assigns an initial information bottleneck score, and updates the cross-entropy loss to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    Q_table[key] = 0
    policy_network[key] = 0
    genetic_representation[key] = obj.size
    bayesian_probabilities[key] = 1.0
    information_bottleneck_score[key] = -math.log(bayesian_probabilities[key])
    cross_entropy_loss[key] = -math.log(bayesian_probabilities[key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The policy updates the Q-value for the evicted object to reflect the cost of eviction, refines the policy network, removes the genetic representation, recalculates Bayesian probabilities for remaining objects, adjusts the information bottleneck scores, and updates the cross-entropy loss to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    Q_table[evicted_key] = Q_table.get(evicted_key, 0) - 1
    policy_network.pop(evicted_key, None)
    genetic_representation.pop(evicted_key, None)
    bayesian_probabilities.pop(evicted_key, None)
    information_bottleneck_score.pop(evicted_key, None)
    cross_entropy_loss.pop(evicted_key, None)
    
    for key in cache_snapshot.cache:
        bayesian_probabilities[key] = bayesian_probabilities.get(key, 1.0) * 0.9
        information_bottleneck_score[key] = -math.log(bayesian_probabilities[key])
        cross_entropy_loss[key] = -math.log(bayesian_probabilities[key])