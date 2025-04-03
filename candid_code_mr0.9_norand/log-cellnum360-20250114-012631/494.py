# Import anything you need below
import time
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS_TIME = 0.3
WEIGHT_CONTEXTUAL_PRIORITY = 0.2
WEIGHT_LATENT_FEATURES = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, contextual tags (e.g., user behavior patterns, time of day), and latent features extracted from historical access patterns.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'contextual_tags': {},
    'latent_features': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a weighted score combining low access frequency, old last access time, low contextual priority, and low relevance of latent features. The item with the lowest score is evicted.
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
        last_access_time = metadata['last_access_time'][key]
        contextual_priority = metadata['contextual_tags'].get(key, 0)
        latent_features = metadata['latent_features'].get(key, 0)
        
        score = (WEIGHT_ACCESS_FREQUENCY * access_frequency +
                 WEIGHT_LAST_ACCESS_TIME * (cache_snapshot.access_count - last_access_time) +
                 WEIGHT_CONTEXTUAL_PRIORITY * contextual_priority +
                 WEIGHT_LATENT_FEATURES * latent_features)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and adjusts the contextual tags and latent features based on the current context and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Update contextual tags and latent features based on current context and access patterns
    metadata['contextual_tags'][key] = get_contextual_priority()
    metadata['latent_features'][key] = extract_latent_features()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns contextual tags based on the insertion context, and extracts initial latent features from the historical access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = get_contextual_priority()
    metadata['latent_features'][key] = extract_latent_features()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the contextual priorities and latent features for the remaining items to ensure they reflect the most current access patterns and context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata of the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    if evicted_key in metadata['latent_features']:
        del metadata['latent_features'][evicted_key]
    
    # Recalculate contextual priorities and latent features for remaining items
    for key in cache_snapshot.cache:
        metadata['contextual_tags'][key] = get_contextual_priority()
        metadata['latent_features'][key] = extract_latent_features()

def get_contextual_priority():
    # Placeholder function to calculate contextual priority
    return 0

def extract_latent_features():
    # Placeholder function to extract latent features
    return 0