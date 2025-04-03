# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
MISPHRASE_DEFAULT = 1.0
PANGLOSSIC_DEFAULT = 1.0
NUDELY_DEFAULT = 1
STRAWEN_DEFAULT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a 'misphrase' score that measures the likelihood of an object being accessed based on historical patterns. It also tracks a 'panglossic' score representing the overall optimism of future accesses, a 'nudely' score indicating the raw access count, and a 'strawen' score reflecting the object's importance in the cache.
metadata = collections.defaultdict(lambda: {
    'misphrase': MISPHRASE_DEFAULT,
    'panglossic': PANGLOSSIC_DEFAULT,
    'nudely': NUDELY_DEFAULT,
    'strawen': STRAWEN_DEFAULT,
    'last_access': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score from the misphrase, panglossic, nudely, and strawen scores. The object with the lowest composite score is selected for eviction, ensuring a balance between access patterns and importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        scores = metadata[key]
        composite_score = (scores['misphrase'] + scores['panglossic'] + scores['nudely'] + scores['strawen']) / 4
        if composite_score < lowest_score:
            lowest_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the nudely score and updates the misphrase score based on the access pattern. The panglossic score is adjusted to reflect increased optimism for future accesses, and the strawen score is recalculated to maintain the object's importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['nudely'] += 1
    metadata[key]['misphrase'] = metadata[key]['nudely'] / (cache_snapshot.access_count + 1)
    metadata[key]['panglossic'] += 0.1
    metadata[key]['strawen'] = metadata[key]['nudely'] * metadata[key]['panglossic']
    metadata[key]['last_access'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the misphrase, panglossic, nudely, and strawen scores based on initial access patterns and predicted importance. The scores are set to default values that will be adjusted as more data is gathered.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'misphrase': MISPHRASE_DEFAULT,
        'panglossic': PANGLOSSIC_DEFAULT,
        'nudely': NUDELY_DEFAULT,
        'strawen': STRAWEN_DEFAULT,
        'last_access': cache_snapshot.access_count
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy recalibrates the misphrase, panglossic, nudely, and strawen scores of remaining objects to ensure balanced cache performance. The scores are adjusted to reflect the removal and to optimize future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata[key]['misphrase'] = metadata[key]['nudely'] / (cache_snapshot.access_count + 1)
        metadata[key]['panglossic'] = max(metadata[key]['panglossic'] - 0.1, PANGLOSSIC_DEFAULT)
        metadata[key]['strawen'] = metadata[key]['nudely'] * metadata[key]['panglossic']