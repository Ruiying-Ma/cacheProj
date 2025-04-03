# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASELINE_NSV = np.array([1, 0, 0, 0, 0])  # Example baseline NSV
NEUTRAL_ESC = 1.0
MODERATE_TR = 5.0
TR_INCREMENT = 1.0
ESC_ADJUSTMENT_FACTOR = 0.1
TR_ADJUSTMENT_FACTOR = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a Neural Signal Vector (NSV) for each cache entry, representing its access pattern as a multi-dimensional vector. It also tracks an Entropic State Capture (ESC) value, indicating the randomness of access patterns, and a Temporal Resilience (TR) score, reflecting the entry's ability to withstand temporal fluctuations in access frequency.
cache_metadata = {
    'NSV': {},  # Dictionary to store NSV for each object
    'ESC': {},  # Dictionary to store ESC for each object
    'TR': {}    # Dictionary to store TR for each object
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of NSV magnitude and TR score, adjusted by the ESC value to prioritize entries with more predictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        nsv_magnitude = np.linalg.norm(cache_metadata['NSV'][key])
        tr_score = cache_metadata['TR'][key]
        esc_value = cache_metadata['ESC'][key]
        
        combined_score = (nsv_magnitude + tr_score) / esc_value
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the NSV of the accessed entry is updated by incrementing the vector component corresponding to the current time slice, the ESC value is recalculated to reflect the new access pattern, and the TR score is increased to enhance the entry's temporal resilience.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    time_slice = cache_snapshot.access_count % len(BASELINE_NSV)
    
    # Update NSV
    cache_metadata['NSV'][key][time_slice] += 1
    
    # Recalculate ESC (example: using entropy-like measure)
    nsv = cache_metadata['NSV'][key]
    esc_value = np.sum(nsv) / (np.linalg.norm(nsv) + 1e-5)
    cache_metadata['ESC'][key] = esc_value
    
    # Increase TR score
    cache_metadata['TR'][key] += TR_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its NSV with a baseline vector, sets the ESC value to a neutral state, and assigns a moderate TR score to allow the entry to adapt to future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    
    # Initialize NSV
    cache_metadata['NSV'][key] = np.copy(BASELINE_NSV)
    
    # Set ESC to neutral state
    cache_metadata['ESC'][key] = NEUTRAL_ESC
    
    # Assign moderate TR score
    cache_metadata['TR'][key] = MODERATE_TR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the ESC values of remaining entries to account for the change in cache dynamics and slightly adjusts the TR scores to maintain balance in temporal resilience across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache.keys():
        # Recalibrate ESC values
        cache_metadata['ESC'][key] *= (1 + ESC_ADJUSTMENT_FACTOR)
        
        # Adjust TR scores
        cache_metadata['TR'][key] *= (1 - TR_ADJUSTMENT_FACTOR)