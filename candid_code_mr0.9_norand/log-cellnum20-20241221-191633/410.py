# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
BASE_TEMPORAL_SCORE = 1
BASE_PREDICTIVE_SCORE = 1
NEUTRAL_REFINEMENT_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal consistency score for each cache entry, an adaptive refinement factor that adjusts based on access patterns, a predictive balance score that estimates future access likelihood, and a multi-tiered queue system to optimize access order.
temporal_scores = defaultdict(lambda: BASE_TEMPORAL_SCORE)
predictive_scores = defaultdict(lambda: BASE_PREDICTIVE_SCORE)
refinement_factors = defaultdict(lambda: NEUTRAL_REFINEMENT_FACTOR)
queue_tiers = defaultdict(deque)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest combined score of temporal consistency and predictive balance, while considering the adaptive refinement factor to ensure dynamic adjustment to changing patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (temporal_scores[key] + predictive_scores[key]) * refinement_factors[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal consistency score is incremented, the adaptive refinement factor is adjusted to reflect the recent access, and the predictive balance score is recalibrated to increase the likelihood of future hits. The entry is also repositioned in the queue to reflect its updated priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] += 1
    refinement_factors[key] *= 1.1  # Example adjustment
    predictive_scores[key] += 1
    
    # Reposition in queue
    for tier in queue_tiers.values():
        if key in tier:
            tier.remove(key)
            tier.appendleft(key)
            break

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal consistency score and predictive balance score to baseline values, while setting the adaptive refinement factor to a neutral state. The object is placed in the appropriate queue tier based on its initial scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] = BASE_TEMPORAL_SCORE
    predictive_scores[key] = BASE_PREDICTIVE_SCORE
    refinement_factors[key] = NEUTRAL_REFINEMENT_FACTOR
    
    # Place in appropriate queue tier
    queue_tiers[0].append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the adaptive refinement factor across the cache to account for the removed entry, adjusts the queue tiers to maintain optimal access order, and updates the predictive balance scores of remaining entries to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove from metadata
    del temporal_scores[evicted_key]
    del predictive_scores[evicted_key]
    del refinement_factors[evicted_key]
    
    # Remove from queue tiers
    for tier in queue_tiers.values():
        if evicted_key in tier:
            tier.remove(evicted_key)
            break
    
    # Recalibrate refinement factors and predictive scores
    for key in cache_snapshot.cache:
        refinement_factors[key] *= 0.9  # Example adjustment
        predictive_scores[key] = max(BASE_PREDICTIVE_SCORE, predictive_scores[key] - 1)