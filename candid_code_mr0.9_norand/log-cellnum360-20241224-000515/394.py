# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASELINE_ACCESS_PATTERN = 0.1
NEUTRAL_COGNITIVE_SCORE = 0.5
CONVERGENCE_INDEX_ADJUSTMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a neural-inspired matrix that records access patterns, a cognitive synthesis score for each cache entry, a dynamic convergence index that adapts to workload changes, and a predictive fusion model that forecasts future access probabilities.
neural_matrix = {}
cognitive_scores = {}
convergence_index = 1.0
predictive_model = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by combining the lowest cognitive synthesis score with the least predicted future access probability, adjusted by the dynamic convergence index to ensure adaptability to changing access patterns.
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
        score = (cognitive_scores[key] + predictive_model[key]) * convergence_index
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the neural-inspired matrix is updated to reinforce the access pattern, the cognitive synthesis score is incremented to reflect increased relevance, and the predictive fusion model is refined to improve future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    neural_matrix[key] += 1
    cognitive_scores[key] += 0.1
    predictive_model[key] = np.tanh(neural_matrix[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the neural-inspired matrix is initialized with baseline access patterns, the cognitive synthesis score is set to a neutral value, and the dynamic convergence index is adjusted to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    neural_matrix[key] = BASELINE_ACCESS_PATTERN
    cognitive_scores[key] = NEUTRAL_COGNITIVE_SCORE
    predictive_model[key] = np.tanh(neural_matrix[key])
    global convergence_index
    convergence_index += CONVERGENCE_INDEX_ADJUSTMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the neural-inspired matrix is recalibrated to remove the evicted entry's influence, the cognitive synthesis scores of remaining entries are normalized, and the dynamic convergence index is updated to reflect the cache's new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in neural_matrix:
        del neural_matrix[evicted_key]
    if evicted_key in cognitive_scores:
        del cognitive_scores[evicted_key]
    if evicted_key in predictive_model:
        del predictive_model[evicted_key]
    
    total_score = sum(cognitive_scores.values())
    if total_score > 0:
        for key in cognitive_scores:
            cognitive_scores[key] /= total_score
    
    global convergence_index
    convergence_index -= CONVERGENCE_INDEX_ADJUSTMENT