# Notes Index

## Algorithm

### DP and State
- [dp_dynamic_programming](algorithm/dp_dynamic_programming.md): DP checklist, types, and pitfalls.
- [edit_distance_dp](algorithm/edit_distance_dp.md): edit distance and string alignment DP.
- [knapsack_dp](algorithm/knapsack_dp.md): 0/1 knapsack patterns.
- [tree_dp](algorithm/tree_dp.md): subtree DP patterns.
- [tree_postorder_subtree_sum](algorithm/tree_postorder_subtree_sum.md): postorder subtree sum aggregation.

### Windows, Prefix, and Two Pointers
- [sliding_window](algorithm/sliding_window.md): two-pointer window scanning.
- [monotonic_queue](algorithm/monotonic_queue.md): deque for window min/max.
- [prefix_sum](algorithm/prefix_sum.md): O(1) range sums after O(n) build.
- [prefix_suffix_penalty_scan](algorithm/prefix_suffix_penalty_scan.md): scan all split points to minimize penalty.
- [two_pointers](algorithm/two_pointers.md): linear scan with two indices.
- [monotonic_three_phase_scan](algorithm/monotonic_three_phase_scan.md): inc→dec→inc phase scan (state machine).

### Counting and Aggregation
- [combinatorics_counting](algorithm/combinatorics_counting.md): common counting formulas and combinations.
- [frequency_counting](algorithm/frequency_counting.md): array-based frequency scans.
- [grouping_aggregation](algorithm/grouping_aggregation.md): map-based aggregation patterns.

### Geometry
- [geometry_line_grouping](algorithm/geometry_line_grouping.md): slope normalization and line keys.

### Graph
- [dijkstra_shortest_path](algorithm/dijkstra_shortest_path.md): shortest paths with non-negative weights.
- [floyd_warshall_all_pairs_shortest_path](algorithm/floyd_warshall_all_pairs_shortest_path.md): all-pairs shortest paths via DP.

### Sweeps and Sorting
- [event_sorting_sweep](algorithm/event_sorting_sweep.md): time-ordered event processing.
- [greedy_sorting_linear_decay](algorithm/greedy_sorting_linear_decay.md): sort-first greedy with linear decay.
- [room_allocation_two_heaps](algorithm/room_allocation_two_heaps.md): room scheduling with available/busy heaps.
- [sorting_custom_order](algorithm/sorting_custom_order.md): rank-based sorting.

### Arrays and Basics
- [dynamic_array_vec](algorithm/dynamic_array_vec.md): dynamic array operations and notes.
- [carry_propagation_addition](algorithm/carry_propagation_addition.md): digit-array addition with carry.
- [fixed_size_subgrid_scan](algorithm/fixed_size_subgrid_scan.md): scan fixed-size subgrids.

## Data Structure

### Graph
- [adjacency_list](data_structure/adjacency_list.md): graph/tree representation.
- [weighted_graph](data_structure/weighted_graph.md): weighted edges and representations.

### Tree
- [binary_tree](data_structure/binary_tree.md): binary tree basics and traversals.

### Queue and Heap
- [deque_vecdeque](data_structure/deque_vecdeque.md): double-ended queue.
- [priority_queue_binary_heap](data_structure/priority_queue_binary_heap.md): binary heap priority queue.

### Hashing
- [hash_map_set](data_structure/hash_map_set.md): hash-based map/set basics.

### Disjoint Set
- [union_find_dsu](data_structure/union_find_dsu.md): disjoint set union.

### Array Precompute
- [dp_1d_array](data_structure/dp_1d_array.md): one-dimensional DP storage.
- [dp_2d_array](data_structure/dp_2d_array.md): two-dimensional DP storage.
- [prefix_suffix_count_array](data_structure/prefix_suffix_count_array.md): prefix/suffix counts for split costs.
- [presence_array](data_structure/presence_array.md): boolean presence tracking for small ranges.
- [state_tracking_array](data_structure/state_tracking_array.md): per-item status tracking.
- [suffix_max_array](data_structure/suffix_max_array.md): suffix maximum lookups.

## Database

Notes on database migrations and schema evolution.

### Overview
- [database/README](database/README.md): database notes landing page.

