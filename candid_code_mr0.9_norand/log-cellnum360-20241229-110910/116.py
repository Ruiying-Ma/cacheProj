# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PROBABILITY = 0.5
MODULATION_INCREMENT = 0.1
MODERATE_ENTROPY = 0.5
TEMPORAL_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Vector for each cache entry, representing the access pattern over time, a Quantum Modulation factor indicating the probability of future access, and an Entropic Feedback score reflecting the uncertainty in access patterns. Predictive Calibration is used to adjust these values based on historical data.
temporal_vectors = defaultdict(lambda: 1.0)
quantum_modulation = defaultdict(lambda: BASELINE_PROBABILITY)
entropic_feedback = defaultdict(lambda: MODERATE_ENTROPY)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, combining the inverse of the Quantum Modulation factor, the Entropic Feedback score, and the Temporal Vector's decay. The entry with the highest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        temporal_decay = temporal_vectors[key] * TEMPORAL_DECAY
        composite_score = (1 / quantum_modulation[key]) + entropic_feedback[key] + temporal_decay
        
        if composite_score > max_score:
            max_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Vector is updated to reflect the recent access, the Quantum Modulation factor is increased slightly to boost the probability of future access, and the Entropic Feedback score is recalibrated to reduce uncertainty.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_vectors[key] *= TEMPORAL_DECAY
    quantum_modulation[key] = min(1.0, quantum_modulation[key] + MODULATION_INCREMENT)
    entropic_feedback[key] = max(0.0, entropic_feedback[key] - MODULATION_INCREMENT)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Temporal Vector is initialized with a neutral pattern, the Quantum Modulation factor is set to a baseline probability, and the Entropic Feedback score is set to a moderate level to allow for rapid adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_vectors[key] = 1.0
    quantum_modulation[key] = BASELINE_PROBABILITY
    entropic_feedback[key] = MODERATE_ENTROPY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Predictive Calibration model using the evicted entry's metadata to refine future predictions, and adjusts the Entropic Feedback scores of remaining entries to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del temporal_vectors[evicted_key]
    del quantum_modulation[evicted_key]
    del entropic_feedback[evicted_key]
    
    for key in cache_snapshot.cache:
        entropic_feedback[key] = min(1.0, entropic_feedback[key] + MODULATION_INCREMENT)