# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
ENTROPY_DECAY = 0.9
INITIAL_ENTROPY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a multidimensional scaling (MDS) map of cache objects, a predictive neural matrix (PNM) for access patterns, entropy values for each object, and temporal signal data for access times.
mds_map = {}
pnm = defaultdict(lambda: defaultdict(float))
entropy_values = {}
temporal_signals = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the object with the highest entropy value and the least recent temporal signal, adjusted by the predictive neural matrix to forecast future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_signal = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropy_values.get(key, INITIAL_ENTROPY)
        signal = temporal_signals.get(key, 0)
        predicted_access = pnm[obj.key].get(key, 0)
        
        if entropy > max_entropy or (entropy == max_entropy and signal < min_signal and predicted_access < 0.5):
            max_entropy = entropy
            min_signal = signal
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the MDS map is updated to reflect the new position of the accessed object, the PNM is adjusted to reinforce the access pattern, the entropy value is reduced, and the temporal signal is refreshed to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Update MDS map
    mds_map[obj.key] = cache_snapshot.access_count
    
    # Adjust PNM
    for key in cache_snapshot.cache:
        if key != obj.key:
            pnm[obj.key][key] += 1
    
    # Reduce entropy value
    entropy_values[obj.key] = entropy_values.get(obj.key, INITIAL_ENTROPY) * ENTROPY_DECAY
    
    # Refresh temporal signal
    temporal_signals[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the MDS map is expanded to include the new object, the PNM is updated to incorporate potential new access patterns, the entropy value is initialized, and the temporal signal is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Expand MDS map
    mds_map[obj.key] = cache_snapshot.access_count
    
    # Update PNM
    for key in cache_snapshot.cache:
        pnm[obj.key][key] = 0
        pnm[key][obj.key] = 0
    
    # Initialize entropy value
    entropy_values[obj.key] = INITIAL_ENTROPY
    
    # Set temporal signal
    temporal_signals[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the MDS map is recalibrated to remove the evicted object, the PNM is adjusted to remove the influence of the evicted object, the entropy values are normalized, and the temporal signals are updated to reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate MDS map
    if evicted_obj.key in mds_map:
        del mds_map[evicted_obj.key]
    
    # Adjust PNM
    if evicted_obj.key in pnm:
        del pnm[evicted_obj.key]
    for key in pnm:
        if evicted_obj.key in pnm[key]:
            del pnm[key][evicted_obj.key]
    
    # Normalize entropy values
    total_entropy = sum(entropy_values.values())
    if total_entropy > 0:
        for key in entropy_values:
            entropy_values[key] /= total_entropy
    
    # Update temporal signals
    for key in temporal_signals:
        temporal_signals[key] = cache_snapshot.access_count