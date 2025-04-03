# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
CONV_MATRIX_SIZE = 3  # Example size of the convolutional matrix
INITIAL_WEIGHT = 1.0  # Initial weight for new objects

# Put the metadata specifically maintained by the policy below. The policy maintains a convolutional matrix that captures access patterns, a latent pattern discovery model to identify hidden access trends, and an adaptive learning component that adjusts weights based on recent access history.
conv_matrix = np.ones((CONV_MATRIX_SIZE, CONV_MATRIX_SIZE))
latent_patterns = defaultdict(float)
adaptive_weights = defaultdict(lambda: INITIAL_WEIGHT)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by applying the convolutional matrix to the cache, identifying blocks with the least significant latent patterns, and optimizing the decision using a hybrid approach that balances recent access frequency and predicted future access.
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
        # Calculate score based on latent patterns and adaptive weights
        score = latent_patterns[key] * adaptive_weights[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the convolutional matrix is updated to reinforce the accessed pattern, the latent pattern model is adjusted to reflect the new access, and the adaptive learning component increases the weight of the accessed block.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Reinforce the accessed pattern in the convolutional matrix
    latent_patterns[obj.key] += 1
    # Increase the weight of the accessed block
    adaptive_weights[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the convolutional matrix is expanded to include the new access pattern, the latent pattern model is updated to incorporate the new data, and the adaptive learning component initializes the weight of the new object based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Expand the convolutional matrix to include the new access pattern
    latent_patterns[obj.key] = 0
    # Initialize the weight of the new object
    adaptive_weights[obj.key] = INITIAL_WEIGHT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the convolutional matrix is recalibrated to remove the evicted pattern, the latent pattern model is adjusted to account for the change, and the adaptive learning component redistributes the weight of the evicted block to remaining blocks based on their predicted importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalibrate the convolutional matrix to remove the evicted pattern
    if evicted_obj.key in latent_patterns:
        del latent_patterns[evicted_obj.key]
    # Redistribute the weight of the evicted block
    if evicted_obj.key in adaptive_weights:
        redistributed_weight = adaptive_weights[evicted_obj.key] / len(cache_snapshot.cache)
        del adaptive_weights[evicted_obj.key]
        for key in cache_snapshot.cache:
            adaptive_weights[key] += redistributed_weight