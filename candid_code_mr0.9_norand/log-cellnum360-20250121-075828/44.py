# Import anything you need below
import time
import math

# Put tunable constant parameters below
ENTROPY_DECAY = 0.9
ANOMALY_THRESHOLD = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and an entropy score for each cache entry. It also keeps a global anomaly score to detect unusual access patterns.
metadata = {}
global_anomaly_score = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the highest entropy score, indicating the least predictability in access patterns. If multiple entries have similar entropy, the one with the lowest predicted future access time is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_predicted_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entry = metadata[key]
        if entry['entropy'] > max_entropy or (entry['entropy'] == max_entropy and entry['predicted_future_access_time'] < min_predicted_time):
            max_entropy = entry['entropy']
            min_predicted_time = entry['predicted_future_access_time']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access timestamp of the entry are updated. The predicted future access time is recalculated using adaptive learning, and the entropy score is adjusted based on the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    entry = metadata[key]
    entry['access_frequency'] += 1
    entry['last_access_timestamp'] = current_time
    entry['predicted_future_access_time'] = current_time + (1 / entry['access_frequency'])
    entry['entropy'] = ENTROPY_DECAY * entry['entropy'] + (1 - ENTROPY_DECAY) * (1 / entry['access_frequency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, last access timestamp, predicted future access time, and entropy score. The global anomaly score is updated to reflect the new state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    metadata[key] = {
        'access_frequency': 1,
        'last_access_timestamp': current_time,
        'predicted_future_access_time': current_time + 1,
        'entropy': 1
    }
    
    update_global_anomaly_score(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates the global anomaly score to account for the removal. It also updates the entropy scores of remaining entries to ensure they reflect the current access patterns accurately.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    update_global_anomaly_score(cache_snapshot)
    for key, entry in metadata.items():
        entry['entropy'] *= ENTROPY_DECAY

def update_global_anomaly_score(cache_snapshot):
    global global_anomaly_score
    total_entropy = sum(entry['entropy'] for entry in metadata.values())
    global_anomaly_score = total_entropy / len(metadata) if metadata else 0