from flask import Blueprint, render_template_string, jsonify, session, redirect, url_for
from utils import get_graph_nodes, get_graph_edges

graph_view_bp = Blueprint('graph_view', __name__)

GRAPH_VIEW_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB Graph View</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            overflow: hidden; /* Prevent scrollbars from graph */
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
        }
        .graph-controls {
            padding: 1rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            text-align: center;
        }
        .btn-back {
            background-color: #9ca3af;
            color: #ffffff;
            border: 1px solid #9ca3af;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-back:hover {
            background-color: #6b7280;
        }
        #graph-container {
            width: 90%;
            height: 80%;
            border: 1px solid #e5e7eb;
            border-radius: 0.75rem;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }
        .node circle {
            stroke: #fff;
            stroke-width: 1.5px;
        }
        .node text {
            font-size: 10px;
            fill: #555;
            pointer-events: none; /* Make text non-interactive for easier node dragging */
            text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff; /* Outline for readability */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="graph-controls">
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Database Network Graph</h1>
            <a href="{{ url_for('dashboard.dashboard') }}" class="btn-back">Back to Dashboard</a>
        </div>
        <div id="graph-container"></div>
    </div>

    <script>
        const width = document.getElementById('graph-container').offsetWidth;
        const height = document.getElementById('graph-container').offsetHeight;

        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", [0, 0, width, height])
            .call(d3.zoom().on("zoom", function(event) {
                g.attr("transform", event.transform);
            }))
            .append("g"); // Group for zooming/panning

        const g = svg.append("g"); // Group for nodes and links

        // Define color scale for node types
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        async function fetchData() {
            try {
                const nodesResponse = await fetch('/graph_data/nodes');
                const nodesData = await nodesResponse.json();
                const edgesResponse = await fetch('/graph_data/edges');
                const edgesData = await edgesResponse.json();

                return { nodes: nodesData.nodes, links: edgesData.edges };
            } catch (error) {
                console.error('Error fetching graph data:', error);
                return { nodes: [], links: [] };
            }
        }

        async function renderGraph() {
            const graph = await fetchData();

            // Create a map for quick node lookup by ID
            const nodeMap = new Map(graph.nodes.map(d => [d.id, d]));

            // Ensure links refer to existing node objects
            graph.links.forEach(link => {
                link.source = nodeMap.get(link.source);
                link.target = nodeMap.get(link.target);
            });

            // Filter out invalid links (where source or target node doesn't exist)
            graph.links = graph.links.filter(link => link.source && link.target);

            const simulation  = d3.forceSimulation(graph.nodes)
                .force("link", d3.forceLink(graph.links)
                    .id(d => d.id)
                    .distance(120)
                    .strength(0.1))
                .force("charge", d3.forceManyBody()
                    .strength(-400)
                    .distanceMax(500))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(20))
                .force("x", d3.forceX(width / 2).strength(0.05))
                .force("y", d3.forceY(height / 2).strength(0.05));

            const link = g.append("g")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .selectAll("line")
                .data(graph.links)
                .join("line")
                .attr("stroke-width", d => Math.sqrt(d.value || 1)); // Use a 'value' if available, otherwise 1

            const node = g.append("g")
                .attr("stroke", "#fff")
                .attr("stroke-width", 1.5)
                .selectAll("circle")
                .data(graph.nodes)
                .join("circle")
                .attr("r", 8)
                .attr("fill", d => color(d.type)) // Color nodes by type
                .call(drag(simulation));

            // Add text labels for nodes
            const labels = g.append("g")
                .selectAll("text")
                .data(graph.nodes)
                .join("text")
                .attr("text-anchor", "middle")
                .attr("dy", "0.35em")
                .style("font-size", "10px")
                .style("fill", "#333")
                .text(d => d.name);


            // Add titles for tooltips
            node.append("title")
                .text(d => `ID: ${d.id}\nName: ${d.name}\nType: ${d.type}`);

            simulation.on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);

                labels
                    .attr("x", d => d.x)
                    .attr("y", d => d.y + 15); // Offset text below node
            });
        }

        const drag = simulation => {
            function dragstarted(event) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }

            function dragged(event) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }

            function dragended(event) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        };

        renderGraph();
    </script>
</body>
</html>
'''

@graph_view_bp.route('/graph_view')
def graph_view():
    """
    Renders the HTML page for the D3.js force-directed graph.
    Requires DM role to access.
    """
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))
    return render_template_string(GRAPH_VIEW_HTML)

@graph_view_bp.route('/graph_data/nodes')
def graph_data_nodes():
    """
    API endpoint to provide graph node data.
    """
    if 'is_dm' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    nodes = get_graph_nodes()
    return jsonify({"nodes": nodes})

@graph_view_bp.route('/graph_data/edges')
def graph_data_edges():
    """
    API endpoint to provide graph edge data.
    """
    if 'is_dm' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    edges = get_graph_edges()
    return jsonify({"edges": edges})
