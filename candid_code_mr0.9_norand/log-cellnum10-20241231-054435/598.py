# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_DYNAMIC_CONTINUUM_SCORE = 0
INITIAL_CASCADE_TIER = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-tiered metadata structure: a Cascade Expansion list for tracking access frequency, a Dynamic Continuum score for temporal locality, a Phase Interlock System for phase detection, and an Adaptive Synchronization counter for workload adaptation.
cascade_expansion = defaultdict(deque)  # Maps tiers to deques of object keys
dynamic_continuum_scores = {}  # Maps object keys to their dynamic continuum scores
phase_interlock_system = {}  # Maps object keys to their phase information
adaptive_synchronization_counter = 0  # Counter for workload adaptation

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by first identifying the lowest Cascade Expansion tier, then choosing the object with the lowest Dynamic Continuum score within that tier. If a tie occurs, the Phase Interlock System is consulted to determine the least recently used phase, and the Adaptive Synchronization counter is used to break any remaining ties.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for tier in sorted(cascade_expansion.keys()):
        if cascade_expansion[tier]:
            # Find the object with the lowest Dynamic Continuum score in this tier
            min_score = float('inf')
            candidates = []
            for key in cascade_expansion[tier]:
                score = dynamic_continuum_scores.get(key, float('inf'))
                if score < min_score:
                    min_score = score
                    candidates = [key]
                elif score == min_score:
                    candidates.append(key)
            
            # If there's a tie, use the Phase Interlock System
            if len(candidates) > 1:
                min_phase = float('inf')
                phase_candidates = []
                for key in candidates:
                    phase = phase_interlock_system.get(key, float('inf'))
                    if phase < min_phase:
                        min_phase = phase
                        phase_candidates = [key]
                    elif phase == min_phase:
                        phase_candidates.append(key)
                candidates = phase_candidates
            
            # If there's still a tie, use the Adaptive Synchronization counter
            if len(candidates) > 1:
                candidates.sort()  # Sort to ensure deterministic choice
                candid_obj_key = candidates[0]
            else:
                candid_obj_key = candidates[0]
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's Cascade Expansion tier is incremented, its Dynamic Continuum score is recalculated based on recent access patterns, the Phase Interlock System is updated to reflect the current phase, and the Adaptive Synchronization counter is adjusted to reflect the current workload dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Increment Cascade Expansion tier
    for tier in sorted(cascade_expansion.keys(), reverse=True):
        if key in cascade_expansion[tier]:
            cascade_expansion[tier].remove(key)
            cascade_expansion[tier + 1].append(key)
            break
    
    # Recalculate Dynamic Continuum score
    dynamic_continuum_scores[key] = cache_snapshot.access_count
    
    # Update Phase Interlock System
    phase_interlock_system[key] = cache_snapshot.access_count
    
    # Adjust Adaptive Synchronization counter
    global adaptive_synchronization_counter
    adaptive_synchronization_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the lowest Cascade Expansion tier, assigned an initial Dynamic Continuum score based on insertion time, integrated into the current phase of the Phase Interlock System, and the Adaptive Synchronization counter is incremented to account for the new workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Place in the lowest Cascade Expansion tier
    cascade_expansion[INITIAL_CASCADE_TIER].append(key)
    
    # Assign initial Dynamic Continuum score
    dynamic_continuum_scores[key] = cache_snapshot.access_count
    
    # Integrate into the current phase of the Phase Interlock System
    phase_interlock_system[key] = cache_snapshot.access_count
    
    # Increment Adaptive Synchronization counter
    global adaptive_synchronization_counter
    adaptive_synchronization_counter += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Cascade Expansion list is rebalanced if necessary, the Dynamic Continuum scores of remaining objects are adjusted to reflect the new cache state, the Phase Interlock System is updated to remove the evicted object's phase data, and the Adaptive Synchronization counter is decremented to reflect the reduced workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove evicted object from Cascade Expansion list
    for tier in cascade_expansion:
        if evicted_key in cascade_expansion[tier]:
            cascade_expansion[tier].remove(evicted_key)
            break
    
    # Adjust Dynamic Continuum scores
    for key in dynamic_continuum_scores:
        dynamic_continuum_scores[key] = max(0, dynamic_continuum_scores[key] - 1)
    
    # Remove evicted object's phase data
    if evicted_key in phase_interlock_system:
        del phase_interlock_system[evicted_key]
    
    # Decrement Adaptive Synchronization counter
    global adaptive_synchronization_counter
    adaptive_synchronization_counter = max(0, adaptive_synchronization_counter - 1)