# Import anything you need below
import collections
import math

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1.0
INITIAL_PRIORITY = 1.0
INITIAL_COHERENCE = 0.5
INITIAL_TEMPORAL_HARMONIC = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a priority score, a forecasted access pattern, a coherence factor, and a temporal harmonic signature. The priority score is adjusted based on recent access frequency and recency. The forecasted access pattern predicts future accesses using historical data. The coherence factor measures the consistency of access patterns. The temporal harmonic signature captures periodic access trends.
metadata = collections.defaultdict(lambda: {
    'priority_score': INITIAL_PRIORITY,
    'forecasted_access_pattern': collections.deque(maxlen=10),
    'coherence_factor': INITIAL_COHERENCE,
    'temporal_harmonic_signature': INITIAL_TEMPORAL_HARMONIC
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score derived from the priority score, forecasted access pattern, coherence factor, and temporal harmonic signature. Entries with low priority, poor forecasted access, low coherence, and weak temporal harmonics are more likely to be evicted.
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
        combined_score = (
            meta['priority_score'] +
            sum(meta['forecasted_access_pattern']) +
            meta['coherence_factor'] +
            meta['temporal_harmonic_signature']
        )
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score is increased to reflect the recent access. The forecasted access pattern is updated using the latest access data to refine future predictions. The coherence factor is adjusted to reflect the consistency of the access pattern. The temporal harmonic signature is recalibrated to account for the new access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['priority_score'] += PRIORITY_INCREMENT
    meta['forecasted_access_pattern'].append(cache_snapshot.access_count)
    meta['coherence_factor'] = len(set(meta['forecasted_access_pattern'])) / len(meta['forecasted_access_pattern'])
    meta['temporal_harmonic_signature'] = math.sin(cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the priority score is initialized based on initial access frequency. The forecasted access pattern is set using initial access data. The coherence factor starts at a neutral value, indicating no established pattern. The temporal harmonic signature is initialized to capture any immediate periodic trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['priority_score'] = INITIAL_PRIORITY
    meta['forecasted_access_pattern'].append(cache_snapshot.access_count)
    meta['coherence_factor'] = INITIAL_COHERENCE
    meta['temporal_harmonic_signature'] = math.sin(cache_snapshot.access_count)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the coherence factor and temporal harmonic signature of remaining entries to ensure they reflect the current cache state. The forecasted access patterns are adjusted to account for the removal of the evicted entry, ensuring predictions remain accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        meta['coherence_factor'] = len(set(meta['forecasted_access_pattern'])) / len(meta['forecasted_access_pattern'])
        meta['temporal_harmonic_signature'] = math.sin(cache_snapshot.access_count)