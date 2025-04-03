# Import anything you need below
import math

# Put tunable constant parameters below
BASE_FREQUENCY = 1
NEUTRAL_PHASE = 0
MAX_ENTROPY = 1.0
FREQUENCY_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access time, a phase synchronization value, and an entropy score. Frequency modulation tracks how often an item is accessed, time-step alignment records the last access time, phase synchronization aligns access patterns, and entropic balancing measures the randomness of access patterns.
cache_metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined score of frequency modulation and phase synchronization, adjusted by the entropy score. This ensures that items with irregular access patterns and low frequency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        score = (metadata['frequency'] + metadata['phase_sync']) * metadata['entropy']
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency modulation is incremented, the time-step alignment is updated to the current time, the phase synchronization is adjusted to reflect the new access pattern, and the entropy score is recalculated to account for the change in access predictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = cache_metadata[obj.key]
    metadata['frequency'] += 1
    metadata['last_access'] = cache_snapshot.access_count
    metadata['phase_sync'] = (metadata['phase_sync'] + 1) % 10  # Example phase adjustment
    metadata['entropy'] = 1 / (1 + math.log(metadata['frequency']))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the frequency modulation is initialized to a base value, the time-step alignment is set to the current time, the phase synchronization is set to a neutral state, and the entropy score is initialized to reflect maximum uncertainty.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'frequency': BASE_FREQUENCY,
        'last_access': cache_snapshot.access_count,
        'phase_sync': NEUTRAL_PHASE,
        'entropy': MAX_ENTROPY
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the phase synchronization values of remaining entries to ensure alignment, adjusts the entropy scores to reflect the new cache state, and may slightly decrease the frequency modulation of all entries to prevent stale data from persisting.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del cache_metadata[evicted_obj.key]
    
    for key, metadata in cache_metadata.items():
        metadata['phase_sync'] = (metadata['phase_sync'] + 1) % 10  # Example recalibration
        metadata['entropy'] = 1 / (1 + math.log(metadata['frequency']))
        metadata['frequency'] *= FREQUENCY_DECAY