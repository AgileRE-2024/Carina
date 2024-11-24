// Get initial data from elements
var data = JSON.parse(document.getElementById("journals-data").textContent);
var links = JSON.parse(document.getElementById("links-data").textContent);
var keyword = "{{ request.GET.keyword }}";

// Set larger dimensions for the visualization
var width = 1200,
    height = 800;

// Create tooltip div
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

var svg = d3.select("#mindmap")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

// Update force simulation with larger distances and stronger forces
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
        .id(d => d.id)
        .distance(150))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(60));

// Create nodes with the same structure
var nodes = data.map((journal, i) => ({
    id: journal.j.title,
    group: i,
    abstract: journal.j.abstract,
    author: journal.j.author,
    relevansi: journal.j.relevansi,
    pdf_link: journal.j.pdf_link,
    subNodes: [
        { id: `${journal.j.title}_goal`, label: "Goal", content: journal.j.goal, type: "goal" },
        { id: `${journal.j.title}_method`, label: "Method", content: journal.j.method, type: "method" },
        { id: `${journal.j.title}_keyword`, label: "Keyword", content: keyword, type: "keyword" },
    ],
}));

// Add sub-nodes to nodes array
nodes.forEach(node => {
    node.subNodes.forEach(subNode => {
        nodes.push({
            id: subNode.id,
            label: subNode.label,
            content: subNode.content,
            type: subNode.type,
            parent: node.id,
        });

        links.push({ source: node.id, target: subNode.id });
    });
});

// Add keyword node
var keywordNode = {
    id: keyword,
    group: nodes.length,
    abstract: "Keyword: " + keyword,
    author: "User",
    relevansi: 15,
    fx: width / 2,
    fy: height / 3,
};
nodes.push(keywordNode);

// Create links from keyword to other nodes
links.push(...nodes
    .map(node => (node.relevansi > 1 && node.id !== keywordNode.id)
        ? { source: keywordNode.id, target: node.id } : null)
    .filter(Boolean));

// Create link elements
var link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("data-type", d => d.type || 'default')
    .attr("stroke-width", d => d.type ? 2 : 1);

// Create node groups with improved text wrapping
var nodeGroup = svg.append("g")
    .attr("class", "nodes")
    .selectAll(".node-group")
    .data(nodes)
    .enter()
    .append("g")
    .attr("class", "node-group")
    .attr("transform", d => `translate(${d.x}, ${d.y})`)
    .on("mouseover", handleMouseOver)
    .on("mouseout", handleMouseOut)
    .on("click", handleClick);

// Add circles to nodes
nodeGroup.append("circle")
    .attr("class", "node-circle")
    .attr("r", d => (!d.id.includes("_") ? 40 : 20))
    .attr("fill", d => {
        if (d.id === keyword) return "#0B192C";
        if (d.type === "goal") return "#FF6500";
        if (d.type === "method") return "#1E3E62";
        if (d.type === "keyword") return "#999";
        return "#F2E5BF";
    });

// Add wrapped text only to main nodes
nodeGroup.each(function (d) {
    if (!d.id.includes("_") || d.id === keyword) {
        var nodeGroup = d3.select(this);
        var title = d.id;
        var networkIndex = title.indexOf("Network");
        if (networkIndex !== -1) {
            title = title.substring(0, networkIndex + "Network".length);
        }

        var words = title.split(/\s+/);
        var text = nodeGroup.append("text")
            .attr("class", d.id === keyword ? "node-label keyword" : "node-label title")
            .attr("text-anchor", "middle")
            .attr("dy", ".35em");

        var fontSize = Math.min(12, 80 / Math.max(...words.map(w => w.length)));
        text.style("font-size", fontSize + "px");

        if (words.length > 1) {
            var circleRadius = !d.id.includes("_") ? 40 : 20;
            var maxWidth = circleRadius * 1.8;
            var lineHeight = fontSize * 1.2;
            var maxLines = Math.floor((circleRadius * 1.8) / lineHeight);
            var lines = [];
            var line = [];
            var tspan = text.append("tspan")
                .attr("x", 0)
                .attr("dy", (-lineHeight * (Math.min(words.length, maxLines) - 1) / 2) + "px");

            words.forEach(word => {
                var testLine = line.concat([word]);
                if (testLine.join(" ").length * fontSize > 70) {
                    if (lines.length < maxLines - 1) {
                        lines.push(line);
                        line = [word];
                    } else {
                        line.push("...");
                        lines.push(line);
                        return;
                    }
                } else {
                    line = testLine;
                }
            });
            if (line.length > 0 && lines.length < maxLines) {
                lines.push(line);
            }

            lines.forEach((line, i) => {
                tspan = text.append("tspan")
                    .attr("x", 0)
                    .attr("dy", i === 0 ? "0" : lineHeight + "px")
                    .text(line.join(" "));
            });
        } else {
            text.text(d.id);
        }
    }
});

