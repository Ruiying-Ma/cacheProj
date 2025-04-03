# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
NEUTRAL_ENTROPIC_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Redistribution Matrix to track access patterns over time, a Quantum Pathway Convergence Map to identify potential future access paths, an Entropic Resonance Feedback score to measure the stability of access patterns, and a Predictive Complexity Vector to estimate the computational complexity of future accesses.
temporal_redistribution_matrix = defaultdict(lambda: defaultdict(int))
quantum_pathway_convergence_map = defaultdict(set)
entropic_resonance_feedback = defaultdict(lambda: NEUTRAL_ENTROPIC_SCORE)
predictive_complexity_vector = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest Entropic Resonance Feedback score, indicating a stable but low-frequency access pattern, and cross-referencing it with the Predictive Complexity Vector to ensure minimal impact on future computational complexity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = entropic_resonance_feedback[key] + predictive_complexity_vector[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Redistribution Matrix is updated to reflect the recent access, the Quantum Pathway Convergence Map is adjusted to reinforce the likelihood of future accesses along similar paths, the Entropic Resonance Feedback score is recalibrated to reflect increased access stability, and the Predictive Complexity Vector is refined to incorporate the latest access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_redistribution_matrix[key][cache_snapshot.access_count] += 1
    quantum_pathway_convergence_map[key].add(cache_snapshot.access_count)
    entropic_resonance_feedback[key] += 0.1  # Increase stability
    predictive_complexity_vector[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Temporal Redistribution Matrix is initialized for the new entry, the Quantum Pathway Convergence Map is updated to include potential new access paths, the Entropic Resonance Feedback score is set to a neutral value, and the Predictive Complexity Vector is adjusted to account for the new entry's potential impact on future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_redistribution_matrix[key] = defaultdict(int)
    quantum_pathway_convergence_map[key] = set()
    entropic_resonance_feedback[key] = NEUTRAL_ENTROPIC_SCORE
    predictive_complexity_vector[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Temporal Redistribution Matrix is purged of the evicted entry's data, the Quantum Pathway Convergence Map is recalibrated to remove obsolete paths, the Entropic Resonance Feedback score is adjusted to reflect the change in cache stability, and the Predictive Complexity Vector is updated to exclude the evicted entry's influence on future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in temporal_redistribution_matrix:
        del temporal_redistribution_matrix[key]
    if key in quantum_pathway_convergence_map:
        del quantum_pathway_convergence_map[key]
    if key in entropic_resonance_feedback:
        del entropic_resonance_feedback[key]
    if key in predictive_complexity_vector:
        del predictive_complexity_vector[key]