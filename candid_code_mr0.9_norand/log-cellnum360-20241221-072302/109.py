# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
REPLICATION_THRESHOLD = 2
LATENCY_WEIGHT = 1.0
FREQUENCY_WEIGHT = 1.0
REPLICATION_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, replication factor, and network latency to the data source. It also tracks fault tolerance levels by monitoring the number of replicas available across the network.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'replication_factor': defaultdict(lambda: 1),
    'network_latency': defaultdict(lambda: 1.0),
    'fault_tolerance': defaultdict(lambda: 1)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that considers low access frequency, high network latency, and low replication factor. Items with the lowest fault tolerance level are prioritized for eviction to ensure redundancy is maintained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        latency = metadata['network_latency'][key]
        replication = metadata['replication_factor'][key]
        fault_tolerance = metadata['fault_tolerance'][key]
        
        score = (LATENCY_WEIGHT * latency) - (FREQUENCY_WEIGHT * frequency) - (REPLICATION_WEIGHT * replication)
        
        if fault_tolerance < REPLICATION_THRESHOLD:
            score += 10  # Prioritize eviction if fault tolerance is low
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, and the last access timestamp is updated. The replication factor is checked, and if it falls below a threshold, a replication request is triggered to maintain fault tolerance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    
    if metadata['replication_factor'][key] < REPLICATION_THRESHOLD:
        metadata['replication_factor'][key] += 1  # Simulate a replication request

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized, and the last access timestamp is set to the current time. The replication factor is assessed, and if necessary, additional replicas are created to meet fault tolerance requirements.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['replication_factor'][key] = 1  # Initial replication factor
    
    if metadata['replication_factor'][key] < REPLICATION_THRESHOLD:
        metadata['replication_factor'][key] += 1  # Simulate creating additional replicas

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the overall cache fault tolerance level and adjusts the replication strategy if needed. It also updates the network latency metrics to optimize future data retrieval paths.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalculate fault tolerance level
    metadata['fault_tolerance'][evicted_key] = max(1, metadata['fault_tolerance'][evicted_key] - 1)
    
    # Adjust replication strategy
    if metadata['replication_factor'][evicted_key] > 1:
        metadata['replication_factor'][evicted_key] -= 1
    
    # Update network latency metrics
    metadata['network_latency'][evicted_key] *= 0.9  # Simulate optimization