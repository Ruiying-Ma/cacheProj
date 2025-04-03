# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SEM_VALUE = 1.0
CONNECTION_STRENGTH_INCREMENT = 0.1
CONNECTION_STRENGTH_DECREMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Neural Matrix (QNM) that represents the cache state as a dynamic graph, Symbiotic Entropy Modulation (SEM) values for each cache entry to measure their interaction with other entries, and Temporal Flux Mapping (TFM) to track the temporal access patterns. Heuristic Phase Coherence (HPC) is used to identify stable phases in access patterns.
QNM = defaultdict(lambda: defaultdict(float))  # Quantum Neural Matrix
SEM = defaultdict(lambda: BASELINE_SEM_VALUE)  # Symbiotic Entropy Modulation
TFM = {}  # Temporal Flux Mapping

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest Symbiotic Entropy Modulation value, indicating minimal beneficial interaction with other entries, and the least contribution to the current phase's coherence as determined by Heuristic Phase Coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_sem_value = float('inf')
    min_phase_coherence = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        sem_value = SEM[key]
        phase_coherence = cache_snapshot.access_count - TFM[key]
        
        if sem_value < min_sem_value or (sem_value == min_sem_value and phase_coherence < min_phase_coherence):
            min_sem_value = sem_value
            min_phase_coherence = phase_coherence
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Neural Matrix is updated to reinforce the connection strength of the accessed entry, the Symbiotic Entropy Modulation value is adjusted to reflect increased interaction, and the Temporal Flux Mapping is updated to capture the latest access time, enhancing phase coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    TFM[obj_key] = cache_snapshot.access_count
    
    for other_key in cache_snapshot.cache:
        if other_key != obj_key:
            QNM[obj_key][other_key] += CONNECTION_STRENGTH_INCREMENT
            QNM[other_key][obj_key] += CONNECTION_STRENGTH_INCREMENT
    
    SEM[obj_key] += CONNECTION_STRENGTH_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Neural Matrix is expanded to include the new entry, initializing its connections. The Symbiotic Entropy Modulation is set to a baseline value, and the Temporal Flux Mapping records the insertion time, contributing to the initial phase coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    TFM[obj_key] = cache_snapshot.access_count
    SEM[obj_key] = BASELINE_SEM_VALUE
    
    for other_key in cache_snapshot.cache:
        if other_key != obj_key:
            QNM[obj_key][other_key] = 0.0
            QNM[other_key][obj_key] = 0.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Quantum Neural Matrix is pruned to remove the evicted entry, recalibrating connections. The Symbiotic Entropy Modulation values of remaining entries are adjusted to reflect the change in cache dynamics, and the Temporal Flux Mapping is updated to maintain phase coherence without the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove evicted entry from QNM
    if evicted_key in QNM:
        del QNM[evicted_key]
    for other_key in QNM:
        if evicted_key in QNM[other_key]:
            del QNM[other_key][evicted_key]
    
    # Adjust SEM values
    for key in SEM:
        SEM[key] = max(BASELINE_SEM_VALUE, SEM[key] - CONNECTION_STRENGTH_DECREMENT)
    
    # Remove from TFM
    if evicted_key in TFM:
        del TFM[evicted_key]