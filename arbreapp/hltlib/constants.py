CONTEXT_ONLY = 0
EDGE_CONTENT_ONLY = 1
VERTEX_CONTENT_ONLY = 2
MULTIPLICATIVE_FUSION = 3
ADDITIVE_FUSION = 4

# Arbitrary ordering, for indexing dicts
def ao(v1, v2):
    if v1 > v2:
        return (v1, v2)
    else:
        return (v2, v1)
