# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_WRITE_BACK_STATUS = 1.0
WEIGHT_BRANCH_PREDICTION_ACCURACY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, write-back status, and branch prediction accuracy for each cache line.
metadata = collections.defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_time': 0,
    'write_back_status': 'clean',  # 'clean' or 'dirty'
    'branch_prediction_accuracy': 1.0  # A value between 0 and 1
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access time, low write-back status, and poor branch prediction accuracy.
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
        score = (WEIGHT_ACCESS_FREQUENCY * meta['access_frequency'] +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - meta['last_access_time']) +
                 WEIGHT_WRITE_BACK_STATUS * (1 if meta['write_back_status'] == 'dirty' else 0) +
                 WEIGHT_BRANCH_PREDICTION_ACCURACY * (1 - meta['branch_prediction_accuracy']))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the last access time to the current time, and adjusts the branch prediction accuracy based on the outcome of the branch prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_time'] = cache_snapshot.access_count
    # Adjust branch prediction accuracy based on the outcome of the branch prediction
    # For simplicity, let's assume the branch prediction accuracy improves by a fixed amount on a hit
    meta['branch_prediction_accuracy'] = min(1.0, meta['branch_prediction_accuracy'] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, marks the write-back status as clean, and initializes branch prediction accuracy based on the initial prediction outcome.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'write_back_status': 'clean',
        'branch_prediction_accuracy': 0.5  # Initial prediction accuracy
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy resets the metadata for the evicted cache line and updates the write-back status if the line was dirty, ensuring cache coherence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if metadata[evicted_obj.key]['write_back_status'] == 'dirty':
        # Ensure cache coherence by writing back the dirty line
        pass  # Implement write-back logic if necessary
    
    # Reset metadata for the evicted object
    del metadata[evicted_obj.key]