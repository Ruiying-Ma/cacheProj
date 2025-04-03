# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_COHERENCE_SCORE = 1
INITIAL_NEUROMORPHIC_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a symbolic sequence of access patterns, a coherence score for each cache line, a neuromorphic-inspired weight for each line indicating its spatial relevance, and a spatial map of cache line interactions.
coherence_scores = defaultdict(lambda: INITIAL_COHERENCE_SCORE)
neuromorphic_weights = defaultdict(lambda: INITIAL_NEUROMORPHIC_WEIGHT)
symbolic_sequence = []
spatial_map = defaultdict(dict)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the lowest coherence score, adjusted by its neuromorphic weight and spatial relevance, ensuring minimal disruption to the symbolic sequence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = coherence_scores[key] * neuromorphic_weights[key]
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the coherence score of the accessed line is incremented, its neuromorphic weight is adjusted based on recent spatial interactions, and the symbolic sequence is updated to reflect the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    coherence_scores[key] += 1
    neuromorphic_weights[key] *= 1.1  # Example adjustment, can be tuned
    symbolic_sequence.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its coherence score and neuromorphic weight based on spatial proximity to existing lines, and updates the symbolic sequence to include the new line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    coherence_scores[key] = INITIAL_COHERENCE_SCORE
    neuromorphic_weights[key] = INITIAL_NEUROMORPHIC_WEIGHT
    symbolic_sequence.append(key)
    
    # Initialize spatial interactions
    for other_key in cache_snapshot.cache:
        if other_key != key:
            spatial_map[key][other_key] = 0
            spatial_map[other_key][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the coherence scores and neuromorphic weights of remaining lines, and updates the spatial map to remove interactions involving the evicted line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del coherence_scores[evicted_key]
    del neuromorphic_weights[evicted_key]
    
    # Remove spatial interactions involving the evicted line
    if evicted_key in spatial_map:
        del spatial_map[evicted_key]
    for other_key in spatial_map:
        if evicted_key in spatial_map[other_key]:
            del spatial_map[other_key][evicted_key]