# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.3
QUANTUM_WEIGHT = 0.2
ENTROPIC_BASELINE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Cognitive Resonance Score' for each cache entry, which is a composite measure derived from access frequency, recency, and a 'Quantum Synchronization Index' that reflects the temporal alignment of access patterns. Additionally, an 'Entropic Amplifier' value is calculated to gauge the unpredictability of access patterns.
cognitive_resonance_scores = defaultdict(lambda: 0)
access_frequencies = defaultdict(lambda: 0)
last_access_times = defaultdict(lambda: 0)
quantum_sync_indices = defaultdict(lambda: 0)
entropic_amplifiers = defaultdict(lambda: ENTROPIC_BASELINE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest Cognitive Resonance Score, adjusted by the Entropic Amplifier to prioritize entries with more predictable access patterns. This ensures that entries with sporadic but synchronized access patterns are retained longer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = cognitive_resonance_scores[key] - entropic_amplifiers[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Cognitive Resonance Score is increased based on the recency and frequency of access, while the Quantum Synchronization Index is recalibrated to reflect the current temporal dynamics. The Entropic Amplifier is adjusted to account for the change in access predictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequencies[obj.key] += 1
    last_access_times[obj.key] = cache_snapshot.access_count
    
    frequency_component = FREQUENCY_WEIGHT * access_frequencies[obj.key]
    recency_component = RECENCY_WEIGHT * (cache_snapshot.access_count - last_access_times[obj.key])
    quantum_component = QUANTUM_WEIGHT * quantum_sync_indices[obj.key]
    
    cognitive_resonance_scores[obj.key] = frequency_component + recency_component + quantum_component
    
    # Recalibrate Quantum Synchronization Index
    quantum_sync_indices[obj.key] = (quantum_sync_indices[obj.key] + 1) % 10
    
    # Adjust Entropic Amplifier
    entropic_amplifiers[obj.key] = ENTROPIC_BASELINE / (1 + access_frequencies[obj.key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Cognitive Resonance Score is initialized based on initial access patterns, and the Quantum Synchronization Index is set to a neutral state. The Entropic Amplifier is calculated to establish a baseline for future unpredictability assessments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequencies[obj.key] = 1
    last_access_times[obj.key] = cache_snapshot.access_count
    quantum_sync_indices[obj.key] = 0
    
    cognitive_resonance_scores[obj.key] = FREQUENCY_WEIGHT + RECENCY_WEIGHT + QUANTUM_WEIGHT * quantum_sync_indices[obj.key]
    entropic_amplifiers[obj.key] = ENTROPIC_BASELINE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Quantum Synchronization Index for remaining entries to reflect the altered temporal dynamics. The Entropic Amplifier is adjusted to account for the reduced cache diversity, ensuring future evictions consider the new access pattern landscape.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        quantum_sync_indices[key] = (quantum_sync_indices[key] + 1) % 10
        entropic_amplifiers[key] = ENTROPIC_BASELINE / (1 + access_frequencies[key])