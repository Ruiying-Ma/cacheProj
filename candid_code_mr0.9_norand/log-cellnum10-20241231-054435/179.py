# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QSS = 1
INITIAL_FCI = 1
INITIAL_DPI = 1
INITIAL_TES = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Signal Strength (QSS) for each cache entry, a Frequency Coupling Index (FCI) that tracks access patterns, a Dynamic Phase Indicator (DPI) that adjusts based on recent access phases, and a Temporal Equilibrium Score (TES) that balances historical and recent access frequencies.
metadata = {
    'QSS': defaultdict(lambda: BASELINE_QSS),
    'FCI': defaultdict(lambda: INITIAL_FCI),
    'DPI': defaultdict(lambda: INITIAL_DPI),
    'TES': defaultdict(lambda: INITIAL_TES)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of QSS and TES, adjusted by the FCI to account for recent access patterns. This ensures that entries with low historical and recent importance are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata['QSS'][key] + metadata['TES'][key]) / metadata['FCI'][key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QSS of the accessed entry is incremented to reflect its increased importance, the FCI is adjusted to strengthen the coupling with other frequently accessed entries, and the DPI is updated to reflect the current access phase, while the TES is recalibrated to balance the new access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['QSS'][key] += 1
    metadata['FCI'][key] += 1
    metadata['DPI'][key] = cache_snapshot.access_count
    metadata['TES'][key] = (metadata['TES'][key] + 1) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QSS is initialized to a baseline value, the FCI is set to reflect initial coupling with similar entries, the DPI is adjusted to integrate the new entry into the current phase, and the TES is initialized to reflect its potential equilibrium state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['QSS'][key] = BASELINE_QSS
    metadata['FCI'][key] = INITIAL_FCI
    metadata['DPI'][key] = cache_snapshot.access_count
    metadata['TES'][key] = INITIAL_TES

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the FCI of remaining entries to reduce coupling with the evicted entry, adjusts the DPI to reflect the phase shift caused by the eviction, and recalculates the TES to maintain temporal balance across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    for key in cache_snapshot.cache:
        if key != evicted_key:
            metadata['FCI'][key] = max(1, metadata['FCI'][key] - 1)
            metadata['DPI'][key] = cache_snapshot.access_count
            metadata['TES'][key] = (metadata['TES'][key] + 1) / 2