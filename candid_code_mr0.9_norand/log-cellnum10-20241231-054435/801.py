# Import anything you need below
import math

# Put tunable constant parameters below
ACCESS_FREQ_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
ENTROPY_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a sparse matrix where each row represents a cache line and each column represents a feature of the data, such as access frequency, recency, and entropy. Additionally, an entropic layer is calculated for each cache line to measure the uncertainty or randomness of access patterns.
cache_metadata = {}

def calculate_entropy(access_frequency):
    # Simple entropy calculation based on access frequency
    if access_frequency == 0:
        return 1.0  # High entropy for never accessed
    return -math.log(access_frequency)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a heuristic score for each cache line, which is a weighted sum of the sparse matrix features and the entropic layer. The line with the lowest heuristic score is selected for eviction, prioritizing lines with low access frequency, low recency, and high entropy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, metadata in cache_metadata.items():
        access_freq = metadata['access_frequency']
        recency = metadata['recency']
        entropy = metadata['entropy']
        
        score = (ACCESS_FREQ_WEIGHT * access_freq +
                 RECENCY_WEIGHT * recency +
                 ENTROPY_WEIGHT * entropy)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the sparse matrix by incrementing the access frequency and adjusting the recency for the accessed line. The entropic layer is recalculated to reflect the reduced uncertainty due to the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    if obj.key in cache_metadata:
        metadata = cache_metadata[obj.key]
        metadata['access_frequency'] += 1
        metadata['recency'] = cache_snapshot.access_count
        metadata['entropy'] = calculate_entropy(metadata['access_frequency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the sparse matrix row for the new cache line with default values, setting low access frequency and high entropy. The entropic layer is calculated based on initial assumptions about access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    cache_metadata[obj.key] = {
        'access_frequency': 0,
        'recency': cache_snapshot.access_count,
        'entropy': calculate_entropy(0)
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted line from the sparse matrix and recalibrates the entropic layers of remaining lines to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in cache_metadata:
        del cache_metadata[evicted_obj.key]
    
    # Recalibrate entropy for remaining lines
    for key, metadata in cache_metadata.items():
        metadata['entropy'] = calculate_entropy(metadata['access_frequency'])