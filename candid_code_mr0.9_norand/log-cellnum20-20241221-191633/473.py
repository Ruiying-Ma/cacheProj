# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.2  # Weight for temporal shift factor
DEFAULT_TEMPORAL_SHIFT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, load factor, and a temporal shift factor for each cache entry. It also tracks a global algorithmic equilibrium score to balance between recency and frequency.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'temporal_shift_factor': defaultdict(lambda: DEFAULT_TEMPORAL_SHIFT),
    'load_factor': 0.0,
    'algorithmic_equilibrium': 0.0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of its access frequency, recency (inverse of last access time), and temporal shift factor. The entry with the lowest score is evicted, with adjustments made based on the current load factor and algorithmic equilibrium.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata['access_frequency'][key]
        recency = 1 / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)
        temporal_shift = metadata['temporal_shift_factor'][key]
        
        score = (ALPHA * freq + BETA * recency + GAMMA * temporal_shift) * metadata['algorithmic_equilibrium']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the entry is incremented, the last access time is updated to the current time, and the temporal shift factor is adjusted based on the time elapsed since the last access. The algorithmic equilibrium score is recalibrated to reflect the updated state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    last_access = metadata['last_access_time'].get(key, cache_snapshot.access_count)
    metadata['temporal_shift_factor'][key] = cache_snapshot.access_count - last_access
    metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Recalibrate algorithmic equilibrium
    metadata['algorithmic_equilibrium'] = (metadata['algorithmic_equilibrium'] + 1) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its access frequency is initialized, the last access time is set to the current time, and the temporal shift factor is set to a default value. The load factor is recalculated, and the algorithmic equilibrium score is adjusted to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['temporal_shift_factor'][key] = DEFAULT_TEMPORAL_SHIFT
    
    # Recalculate load factor
    metadata['load_factor'] = cache_snapshot.size / cache_snapshot.capacity
    
    # Adjust algorithmic equilibrium
    metadata['algorithmic_equilibrium'] = (metadata['algorithmic_equilibrium'] + metadata['load_factor']) / 2

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the load factor is updated to reflect the reduced cache size, and the algorithmic equilibrium score is recalibrated to maintain balance between recency and frequency across the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['temporal_shift_factor'][evicted_key]
    
    # Update load factor
    metadata['load_factor'] = cache_snapshot.size / cache_snapshot.capacity
    
    # Recalibrate algorithmic equilibrium
    metadata['algorithmic_equilibrium'] = (metadata['algorithmic_equilibrium'] + metadata['load_factor']) / 2