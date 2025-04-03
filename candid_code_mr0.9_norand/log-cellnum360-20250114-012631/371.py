# Import anything you need below
import numpy as np

# Put tunable constant parameters below
DEFAULT_ENTROPY_SCORE = 100.0
DEFAULT_SPECTRUM_ESTIMATION = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Neural Congruence Matrix (NCM) to track access patterns, an entropy score for each cache line to measure predictability, and a dynamic spectrum estimation to monitor frequency of accesses. It also uses a predictive fusion model to combine these metrics and predict future access patterns.
NCM = {}
entropy_scores = {}
spectrum_estimations = {}
predictive_fusion_model = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the highest entropy score, indicating the least predictable access pattern, and the lowest dynamic spectrum estimation, indicating infrequent access. The predictive fusion model is used to validate this choice.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_spectrum = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropy_scores.get(key, DEFAULT_ENTROPY_SCORE)
        spectrum = spectrum_estimations.get(key, DEFAULT_SPECTRUM_ESTIMATION)
        
        if entropy > max_entropy or (entropy == max_entropy and spectrum < min_spectrum):
            max_entropy = entropy
            min_spectrum = spectrum
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the NCM is updated to reinforce the access pattern, the entropy score is recalculated to reflect the increased predictability, and the dynamic spectrum estimation is adjusted to account for the recent access frequency. The predictive fusion model is also updated with the new data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    
    # Update NCM
    if key not in NCM:
        NCM[key] = np.zeros(len(cache_snapshot.cache))
    NCM[key] += 1
    
    # Recalculate entropy score
    entropy_scores[key] = -np.sum(NCM[key] * np.log(NCM[key] + 1e-9))
    
    # Adjust dynamic spectrum estimation
    spectrum_estimations[key] = spectrum_estimations.get(key, DEFAULT_SPECTRUM_ESTIMATION) + 1
    
    # Update predictive fusion model
    predictive_fusion_model[key] = (entropy_scores[key], spectrum_estimations[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the NCM is initialized for the new cache line, the entropy score is set to a default high value indicating initial unpredictability, and the dynamic spectrum estimation is set to a low value. The predictive fusion model is updated to include the new cache line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    
    # Initialize NCM for the new cache line
    NCM[key] = np.zeros(len(cache_snapshot.cache))
    
    # Set entropy score to default high value
    entropy_scores[key] = DEFAULT_ENTROPY_SCORE
    
    # Set dynamic spectrum estimation to low value
    spectrum_estimations[key] = DEFAULT_SPECTRUM_ESTIMATION
    
    # Update predictive fusion model
    predictive_fusion_model[key] = (entropy_scores[key], spectrum_estimations[key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the NCM is adjusted to remove the evicted cache line, the entropy scores are recalibrated for the remaining lines, and the dynamic spectrum estimation is updated to reflect the removal. The predictive fusion model is also updated to exclude the evicted cache line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Adjust NCM to remove the evicted cache line
    if evicted_key in NCM:
        del NCM[evicted_key]
    
    # Recalibrate entropy scores for the remaining lines
    for key in cache_snapshot.cache:
        if key in NCM:
            entropy_scores[key] = -np.sum(NCM[key] * np.log(NCM[key] + 1e-9))
    
    # Update dynamic spectrum estimation to reflect the removal
    if evicted_key in spectrum_estimations:
        del spectrum_estimations[evicted_key]
    
    # Update predictive fusion model to exclude the evicted cache line
    if evicted_key in predictive_fusion_model:
        del predictive_fusion_model[evicted_key]