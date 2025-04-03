# Import anything you need below
import numpy as np

# Put tunable constant parameters below
INITIAL_HEURISTIC_SCORE = 1.0
ENTROPY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a sequential access counter, a state transformation matrix, predictive heuristics scores for each cache entry, and an entropy value representing the diversity of access patterns.
sequential_access_counter = 0
state_transformation_matrix = {}
predictive_heuristic_scores = {}
entropy_value = 0.0

def calculate_entropy(cache_snapshot):
    # Calculate entropy based on access patterns
    total_accesses = cache_snapshot.access_count
    if total_accesses == 0:
        return 0.0
    hit_ratio = cache_snapshot.hit_count / total_accesses
    miss_ratio = cache_snapshot.miss_count / total_accesses
    if hit_ratio == 0 or miss_ratio == 0:
        return 0.0
    return - (hit_ratio * np.log2(hit_ratio) + miss_ratio * np.log2(miss_ratio))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest predictive heuristic score, adjusted by the entropy value to ensure a balance between frequently and infrequently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = predictive_heuristic_scores.get(key, INITIAL_HEURISTIC_SCORE) - ENTROPY_WEIGHT * entropy_value
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential access counter is incremented, the state transformation matrix is updated to reflect the transition to a more stable state, and the predictive heuristic score for the accessed entry is increased to reflect its recent use.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global sequential_access_counter
    sequential_access_counter += 1
    
    # Update state transformation matrix
    state_transformation_matrix[obj.key] = state_transformation_matrix.get(obj.key, 0) + 1
    
    # Update predictive heuristic score
    predictive_heuristic_scores[obj.key] = predictive_heuristic_scores.get(obj.key, INITIAL_HEURISTIC_SCORE) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequential access counter is reset, the state transformation matrix is adjusted to account for the new entry, and the predictive heuristic score is initialized based on the current entropy value to predict its future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global sequential_access_counter
    sequential_access_counter = 0
    
    # Adjust state transformation matrix
    state_transformation_matrix[obj.key] = 0
    
    # Initialize predictive heuristic score
    predictive_heuristic_scores[obj.key] = INITIAL_HEURISTIC_SCORE + ENTROPY_WEIGHT * entropy_value

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the sequential access counter is decremented, the state transformation matrix is updated to reflect the removal of the entry, and the entropy value is recalculated to ensure a balanced distribution of access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global sequential_access_counter, entropy_value
    sequential_access_counter -= 1
    
    # Update state transformation matrix
    if evicted_obj.key in state_transformation_matrix:
        del state_transformation_matrix[evicted_obj.key]
    
    # Recalculate entropy value
    entropy_value = calculate_entropy(cache_snapshot)