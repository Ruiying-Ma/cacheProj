# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
BASE_QUANTUM_FREQUENCY = 1
NEUTRAL_ENTROPIC_MODULE = 0.5
PREDICTIVE_SIGNAL_BASE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Frequency counter for each cache entry, an Entropic Module to measure the randomness of access patterns, a Temporal Fusion timestamp to track the last access time, and a Predictive Signal score to estimate future access likelihood.
quantum_frequency = defaultdict(lambda: BASE_QUANTUM_FREQUENCY)
entropic_module = defaultdict(lambda: NEUTRAL_ENTROPIC_MODULE)
temporal_fusion = {}
predictive_signal = defaultdict(lambda: PREDICTIVE_SIGNAL_BASE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Predictive Signal score, breaking ties by selecting the entry with the highest Entropic Module value, indicating the least predictable access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_predictive_signal = float('inf')
    max_entropic_module = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        ps = predictive_signal[key]
        em = entropic_module[key]
        
        if ps < min_predictive_signal or (ps == min_predictive_signal and em > max_entropic_module):
            min_predictive_signal = ps
            max_entropic_module = em
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Frequency counter is incremented, the Entropic Module is recalculated to reflect the updated access pattern, the Temporal Fusion timestamp is updated to the current time, and the Predictive Signal score is adjusted based on recent access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    quantum_frequency[key] += 1
    temporal_fusion[key] = cache_snapshot.access_count
    
    # Recalculate Entropic Module
    entropic_module[key] = 1 - (1 / (1 + math.log(quantum_frequency[key])))
    
    # Adjust Predictive Signal
    predictive_signal[key] = min(1.0, predictive_signal[key] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Frequency counter is initialized to a base value, the Entropic Module is set to a neutral state, the Temporal Fusion timestamp is set to the current time, and the Predictive Signal score is initialized using historical data if available.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    quantum_frequency[key] = BASE_QUANTUM_FREQUENCY
    entropic_module[key] = NEUTRAL_ENTROPIC_MODULE
    temporal_fusion[key] = cache_snapshot.access_count
    predictive_signal[key] = PREDICTIVE_SIGNAL_BASE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the Entropic Module to account for the reduced cache size, adjusts the Predictive Signal scores of remaining entries to reflect the new cache dynamics, and resets any dependent metadata as necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del quantum_frequency[evicted_key]
    del entropic_module[evicted_key]
    del temporal_fusion[evicted_key]
    del predictive_signal[evicted_key]
    
    # Recalibrate Entropic Module and Predictive Signal for remaining entries
    for key in cache_snapshot.cache:
        entropic_module[key] = 1 - (1 / (1 + math.log(quantum_frequency[key])))
        predictive_signal[key] = max(0.0, predictive_signal[key] - 0.05)