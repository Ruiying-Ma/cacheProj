# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_ACCESS_FREQUENCY = 1
VIRTUAL_SYNC_SCORE_BASELINE = 0.5
RECENCY_WEIGHT = 0.4
FREQUENCY_WEIGHT = 0.3
VIRTUAL_SYNC_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, context tags (e.g., user behavior, time of day), and a virtual synchronization score that predicts future access patterns based on historical data.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'context_tags': defaultdict(lambda: defaultdict(int)),
    'virtual_sync_score': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines low access frequency, low recency, and low virtual synchronization score, while also considering context tags to avoid evicting items likely to be needed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = metadata['recency'][key]
        virtual_sync_score = metadata['virtual_sync_score'][key]
        
        # Calculate composite score
        score = (FREQUENCY_WEIGHT * frequency +
                 RECENCY_WEIGHT * recency +
                 VIRTUAL_SYNC_WEIGHT * virtual_sync_score)
        
        # Consider context tags (simplified for this example)
        context_score = sum(metadata['context_tags'][key].values())
        score -= context_score
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the recency timestamp, and adjusts the virtual synchronization score based on the current context tags to better predict future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    # Adjust virtual sync score based on context tags (simplified)
    metadata['virtual_sync_score'][key] += sum(metadata['context_tags'][key].values()) * 0.1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline access frequency, the current timestamp for recency, and a virtual synchronization score derived from similar context tags, ensuring it aligns with predicted access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = BASELINE_ACCESS_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    # Initialize virtual sync score (simplified)
    metadata['virtual_sync_score'][key] = VIRTUAL_SYNC_SCORE_BASELINE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the virtual synchronization model using the evicted item's metadata to refine future predictions, and updates context tag weights to improve decision-making for similar scenarios.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate virtual sync model (simplified)
    for tag, weight in metadata['context_tags'][evicted_key].items():
        metadata['context_tags'][evicted_key][tag] *= 0.9  # Decay factor