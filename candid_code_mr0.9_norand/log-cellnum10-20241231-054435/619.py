# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SYNAPTIC_FEEDBACK = 1
NEUTRAL_QUANTUM_PHASE = 0
MODERATE_NEURAL_SYNC = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a Synaptic Feedback Loop index for each cache entry, a Quantum Phase Equilibrium state, an Entropic Density Field value, and a Neural Synchronization Module score. These metadata elements collectively represent the dynamic state and priority of each cache entry.
synaptic_feedback = defaultdict(lambda: BASELINE_SYNAPTIC_FEEDBACK)
quantum_phase_equilibrium = defaultdict(lambda: NEUTRAL_QUANTUM_PHASE)
entropic_density_field = defaultdict(int)
neural_sync_module = defaultdict(lambda: MODERATE_NEURAL_SYNC)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest Neural Synchronization Module score, which indicates the least synchronized entry with current access patterns. In case of a tie, the entry with the highest Entropic Density Field value is selected, representing the most chaotic state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_sync_score = float('inf')
    max_entropy = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        sync_score = neural_sync_module[key]
        entropy = entropic_density_field[key]
        
        if sync_score < min_sync_score or (sync_score == min_sync_score and entropy > max_entropy):
            min_sync_score = sync_score
            max_entropy = entropy
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Synaptic Feedback Loop index is incremented to reinforce the entry's relevance, the Quantum Phase Equilibrium state is adjusted to reflect increased stability, the Entropic Density Field value is decreased to indicate reduced chaos, and the Neural Synchronization Module score is increased to enhance synchronization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    synaptic_feedback[key] += 1
    quantum_phase_equilibrium[key] += 1
    entropic_density_field[key] = max(0, entropic_density_field[key] - 1)
    neural_sync_module[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Synaptic Feedback Loop index is initialized to a baseline value, the Quantum Phase Equilibrium state is set to a neutral position, the Entropic Density Field value is calculated based on initial access patterns, and the Neural Synchronization Module score is set to a moderate level to allow rapid adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    synaptic_feedback[key] = BASELINE_SYNAPTIC_FEEDBACK
    quantum_phase_equilibrium[key] = NEUTRAL_QUANTUM_PHASE
    entropic_density_field[key] = 0  # Initial value, can be adjusted based on specific patterns
    neural_sync_module[key] = MODERATE_NEURAL_SYNC

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Synaptic Feedback Loop index of remaining entries is slightly adjusted to reflect the change in cache dynamics, the Quantum Phase Equilibrium state is recalibrated to maintain balance, the Entropic Density Field values are normalized to account for the removed entry, and the Neural Synchronization Module scores are fine-tuned to optimize future synchronization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        synaptic_feedback[key] = max(1, synaptic_feedback[key] - 1)
        quantum_phase_equilibrium[key] = max(0, quantum_phase_equilibrium[key] - 1)
        entropic_density_field[key] = max(0, entropic_density_field[key] - 1)
        neural_sync_module[key] = max(1, neural_sync_module[key] - 1)