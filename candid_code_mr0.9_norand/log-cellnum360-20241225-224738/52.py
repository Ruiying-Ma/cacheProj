# Import anything you need below
import time

# Put tunable constant parameters below
DEFAULT_PRIORITY_SCORE = 1.0
TEMPORAL_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
STRATIFICATION_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including priority score, last access timestamp, access frequency, and stratification level. Priority score is calculated based on a combination of temporal consistency and differential weighting of access patterns.
cache_metadata = {}

def calculate_priority_score(last_access, frequency, stratification, current_time):
    temporal_consistency = current_time - last_access
    return (TEMPORAL_WEIGHT * temporal_consistency +
            FREQUENCY_WEIGHT * frequency +
            STRATIFICATION_WEIGHT * stratification)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score, which is determined by a weighted combination of infrequent access, outdated temporal consistency, and low stratification level.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        priority_score = calculate_priority_score(
            metadata['last_access'],
            metadata['frequency'],
            metadata['stratification'],
            cache_snapshot.access_count
        )
        if priority_score < lowest_priority_score:
            lowest_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the last access timestamp to the current time, increases the access frequency, and recalculates the priority score by adjusting the weights based on the updated temporal consistency and stratification level.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = cache_metadata[obj.key]
    metadata['last_access'] = cache_snapshot.access_count
    metadata['frequency'] += 1
    metadata['priority_score'] = calculate_priority_score(
        metadata['last_access'],
        metadata['frequency'],
        metadata['stratification'],
        cache_snapshot.access_count
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the metadata with a default priority score, sets the last access timestamp to the current time, initializes access frequency to one, and assigns a stratification level based on the initial access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'priority_score': DEFAULT_PRIORITY_SCORE,
        'last_access': cache_snapshot.access_count,
        'frequency': 1,
        'stratification': 1  # Initial stratification level
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the differential weighting factors for the remaining entries to ensure balanced priority alignment and adjusts stratification levels to reflect the current cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del cache_metadata[evicted_obj.key]
    
    # Recalibrate weights and adjust stratification levels
    for key, metadata in cache_metadata.items():
        metadata['priority_score'] = calculate_priority_score(
            metadata['last_access'],
            metadata['frequency'],
            metadata['stratification'],
            cache_snapshot.access_count
        )
        # Adjust stratification level based on current cache dynamics
        metadata['stratification'] = max(1, metadata['stratification'] - 1)