// Event handlers
function handleMouseOver(event, d) {
    highlightConnections(d);
    tooltip.transition().duration(200).style("opacity", 1);
    tooltip
        .html(
            `<div class="tooltip-title">${d.id.includes("_") ? d.label : d.id}</div>
    <div class="tooltip-content">${d.content ? d.content.substring(0, 150) + "..." : ""}</div>
    ${d.author && !d.id.includes("_") ? `<div class="tooltip-author">By: ${d.author}</div>` : ""}`
        )
        .style("left", event.pageX + 10 + "px")
        .style("top", event.pageY - 10 + "px");
}

function handleMouseOut() {
    removeHighlights();
    tooltip.transition().duration(500).style("opacity", 0);
}

function handleClick(event, d) {
    if (d.pdf_link) {
        window.open(d.pdf_link, "_blank");
    } else if (!d.id.includes("_")) {
        alert("Tidak ada link tersedia untuk jurnal ini.");
    }
}

// Simulation tick function
function ticked() {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    nodeGroup.attr("transform", d => {
        d.x = Math.max(40, Math.min(width - 40, d.x));
        d.y = Math.max(40, Math.min(height - 40, d.y));
        return `translate(${d.x}, ${d.y})`;
    });
}

// Function to highlight connected nodes and links
function highlightConnections(d) {
    var connectedNodeIds = new Set([d.id]);
    links.forEach(link => {
        if (link.source.id === d.id || link.target.id === d.id) {
            connectedNodeIds.add(link.source.id);
            connectedNodeIds.add(link.target.id);
        }
    });

    nodeGroup.classed("highlighted", n => connectedNodeIds.has(n.id))
        .classed("dimmed", n => !connectedNodeIds.has(n.id));
    link.classed("highlighted", l => l.source.id === d.id || l.target.id === d.id);
}

// Function to remove highlights
function removeHighlights() {
    nodeGroup.classed("highlighted", false).classed("dimmed", false);
    link.classed("highlighted", false);
}

// Start simulation
simulation.nodes(nodes).on("tick", ticked);
simulation.force("link").links(links);

// Di bagian script setelah deklarasi nodes
const showKeyword = document.getElementById('show-keyword');
const showMethod = document.getElementById('show-method');
const showGoal = document.getElementById('show-goal');

function updateVisibility() {
    // Update node visibility
    d3.selectAll('.node-group').each(function (d) {
        if (d.id.includes('_keyword')) {
            d3.select(this).style('display', showKeyword.checked ? 'block' : 'none');
        } else if (d.id.includes('_method')) {
            d3.select(this).style('display', showMethod.checked ? 'block' : 'none');
        } else if (d.id.includes('_goal')) {
            d3.select(this).style('display', showGoal.checked ? 'block' : 'none');
        }
    });

    // Update link visibility
    d3.selectAll('.links line').each(function (d) {
        const sourceId = d.source.id || d.source;
        const targetId = d.target.id || d.target;
        let shouldShow = true;

        if (d.type === 'method') {
            shouldShow = showMethod.checked;
        } else if (d.type === 'goal') {
            shouldShow = showGoal.checked;
        }

        d3.select(this).style('display', shouldShow ? 'block' : 'none');
    });
}
var link = svg
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("class", function (d) {
        return d.type ? `link-${d.type}` : "link-default";
    })
    .attr("stroke-width", function (d) {
        return d.type ? 2 : 1;
    })
    .attr("stroke", function (d) {
        if (d.type === 'method') return "#1E3E62";
        if (d.type === 'goal') return "#FF6500";
        return "#999";
    })
    .attr("stroke-dasharray", function (d) {
        return d.type ? "5,5" : "none";
    });

// Add event listeners
showKeyword.addEventListener('change', updateVisibility);
showMethod.addEventListener('change', updateVisibility);
showGoal.addEventListener('change', updateVisibility);

