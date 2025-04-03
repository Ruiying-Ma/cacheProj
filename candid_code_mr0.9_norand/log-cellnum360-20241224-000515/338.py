# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SCORE = 1.0
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
CONTEXTUAL_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, contextual tags, and a dynamic equilibrium score for each cache entry. Contextual tags are derived from heuristic analysis of access patterns and workload characteristics.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'contextual_tags': defaultdict(set),
    'dynamic_equilibrium_score': defaultdict(lambda: BASELINE_SCORE)
}

def calculate_dynamic_equilibrium_score(key):
    frequency = metadata['access_frequency'][key]
    recency = metadata['recency'][key]
    contextual_relevance = len(metadata['contextual_tags'][key])
    score = (FREQUENCY_WEIGHT * frequency +
             RECENCY_WEIGHT * recency +
             CONTEXTUAL_WEIGHT * contextual_relevance)
    return score

def evict(cache_snapshot, obj):
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_dynamic_equilibrium_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['dynamic_equilibrium_score'][key] = calculate_dynamic_equilibrium_score(key)
    # Re-evaluate contextual tags (placeholder for heuristic analysis)
    metadata['contextual_tags'][key].add('recently_accessed')

def update_after_insert(cache_snapshot, obj):
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['contextual_tags'][key] = {'newly_inserted'}
    metadata['dynamic_equilibrium_score'][key] = BASELINE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['contextual_tags']:
        del metadata['contextual_tags'][evicted_key]
    if evicted_key in metadata['dynamic_equilibrium_score']:
        del metadata['dynamic_equilibrium_score'][evicted_key]
    
    # Adjust scores and re-assess contextual tags for remaining entries
    for key in cache_snapshot.cache:
        metadata['dynamic_equilibrium_score'][key] = calculate_dynamic_equilibrium_score(key)
        # Re-assess contextual tags (placeholder for heuristic analysis)
        if 'newly_inserted' in metadata['contextual_tags'][key]:
            metadata['contextual_tags'][key].remove('newly_inserted')
        metadata['contextual_tags'][key].add('post_eviction_adjustment')