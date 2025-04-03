# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_RECENCY = 1.0
WEIGHT_CONSISTENCY_SCORE = 1.0
WEIGHT_REPLICATION_FACTOR = -1.0  # Negative because less replicated data is more valuable

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, transaction consistency score, and replication factor. Each cache entry is tagged with a consistency score that reflects its importance in maintaining transaction consistency, and a replication factor indicating how many replicas exist across the system.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_timestamp': {},
    'consistency_score': {},
    'replication_factor': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of its access frequency, recency, consistency score, and replication factor. Entries with lower composite scores are prioritized for eviction, ensuring that frequently accessed, transaction-critical, and less-replicated data is retained.
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
        consistency_score = metadata['consistency_score'][key]
        replication_factor = metadata['replication_factor'][key]
        
        composite_score = (
            WEIGHT_ACCESS_FREQUENCY * access_frequency +
            WEIGHT_RECENCY * recency +
            WEIGHT_CONSISTENCY_SCORE * consistency_score +
            WEIGHT_REPLICATION_FACTOR * replication_factor
        )
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access timestamp of the entry are updated. The transaction consistency score is recalculated if the hit is part of a transaction, ensuring that the entry's importance is accurately reflected.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    
    # Recalculate consistency score if part of a transaction
    # Placeholder for transaction check
    if True:  # Replace with actual transaction check
        metadata['consistency_score'][key] = calculate_consistency_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to one, sets the last access timestamp to the current time, assigns a default transaction consistency score based on its initial context, and records its replication factor based on system-wide data distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['consistency_score'][key] = default_consistency_score(obj)
    metadata['replication_factor'][key] = determine_replication_factor(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy adjusts the replication factor metadata for remaining entries to reflect the change in data distribution. It also recalibrates the transaction consistency scores of related entries to ensure ongoing transaction integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_timestamp'][evicted_key]
    del metadata['consistency_score'][evicted_key]
    del metadata['replication_factor'][evicted_key]
    
    # Adjust replication factors and consistency scores
    for key in cache_snapshot.cache:
        metadata['replication_factor'][key] = adjust_replication_factor(key)
        metadata['consistency_score'][key] = recalculate_consistency_score(key)

def calculate_consistency_score(obj):
    # Placeholder function to calculate consistency score
    return 1.0

def default_consistency_score(obj):
    # Placeholder function to determine default consistency score
    return 1.0

def determine_replication_factor(obj):
    # Placeholder function to determine replication factor
    return 1

def adjust_replication_factor(key):
    # Placeholder function to adjust replication factor
    return metadata['replication_factor'][key]

def recalculate_consistency_score(key):
    # Placeholder function to recalculate consistency score
    return metadata['consistency_score'][key]