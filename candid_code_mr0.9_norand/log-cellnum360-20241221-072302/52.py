# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BURST_DECAY_FACTOR = 0.9  # Decay factor for burst score recalibration

# Put the metadata specifically maintained by the policy below. The policy maintains a metadata index that includes access frequency, recency, and a burst score for each cache entry. The burst score is a quantitative measure of sudden access spikes, scaled to prioritize entries with recent high access bursts.
metadata = defaultdict(lambda: {'frequency': 0, 'recency': 0, 'burst_score': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of frequency, recency, and burst score. This ensures that entries with consistent access patterns and recent bursts are retained longer.
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
        combined_score = meta['frequency'] + meta['recency'] + meta['burst_score']
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the recency is updated to the current time, and the burst score is recalculated based on the recent access pattern, giving more weight to recent accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['frequency'] += 1
    meta['recency'] = cache_snapshot.access_count
    # Recalculate burst score with more weight to recent accesses
    meta['burst_score'] = (meta['burst_score'] * BURST_DECAY_FACTOR) + (1 - BURST_DECAY_FACTOR) * meta['frequency']

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency to 1, sets its recency to the current time, and calculates an initial burst score based on the current access context, allowing for quick adaptation to access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'frequency': 1,
        'recency': cache_snapshot.access_count,
        'burst_score': 1  # Initial burst score
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the burst scores of remaining entries to ensure that the burst handling mechanism remains sensitive to ongoing access patterns, potentially adjusting the scaling factor for burst score calculation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata of evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    # Recalibrate burst scores for remaining entries
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['burst_score'] *= BURST_DECAY_FACTOR