# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_ALIGNMENT_INCREMENT = 1
LATENCY_MAPPING_FACTOR = 1.0
DISTRIBUTION_INDEX_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including Priority Alignment (a score based on access frequency and recency), Latency Mapping (estimated time to retrieve from the main memory), Distribution Index (a measure of how evenly the cache is accessed), and Load Calibration (current load factor of the cache).
metadata = {
    'priority_alignment': defaultdict(int),
    'latency_mapping': defaultdict(lambda: LATENCY_MAPPING_FACTOR),
    'distribution_index': defaultdict(lambda: DISTRIBUTION_INDEX_FACTOR),
    'load_calibration': 0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Priority Alignment score, adjusted by a factor of Latency Mapping and Distribution Index to ensure balanced access and minimal latency impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata['priority_alignment'][key] /
                 (metadata['latency_mapping'][key] * metadata['distribution_index'][key]))
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Priority Alignment score is increased to reflect recent access, Latency Mapping is recalibrated based on current retrieval times, and the Distribution Index is updated to reflect the access pattern change.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority_alignment'][key] += PRIORITY_ALIGNMENT_INCREMENT
    metadata['latency_mapping'][key] = LATENCY_MAPPING_FACTOR  # Recalibrate as needed
    metadata['distribution_index'][key] = DISTRIBUTION_INDEX_FACTOR  # Update as needed

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Priority Alignment is initialized based on initial access frequency, Latency Mapping is set using the estimated retrieval time, and the Distribution Index is adjusted to account for the new entry's impact on access distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['priority_alignment'][key] = 1  # Initial access frequency
    metadata['latency_mapping'][key] = LATENCY_MAPPING_FACTOR  # Initial retrieval time
    metadata['distribution_index'][key] = DISTRIBUTION_INDEX_FACTOR  # Adjust for new entry

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Load Calibration is updated to reflect the reduced cache load, and the Distribution Index is recalibrated to ensure even access distribution across remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    metadata['load_calibration'] = cache_snapshot.size / cache_snapshot.capacity
    for key in cache_snapshot.cache:
        metadata['distribution_index'][key] = DISTRIBUTION_INDEX_FACTOR  # Recalibrate as needed