# Import anything you need below
import numpy as np

# Put tunable constant parameters below
BASELINE_ACF = 1.0
INITIAL_PSB = 0.5
ENTROPY_DECAY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Hyperplane Projection (QHP) matrix for each cache line, an Adaptive Capacitor Flux (ACF) value representing the dynamic 'charge' of each line, an Entropic Gradient Vector (EGV) indicating the entropy change rate, and a Predictive State Balance (PSB) score forecasting future access patterns.
metadata = {
    'QHP': {},  # QHP matrix for each object
    'ACF': {},  # ACF value for each object
    'EGV': {},  # EGV value for each object
    'PSB': {}   # PSB score for each object
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache line with the lowest PSB score, adjusted by the EGV to account for recent entropy changes, and the ACF to ensure lines with higher 'charge' are retained longer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        psb = metadata['PSB'].get(key, INITIAL_PSB)
        egv = metadata['EGV'].get(key, 0)
        acf = metadata['ACF'].get(key, BASELINE_ACF)
        
        # Calculate adjusted score
        adjusted_score = psb - egv + (1 / acf)
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QHP matrix is recalibrated to reflect the current access pattern, the ACF is incremented to increase the line's 'charge', the EGV is updated to reflect the reduced entropy, and the PSB score is adjusted to predict future hits more accurately.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    
    # Recalibrate QHP matrix
    metadata['QHP'][key] = np.identity(2)  # Example recalibration
    
    # Increment ACF
    metadata['ACF'][key] = metadata['ACF'].get(key, BASELINE_ACF) + 1
    
    # Update EGV
    metadata['EGV'][key] = metadata['EGV'].get(key, 0) - ENTROPY_DECAY
    
    # Adjust PSB score
    metadata['PSB'][key] = metadata['PSB'].get(key, INITIAL_PSB) + 0.1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QHP matrix is initialized to a neutral state, the ACF is set to a baseline value, the EGV is calculated based on initial entropy conditions, and the PSB score is initialized using historical access data if available.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    
    # Initialize QHP matrix
    metadata['QHP'][key] = np.zeros((2, 2))  # Neutral state
    
    # Set ACF to baseline
    metadata['ACF'][key] = BASELINE_ACF
    
    # Calculate EGV
    metadata['EGV'][key] = ENTROPY_DECAY
    
    # Initialize PSB score
    metadata['PSB'][key] = INITIAL_PSB

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QHP matrix of the evicted line is archived for potential future use, the ACF is reset, the EGV is recalibrated to reflect the new cache state, and the PSB scores of remaining lines are adjusted to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Archive QHP matrix
    archived_qhp = metadata['QHP'].pop(evicted_key, None)
    
    # Reset ACF
    metadata['ACF'].pop(evicted_key, None)
    
    # Recalibrate EGV
    for key in cache_snapshot.cache:
        metadata['EGV'][key] = metadata['EGV'].get(key, 0) + ENTROPY_DECAY
    
    # Adjust PSB scores
    for key in cache_snapshot.cache:
        metadata['PSB'][key] = metadata['PSB'].get(key, INITIAL_PSB) - 0.05