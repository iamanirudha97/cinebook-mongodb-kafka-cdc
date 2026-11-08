# CineBook — MongoDB Query Performance Benchmark

## 1. Objective

Evaluate how the **existing** `idx_bookings_show` index affects a selective booking lookup compared with a forced collection scan. The experiment measures MongoDB server-reported execution statistics; it does **not** measure application-level latency or benchmark a newly created index.

## 2. Environment and dataset

| Property | Value |
|---|---|
| Project | CineBook — MongoDB Atlas movie-booking application |
| Database | `cinebook` |
| Collection | `bookings` |
| Documents in collection at test time | 104 |
| Query filter | `{ "show_id": "SHW-000002" }` |
| Matching documents | 5 |
| Existing index | `idx_bookings_show` on `{ show_id: 1 }` |
| Driver | Async PyMongo, invoked from Python |
| Benchmark script | `scripts/benchmark_queries.py` |

The collection contained 100 bookings generated through the API plus four earlier test bookings. The 104-document count was independently observed in Atlas and in the benchmark's forced collection scan.

## 3. Methodology

Run the **same** equality filter twice using MongoDB's `explain` command with `executionStats` verbosity. Change only the index hint:

**Baseline — forced collection scan**

```javascript
{
  explain: {
    find: "bookings",
    filter: { show_id: "SHW-000002" },
    hint: { $natural: 1 }
  },
  verbosity: "executionStats"
}
```

**Indexed query — forced use of existing index**

```javascript
{
  explain: {
    find: "bookings",
    filter: { show_id: "SHW-000002" },
    hint: "idx_bookings_show"
  },
  verbosity: "executionStats"
}
```

Both commands are read-only. No bookings, collection validators, or indexes are modified. The hints make the access-path comparison explicit rather than relying on the query planner to select different plans automatically.

## 4. Observed results

Results from the local run of `uv run python -m scripts.benchmark_queries`:

| Metric | Forced COLLSCAN | Forced IXSCAN |
|---|---:|---:|
| Documents returned | 5 | 5 |
| Documents examined (`totalDocsExamined`) | 104 | 5 |
| Index keys examined (`totalKeysExamined`) | 0 | 5 |
| Execution time (`executionTimeMillis`) | 1 ms | 1 ms |

The Atlas Explain visual tree independently showed `IXSCAN → FETCH` using `idx_bookings_show`, with five documents and five index keys examined for the indexed filter.

### Reduction in documents examined

\[
\frac{104 - 5}{104} \times 100 = 95.19\%
\]

The indexed query examined **99 fewer documents**, a **95.19% reduction in documents examined**, while returning the same five results.

## 5. Interpretation

- **Collection scan:** MongoDB examined all 104 booking documents to find the five matching `show_id` values.
- **Index scan:** MongoDB traversed five index entries and fetched five matching documents, avoiding examination of the other 99 documents.
- **Latency:** Both plans reported **1 ms**. These results **do not establish a measurable execution-time improvement**.
- **Scale:** With only 104 documents, the workload is too small for reliable latency conclusions. The improvement shown is in *work performed* (`totalDocsExamined`), not proven wall-clock speed.
- **Existing index:** `idx_bookings_show` was created during the project's initial indexing setup. This experiment compares access paths; it is **not** a before-and-after index creation benchmark.

## 6. Relationship to revenue analytics

The `GET /analytics/revenue` endpoint aggregates confirmed bookings by movie. Its Atlas Explain plan showed:

| Metric | Observed value |
|---|---:|
| Access path | `COLLSCAN` |
| Documents examined | 104 |
| Index keys examined | 0 |
| Aggregation output documents | 20 |
| Reported execution time | 0 ms |

All 104 bookings were `CONFIRMED` at the time of testing. Because `{ status: "CONFIRMED" }` matches the entire collection, a collection scan is reasonable for this small dataset. The selective `show_id` lookup is a **separate benchmark**; its 95.19% reduction must **not** be attributed to the revenue aggregation.

## 7. Reproduce the benchmark

From the repository root, with the project's existing MongoDB Atlas configuration available:

```bash
uv run python -m scripts.benchmark_queries
```

The script connects through `backend.app.db.mongodb`, runs both `explain` commands, prints the comparison, and closes the connection. It does not insert or update data.

Results may differ as bookings are added, removed, or reassigned, and reported execution times can vary between runs. To compare results fairly, use the same dataset and query filter.

## 8. Conclusion and next steps

The existing `{ show_id: 1 }` index reduced documents examined from **104 to 5** for the tested booking lookup, while both access paths reported **1 ms** execution time. This verifies effective index selectivity but does not prove faster response times.

For a stronger future performance study, test a larger representative dataset, repeat measurements, report latency distributions, and benchmark queries that reflect actual application traffic. Do not add an index to the revenue aggregation solely to eliminate `COLLSCAN` when its filter matches every document.
