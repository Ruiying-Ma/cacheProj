# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_TEMPORAL_LOCALITY_SCORE = 1
INITIAL_COHERENCE_STATE = 'exclusive'  # Possible states: 'exclusive', 'shared', 'modified'

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical structure of cache levels, predictive prefetching patterns, temporal locality scores, and cache coherence states for each cached object.
temporal_locality_scores = defaultdict(lambda: INITIAL_TEMPORAL_LOCALITY_SCORE)
coherence_states = defaultdict(lambda: INITIAL_COHERENCE_STATE)
hierarchical_structure = deque()  # Using deque to maintain order of usage
predictive_prefetching_patterns = defaultdict(list)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest temporal locality score, least recent use, and the coherence state indicating the least shared or modified data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = temporal_locality_scores[key]
        if score < min_score or (score == min_score and coherence_states[key] == 'exclusive'):
            min_score = score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the temporal locality score of the accessed object is increased, its position in the hierarchical structure is updated to reflect recent use, and the coherence state is checked and updated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_locality_scores[key] += 1
    if key in hierarchical_structure:
        hierarchical_structure.remove(key)
    hierarchical_structure.append(key)
    # Coherence state update logic can be added here if necessary

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal locality score, places it in the appropriate level of the hierarchical cache, and sets its initial coherence state. Predictive prefetching patterns are also updated based on the new insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_locality_scores[key] = INITIAL_TEMPORAL_LOCALITY_SCORE
    coherence_states[key] = INITIAL_COHERENCE_STATE
    hierarchical_structure.append(key)
    # Update predictive prefetching patterns if necessary

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes its metadata from the hierarchical structure, adjusts the temporal locality scores of remaining objects if necessary, and updates the coherence states to reflect the removal. Predictive prefetching patterns are also recalibrated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_locality_scores:
        del temporal_locality_scores[evicted_key]
    if evicted_key in coherence_states:
        del coherence_states[evicted_key]
    if evicted_key in hierarchical_structure:
        hierarchical_structure.remove(evicted_key)
    # Adjust temporal locality scores and coherence states if necessary
    # Recalibrate predictive prefetching patterns if necessary