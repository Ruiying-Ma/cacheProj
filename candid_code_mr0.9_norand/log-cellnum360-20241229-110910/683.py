# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASELINE_COHESION_SCORE = 1.0
NEURAL_PATTERN_DECAY = 0.9
COHESION_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a recursive neural pattern matrix for each cache entry, capturing access patterns and temporal dynamics. It also tracks a cohesion score that reflects the algorithmic similarity between cache entries.
neural_pattern_matrices = {}
cohesion_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest cohesion score and least neural pattern activity, ensuring that entries with unique or frequently accessed patterns are retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_cohesion_score = float('inf')
    min_pattern_activity = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        cohesion_score = cohesion_scores.get(key, BASELINE_COHESION_SCORE)
        pattern_activity = np.sum(neural_pattern_matrices.get(key, np.zeros((1, 1))))
        
        if (cohesion_score < min_cohesion_score) or (cohesion_score == min_cohesion_score and pattern_activity < min_pattern_activity):
            min_cohesion_score = cohesion_score
            min_pattern_activity = pattern_activity
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the neural pattern matrix for the accessed entry is augmented to reinforce the detected access pattern, and the cohesion score is recalculated to reflect the updated algorithmic similarity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in neural_pattern_matrices:
        neural_pattern_matrices[key] *= NEURAL_PATTERN_DECAY
        neural_pattern_matrices[key] += np.eye(neural_pattern_matrices[key].shape[0])
    
    # Recalculate cohesion score
    cohesion_scores[key] = BASELINE_COHESION_SCORE + COHESION_ADJUSTMENT_FACTOR * np.sum(neural_pattern_matrices[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its neural pattern matrix and assigns a baseline cohesion score based on initial access patterns and similarity to existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    neural_pattern_matrices[key] = np.eye(1)  # Initialize with a simple identity matrix
    cohesion_scores[key] = BASELINE_COHESION_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the cohesion scores of remaining entries to account for the removal, and adjusts the neural pattern matrices to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in neural_pattern_matrices:
        del neural_pattern_matrices[evicted_key]
    if evicted_key in cohesion_scores:
        del cohesion_scores[evicted_key]
    
    # Recalibrate cohesion scores for remaining entries
    for key in cache_snapshot.cache.keys():
        cohesion_scores[key] = BASELINE_COHESION_SCORE + COHESION_ADJUSTMENT_FACTOR * np.sum(neural_pattern_matrices[key])