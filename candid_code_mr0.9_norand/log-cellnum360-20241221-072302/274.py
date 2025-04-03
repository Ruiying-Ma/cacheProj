# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_WEIGHT = 0.4
PREDICTIVE_WEIGHT = 0.3
ENTROPY_WEIGHT = 0.2
ADAPTIVE_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal score for each cache entry, a predictive resilience factor, an entropy value, and an adaptive feedback loop score. The temporal score tracks the recency and frequency of access, the predictive resilience factor estimates future access likelihood, the entropy value measures access pattern randomness, and the adaptive feedback loop score adjusts based on cache performance.
temporal_scores = defaultdict(lambda: 0)
predictive_resilience_factors = defaultdict(lambda: 0)
entropy_values = defaultdict(lambda: 0)
adaptive_feedback_loop_score = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score derived from a weighted sum of the temporal score, predictive resilience factor, and entropy value, adjusted by the adaptive feedback loop score to dynamically prioritize different factors based on recent cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            TEMPORAL_WEIGHT * temporal_scores[key] +
            PREDICTIVE_WEIGHT * predictive_resilience_factors[key] +
            ENTROPY_WEIGHT * entropy_values[key] -
            ADAPTIVE_WEIGHT * adaptive_feedback_loop_score
        )
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score is incremented to reflect increased recency and frequency, the predictive resilience factor is recalibrated using recent access patterns, the entropy value is adjusted to reflect the change in access predictability, and the adaptive feedback loop score is updated based on the overall cache hit rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] += 1
    predictive_resilience_factors[key] = math.log(temporal_scores[key] + 1)
    entropy_values[key] = -math.log(1 / (temporal_scores[key] + 1))
    adaptive_feedback_loop_score = cache_snapshot.hit_count / (cache_snapshot.access_count + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal score is initialized to a baseline value, the predictive resilience factor is set using initial access predictions, the entropy value is calculated based on initial access randomness, and the adaptive feedback loop score is adjusted to account for the new entry's impact on cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] = 1
    predictive_resilience_factors[key] = math.log(2)
    entropy_values[key] = -math.log(0.5)
    adaptive_feedback_loop_score = cache_snapshot.hit_count / (cache_snapshot.access_count + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal scores of remaining entries are recalibrated to reflect the change in cache state, the predictive resilience factors are updated to account for the removal of the evicted entry, the entropy values are recalculated to reflect the new access pattern landscape, and the adaptive feedback loop score is adjusted to learn from the eviction's impact on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_scores:
        del temporal_scores[evicted_key]
        del predictive_resilience_factors[evicted_key]
        del entropy_values[evicted_key]
    
    for key in cache_snapshot.cache:
        temporal_scores[key] *= 0.9
        predictive_resilience_factors[key] = math.log(temporal_scores[key] + 1)
        entropy_values[key] = -math.log(1 / (temporal_scores[key] + 1))
    
    adaptive_feedback_loop_score = cache_snapshot.hit_count / (cache_snapshot.access_count + 1)