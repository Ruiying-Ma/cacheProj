# Import anything you need below
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_DATA_PROPAGATION_STATUS = 1.0
WEIGHT_QUANTUM_MEMORY_SLOT_USAGE = 1.0
WEIGHT_COMPRESSION_RATIO = 1.0
WEIGHT_PREDICTED_LATENCY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data propagation status, quantum memory slot usage, compression ratio, and predicted latency for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'data_propagation_status': {},
    'quantum_memory_slot_usage': {},
    'compression_ratio': {},
    'predicted_latency': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score derived from access frequency, last access time, data propagation status, quantum memory slot usage, compression ratio, and predicted latency. Entries with lower scores are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (
            WEIGHT_ACCESS_FREQUENCY * metadata['access_frequency'].get(key, 0) +
            WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - metadata['last_access_time'].get(key, 0)) +
            WEIGHT_DATA_PROPAGATION_STATUS * metadata['data_propagation_status'].get(key, 0) +
            WEIGHT_QUANTUM_MEMORY_SLOT_USAGE * metadata['quantum_memory_slot_usage'].get(key, 0) +
            WEIGHT_COMPRESSION_RATIO * metadata['compression_ratio'].get(key, 0) +
            WEIGHT_PREDICTED_LATENCY * metadata['predicted_latency'].get(key, 0)
        )
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, checks and updates the data propagation status, adjusts the quantum memory slot usage if necessary, recalculates the compression ratio, and updates the predicted latency based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Update other metadata as needed
    # For simplicity, we assume these are updated in some manner
    metadata['data_propagation_status'][key] = 1  # Example update
    metadata['quantum_memory_slot_usage'][key] = 1  # Example update
    metadata['compression_ratio'][key] = 1  # Example update
    metadata['predicted_latency'][key] = 1  # Example update

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, marks the data propagation status as pending, assigns an available quantum memory slot, applies adaptive compression to determine the initial compression ratio, and predicts the initial latency based on the object's characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['data_propagation_status'][key] = 0  # Pending
    metadata['quantum_memory_slot_usage'][key] = 1  # Example assignment
    metadata['compression_ratio'][key] = 1  # Example initial compression ratio
    metadata['predicted_latency'][key] = 1  # Example initial latency prediction

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted entry, updates the data propagation status to reflect the removal, frees up the quantum memory slot used by the evicted entry, and recalibrates the overall cache compression ratio and latency predictions based on the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in metadata['access_frequency']:
        del metadata['access_frequency'][key]
    if key in metadata['last_access_time']:
        del metadata['last_access_time'][key]
    if key in metadata['data_propagation_status']:
        del metadata['data_propagation_status'][key]
    if key in metadata['quantum_memory_slot_usage']:
        del metadata['quantum_memory_slot_usage'][key]
    if key in metadata['compression_ratio']:
        del metadata['compression_ratio'][key]
    if key in metadata['predicted_latency']:
        del metadata['predicted_latency'][key]
    # Recalibrate overall cache compression ratio and latency predictions
    # For simplicity, we assume these are recalibrated in some manner