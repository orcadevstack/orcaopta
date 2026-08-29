from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, when, sum as spark_sum


def build_root_cause_graph(correlation: DataFrame):
    """
    Build a graph view from correlation:
      - SERVICE nodes (sources)
      - METRIC nodes (metric_name)
      - WINDOW nodes (time buckets)
      - Edges with weights from correlation_score
    """

    # Service–metric edges
    service_metric_edges = (
        correlation.select(
            col("source").alias("from"),
            col("metric_name").alias("to"),
            col("correlation_score").alias("weight"),
        )
        .withColumn("edge_type", lit("SERVICE_METRIC"))
    )

    # Metric–window edges
    metric_window_edges = (
        correlation.select(
            col("metric_name").alias("from"),
            col("window").alias("to"),
            col("correlation_score").alias("weight"),
        )
        .withColumn("edge_type", lit("METRIC_WINDOW"))
    )

    edges = service_metric_edges.unionByName(metric_window_edges, allowMissingColumns=True)

    # Nodes
    service_nodes = (
        correlation.select(col("source").alias("id"))
        .distinct()
        .withColumn("type", lit("SERVICE"))
    )

    metric_nodes = (
        correlation.select(col("metric_name").alias("id"))
        .distinct()
        .withColumn("type", lit("METRIC"))
    )

    window_nodes = (
        correlation.select(col("window").alias("id"))
        .distinct()
        .withColumn("type", lit("WINDOW"))
    )

    nodes = service_nodes.unionByName(metric_nodes).unionByName(window_nodes)

    return nodes, edges


def propagate_scores(nodes: DataFrame, edges: DataFrame, initial_scores: DataFrame, iterations: int = 3):
    """
    Simple score propagation over the graph:
      - initial_scores: DataFrame[id, score]
      - edges: from, to, weight
      - nodes: id, type

    Each iteration:
      new_score(to) += score(from) * normalized_weight
    """

    # Attach initial scores to nodes
    scored_nodes = nodes.join(initial_scores, on="id", how="left").fillna({"score": 0.0})

    for _ in range(iterations):
        # Join edges with current scores
        propagated = (
            edges.join(scored_nodes.select("id", "score"), edges["from"] == scored_nodes["id"], "left")
                 .select(
                     col("from"),
                     col("to"),
                     col("weight"),
                     col("score").alias("from_score"),
                 )
        )

        # Contribution from each edge
        contributions = propagated.withColumn(
            "contrib",
            col("from_score") * col("weight")
        )

        # Aggregate contributions per target node
        new_scores = (
            contributions.groupBy("to")
                         .agg(spark_sum("contrib").alias("score"))
                         .withColumnRenamed("to", "id")
        )

        # Merge back into scored_nodes
        scored_nodes = (
            scored_nodes.drop("score")
                        .join(new_scores, on="id", how="left")
                        .fillna({"score": 0.0})
        )

    return scored_nodes


def build_graph_based_rca(correlation: DataFrame, root_cause_df: DataFrame):
    """
    High-level RCA:
      1. Build graph from correlation.
      2. Use root_cause_score as initial scores on SERVICE nodes.
      3. Propagate scores through SERVICE→METRIC→WINDOW.
      4. Return ranked nodes by propagated score.
    """

    nodes, edges = build_root_cause_graph(correlation)

    # Initial scores: services get their root_cause_score, others start at 0
    initial_scores = (
        root_cause_df.select(col("source").alias("id"), col("root_cause_score").alias("score"))
    )

    propagated_nodes = propagate_scores(nodes, edges, initial_scores, iterations=3)

    # Rank nodes by propagated score
    ranked = propagated_nodes.orderBy(col("score").desc())

    return ranked, edges
