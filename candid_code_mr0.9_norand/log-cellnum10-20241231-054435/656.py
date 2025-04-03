# Import anything you need below
import math

# Put tunable constant parameters below
DEFAULT_TV = 1.0
INITIAL_QR = 1.0
INITIAL_EB = 0.0
DPA_SENSITIVITY = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including Temporal Variability (TV), Quantum Rhythm (QR), and Entropic Balance (EB). TV tracks the time intervals between accesses, QR represents a cyclic pattern of access frequencies, and EB measures the randomness of access patterns. Additionally, a Dynamic Phase Adaptation (DPA) state is maintained globally to adjust the policy's sensitivity to these factors.
cache_metadata = {}
DPA_state = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry based on its TV, QR, and EB values. Entries with high TV (indicating infrequent access), low QR (indicating non-cyclic access), and high EB (indicating random access) are prioritized for eviction. The DPA state influences the weight of each factor in the composite score.
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
        TV = metadata['TV']
        QR = metadata['QR']
        EB = metadata['EB']
        
        # Calculate composite score
        score = (DPA_state * TV) - (DPA_state * QR) + (DPA_state * EB)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the TV is updated by recalculating the time interval since the last access, QR is adjusted to reflect the current phase of access frequency, and EB is recalculated to account for the new access pattern. The DPA state is checked and adjusted if necessary to ensure optimal sensitivity to access pattern changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    if key in cache_metadata:
        metadata = cache_metadata[key]
        last_access_time = metadata['last_access_time']
        
        # Update TV
        metadata['TV'] = current_time - last_access_time
        
        # Update QR
        metadata['QR'] = (metadata['QR'] + 1) % 10  # Example cyclic pattern
        
        # Update EB
        metadata['EB'] = -math.log(1.0 / (metadata['QR'] + 1))
        
        # Update last access time
        metadata['last_access_time'] = current_time
        
        # Adjust DPA state
        global DPA_state
        DPA_state = max(0.1, DPA_state * (1 + DPA_SENSITIVITY * (metadata['EB'] - 0.5)))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the TV is initialized to a default value, QR is set to the initial phase of the access cycle, and EB is initialized to reflect minimal randomness. The DPA state is evaluated to determine if the insertion alters the overall cache dynamics, potentially triggering an adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata
    cache_metadata[key] = {
        'TV': DEFAULT_TV,
        'QR': INITIAL_QR,
        'EB': INITIAL_EB,
        'last_access_time': current_time
    }
    
    # Evaluate DPA state
    global DPA_state
    DPA_state = max(0.1, DPA_state * (1 - DPA_SENSITIVITY * 0.1))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the DPA state to account for the removal of the evicted entry's influence on the cache's overall access pattern. This may involve adjusting the sensitivity to TV, QR, and EB to maintain balance and efficiency in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    if evicted_key in cache_metadata:
        del cache_metadata[evicted_key]
    
    # Recalibrate DPA state
    global DPA_state
    DPA_state = max(0.1, DPA_state * (1 + DPA_SENSITIVITY * 0.1))