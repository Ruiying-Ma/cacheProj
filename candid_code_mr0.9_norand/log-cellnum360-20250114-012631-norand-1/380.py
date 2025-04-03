# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
MAX_HISTORY = 1000  # Maximum history size for access patterns

# Put the metadata specifically maintained by the policy below. The policy maintains a latent variable model representing the hidden states of cache objects, contextual data inferred from access patterns, a causal structure graph to understand dependencies, and a dynamic Bayesian network to predict future accesses.
access_history = collections.deque(maxlen=MAX_HISTORY)  # To store access patterns
latent_variable_model = {}  # To store latent variables for each object
causal_structure_graph = {}  # To store dependencies between objects
dynamic_bayesian_network = {}  # To store predicted future accesses

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating the probability of future accesses using the dynamic Bayesian network, prioritizing objects with the lowest predicted access probability and considering causal dependencies to minimize impact on related objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_prob = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        prob = dynamic_bayesian_network.get(key, 0)
        if prob < min_prob:
            min_prob = prob
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the latent variable model to reflect the new access, refines the contextual data with the latest access pattern, adjusts the causal structure graph to account for any new dependencies, and updates the dynamic Bayesian network to improve future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_history.append(obj.key)
    latent_variable_model[obj.key] = latent_variable_model.get(obj.key, 0) + 1
    # Update causal structure graph and dynamic Bayesian network
    for key in cache_snapshot.cache:
        if key != obj.key:
            causal_structure_graph.setdefault(key, set()).add(obj.key)
            dynamic_bayesian_network[key] = dynamic_bayesian_network.get(key, 0) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy incorporates the object into the latent variable model, initializes its contextual data, updates the causal structure graph to include potential new dependencies, and adjusts the dynamic Bayesian network to account for the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_history.append(obj.key)
    latent_variable_model[obj.key] = 1
    # Initialize causal structure graph and dynamic Bayesian network
    for key in cache_snapshot.cache:
        if key != obj.key:
            causal_structure_graph.setdefault(key, set()).add(obj.key)
            dynamic_bayesian_network[key] = dynamic_bayesian_network.get(key, 0) + 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the object from the latent variable model, purges its contextual data, updates the causal structure graph to remove dependencies related to the evicted object, and refines the dynamic Bayesian network to exclude the evicted object from future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in latent_variable_model:
        del latent_variable_model[evicted_obj.key]
    if evicted_obj.key in causal_structure_graph:
        del causal_structure_graph[evicted_obj.key]
    if evicted_obj.key in dynamic_bayesian_network:
        del dynamic_bayesian_network[evicted_obj.key]
    for key in causal_structure_graph:
        if evicted_obj.key in causal_structure_graph[key]:
            causal_structure_graph[key].remove(evicted_obj.key)