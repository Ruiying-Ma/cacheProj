# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COHERENCE_SCORE_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including an algorithmic coherence score, a spatial anomaly flag, a frequency interpolation counter, and a temporal bridge timestamp. The coherence score measures how well the data aligns with expected access patterns, the spatial anomaly flag indicates unusual access patterns, the frequency counter tracks access frequency, and the temporal bridge timestamp records the last access time.
metadata = defaultdict(lambda: {
    'coherence_score': 0.0,
    'spatial_anomaly': False,
    'frequency_counter': 0,
    'temporal_bridge': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest algorithmic coherence score. If there is a tie, it considers entries with a spatial anomaly flag set to true. Among these, it selects the entry with the lowest frequency interpolation counter. If still tied, it evicts the entry with the oldest temporal bridge timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_coherence_score = float('inf')
    candidates = []

    # Find the minimum coherence score
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata[key]['coherence_score']
        if score < min_coherence_score:
            min_coherence_score = score
            candidates = [key]
        elif score == min_coherence_score:
            candidates.append(key)

    # Filter by spatial anomaly flag
    candidates = [key for key in candidates if metadata[key]['spatial_anomaly']]

    if not candidates:
        candidates = [key for key in cache_snapshot.cache.keys() if metadata[key]['coherence_score'] == min_coherence_score]

    # Filter by frequency counter
    min_frequency = float('inf')
    frequency_candidates = []
    for key in candidates:
        frequency = metadata[key]['frequency_counter']
        if frequency < min_frequency:
            min_frequency = frequency
            frequency_candidates = [key]
        elif frequency == min_frequency:
            frequency_candidates.append(key)

    # Filter by temporal bridge timestamp
    oldest_time = float('inf')
    for key in frequency_candidates:
        time = metadata[key]['temporal_bridge']
        if time < oldest_time:
            oldest_time = time
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the algorithmic coherence score is increased slightly to reflect the alignment with expected patterns. The spatial anomaly flag is reset if the access pattern normalizes. The frequency interpolation counter is incremented to reflect increased access frequency, and the temporal bridge timestamp is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key]['coherence_score'] += COHERENCE_SCORE_INCREMENT
    metadata[key]['spatial_anomaly'] = False  # Assuming access pattern normalizes
    metadata[key]['frequency_counter'] += 1
    metadata[key]['temporal_bridge'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the algorithmic coherence score is initialized based on initial access patterns. The spatial anomaly flag is set to false, assuming normal access. The frequency interpolation counter starts at one, and the temporal bridge timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata[key]['coherence_score'] = 1.0  # Initial coherence score
    metadata[key]['spatial_anomaly'] = False
    metadata[key]['frequency_counter'] = 1
    metadata[key]['temporal_bridge'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the algorithmic coherence scores of remaining entries to ensure they reflect current access patterns. It checks and updates spatial anomaly flags for any entries showing unusual patterns. Frequency interpolation counters are adjusted to maintain relative frequency information, and temporal bridge timestamps are left unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for key in cache_snapshot.cache.keys():
        # Recalibrate coherence scores
        metadata[key]['coherence_score'] *= 0.9  # Example recalibration factor

        # Check and update spatial anomaly flags
        if metadata[key]['frequency_counter'] < 2:  # Example condition for anomaly
            metadata[key]['spatial_anomaly'] = True

        # Adjust frequency interpolation counters
        metadata[key]['frequency_counter'] = max(1, metadata[key]['frequency_counter'] - 1)