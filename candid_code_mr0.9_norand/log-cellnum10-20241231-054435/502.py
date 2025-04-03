# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_EQ_SCORE = 1.0
INITIAL_PREDICTIVE_SCORE = 1.0
INITIAL_CONTEXTUAL_RELEVANCE = 1.0
EQ_SCORE_INCREMENT = 0.1
PREDICTIVE_SCORE_ADJUSTMENT = 0.05
CONTEXTUAL_RELEVANCE_ADJUSTMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic equilibrium score for each cache entry, a predictive access pattern score, and a contextual relevance factor. These scores are periodically adjusted based on system-wide access patterns and individual entry behavior.
equilibrium_scores = defaultdict(lambda: BASELINE_EQ_SCORE)
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
contextual_relevance = defaultdict(lambda: INITIAL_CONTEXTUAL_RELEVANCE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest combined score of equilibrium, predictive access, and contextual relevance. This ensures that entries with low future utility and relevance are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (equilibrium_scores[key] + 
                          predictive_scores[key] + 
                          contextual_relevance[key])
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the equilibrium score is increased to reflect the entry's current utility, the predictive access score is adjusted based on recent access patterns, and the contextual relevance factor is recalibrated to account for the current workload context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    equilibrium_scores[key] += EQ_SCORE_INCREMENT
    predictive_scores[key] += PREDICTIVE_SCORE_ADJUSTMENT
    contextual_relevance[key] += CONTEXTUAL_RELEVANCE_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the equilibrium score is initialized to a baseline value, the predictive access score is set based on initial access predictions, and the contextual relevance factor is adjusted to align with the current system context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    equilibrium_scores[key] = BASELINE_EQ_SCORE
    predictive_scores[key] = INITIAL_PREDICTIVE_SCORE
    contextual_relevance[key] = INITIAL_CONTEXTUAL_RELEVANCE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the equilibrium scores of remaining entries to maintain systemic balance, updates predictive scores to reflect the change in cache composition, and adjusts contextual relevance factors to ensure alignment with the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        equilibrium_scores[key] *= 0.95
        predictive_scores[key] *= 0.95
        contextual_relevance[key] *= 0.95