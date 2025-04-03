# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ACCESS_FREQUENCY = 1
DEFAULT_HEURISTIC_SCORE = 0.5
SYNCHRONIZATION_STATUS_UP_TO_DATE = True
SYNCHRONIZATION_STATUS_OUTDATED = False

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data synchronization status, and context tags for each cache entry. It also keeps a heuristic score that predicts future access patterns based on historical data and context adaptation.
metadata = defaultdict(lambda: {
    'access_frequency': DEFAULT_ACCESS_FREQUENCY,
    'last_access_timestamp': 0,
    'synchronization_status': SYNCHRONIZATION_STATUS_UP_TO_DATE,
    'context_tags': set(),
    'heuristic_score': DEFAULT_HEURISTIC_SCORE
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which considers low access frequency, outdated synchronization status, and low heuristic prediction scores. Entries with the lowest composite score are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (
            meta['access_frequency'] +
            (1 if meta['synchronization_status'] == SYNCHRONIZATION_STATUS_OUTDATED else 0) +
            meta['heuristic_score']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access timestamp for the entry. It also refines the heuristic prediction score using the current context and access pattern, and checks if data synchronization status needs updating.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    # Update heuristic score based on some logic (e.g., increase if frequently accessed)
    meta['heuristic_score'] = min(1.0, meta['heuristic_score'] + 0.1)
    # Check and update synchronization status if needed
    if meta['synchronization_status'] == SYNCHRONIZATION_STATUS_OUTDATED:
        meta['synchronization_status'] = SYNCHRONIZATION_STATUS_UP_TO_DATE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a default access frequency, current timestamp, and context tags. It also assigns an initial heuristic prediction score based on similar entries and sets the synchronization status to up-to-date.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'access_frequency': DEFAULT_ACCESS_FREQUENCY,
        'last_access_timestamp': cache_snapshot.access_count,
        'synchronization_status': SYNCHRONIZATION_STATUS_UP_TO_DATE,
        'context_tags': set(),  # Initialize with empty or default context tags
        'heuristic_score': DEFAULT_HEURISTIC_SCORE
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the heuristic prediction model using the evicted entry's metadata to improve future predictions. It also updates global context adaptation parameters to better align with current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_meta = metadata.pop(evicted_obj.key, None)
    if evicted_meta:
        # Recalibrate heuristic prediction model using evicted entry's metadata
        # For example, adjust global parameters or context adaptation logic
        pass