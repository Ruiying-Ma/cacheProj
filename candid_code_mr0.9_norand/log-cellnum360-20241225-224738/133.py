# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_RECENCY = 1.0
WEIGHT_PREDICTED_FUTURE_ACCESS = 1.0
WEIGHT_LATENCY_COMPENSATION = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and a latency compensation score for each cache entry.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'predicted_future_access_time': {},
    'latency_compensation_score': defaultdict(lambda: 1.0)  # Default score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of its access frequency, recency, predicted future access time, and latency compensation score. The entry with the lowest score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'][key]
        recency = cache_snapshot.access_count - metadata['last_access_timestamp'][key]
        predicted_future_access = metadata['predicted_future_access_time'][key]
        latency_compensation = metadata['latency_compensation_score'][key]
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_RECENCY * recency +
                 WEIGHT_PREDICTED_FUTURE_ACCESS * predicted_future_access +
                 WEIGHT_LATENCY_COMPENSATION * latency_compensation)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access timestamp to the current time, and recalculates the predicted future access time using a simple predictive model based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    
    # Simple predictive model: assume next access is in the same interval as the last two accesses
    if metadata['access_frequency'][key] > 1:
        last_access = metadata['last_access_timestamp'][key]
        previous_access = last_access - (cache_snapshot.access_count - last_access)
        metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + (last_access - previous_access)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, estimates the predicted future access time based on initial access patterns, and assigns a default latency compensation score based on the object's type or source.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 10  # Arbitrary initial prediction
    metadata['latency_compensation_score'][key] = 1.0  # Default score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy adjusts the latency compensation scores of remaining entries to ensure optimal queue performance, potentially increasing scores for entries that are frequently accessed or have high predicted future access times.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        if key != evicted_obj.key:
            access_frequency = metadata['access_frequency'][key]
            predicted_future_access = metadata['predicted_future_access_time'][key]
            
            # Adjust latency compensation score based on access frequency and predicted future access
            metadata['latency_compensation_score'][key] += 0.1 * access_frequency + 0.1 * predicted_future_access