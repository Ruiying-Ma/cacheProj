# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_ENTROPY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a vector for each cache entry, representing its access frequency, recency, and a temporal shift factor. Additionally, an entropy score is calculated for each entry to measure its access pattern stability.
cache_metadata = {}

def calculate_entropy(access_frequency, recency):
    # A simple entropy calculation based on access frequency and recency
    if access_frequency == 0 or recency == 0:
        return float('inf')  # High entropy for unused or very old items
    return - (access_frequency * math.log(access_frequency) + recency * math.log(recency))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the highest entropy score, indicating the most unstable access pattern, and the lowest temporal shift factor, suggesting it is least likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_temporal_shift = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        metadata = cache_metadata[key]
        entropy = metadata['entropy']
        temporal_shift = metadata['temporal_shift']

        if entropy > max_entropy or (entropy == max_entropy and temporal_shift < min_temporal_shift):
            max_entropy = entropy
            min_temporal_shift = temporal_shift
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency components of the vector are incremented, and the temporal shift factor is adjusted to reflect the time since the last access. The entropy score is recalculated to account for the updated access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata = cache_metadata[obj.key]
    metadata['access_frequency'] += 1
    metadata['recency'] = cache_snapshot.access_count
    metadata['temporal_shift'] = cache_snapshot.access_count - metadata['last_access_time']
    metadata['entropy'] = calculate_entropy(metadata['access_frequency'], metadata['recency'])
    metadata['last_access_time'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its vector is initialized with default values, and its entropy score is set to a baseline level. The temporal shift factor is initialized to reflect the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'access_frequency': 1,
        'recency': cache_snapshot.access_count,
        'temporal_shift': 0,
        'entropy': BASELINE_ENTROPY,
        'last_access_time': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the vectors of remaining entries by normalizing their access frequency and recency components, and recalculates their entropy scores to ensure stability in the cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del cache_metadata[evicted_obj.key]
    
    for key, metadata in cache_metadata.items():
        # Normalize access frequency and recency
        metadata['access_frequency'] = max(1, metadata['access_frequency'] // 2)
        metadata['recency'] = max(1, metadata['recency'] // 2)
        # Recalculate entropy
        metadata['entropy'] = calculate_entropy(metadata['access_frequency'], metadata['recency'])