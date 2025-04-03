# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LRU_WEIGHT = 0.5
LFU_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a redundancy score for each cache entry, a hybrid score combining LRU and LFU metrics, a prediction accuracy score for access patterns, and a transaction verification status to ensure consistency during concurrent accesses.
metadata = {
    'hybrid_score': defaultdict(lambda: {'lru': 0, 'lfu': 0}),
    'redundancy_score': defaultdict(int),
    'prediction_accuracy': defaultdict(float),
    'transaction_verified': defaultdict(bool)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest hybrid score, adjusted by the redundancy score to prioritize evicting redundant data, and further refined by the prediction accuracy score to avoid evicting entries likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        hybrid_score = (LRU_WEIGHT * metadata['hybrid_score'][key]['lru'] +
                        LFU_WEIGHT * metadata['hybrid_score'][key]['lfu'])
        adjusted_score = hybrid_score - metadata['redundancy_score'][key] + metadata['prediction_accuracy'][key]
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the hybrid score by increasing the LFU component and adjusting the LRU component to reflect recent access, recalculates the prediction accuracy score based on the hit, and verifies the transaction status to ensure consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['hybrid_score'][key]['lfu'] += 1
    metadata['hybrid_score'][key]['lru'] = cache_snapshot.access_count
    metadata['prediction_accuracy'][key] = 1.0  # Simplified prediction accuracy update
    metadata['transaction_verified'][key] = True

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the hybrid score with a balanced LRU and LFU value, sets the redundancy score based on data characteristics, initializes the prediction accuracy score, and marks the transaction as verified.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['hybrid_score'][key] = {'lru': cache_snapshot.access_count, 'lfu': 1}
    metadata['redundancy_score'][key] = 0  # Simplified redundancy score
    metadata['prediction_accuracy'][key] = 0.5  # Initial prediction accuracy
    metadata['transaction_verified'][key] = True

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the prediction accuracy metric for remaining entries, updates the redundancy scores to reflect the new cache state, and verifies the transaction status to ensure no inconsistencies arose during the eviction process.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata['prediction_accuracy'][key] *= 0.9  # Decay prediction accuracy
        metadata['redundancy_score'][key] = max(0, metadata['redundancy_score'][key] - 1)  # Simplified update
        metadata['transaction_verified'][key] = True