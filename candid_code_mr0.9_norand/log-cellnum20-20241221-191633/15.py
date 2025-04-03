# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
PRIORITY_WEIGHT = 1.0
RECENCY_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a weighted score for each cache entry, a hierarchical level indicator, and an event priority counter. The weighted score is a composite of access frequency, recency, and event priority. The hierarchical level indicates the cache tier the entry belongs to, and the event priority counter tracks the importance of the events that accessed the entry.
cache_metadata = {
    'frequency': defaultdict(int),
    'recency': defaultdict(int),
    'priority': defaultdict(int),
    'hierarchical_level': defaultdict(lambda: 0),
}

def calculate_weighted_score(key):
    frequency = cache_metadata['frequency'][key]
    recency = cache_metadata['recency'][key]
    priority = cache_metadata['priority'][key]
    return (FREQUENCY_WEIGHT * frequency +
            RECENCY_WEIGHT * recency +
            PRIORITY_WEIGHT * priority)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest weighted score within the lowest hierarchical level. If there is a tie, the entry with the lowest event priority counter is chosen. This ensures that less important and less frequently accessed entries are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    min_priority = float('inf')
    min_level = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        level = cache_metadata['hierarchical_level'][key]
        score = calculate_weighted_score(key)
        priority = cache_metadata['priority'][key]

        if (level < min_level or
            (level == min_level and score < min_score) or
            (level == min_level and score == min_score and priority < min_priority)):
            min_level = level
            min_score = score
            min_priority = priority
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the weighted score of the accessed entry by incrementing its access frequency and recency components. The event priority counter is also incremented based on the priority of the accessing event, ensuring that more critical accesses boost the entry's score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] += 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['priority'][key] += 1  # Assuming each hit has a priority increment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its weighted score based on the initial access event's priority and sets its hierarchical level to the lowest tier. The event priority counter is set according to the importance of the insertion event, allowing the entry to adaptively adjust its score over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['frequency'][key] = 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    cache_metadata['priority'][key] = 1  # Assuming initial insertion has a priority of 1
    cache_metadata['hierarchical_level'][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the weighted scores of remaining entries by slightly decreasing their recency component to reflect the increased competition for cache space. The hierarchical levels are also adjusted if necessary to maintain balance across cache tiers, ensuring efficient use of the cache hierarchy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        cache_metadata['recency'][key] *= RECENCY_DECAY
        # Adjust hierarchical levels if needed (not specified how, so assuming no change)