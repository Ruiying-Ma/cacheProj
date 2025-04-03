# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
SCHEMA_VERSION = 1
DEFAULT_PRIORITY = 1
TRANSACTIONAL_MEMORY_DEFAULT = False
COHERENCE_STATE_DEFAULT = False

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, transactional memory state, and schema version for each cache entry. It also tracks cache coherence state and parallel processing priority levels.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_timestamp': 0,
    'transactional_memory_state': TRANSACTIONAL_MEMORY_DEFAULT,
    'schema_version': SCHEMA_VERSION,
    'coherence_state': COHERENCE_STATE_DEFAULT,
    'parallel_processing_priority': DEFAULT_PRIORITY
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, older schema versions, and lower parallel processing priority. Entries involved in active transactions or with pending coherence updates are less likely to be evicted.
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
        if meta['transactional_memory_state'] or meta['coherence_state']:
            continue
        
        score = (meta['access_frequency'] * 0.5) + \
                (meta['schema_version'] * 0.3) + \
                (meta['parallel_processing_priority'] * 0.2)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the last access timestamp, and checks for any schema evolution updates. It also adjusts the parallel processing priority based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    # Assume schema evolution check is a placeholder for actual logic
    meta['schema_version'] = SCHEMA_VERSION
    # Adjust priority based on access patterns
    meta['parallel_processing_priority'] = min(meta['parallel_processing_priority'] + 1, 10)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to one, sets the current timestamp, assigns the latest schema version, and sets the transactional memory and coherence states to default. It also assigns a default parallel processing priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'transactional_memory_state': TRANSACTIONAL_MEMORY_DEFAULT,
        'schema_version': SCHEMA_VERSION,
        'coherence_state': COHERENCE_STATE_DEFAULT,
        'parallel_processing_priority': DEFAULT_PRIORITY
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy logs the schema version and coherence state of the evicted entry for future analysis. It also adjusts the parallel processing priorities of remaining entries to optimize for current workload demands.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_meta = metadata.pop(evicted_obj.key, None)
    if evicted_meta:
        # Log schema version and coherence state
        print(f"Evicted {evicted_obj.key}: Schema Version {evicted_meta['schema_version']}, Coherence State {evicted_meta['coherence_state']}")
    
    # Adjust priorities of remaining entries
    for key in cache_snapshot.cache:
        metadata[key]['parallel_processing_priority'] = max(metadata[key]['parallel_processing_priority'] - 1, 1)