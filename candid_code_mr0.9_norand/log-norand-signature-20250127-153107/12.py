# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import math

# Put tunable constant parameters below
ENTROPY_DECAY_RATE = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a probabilistic graph model representing the relationships between cached items, entropic state encodings for each item to capture their access patterns, and dynamic latent variables to adapt to changing access patterns over time.
probabilistic_graph = {}
entropic_state_encodings = {}
dynamic_latent_variables = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating the entropic state encodings and dynamic latent variables, selecting the item with the highest entropy and least recent access probability as determined by the recursive neural architecture.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -math.inf
    min_access_prob = math.inf

    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropic_state_encodings.get(key, 0)
        access_prob = dynamic_latent_variables.get(key, 1)
        
        if entropy > max_entropy or (entropy == max_entropy and access_prob < min_access_prob):
            max_entropy = entropy
            min_access_prob = access_prob
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the entropic state encoding of the accessed item to reflect the new access pattern and adjusts the dynamic latent variables to decrease the entropy associated with the item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    entropic_state_encodings[key] = entropic_state_encodings.get(key, 0) * ENTROPY_DECAY_RATE
    dynamic_latent_variables[key] = dynamic_latent_variables.get(key, 1) * ENTROPY_DECAY_RATE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its entropic state encoding and dynamic latent variables based on the current state of the probabilistic graph model, ensuring the new item is integrated into the existing access pattern structure.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    entropic_state_encodings[key] = 1  # Initialize with high entropy
    dynamic_latent_variables[key] = 1  # Initialize with default access probability

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the probabilistic graph model to remove the evicted item, recalculates the entropic state encodings for the remaining items, and adjusts the dynamic latent variables to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in entropic_state_encodings:
        del entropic_state_encodings[evicted_key]
    if evicted_key in dynamic_latent_variables:
        del dynamic_latent_variables[evicted_key]
    
    # Recalculate entropic state encodings and dynamic latent variables for remaining items
    for key in cache_snapshot.cache:
        entropic_state_encodings[key] = entropic_state_encodings.get(key, 0) * ENTROPY_DECAY_RATE
        dynamic_latent_variables[key] = dynamic_latent_variables.get(key, 1) * ENTROPY_DECAY_RATE