# Search System Design

## Definition

A **search system** indexes content for fast retrieval and ranks results by relevance.
It usually combines ingestion pipelines, index storage, and query-time ranking.

## Key Concepts

### Indexing
- Inverted index maps terms to document IDs
- Tokenization, stemming, stop-word removal
- Incremental indexing for freshness

### Query Processing
- Parsing: spelling correction, synonym expansion, query rewriting
- Retrieval: candidate generation from index
- Ranking: BM25/vector score + business signals

### Freshness and Quality
- Near-real-time indexing for recent content
- Offline relevance evaluation
- Anti-spam and abuse filtering

## Real-World Examples

### E-commerce Search
- Index product title, description, category, availability
- Ranking combines textual match + click-through + inventory
- Faceted filters: brand, price, rating

### Docs Search
- Index code/docs with language-aware analyzers
- Boost exact symbol matches
- Autocomplete from popular prefixes

## When to Use

- Large content catalogs
- User workflows requiring fast retrieval
- Systems where ranking quality affects conversion/engagement

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Frequent index updates | Better freshness | Higher ingestion load |
| Complex ranking model | Better relevance | Higher query latency |
| Broad query expansion | Better recall | More noisy results |

## Implementation Tips

1. Separate retrieval and ranking stages.
2. Cache hot queries and top results.
3. Track p50/p95/p99 latency and relevance metrics.
4. Keep explicit schema for searchable vs filterable fields.
5. Support reindexing pipelines for mapping changes.

## Common Pitfalls

- Mixing transactional DB concerns with search index design
- No strategy for stale index data
- Ranking changes without offline/online evaluation
- Poor handling of typo tolerance and synonyms

## Related Topics

- [Caching](./07-caching.md)
- [Distributed Caching](./08-distributed-caching.md)
- [Data Modeling and Schema Evolution](./59-data-modeling-and-schema-evolution.md)
- [Backpressure, Load Shedding, and Graceful Degradation](./58-backpressure-load-shedding-and-graceful-degradation.md)

## Interview Tips

- Clarify search type: keyword, semantic, or hybrid.
- Discuss recall vs precision trade-offs.
- Mention index partitioning/sharding at scale.
- Include relevance feedback loop from user behavior.
