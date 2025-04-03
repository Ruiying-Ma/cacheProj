# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1
INITIAL_PRIORITY = 1
PREDICTIVE_SCORE_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including latent access patterns derived from historical data, priority scores modulated by access frequency and recency, adaptive cache size thresholds, and predictive allocation scores based on anticipated future accesses.
latent_access_patterns = defaultdict(int)
priority_scores = defaultdict(lambda: INITIAL_PRIORITY)
predictive_allocation_scores = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by analyzing latent patterns to identify low-priority items, modulating priority scores to account for recent access trends, and choosing the item with the lowest predictive allocation score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate the effective score for eviction decision
        effective_score = (priority_scores[key] * predictive_allocation_scores[key])
        
        if effective_score < min_score:
            min_score = effective_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the latent access patterns to reflect the new access, increases the priority score of the accessed item, and adjusts the predictive allocation score to anticipate future accesses more accurately.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    latent_access_patterns[key] += 1
    priority_scores[key] += PRIORITY_INCREMENT
    predictive_allocation_scores[key] = (predictive_allocation_scores[key] * PREDICTIVE_SCORE_DECAY) + 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates latent patterns to include the new access, assigns an initial priority score based on current access trends, and calculates a predictive allocation score to estimate future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    latent_access_patterns[key] = 1
    priority_scores[key] = INITIAL_PRIORITY
    predictive_allocation_scores[key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates latent patterns to remove the influence of the evicted item, adjusts priority scores of remaining items to reflect the new cache state, and recalculates predictive allocation scores to optimize future cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in latent_access_patterns:
        del latent_access_patterns[evicted_key]
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
    if evicted_key in predictive_allocation_scores:
        del predictive_allocation_scores[evicted_key]
    
    # Recalculate scores for remaining items
    for key in cache_snapshot.cache:
        predictive_allocation_scores[key] *= PREDICTIVE_SCORE_DECAY