# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_ENTROPIC_FUSION_SCORE = 1.0
NEUTRAL_QUANTUM_PHASE_SHIFT = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Matrix that calibrates access patterns, a Quantum Phase Shift indicator for each cache entry, an Entropic Fusion score representing the entropy of data access, and a Temporal Data Stream log to track the recency and frequency of accesses.
predictive_matrix = defaultdict(lambda: defaultdict(float))
quantum_phase_shift = defaultdict(lambda: NEUTRAL_QUANTUM_PHASE_SHIFT)
entropic_fusion_score = defaultdict(lambda: INITIAL_ENTROPIC_FUSION_SCORE)
temporal_data_stream = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest Entropic Fusion score, adjusted by the Quantum Phase Shift indicator, and the least recent access in the Temporal Data Stream.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = entropic_fusion_score[key] + quantum_phase_shift[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key

    # Ensure the least recent access is considered
    for key in temporal_data_stream:
        if key in cache_snapshot.cache:
            if entropic_fusion_score[key] + quantum_phase_shift[key] == min_score:
                candid_obj_key = key
                break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Predictive Matrix is recalibrated to increase the probability of future accesses, the Quantum Phase Shift indicator is adjusted to reflect the current state of access, the Entropic Fusion score is incremented to reflect increased entropy, and the Temporal Data Stream is updated to log the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Update Predictive Matrix
    for other_key in cache_snapshot.cache:
        if other_key != obj.key:
            predictive_matrix[obj.key][other_key] += 1

    # Adjust Quantum Phase Shift
    quantum_phase_shift[obj.key] += 0.1

    # Increment Entropic Fusion Score
    entropic_fusion_score[obj.key] += 0.1

    # Update Temporal Data Stream
    if obj.key in temporal_data_stream:
        temporal_data_stream.remove(obj.key)
    temporal_data_stream.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Predictive Matrix is updated to include the new access pattern, the Quantum Phase Shift is initialized to a neutral state, the Entropic Fusion score is set based on initial access entropy, and the Temporal Data Stream logs the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Update Predictive Matrix
    for other_key in cache_snapshot.cache:
        if other_key != obj.key:
            predictive_matrix[obj.key][other_key] = 0

    # Initialize Quantum Phase Shift
    quantum_phase_shift[obj.key] = NEUTRAL_QUANTUM_PHASE_SHIFT

    # Set Entropic Fusion Score
    entropic_fusion_score[obj.key] = INITIAL_ENTROPIC_FUSION_SCORE

    # Log insertion time in Temporal Data Stream
    temporal_data_stream.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Predictive Matrix is recalibrated to remove the evicted pattern, the Quantum Phase Shift indicators are adjusted to reflect the new cache state, the Entropic Fusion scores are recalculated to account for the change in entropy, and the Temporal Data Stream is purged of the evicted entry's logs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalibrate Predictive Matrix
    if evicted_obj.key in predictive_matrix:
        del predictive_matrix[evicted_obj.key]
    for key in predictive_matrix:
        if evicted_obj.key in predictive_matrix[key]:
            del predictive_matrix[key][evicted_obj.key]

    # Adjust Quantum Phase Shift
    if evicted_obj.key in quantum_phase_shift:
        del quantum_phase_shift[evicted_obj.key]

    # Recalculate Entropic Fusion Scores
    if evicted_obj.key in entropic_fusion_score:
        del entropic_fusion_score[evicted_obj.key]

    # Purge Temporal Data Stream
    if evicted_obj.key in temporal_data_stream:
        temporal_data_stream.remove(evicted_obj.key)