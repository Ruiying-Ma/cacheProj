# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_SIGNAL_STRENGTH = 1.0
BASE_ENTROPY_SCORE = 1.0
INITIAL_VIRTUAL_STATE = 0
FREQUENCY_INCREMENT = 1
SIGNAL_AMPLIFICATION_FACTOR = 1.5
ENTROPY_RECALIBRATION_FACTOR = 0.9
VIRTUAL_STATE_STABILITY_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, entropy score, virtual state, and signal strength for each cache entry. Access frequency is dynamically modulated, entropy coherence measures randomness in access patterns, virtual state represents the transition state of an entry, and signal strength indicates the importance of an entry.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'entropy_score': BASE_ENTROPY_SCORE,
    'virtual_state': INITIAL_VIRTUAL_STATE,
    'signal_strength': BASE_SIGNAL_STRENGTH
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of signal strength and entropy coherence, while considering virtual state transitions to avoid evicting entries that are likely to become more important soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entry_metadata = metadata[key]
        combined_score = (entry_metadata['signal_strength'] + entry_metadata['entropy_score']) / (entry_metadata['virtual_state'] + 1)
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is dynamically increased, the entropy score is recalculated to reflect the new access pattern, the virtual state is transitioned to a more stable state, and the signal strength is amplified to prioritize the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    entry_metadata = metadata[obj.key]
    entry_metadata['access_frequency'] += FREQUENCY_INCREMENT
    entry_metadata['entropy_score'] = BASE_ENTROPY_SCORE / (entry_metadata['access_frequency'] + 1)
    entry_metadata['virtual_state'] += VIRTUAL_STATE_STABILITY_INCREMENT
    entry_metadata['signal_strength'] *= SIGNAL_AMPLIFICATION_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized, the entropy score is set based on initial access patterns, the virtual state is set to an initial state, and the signal strength is set to a baseline level to allow for future amplification.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 0,
        'entropy_score': BASE_ENTROPY_SCORE,
        'virtual_state': INITIAL_VIRTUAL_STATE,
        'signal_strength': BASE_SIGNAL_STRENGTH
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the entropy coherence of remaining entries, adjusts virtual states to reflect the new cache composition, and redistributes signal strength to ensure balanced importance across entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        entry_metadata = metadata[key]
        entry_metadata['entropy_score'] *= ENTROPY_RECALIBRATION_FACTOR
        entry_metadata['virtual_state'] = max(0, entry_metadata['virtual_state'] - 1)
        entry_metadata['signal_strength'] = max(BASE_SIGNAL_STRENGTH, entry_metadata['signal_strength'] * ENTROPY_RECALIBRATION_FACTOR)