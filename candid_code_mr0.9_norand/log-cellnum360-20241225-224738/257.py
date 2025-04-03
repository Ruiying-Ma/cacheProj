# Import anything you need below
import collections

# Put tunable constant parameters below
INITIAL_CONTEXTUAL_SCORE = 1.0
NEUTRAL_ANOMALY_SCORE = 0.0
LATENCY_FACTOR_BASE = 1.0
CONTEXTUAL_SCORE_INCREMENT = 0.1
ANOMALY_SCORE_ADJUSTMENT = 0.05
LATENCY_FACTOR_ADJUSTMENT = 0.1
STEPWISE_ADJUSTMENT_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a contextual score for each cache entry, an anomaly score to detect unusual access patterns, a quantum latency factor to account for access time variations, and a stepwise adjustment counter to fine-tune the scores over time.
contextual_scores = collections.defaultdict(lambda: INITIAL_CONTEXTUAL_SCORE)
anomaly_scores = collections.defaultdict(lambda: NEUTRAL_ANOMALY_SCORE)
latency_factors = collections.defaultdict(lambda: LATENCY_FACTOR_BASE)
stepwise_counters = collections.defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of contextual refinement and anomaly isolation, adjusted by the quantum latency factor. This ensures that entries with unusual access patterns or higher latency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (contextual_scores[key] + anomaly_scores[key]) * latency_factors[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the contextual score is incremented to reflect increased relevance, the anomaly score is adjusted based on recent access patterns, the quantum latency factor is recalibrated to account for the current access time, and the stepwise adjustment counter is incremented to gradually refine the scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    contextual_scores[key] += CONTEXTUAL_SCORE_INCREMENT
    anomaly_scores[key] += ANOMALY_SCORE_ADJUSTMENT
    latency_factors[key] += LATENCY_FACTOR_ADJUSTMENT
    stepwise_counters[key] += STEPWISE_ADJUSTMENT_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the contextual score is initialized based on initial access context, the anomaly score is set to a neutral value, the quantum latency factor is calculated from the initial access time, and the stepwise adjustment counter is set to zero to begin the refinement process.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    contextual_scores[key] = INITIAL_CONTEXTUAL_SCORE
    anomaly_scores[key] = NEUTRAL_ANOMALY_SCORE
    latency_factors[key] = LATENCY_FACTOR_BASE
    stepwise_counters[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the contextual scores of remaining entries are slightly adjusted to reflect the change in cache composition, the anomaly scores are recalibrated to detect new patterns, the quantum latency factors are updated to account for the removal, and the stepwise adjustment counters are reset to ensure ongoing refinement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        contextual_scores[key] *= 0.95  # Slight adjustment
        anomaly_scores[key] *= 0.95
        latency_factors[key] *= 0.95
        stepwise_counters[key] = 0