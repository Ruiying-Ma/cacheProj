# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TOKEN_COUNT = 1
CAPACITY_THRESHOLD_FACTOR = 0.8

# Put the metadata specifically maintained by the policy below. The policy maintains a token count for each cache entry, a batch insertion timestamp, a stream identifier, and a dynamic capacity threshold. Tokens represent the frequency and recency of access, while the batch timestamp helps manage entries inserted together. The stream identifier categorizes entries based on their data source or type, and the capacity threshold adjusts based on cache performance.
token_count = defaultdict(int)
batch_timestamp = {}
stream_identifier = {}
stream_access_frequency = defaultdict(int)
dynamic_capacity_threshold = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects eviction victims by first identifying entries with the lowest token count. Among these, it prioritizes entries from the least accessed stream. If a tie persists, it evicts the oldest batch insertion timestamp. This ensures that less relevant and less frequently accessed data is removed first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_token_count = float('inf')
    min_stream_access = float('inf')
    oldest_timestamp = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        tokens = token_count[key]
        stream_id = stream_identifier[key]
        stream_access = stream_access_frequency[stream_id]
        timestamp = batch_timestamp[key]

        if (tokens < min_token_count or
            (tokens == min_token_count and stream_access < min_stream_access) or
            (tokens == min_token_count and stream_access == min_stream_access and timestamp < oldest_timestamp)):
            min_token_count = tokens
            min_stream_access = stream_access
            oldest_timestamp = timestamp
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the token count for the accessed entry, indicating increased relevance. It also updates the stream's access frequency, which may influence future eviction decisions. The batch timestamp remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    token_count[key] += 1
    stream_id = stream_identifier[key]
    stream_access_frequency[stream_id] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial token count and records the current time as the batch insertion timestamp. It also updates the stream identifier and recalibrates the capacity threshold based on current cache performance metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    token_count[key] = INITIAL_TOKEN_COUNT
    batch_timestamp[key] = cache_snapshot.access_count
    stream_identifier[key] = obj.key.split('_')[0]  # Example stream identifier logic
    dynamic_capacity_threshold = int(cache_snapshot.capacity * CAPACITY_THRESHOLD_FACTOR)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy decreases the token count of the evicted entry's stream, reflecting its reduced relevance. It also recalibrates the capacity threshold to ensure optimal cache utilization and updates the batch insertion records to maintain accurate historical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    stream_id = stream_identifier[evicted_key]
    stream_access_frequency[stream_id] -= 1
    dynamic_capacity_threshold = int(cache_snapshot.capacity * CAPACITY_THRESHOLD_FACTOR)
    del token_count[evicted_key]
    del batch_timestamp[evicted_key]
    del stream_identifier[evicted_key]