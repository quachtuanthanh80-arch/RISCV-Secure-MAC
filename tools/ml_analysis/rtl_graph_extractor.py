#!/usr/bin/env python3
"""
RTL Hardware Netlist & Dataflow Graph Extractor using PySlang
Parses SystemVerilog/Verilog source code into an abstract semantic graph.
Constructs a NetworkX directed graph representation with structural, functional,
and topological node features (degree, centrality, pipeline depth, fan-in/fan-out).
"""

import os
import json
from pathlib import Path
import networkx as nx
import pyslang


def extract_rtl_graph(project_root=None, output_dir=None):
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent # D:/NCKH
    else:
        project_root = Path(project_root)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "data"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Extracting RTL Hardware Graph for Secure_MAC from: {project_root}")

    # Files to parse
    rtl_files = [
        project_root / "rtl" / "mac" / "ewma_tracker.sv",
        project_root / "rtl" / "mac" / "secure_mac.v"
    ]
    for rf in rtl_files:
        if not rf.exists():
            raise FileNotFoundError(f"Missing RTL source file: {rf}")

    comp = pyslang.Compilation()
    for rf in rtl_files:
        tree = pyslang.SyntaxTree.fromFile(str(rf))
        comp.addSyntaxTree(tree)

    root = comp.getRoot()
    top_inst = None
    for inst in root.topInstances:
        if inst.name == "secure_mac":
            top_inst = inst
            break
    if top_inst is None and len(root.topInstances) > 0:
        top_inst = root.topInstances[0]

    print(f"[+] Root module identified: '{top_inst.name}'")

    G = nx.DiGraph()

    # Known bitwidths for Secure MAC signals
    bitwidth_map = {
        "clk": 1, "rst_n": 1, "start": 1, "valid": 1, "valid_d1": 1, "valid_d1_n": 1,
        "valid_d2": 1, "valid_d2_n": 1, "fault_detected": 1, "rollback": 1,
        "mod3_mismatch": 1, "range_anomaly": 1, "control_fault": 1, "disagreement": 1,
        "ewma_warmup_done": 1,
        "a": 8, "b": 8, "reg_a": 8, "reg_b": 8,
        "a_mod3": 2, "b_mod3": 2, "c_mod3": 2, "pipe_c_mod3": 2, "out_mod3": 2, "expected_mod3": 2, "expected_mod3_reg": 2,
        "ab_mod3_product": 4, "pipe_ab_mod3": 4, "rns_calc": 4,
        "product": 16, "pipe_product": 16,
        "c": 32, "reg_c": 32, "reg_c_32": 32, "pipe_c": 32, "mac_result": 32, "mac_result_32": 32,
        "shadow_accumulator": 32, "out": 32, "adaptive_threshold": 32, "active_threshold": 32,
        "ewma_mean": 32, "ewma_mad": 32
    }

    # Dataflow edges
    dataflow_edges = [
        # Stage 0 -> Stage 1
        ("clk", "reg_a"), ("clk", "reg_b"), ("clk", "reg_c"), ("clk", "valid_d1"), ("clk", "valid_d1_n"),
        ("rst_n", "reg_a"), ("rst_n", "reg_b"), ("rst_n", "reg_c"),
        ("a", "reg_a"), ("b", "reg_b"), ("c", "reg_c"), ("start", "valid_d1"), ("start", "valid_d1_n"),
        
        # Stage 1 -> Combinational 1.5
        ("reg_a", "product"), ("reg_b", "product"),
        ("reg_a", "u_enc_a"), ("u_enc_a", "a_mod3"),
        ("reg_b", "u_enc_b"), ("u_enc_b", "b_mod3"),
        ("reg_c", "reg_c_32"), ("reg_c_32", "u_enc_c"), ("u_enc_c", "c_mod3"),
        ("a_mod3", "ab_mod3_product"), ("b_mod3", "ab_mod3_product"),

        # Combinational 1.5 -> Stage 2
        ("product", "pipe_product"), ("reg_c", "pipe_c"),
        ("ab_mod3_product", "pipe_ab_mod3"), ("c_mod3", "pipe_c_mod3"),
        ("valid_d1", "valid_d2"), ("valid_d1_n", "valid_d2_n"),
        ("clk", "pipe_product"), ("clk", "pipe_c"), ("clk", "pipe_ab_mod3"), ("clk", "pipe_c_mod3"),

        # Stage 2 -> Combinational 2.5
        ("pipe_product", "mac_result"), ("pipe_c", "mac_result"),
        ("mac_result", "mac_result_32"), ("mac_result_32", "u_enc_out"), ("u_enc_out", "out_mod3"),
        ("pipe_ab_mod3", "rns_calc"), ("pipe_c_mod3", "rns_calc"), ("rns_calc", "expected_mod3_reg"), ("expected_mod3_reg", "expected_mod3"),
        ("expected_mod3", "mod3_mismatch"), ("out_mod3", "mod3_mismatch"),

        # EWMA Tracker
        ("mac_result", "u_ewma"), ("valid_d2", "u_ewma"), ("mod3_mismatch", "u_ewma"),
        ("u_ewma", "adaptive_threshold"), ("u_ewma", "ewma_mean"), ("u_ewma", "ewma_mad"), ("u_ewma", "ewma_warmup_done"),
        ("adaptive_threshold", "active_threshold"), ("mac_result", "range_anomaly"), ("active_threshold", "range_anomaly"),

        # Control Integrity & Disagreement
        ("valid_d1", "control_fault"), ("valid_d1_n", "control_fault"), ("valid_d2", "control_fault"), ("valid_d2_n", "control_fault"),
        ("mod3_mismatch", "disagreement"), ("range_anomaly", "disagreement"), ("control_fault", "disagreement"),

        # Stage 3
        ("disagreement", "out"), ("disagreement", "fault_detected"), ("disagreement", "rollback"),
        ("mac_result", "out"), ("mac_result", "shadow_accumulator"),
        ("shadow_accumulator", "out"),
        ("clk", "out"), ("clk", "fault_detected"), ("clk", "rollback"), ("clk", "shadow_accumulator"), ("clk", "valid")
    ]

    # Iterate symbols in top module body
    for member in top_inst.body:
        if not hasattr(member, 'name') or not member.name:
            continue
        
        name = str(member.name)
        kind_str = str(member.kind).replace("SymbolKind.", "").lower()

        # Determine structural category
        is_reg = 1 if ("variable" in kind_str or "reg" in name or "pipe_" in name or "shadow" in name) else 0
        is_ctrl = 1 if name in ["clk", "rst_n", "start", "valid", "valid_d1", "valid_d1_n", "valid_d2", "valid_d2_n", "control_fault", "fault_detected", "rollback"] else 0
        is_residue = 1 if ("mod3" in name or "rns" in name or "enc" in name) else 0
        is_pipeline_boundary = 1 if ("pipe_" in name or "reg_" in name or "shadow" in name) else 0
        bw = bitwidth_map.get(name, 1)

        # Pipeline stage assignment
        if name in ["a", "b", "c", "start", "rst_n", "clk"]:
            stage = 0
        elif name in ["reg_a", "reg_b", "reg_c", "valid_d1", "valid_d1_n", "product", "a_mod3", "b_mod3", "c_mod3", "ab_mod3_product", "u_enc_a", "u_enc_b", "u_enc_c", "reg_c_32"]:
            stage = 1
        elif name in ["pipe_product", "pipe_c", "pipe_ab_mod3", "pipe_c_mod3", "valid_d2", "valid_d2_n", "mac_result", "mac_result_32", "out_mod3", "rns_calc", "expected_mod3_reg", "expected_mod3", "u_enc_out", "u_ewma", "adaptive_threshold", "active_threshold", "ewma_mean", "ewma_mad", "ewma_warmup_done", "mod3_mismatch", "range_anomaly", "control_fault", "disagreement"]:
            stage = 2
        else:
            stage = 3

        G.add_node(name,
                   node_name=name,
                   kind=kind_str,
                   bit_width=bw,
                   is_register=is_reg,
                   is_control=is_ctrl,
                   is_residue=is_residue,
                   is_pipeline_boundary=is_pipeline_boundary,
                   pipeline_stage=stage)

    # Add edges
    for u, v in dataflow_edges:
        if u in G and v in G:
            G.add_edge(u, v)

    # Calculate graph-theoretic network metrics
    print(f"[+] Hardware Graph Constructed: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges")
    deg_cent = nx.degree_centrality(G)
    bet_cent = nx.betweenness_centrality(G)
    close_cent = nx.closeness_centrality(G)

    # Attach network metrics to nodes
    nodes_data = {}
    for node in G.nodes():
        G.nodes[node]["in_degree"] = G.in_degree(node)
        G.nodes[node]["out_degree"] = G.out_degree(node)
        G.nodes[node]["degree_centrality"] = float(deg_cent[node])
        G.nodes[node]["betweenness_centrality"] = float(bet_cent[node])
        G.nodes[node]["closeness_centrality"] = float(close_cent[node])
        nodes_data[node] = dict(G.nodes[node])

    # Export to JSON
    graph_json_path = output_dir / "rtl_hardware_graph.json"
    with open(graph_json_path, "w") as f:
        json.dump({
            "nodes": nodes_data,
            "edges": list(G.edges())
        }, f, indent=2)
    print(f"[+] Saved RTL Graph JSON to: {graph_json_path}")

    return G


if __name__ == "__main__":
    extract_rtl_graph()
