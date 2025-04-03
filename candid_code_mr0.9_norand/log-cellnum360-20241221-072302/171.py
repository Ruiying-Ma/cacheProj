# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
NOISE_FILTER_ALPHA = 0.1  # Tunable parameter for noise filtering

# Put the metadata specifically maintained by the policy below. The policy maintains a frequency spectrum for each cache object, representing the access pattern as a time series. It also keeps a noise-filtered signal approximation of these patterns to predict future accesses.
frequency_spectrum = defaultdict(list)
signal_approximation = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy performs spectral analysis on the frequency spectrum of each object to identify the least likely to be accessed in the near future. It uses noise filtering to refine predictions and selects the object with the lowest predicted access frequency for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predicted_access = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Perform spectral analysis (e.g., using FFT) on the frequency spectrum
        spectrum = np.fft.fft(frequency_spectrum[key])
        # Use the noise-filtered signal approximation
        predicted_access = signal_approximation[key]
        
        # Select the object with the lowest predicted access frequency
        if predicted_access < min_predicted_access:
            min_predicted_access = predicted_access
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the frequency spectrum of the accessed object by adding the current access to the time series. It then recalculates the noise-filtered signal approximation to adjust future access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Update the frequency spectrum with the current access
    frequency_spectrum[obj.key].append(cache_snapshot.access_count)
    
    # Recalculate the noise-filtered signal approximation
    if len(frequency_spectrum[obj.key]) > 1:
        signal_approximation[obj.key] = (1 - NOISE_FILTER_ALPHA) * signal_approximation[obj.key] + NOISE_FILTER_ALPHA * frequency_spectrum[obj.key][-1]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency spectrum with a baseline pattern derived from similar objects. It applies initial noise filtering to establish a preliminary signal approximation for future access prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize frequency spectrum with a baseline pattern
    frequency_spectrum[obj.key] = [cache_snapshot.access_count]
    
    # Apply initial noise filtering
    signal_approximation[obj.key] = frequency_spectrum[obj.key][0]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted object's metadata and recalibrates the frequency spectra of remaining objects to account for the change in cache dynamics, ensuring accurate future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove the evicted object's metadata
    if evicted_obj.key in frequency_spectrum:
        del frequency_spectrum[evicted_obj.key]
    if evicted_obj.key in signal_approximation:
        del signal_approximation[evicted_obj.key]
    
    # Recalibrate the frequency spectra of remaining objects
    for key in frequency_spectrum:
        # Adjust the signal approximation based on new cache dynamics
        signal_approximation[key] = (1 - NOISE_FILTER_ALPHA) * signal_approximation[key] + NOISE_FILTER_ALPHA * frequency_spectrum[key][-1]