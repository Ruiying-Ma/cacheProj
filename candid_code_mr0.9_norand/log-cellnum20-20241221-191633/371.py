# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_HARMONY_SCORE = 1.0
LATENCY_COST_FACTOR = 0.1
ENTROPY_GRADIENT_FACTOR = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a 'predictive harmony score' for each cache entry, which is a composite metric derived from access frequency, recency, and a causal dynamics model predicting future access patterns. It also tracks 'latency symmetry' to balance the cost of fetching data from different sources and an 'entropy gradient' to measure the variability in access patterns.
predictive_harmony_scores = defaultdict(lambda: INITIAL_PREDICTIVE_HARMONY_SCORE)
latency_symmetry = defaultdict(float)
entropy_gradient = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive harmony score, ensuring that the choice aligns with minimizing future cache misses. It also considers latency symmetry to avoid evicting entries that would result in high retrieval costs and checks the entropy gradient to ensure stability in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_harmony_scores[key] + latency_symmetry[key] * LATENCY_COST_FACTOR
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive harmony score of the accessed entry is increased, reflecting its continued relevance. The latency symmetry is adjusted to reflect the reduced cost of accessing this entry, and the entropy gradient is recalibrated to account for the change in access pattern stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_harmony_scores[key] += 1
    latency_symmetry[key] -= LATENCY_COST_FACTOR
    global entropy_gradient
    entropy_gradient -= ENTROPY_GRADIENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive harmony score based on initial access predictions and updates the latency symmetry to include the new entry's retrieval cost. The entropy gradient is recalculated to incorporate the new entry's potential impact on access pattern variability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_harmony_scores[key] = INITIAL_PREDICTIVE_HARMONY_SCORE
    latency_symmetry[key] = obj.size * LATENCY_COST_FACTOR
    global entropy_gradient
    entropy_gradient += ENTROPY_GRADIENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive harmony scores of remaining entries are adjusted to reflect the new cache composition. The latency symmetry is updated to remove the evicted entry's influence, and the entropy gradient is recalculated to ensure the cache's access pattern stability is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del predictive_harmony_scores[evicted_key]
    del latency_symmetry[evicted_key]
    global entropy_gradient
    entropy_gradient -= ENTROPY_GRADIENT_FACTOR