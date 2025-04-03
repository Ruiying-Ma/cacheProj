# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_ENTROPIC_SCALING = 1.0
INITIAL_QFI_SCORE = 1.0
QFI_INCREMENT = 1.0
ENTROPIC_SCALING_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Synchronization Grid (TSG) that maps cache entries to temporal phases, an Entropic Scaling factor for each entry to measure access irregularity, and a Quantum Feedback Integration (QFI) score that adjusts based on recent access patterns.
temporal_phases = defaultdict(int)  # Maps object keys to their temporal phase
entropic_scaling = defaultdict(lambda: INITIAL_ENTROPIC_SCALING)  # Maps object keys to their entropic scaling
qfi_scores = defaultdict(lambda: INITIAL_QFI_SCORE)  # Maps object keys to their QFI score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying entries with the lowest QFI score within the least active temporal phase of the TSG, factoring in the Entropic Scaling to prioritize entries with more predictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the least active temporal phase
    min_phase = min(temporal_phases.values(), default=None)
    if min_phase is not None:
        # Filter objects in the least active phase
        candidates = [key for key, phase in temporal_phases.items() if phase == min_phase]
        # Find the candidate with the lowest QFI score, factoring in entropic scaling
        candid_obj_key = min(candidates, key=lambda k: (qfi_scores[k], entropic_scaling[k]), default=None)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the TSG phase of the accessed entry is updated to reflect its current temporal activity, the Entropic Scaling is adjusted to reflect the regularity of access, and the QFI score is incremented to reward recent usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Update the TSG phase to the current access count
    temporal_phases[obj.key] = cache_snapshot.access_count
    # Adjust the entropic scaling to reflect regularity
    entropic_scaling[obj.key] += ENTROPIC_SCALING_ADJUSTMENT
    # Increment the QFI score
    qfi_scores[obj.key] += QFI_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to the current active phase in the TSG, initializes its Entropic Scaling to a neutral value, and sets its QFI score based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Assign to the current active phase
    temporal_phases[obj.key] = cache_snapshot.access_count
    # Initialize entropic scaling to a neutral value
    entropic_scaling[obj.key] = INITIAL_ENTROPIC_SCALING
    # Set QFI score based on initial access predictions
    qfi_scores[obj.key] = INITIAL_QFI_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the TSG is recalibrated to reflect the removal, the Entropic Scaling of remaining entries is adjusted to account for the change in cache dynamics, and the QFI scores are normalized to maintain balance across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Remove the evicted object from metadata
    if evicted_obj.key in temporal_phases:
        del temporal_phases[evicted_obj.key]
    if evicted_obj.key in entropic_scaling:
        del entropic_scaling[evicted_obj.key]
    if evicted_obj.key in qfi_scores:
        del qfi_scores[evicted_obj.key]
    
    # Adjust entropic scaling and normalize QFI scores
    for key in cache_snapshot.cache:
        entropic_scaling[key] = max(1.0, entropic_scaling[key] - ENTROPIC_SCALING_ADJUSTMENT)
        qfi_scores[key] = max(1.0, qfi_scores[key] - QFI_INCREMENT / 2)