### Migrations
- [database/alembic/README](database/alembic/README.md): Alembic notes index and quick start.
- [database/alembic/01-baseline](database/alembic/01-baseline.md): baseline setup for existing databases.
- [database/alembic/02-autogenerate](database/alembic/02-autogenerate.md): autogenerate workflow and limits.
- [database/alembic/03-data-migrations](database/alembic/03-data-migrations.md): data migrations and seed strategies.
- [database/alembic/04-commands](database/alembic/04-commands.md): common Alembic commands.
- [database/alembic/05-troubleshooting](database/alembic/05-troubleshooting.md): frequent issues and fixes.

### Foundations
- [database/indexing](database/indexing.md): indexing basics and common pitfalls.
- [database/transactions](database/transactions.md): transactions and ACID summary.
- [database/isolation_levels](database/isolation_levels.md): isolation levels overview.

### PostgreSQL
- [database/postgres_gotchas](database/postgres_gotchas.md): operational gotchas and maintenance notes.
- [database/postgres_explain_guide](database/postgres_explain_guide.md): EXPLAIN/ANALYZE guide and plan node glossary.
- [database/postgres_explain_examples](database/postgres_explain_examples.md): EXPLAIN plan examples with annotations.
- [database/postgres_index_join_guide](database/postgres_index_join_guide.md): index and join strategy decision guide.
- [database/postgres_lock_troubleshooting](database/postgres_lock_troubleshooting.md): lock waits and deadlock troubleshooting.
- [database/postgres_slow_query_triage](database/postgres_slow_query_triage.md): slow query triage checklist.

## Reverse Index

### Algorithm Notes -> LeetCode
- [combinatorics_counting](algorithm/combinatorics_counting.md): [q2147](leetcode/q2147.md), [q3577](leetcode/q3577.md), [q3623](leetcode/q3623.md), [q3625](leetcode/q3625.md)
- [carry_propagation_addition](algorithm/carry_propagation_addition.md): [q66](leetcode/q66.md)
- [dp_dynamic_programming](algorithm/dp_dynamic_programming.md): [q712](leetcode/q712.md), [q2110](leetcode/q2110.md), [q2147](leetcode/q2147.md), [q3562](leetcode/q3562.md), [q3573](leetcode/q3573.md), [q3578](leetcode/q3578.md)
- [edit_distance_dp](algorithm/edit_distance_dp.md): [q712](leetcode/q712.md)
- [event_sorting_sweep](algorithm/event_sorting_sweep.md): [q2092](leetcode/q2092.md), [q3433](leetcode/q3433.md)
- [frequency_counting](algorithm/frequency_counting.md): [q3583](leetcode/q3583.md)
- [greedy_sorting_linear_decay](algorithm/greedy_sorting_linear_decay.md): [q3075](leetcode/q3075.md)
- [geometry_line_grouping](algorithm/geometry_line_grouping.md): [q3625](leetcode/q3625.md)
- [grouping_aggregation](algorithm/grouping_aggregation.md): [q3531](leetcode/q3531.md), [q3623](leetcode/q3623.md)
- [knapsack_dp](algorithm/knapsack_dp.md): [q3562](leetcode/q3562.md)
- [monotonic_queue](algorithm/monotonic_queue.md): [q3578](leetcode/q3578.md)
- [prefix_sum](algorithm/prefix_sum.md): [q3578](leetcode/q3578.md), [q3652](leetcode/q3652.md)
- [prefix_suffix_penalty_scan](algorithm/prefix_suffix_penalty_scan.md): [q2483](leetcode/q2483.md)
- [room_allocation_two_heaps](algorithm/room_allocation_two_heaps.md): [q2402](leetcode/q2402.md)
- [sliding_window](algorithm/sliding_window.md): [q3578](leetcode/q3578.md), [q3652](leetcode/q3652.md)
- [sorting_custom_order](algorithm/sorting_custom_order.md): [q3606](leetcode/q3606.md)
- [tree_dp](algorithm/tree_dp.md): [q3562](leetcode/q3562.md)
- [tree_postorder_subtree_sum](algorithm/tree_postorder_subtree_sum.md): [q1339](leetcode/q1339.md)
- [two_pointers](algorithm/two_pointers.md): [q2211](leetcode/q2211.md)
- [monotonic_three_phase_scan](algorithm/monotonic_three_phase_scan.md): [q3637](leetcode/q3637.md)
- [dynamic_array_vec](algorithm/dynamic_array_vec.md): [q66](leetcode/q66.md), [q3075](leetcode/q3075.md)
- [fixed_size_subgrid_scan](algorithm/fixed_size_subgrid_scan.md): [q840](leetcode/q840.md)
- [dijkstra_shortest_path](algorithm/dijkstra_shortest_path.md): [q3650](leetcode/q3650.md)
- [floyd_warshall_all_pairs_shortest_path](algorithm/floyd_warshall_all_pairs_shortest_path.md): [q2976](leetcode/q2976.md)

