# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_BANDWIDTH_WEIGHT = 0.25
TEMPORAL_COHERENCE_WEIGHT = 0.25
HEURISTIC_MODULATION_WEIGHT = 0.25
ADAPTIVE_FREQUENCY_WEIGHT = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including predictive bandwidth usage, temporal coherence score, heuristic modulation factor, and adaptive frequency counter. Predictive bandwidth estimates future data transfer needs, temporal coherence tracks the likelihood of repeated access, heuristic modulation adjusts based on access patterns, and adaptive frequency measures access frequency changes.
metadata = defaultdict(lambda: {
    'predictive_bandwidth': 1.0,
    'temporal_coherence': 1.0,
    'heuristic_modulation': 1.0,
    'adaptive_frequency': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry using a weighted sum of inverse predictive bandwidth, temporal coherence, heuristic modulation, and adaptive frequency. The entry with the lowest score is selected for eviction, prioritizing entries with low future bandwidth needs and low likelihood of repeated access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (
            PREDICTIVE_BANDWIDTH_WEIGHT * (1 / meta['predictive_bandwidth']) +
            TEMPORAL_COHERENCE_WEIGHT * meta['temporal_coherence'] +
            HEURISTIC_MODULATION_WEIGHT * meta['heuristic_modulation'] +
            ADAPTIVE_FREQUENCY_WEIGHT * meta['adaptive_frequency']
        )
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive bandwidth is adjusted based on recent access patterns, temporal coherence is increased to reflect repeated access, heuristic modulation is recalibrated to account for the hit, and the adaptive frequency counter is incremented to reflect increased access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['predictive_bandwidth'] *= 0.9  # Example adjustment
    meta['temporal_coherence'] += 1
    meta['heuristic_modulation'] *= 1.1  # Example recalibration
    meta['adaptive_frequency'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive bandwidth is initialized based on initial access patterns, temporal coherence is set to a baseline value, heuristic modulation is initialized to reflect initial access assumptions, and the adaptive frequency counter is set to zero to start tracking future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'predictive_bandwidth': 1.0,  # Initial value
        'temporal_coherence': 1.0,    # Baseline value
        'heuristic_modulation': 1.0,  # Initial assumption
        'adaptive_frequency': 0       # Start tracking
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the heuristic modulation factors of remaining entries to reflect the change in cache composition, adjusts predictive bandwidth estimates based on the freed resources, and resets the temporal coherence and adaptive frequency counters for the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata[key]['heuristic_modulation'] *= 0.95  # Example recalibration
        metadata[key]['predictive_bandwidth'] *= 1.05  # Example adjustment

    # Reset metadata for the evicted object
    metadata[evicted_obj.key] = {
        'predictive_bandwidth': 1.0,
        'temporal_coherence': 0,
        'heuristic_modulation': 1.0,
        'adaptive_frequency': 0
    }