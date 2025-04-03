# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_FREQUENCY = 1
DEFAULT_RECENCY = 1
DEFAULT_PREDICTIVE_SCORE = 0.5
COHERENCE_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a fusion matrix that combines access frequency, recency, and a predictive score for each cache entry. It also tracks coherence levels between cache entries to adaptively adjust priorities.
fusion_matrix = defaultdict(lambda: {
    'frequency': DEFAULT_FREQUENCY,
    'recency': DEFAULT_RECENCY,
    'predictive_score': DEFAULT_PREDICTIVE_SCORE,
    'coherence': 1.0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by applying a heuristic transformation to the fusion matrix, prioritizing entries with low predictive scores and coherence levels, while considering recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entry = fusion_matrix[key]
        score = (entry['predictive_score'] * entry['coherence']) / (entry['frequency'] * entry['recency'])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency values in the fusion matrix are incremented for the accessed entry, and the predictive score is adjusted based on the observed access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    entry = fusion_matrix[obj.key]
    entry['frequency'] += 1
    entry['recency'] = cache_snapshot.access_count
    entry['predictive_score'] = min(1.0, entry['predictive_score'] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its fusion matrix entry with default frequency and recency values, and a predictive score based on initial access patterns. Coherence levels are recalibrated across all entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    fusion_matrix[obj.key] = {
        'frequency': DEFAULT_FREQUENCY,
        'recency': cache_snapshot.access_count,
        'predictive_score': DEFAULT_PREDICTIVE_SCORE,
        'coherence': 1.0
    }
    
    # Recalibrate coherence levels
    for key in fusion_matrix:
        if key != obj.key:
            fusion_matrix[key]['coherence'] *= (1 - COHERENCE_ADJUSTMENT_FACTOR)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the coherence levels in the fusion matrix to reflect the removal, and adjusts predictive scores for remaining entries to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in fusion_matrix:
        del fusion_matrix[evicted_obj.key]
    
    # Recalibrate coherence levels and adjust predictive scores
    for key in fusion_matrix:
        fusion_matrix[key]['coherence'] *= (1 + COHERENCE_ADJUSTMENT_FACTOR)
        fusion_matrix[key]['predictive_score'] = max(0.0, fusion_matrix[key]['predictive_score'] - 0.05)