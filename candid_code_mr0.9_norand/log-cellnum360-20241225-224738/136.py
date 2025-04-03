# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_INVERSE_ACCESS_FREQUENCY = 1.0
WEIGHT_RECENCY_OF_ACCESS = 1.0
WEIGHT_PRIORITY_LEVEL = 1.0
WEIGHT_NETWORK_LATENCY_IMPACT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, priority level based on resource allocation, and network latency impact score.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'priority_level': 0,
    'network_latency_impact': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of inverse access frequency, recency of access, priority level, and network latency impact. The entry with the highest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = float('-inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        inverse_access_frequency = 1 / (meta['access_frequency'] + 1)
        recency_of_access = cache_snapshot.access_count - meta['last_access_timestamp']
        priority_level = meta['priority_level']
        network_latency_impact = meta['network_latency_impact']
        
        composite_score = (
            WEIGHT_INVERSE_ACCESS_FREQUENCY * inverse_access_frequency +
            WEIGHT_RECENCY_OF_ACCESS * recency_of_access +
            WEIGHT_PRIORITY_LEVEL * priority_level +
            WEIGHT_NETWORK_LATENCY_IMPACT * network_latency_impact
        )
        
        if composite_score > max_score:
            max_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access timestamp is updated to the current time, and the priority level is adjusted based on the current resource allocation and network conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    # Adjust priority level based on current resource allocation and network conditions
    meta['priority_level'] = calculate_priority_level()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, assigns a priority level based on initial resource allocation, and calculates the network latency impact score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'priority_level': calculate_initial_priority_level(),
        'network_latency_impact': calculate_network_latency_impact()
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the priority levels of remaining entries based on the freed resources and updates the network latency impact scores to reflect the current network efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        meta = metadata[key]
        # Recalibrate priority levels based on freed resources
        meta['priority_level'] = recalculate_priority_level()
        # Update network latency impact scores
        meta['network_latency_impact'] = recalculate_network_latency_impact()

def calculate_priority_level():
    # Placeholder function to calculate priority level
    return 1

def calculate_initial_priority_level():
    # Placeholder function to calculate initial priority level
    return 1

def calculate_network_latency_impact():
    # Placeholder function to calculate network latency impact
    return 1

def recalculate_priority_level():
    # Placeholder function to recalculate priority level
    return 1

def recalculate_network_latency_impact():
    # Placeholder function to recalculate network latency impact
    return 1