# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
INITIAL_PROBABILITY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Bayesian network to model the conditional dependencies between cache objects, a recursive partitioning tree to segment the cache into regions based on access patterns, and a Markov blanket for each object to capture its relevant probabilistic dependencies.
bayesian_network = {}
recursive_partitioning_tree = collections.defaultdict(list)
markov_blankets = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating the conditional probabilities of future accesses for each object using the Bayesian network. It then uses the recursive partitioning tree to identify the region with the least expected future accesses and selects the object within that region with the lowest probability of being accessed, as determined by its Markov blanket.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_prob = float('inf')
    
    # Identify the region with the least expected future accesses
    for region, objects in recursive_partitioning_tree.items():
        for obj_key in objects:
            if obj_key in cache_snapshot.cache:
                prob = markov_blankets[obj_key].get('access_prob', INITIAL_PROBABILITY)
                if prob < min_prob:
                    min_prob = prob
                    candid_obj_key = obj_key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the Bayesian network to reflect the new access pattern, adjusts the recursive partitioning tree to account for the updated access frequency, and recalculates the conditional probabilities within the Markov blanket of the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    if obj_key in bayesian_network:
        bayesian_network[obj_key]['access_count'] += 1
    else:
        bayesian_network[obj_key] = {'access_count': 1}
    
    # Update the Markov blanket
    markov_blankets[obj_key] = {'access_prob': bayesian_network[obj_key]['access_count'] / cache_snapshot.access_count}
    
    # Adjust the recursive partitioning tree
    region = obj_key[0]  # Example: using the first character of the key as the region
    if obj_key not in recursive_partitioning_tree[region]:
        recursive_partitioning_tree[region].append(obj_key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy incorporates the new object into the Bayesian network, updates the recursive partitioning tree to include the new object in the appropriate region, and initializes the Markov blanket for the new object with initial conditional probabilities based on observed access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    bayesian_network[obj_key] = {'access_count': 1}
    
    # Initialize the Markov blanket
    markov_blankets[obj_key] = {'access_prob': INITIAL_PROBABILITY}
    
    # Update the recursive partitioning tree
    region = obj_key[0]  # Example: using the first character of the key as the region
    recursive_partitioning_tree[region].append(obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted object from the Bayesian network, adjusts the recursive partitioning tree to reflect the removal, and recalculates the conditional probabilities within the Markov blankets of the remaining objects to account for the change in the cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove from Bayesian network
    if evicted_key in bayesian_network:
        del bayesian_network[evicted_key]
    
    # Remove from Markov blankets
    if evicted_key in markov_blankets:
        del markov_blankets[evicted_key]
    
    # Adjust the recursive partitioning tree
    region = evicted_key[0]  # Example: using the first character of the key as the region
    if evicted_key in recursive_partitioning_tree[region]:
        recursive_partitioning_tree[region].remove(evicted_key)
    
    # Recalculate the conditional probabilities within the Markov blankets of the remaining objects
    for obj_key in cache_snapshot.cache:
        if obj_key in markov_blankets:
            markov_blankets[obj_key]['access_prob'] = bayesian_network[obj_key]['access_count'] / cache_snapshot.access_count