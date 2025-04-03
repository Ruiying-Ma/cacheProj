# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency in composite score
BETA = 0.3   # Weight for recency in composite score
GAMMA = 0.1  # Weight for context relevance in composite score
DELTA = 0.1  # Weight for semantic relevance in composite score

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data context tags, and semantic relevance scores. It also tracks query patterns and workflow states to adaptively manage cache entries.
metadata = {
    'access_frequency': {},  # {obj.key: frequency}
    'last_access_time': {},  # {obj.key: last_access_time}
    'context_tags': {},      # {obj.key: context_tags}
    'semantic_relevance': {} # {obj.key: semantic_relevance_score}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a composite score derived from access frequency, recency, context relevance, and semantic matching. Entries with the lowest composite score are selected for eviction, ensuring that frequently accessed and contextually relevant data is retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        context_relevance = metadata['context_tags'].get(key, 0)
        semantic_relevance = metadata['semantic_relevance'].get(key, 0)
        
        composite_score = (ALPHA * access_freq +
                           BETA * (cache_snapshot.access_count - last_access) +
                           GAMMA * context_relevance +
                           DELTA * semantic_relevance)
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time for the entry. It also re-evaluates the context tags and semantic relevance score based on the current query and workflow state, ensuring the metadata reflects the latest usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    # Re-evaluate context tags and semantic relevance score
    metadata['context_tags'][key] = evaluate_context_tags(obj)
    metadata['semantic_relevance'][key] = evaluate_semantic_relevance(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency and last access time. It assigns context tags and calculates an initial semantic relevance score based on the insertion context and query patterns, integrating the new entry into the adaptive management framework.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['context_tags'][key] = evaluate_context_tags(obj)
    metadata['semantic_relevance'][key] = evaluate_semantic_relevance(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the remaining entries' metadata by adjusting context tags and semantic relevance scores to reflect the removal. It also updates the query pattern and workflow state metadata to ensure ongoing adaptive optimization of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['context_tags']:
        del metadata['context_tags'][evicted_key]
    if evicted_key in metadata['semantic_relevance']:
        del metadata['semantic_relevance'][evicted_key]
    
    # Rebalance remaining entries' metadata
    for key in cache_snapshot.cache:
        metadata['context_tags'][key] = evaluate_context_tags(cache_snapshot.cache[key])
        metadata['semantic_relevance'][key] = evaluate_semantic_relevance(cache_snapshot.cache[key])

def evaluate_context_tags(obj):
    # Placeholder function to evaluate context tags
    return 1  # Replace with actual context tag evaluation logic

def evaluate_semantic_relevance(obj):
    # Placeholder function to evaluate semantic relevance score
    return 1  # Replace with actual semantic relevance evaluation logic