# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import numpy as np

# Put tunable constant parameters below
INITIAL_CONVERGENCE_SCORE = 1.0
NEURAL_MATRIX_DIM = 10  # Example dimension for the neural transformation matrix

# Put the metadata specifically maintained by the policy below. The policy maintains a neural transformation matrix for each cache entry, a convergence score, a predictive interpolation vector, and a vectorized computation history.
metadata = {
    'neural_matrices': {},  # key -> neural transformation matrix
    'convergence_scores': {},  # key -> convergence score
    'predictive_vectors': {},  # key -> predictive interpolation vector
    'computation_histories': {}  # key -> vectorized computation history
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest convergence score, which is computed using the neural transformation matrix and predictive interpolation vector.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_convergence_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['convergence_scores'][key]
        if score < min_convergence_score:
            min_convergence_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the neural transformation matrix is updated using the vectorized computation history, the convergence score is recalculated, and the predictive interpolation vector is adjusted based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    history = metadata['computation_histories'][key]
    matrix = metadata['neural_matrices'][key]
    predictive_vector = metadata['predictive_vectors'][key]
    
    # Update the neural transformation matrix
    matrix += np.outer(history, predictive_vector)
    
    # Recalculate the convergence score
    metadata['convergence_scores'][key] = np.linalg.norm(matrix @ predictive_vector)
    
    # Adjust the predictive interpolation vector
    metadata['predictive_vectors'][key] = predictive_vector + history

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the neural transformation matrix with random values, sets an initial convergence score, and generates a predictive interpolation vector based on the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    
    # Initialize the neural transformation matrix with fixed values
    metadata['neural_matrices'][key] = np.ones((NEURAL_MATRIX_DIM, NEURAL_MATRIX_DIM))
    
    # Set an initial convergence score
    metadata['convergence_scores'][key] = INITIAL_CONVERGENCE_SCORE
    
    # Generate a predictive interpolation vector based on the current state of the cache
    metadata['predictive_vectors'][key] = np.ones(NEURAL_MATRIX_DIM)
    
    # Initialize the vectorized computation history
    metadata['computation_histories'][key] = np.zeros(NEURAL_MATRIX_DIM)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the convergence scores for the remaining entries, updates the neural transformation matrices to reflect the new cache state, and adjusts the predictive interpolation vectors accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for the evicted object
    del metadata['neural_matrices'][evicted_key]
    del metadata['convergence_scores'][evicted_key]
    del metadata['predictive_vectors'][evicted_key]
    del metadata['computation_histories'][evicted_key]
    
    # Recalculate convergence scores for remaining entries
    for key in cache_snapshot.cache.keys():
        matrix = metadata['neural_matrices'][key]
        predictive_vector = metadata['predictive_vectors'][key]
        metadata['convergence_scores'][key] = np.linalg.norm(matrix @ predictive_vector)