### Data Structure Notes -> LeetCode
- [adjacency_list](data_structure/adjacency_list.md): [q3562](leetcode/q3562.md), [q3650](leetcode/q3650.md)
- [binary_tree](data_structure/binary_tree.md): [q1339](leetcode/q1339.md)
- [deque_vecdeque](data_structure/deque_vecdeque.md): [q3578](leetcode/q3578.md)
- [dp_1d_array](data_structure/dp_1d_array.md): [q960](leetcode/q960.md)
- [dp_2d_array](data_structure/dp_2d_array.md): [q712](leetcode/q712.md), [q2976](leetcode/q2976.md)
- [hash_map_set](data_structure/hash_map_set.md): [q2092](leetcode/q2092.md), [q3531](leetcode/q3531.md), [q3606](leetcode/q3606.md), [q3623](leetcode/q3623.md), [q3625](leetcode/q3625.md)
- [prefix_suffix_count_array](data_structure/prefix_suffix_count_array.md): [q2483](leetcode/q2483.md)
- [presence_array](data_structure/presence_array.md): [q840](leetcode/q840.md)
- [priority_queue_binary_heap](data_structure/priority_queue_binary_heap.md): [q2402](leetcode/q2402.md), [q3433](leetcode/q3433.md), [q3650](leetcode/q3650.md)
- [state_tracking_array](data_structure/state_tracking_array.md): [q955](leetcode/q955.md)
- [suffix_max_array](data_structure/suffix_max_array.md): [q2054](leetcode/q2054.md)
- [union_find_dsu](data_structure/union_find_dsu.md): [q2092](leetcode/q2092.md)
- [weighted_graph](data_structure/weighted_graph.md): [q2976](leetcode/q2976.md)

### Database Notes -> Alembic
- [database/alembic/README](database/alembic/README.md): Alembic notes index and quick start.
- [database/alembic/01-baseline](database/alembic/01-baseline.md): baseline setup for existing databases.
- [database/alembic/02-autogenerate](database/alembic/02-autogenerate.md): autogenerate workflow and limits.
- [database/alembic/03-data-migrations](database/alembic/03-data-migrations.md): data migrations and seed strategies.
- [database/alembic/04-commands](database/alembic/04-commands.md): common Alembic commands.
- [database/alembic/05-troubleshooting](database/alembic/05-troubleshooting.md): frequent issues and fixes.

### Database Notes -> Foundations
- [database/indexing](database/indexing.md): indexing basics and common pitfalls.
- [database/transactions](database/transactions.md): transactions and ACID summary.
- [database/isolation_levels](database/isolation_levels.md): isolation levels overview.

### Database Notes -> PostgreSQL
- [database/postgres_gotchas](database/postgres_gotchas.md): operational gotchas and maintenance notes.
- [database/postgres_explain_guide](database/postgres_explain_guide.md): EXPLAIN/ANALYZE guide and plan node glossary.
- [database/postgres_explain_examples](database/postgres_explain_examples.md): EXPLAIN plan examples with annotations.
- [database/postgres_index_join_guide](database/postgres_index_join_guide.md): index and join strategy decision guide.
- [database/postgres_lock_troubleshooting](database/postgres_lock_troubleshooting.md): lock waits and deadlock troubleshooting.
- [database/postgres_slow_query_triage](database/postgres_slow_query_triage.md): slow query triage checklist.
