# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_CONFLUENCE_SCORE = 1.0
INITIAL_AI_INDEX = 1.0
CONFLUENCE_SCORE_INCREMENT = 0.1
AI_INDEX_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Pattern Synthesis Matrix' that records access patterns, a 'Confluence Score' for each cache entry indicating its relevance to current data trends, and an 'Algorithmic Intelligence Index' that predicts future access likelihood based on historical data.
pattern_synthesis_matrix = defaultdict(int)
confluence_scores = defaultdict(lambda: INITIAL_CONFLUENCE_SCORE)
ai_indices = defaultdict(lambda: INITIAL_AI_INDEX)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined Confluence Score and Algorithmic Intelligence Index, ensuring that entries least likely to be accessed soon and least relevant to current data trends are evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = confluence_scores[key] + ai_indices[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Pattern Synthesis Matrix is updated to reinforce the detected access pattern, the Confluence Score of the accessed entry is increased to reflect its relevance, and the Algorithmic Intelligence Index is adjusted to predict future accesses more accurately.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    pattern_synthesis_matrix[obj.key] += 1
    confluence_scores[obj.key] += CONFLUENCE_SCORE_INCREMENT
    ai_indices[obj.key] += AI_INDEX_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Pattern Synthesis Matrix is updated to include the new access pattern, the Confluence Score is initialized based on the object's initial relevance, and the Algorithmic Intelligence Index is set using initial predictions of access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    pattern_synthesis_matrix[obj.key] = 1
    confluence_scores[obj.key] = INITIAL_CONFLUENCE_SCORE
    ai_indices[obj.key] = INITIAL_AI_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Pattern Synthesis Matrix is adjusted to remove outdated patterns, the Confluence Scores of remaining entries are recalibrated to reflect the new data landscape, and the Algorithmic Intelligence Index is refined to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in pattern_synthesis_matrix:
        del pattern_synthesis_matrix[evicted_obj.key]
    if evicted_obj.key in confluence_scores:
        del confluence_scores[evicted_obj.key]
    if evicted_obj.key in ai_indices:
        del ai_indices[evicted_obj.key]
    
    # Recalibrate scores for remaining entries
    for key in cache_snapshot.cache:
        confluence_scores[key] *= 0.9  # Example recalibration
        ai_indices[key] *= 0.9  # Example recalibration