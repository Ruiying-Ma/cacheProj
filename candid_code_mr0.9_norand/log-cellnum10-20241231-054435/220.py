# Import anything you need below
from collections import deque, defaultdict
import math

# Put tunable constant parameters below
ENTROPY_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a circular list of cache entries, a phase transition counter for each entry, a temporal coherence map that tracks access patterns over time, and an adaptive entropy value that adjusts based on access frequency and pattern shifts.
circular_list = deque()
phase_transition_counter = defaultdict(int)
temporal_coherence_map = defaultdict(int)
adaptive_entropy = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim for eviction by iterating through the circular list and identifying entries with the highest phase transition counter and lowest temporal coherence, adjusted by the adaptive entropy shift to prioritize entries with less predictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -math.inf
    
    for key in circular_list:
        ptc = phase_transition_counter[key]
        tc = temporal_coherence_map[key]
        score = ptc - (tc + adaptive_entropy)
        
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the phase transition counter for the accessed entry is incremented, the temporal coherence map is updated to reflect the recent access, and the adaptive entropy is recalculated to account for the change in access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    phase_transition_counter[key] += 1
    temporal_coherence_map[key] = cache_snapshot.access_count
    global adaptive_entropy
    adaptive_entropy += ENTROPY_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the phase transition counter is initialized, the temporal coherence map is updated to include the new entry with its initial access pattern, and the adaptive entropy is adjusted to reflect the addition of a new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    circular_list.append(key)
    phase_transition_counter[key] = 0
    temporal_coherence_map[key] = cache_snapshot.access_count
    global adaptive_entropy
    adaptive_entropy += ENTROPY_ADJUSTMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the phase transition counter for the evicted entry is reset, the temporal coherence map is purged of the evicted entry's data, and the adaptive entropy is recalibrated to account for the reduced cache size and altered access dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    circular_list.remove(key)
    del phase_transition_counter[key]
    del temporal_coherence_map[key]
    global adaptive_entropy
    adaptive_entropy -= ENTROPY_ADJUSTMENT_FACTOR