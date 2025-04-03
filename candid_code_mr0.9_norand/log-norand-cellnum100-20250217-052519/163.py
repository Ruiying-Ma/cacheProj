# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
DEFAULT_NEURAL_ADAPTATION_SCORE = 1.0
DEFAULT_BAYESIAN_CONFIDENCE_INTERVAL = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a neural adaptation score for each cache entry, a predictive index based on access patterns, Bayesian confidence intervals for access frequency, and an anomaly detection flag.
neural_adaptation_scores = {}
predictive_index = {}
bayesian_confidence_intervals = {}
anomaly_flags = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest neural adaptation score, adjusted by Bayesian confidence intervals, and prioritizes entries flagged as anomalies.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = neural_adaptation_scores[key] - bayesian_confidence_intervals[key]
        if anomaly_flags[key]:
            score -= 1  # Prioritize anomalies for eviction
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the neural adaptation score is increased, the predictive index is updated to reflect the recent access, Bayesian confidence intervals are recalculated, and the anomaly flag is checked and reset if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    neural_adaptation_scores[key] += 1
    predictive_index[key] = cache_snapshot.access_count
    bayesian_confidence_intervals[key] = math.sqrt(neural_adaptation_scores[key])
    anomaly_flags[key] = False

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the neural adaptation score is initialized, the predictive index is updated to include the new entry, Bayesian confidence intervals are set to default values, and the anomaly flag is set to false.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    neural_adaptation_scores[key] = DEFAULT_NEURAL_ADAPTATION_SCORE
    predictive_index[key] = cache_snapshot.access_count
    bayesian_confidence_intervals[key] = DEFAULT_BAYESIAN_CONFIDENCE_INTERVAL
    anomaly_flags[key] = False

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the neural adaptation scores of remaining entries are adjusted, the predictive index is recalibrated, Bayesian confidence intervals are updated to reflect the new cache state, and any anomaly flags are re-evaluated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del neural_adaptation_scores[evicted_key]
    del predictive_index[evicted_key]
    del bayesian_confidence_intervals[evicted_key]
    del anomaly_flags[evicted_key]
    
    for key in cache_snapshot.cache:
        neural_adaptation_scores[key] *= 0.9  # Adjust scores
        bayesian_confidence_intervals[key] = math.sqrt(neural_adaptation_scores[key])
        anomaly_flags[key] = False  # Re-evaluate anomaly flags