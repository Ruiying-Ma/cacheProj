# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASELINE_TFC = 1.0
DEFAULT_EDR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Spectral Analysis Matrix to capture access patterns, a Temporal Fusion Coefficient to weigh recent accesses, an Entropic Decay Rate to model the likelihood of future accesses, and a Predictive Synchronization Model to align cache state with predicted access sequences.
spectral_analysis_matrix = {}
temporal_fusion_coefficient = {}
entropic_decay_rate = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score from the Spectral Analysis Matrix and Temporal Fusion Coefficient, adjusted by the Entropic Decay Rate to account for future access probability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        sam_score = spectral_analysis_matrix.get(key, 0)
        tfc_score = temporal_fusion_coefficient.get(key, BASELINE_TFC)
        edr_score = entropic_decay_rate.get(key, DEFAULT_EDR)
        
        combined_score = sam_score + tfc_score - edr_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Spectral Analysis Matrix is updated to reflect the new access pattern, the Temporal Fusion Coefficient is incremented to emphasize recent access, and the Entropic Decay Rate is recalibrated to adjust the likelihood of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    spectral_analysis_matrix[key] = spectral_analysis_matrix.get(key, 0) + 1
    temporal_fusion_coefficient[key] = temporal_fusion_coefficient.get(key, BASELINE_TFC) + 1
    entropic_decay_rate[key] = DEFAULT_EDR * (1 + np.log1p(spectral_analysis_matrix[key]))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Spectral Analysis Matrix is expanded to include the new access pattern, the Temporal Fusion Coefficient is initialized to a baseline value, and the Entropic Decay Rate is set to a default decay value to start tracking future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    spectral_analysis_matrix[key] = 1
    temporal_fusion_coefficient[key] = BASELINE_TFC
    entropic_decay_rate[key] = DEFAULT_EDR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Spectral Analysis Matrix is adjusted to remove the evicted entry's influence, the Temporal Fusion Coefficient is recalculated to redistribute weight among remaining entries, and the Entropic Decay Rate is updated to reflect the new cache state dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in spectral_analysis_matrix:
        del spectral_analysis_matrix[evicted_key]
    if evicted_key in temporal_fusion_coefficient:
        del temporal_fusion_coefficient[evicted_key]
    if evicted_key in entropic_decay_rate:
        del entropic_decay_rate[evicted_key]
    
    # Recalculate TFC and EDR for remaining entries
    for key in cache_snapshot.cache:
        temporal_fusion_coefficient[key] = BASELINE_TFC
        entropic_decay_rate[key] = DEFAULT_EDR * (1 + np.log1p(spectral_analysis_matrix.get(key, 0)))