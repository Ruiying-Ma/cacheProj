# Import anything you need below
import time

# Put tunable constant parameters below
BASELINE_REF_COUNT = 1
PREDICTIVE_SCORE_INCREMENT = 10
TIME_DECAY_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a predictive score for each cache entry, a timestamp of the last access, and a dynamic reference count that adjusts based on access patterns and predicted future accesses.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, factoring in both the time since last access and the dynamic reference count, ensuring that entries with low future access probability are prioritized for eviction.
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
        time_since_last_access = cache_snapshot.access_count - meta['last_access']
        predictive_score = meta['predictive_score'] - (time_since_last_access * TIME_DECAY_FACTOR) + meta['ref_count']
        
        if predictive_score < min_score:
            min_score = predictive_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased based on a synthesis of recent access patterns, the timestamp is updated to the current time, and the dynamic reference count is incremented to reflect increased likelihood of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if key in metadata:
        metadata[key]['predictive_score'] += PREDICTIVE_SCORE_INCREMENT
        metadata[key]['last_access'] = cache_snapshot.access_count
        metadata[key]['ref_count'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns, sets the timestamp to the current time, and starts the dynamic reference count at a baseline level to allow for rapid adjustment based on early access behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'predictive_score': PREDICTIVE_SCORE_INCREMENT,
        'last_access': cache_snapshot.access_count,
        'ref_count': BASELINE_REF_COUNT
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries to account for the changed cache state, adjusts timestamps to reflect the new cache dynamics, and modifies dynamic reference counts to ensure they remain relevant to current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key, meta in metadata.items():
        time_since_last_access = cache_snapshot.access_count - meta['last_access']
        meta['predictive_score'] -= (time_since_last_access * TIME_DECAY_FACTOR)
        meta['last_access'] = cache_snapshot.access_count
        meta['ref_count'] = max(BASELINE_REF_COUNT, meta['ref_count'] - 1)