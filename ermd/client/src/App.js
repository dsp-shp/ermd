import { useState, useEffect } from "react";
import ReactFlow, { Handle, Position } from "reactflow";
import defaultInput from "./defaultInput";

import "reactflow/dist/style.css";
const ELK = require("elkjs/lib/elk.bundled");

const nodeWidth = 400;
const nodeHeight = 200;
const elk = new ELK();

const TableNode = ({ data }) => {
  return (
    <div
      style={{
        border: "3px solid #777",
        borderRadius: 16,
        padding: 10,
        background: "white",
        fontSize: 14,
        zIndex: 0,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "left",
          alignItems: "center",
          gap: "8px",
          marginBottom: 12,
        }}
      >
        <div
          style={{
            padding: "0px 4px",
            borderRadius: "6px",
            border: "1.5px solid #222",
            fontSize: "12px",
            fontWeight: 600,
          }}
        >
          {data.type}
        </div>
        <div style={{ fontSize: "16px", fontWeight: 800 }}>{data.name}</div>
      </div>
      {data.desc && (
        <div
          style={{
            maxWidth: "350px",
            fontWeight: 400,
            fontStyle: "italic",
            color: "#444",
            marginBottom: "16px",
          }}
        >
          «{data.desc}»
        </div>
      )}
      <table
        style={{ width: "100%", padding: "0px", borderCollapse: "collapse" }}
      >
        <tbody>
          {console.log(data.fields)}
          {data.fields.map(
            ({ name, keys, data_type, desc, l_type, r_type }) => {
              const handleId = `${data.name}-${name}`;
              return (
                <tr
                  key={name}
                  style={{
                    position: "relative",
                    borderBottom:
                      name === data.fields[data.fields.length - 1].name
                        ? "none"
                        : "1px solid #ddd",
                  }}
                >
                  <td
                    style={{
                      margin: 0,
                      padding: 0,
                      width: 0,
                      position: "relative",
                    }}
                  >
                    <div
                      style={{
                        padding: "5px 0px 5px 10px",
                        display: "flex",
                        justifyContent: "end",
                        fontFamily: "Archivo, sans-serif",
                        fontSize: "16px",
                        textAlign: "right",
                        width: "18px",
                        height: "10px",
                        fontWeight: "1000",
                        position: "absolute",
                        visibility: l_type ? "visible" : "hidden",
                        left: "-45px",
                        top: "-8px",
                        background: "transparent",
                      }}
                    >
                      <p
                        style={{
                          margin: 0,
                          height: "16px",
                          padding: "5px 0px 5px 5px",
                          background: "white",
                        }}
                      >
                        {l_type}
                      </p>
                    </div>

                    <Handle
                      type="target"
                      position={Position.Left}
                      id={handleId}
                      style={{
                        top: "50%",
                        transform: "translateY(-50%)",
                        left: "-20px",
                        width: 0,
                        height: 10,
                        visibility: "hidden",
                        cursor: "grab",
                      }}
                    />
                  </td>
                  <td
                    style={{
                      padding: "2px 8px 2px 0px",
                    }}
                  >
                    <div
                      style={{
                        fontFamily: "Archivo Narrow",
                        color: "#888",
                      }}
                    >
                      {(data_type ? data_type : "UNKNOWN").toUpperCase()}
                    </div>
                  </td>
                  <td
                    style={{
                      padding: "2px 8px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "left",
                        alignItems: "center",
                        gap: "10px",
                      }}
                    >
                      {name}
                      {keys.map((key) => (
                        <div
                          key={key}
                          style={{
                            padding: "0px 4px",
                            borderRadius: "6px",
                            border: "1.5px solid",
                            borderColor: key === "PK" ? "#222" : "#888",
                            fontSize: "12px",
                            fontWeight: 600,
                            display: key ? "block" : "none",
                            color: key === "FK" ? "#666" : "#000",
                          }}
                        >
                          {key === "PK" ? "PK" : key === "FK" ? "FK" : ""}
                        </div>
                      ))}
                    </div>
                  </td>

                  <td
                    style={{
                      maxWidth: "150px",
                      padding: "2px 0px 2px 8px",
                      fontSize: "12px",
                      fontWeight: 600,
                      fontStyle: "italic",
                      color: "#444",
                    }}
                  >
                    {desc
                      ? desc.length > 55
                        ? desc.slice(0, 55) + "..."
                        : desc
                      : ""}
                  </td>
                  <td style={{ padding: 0, width: 0, position: "relative" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "start",
                        fontFamily: "Archivo, sans-serif",
                        width: "18px",
                        fontSize: "16px",
                        textAlign: "left",
                        fontWeight: "1000",
                        position: "absolute",
                        visibility: r_type ? "visible" : "hidden",
                        right: "-31px",
                        top: -4,
                        background: "transparent",
                      }}
                    >
                      <p
                        style={{
                          margin: 0,
                          height: "16px",
                          padding: "5px 5px 5px 4px",
                          background: "white",
                        }}
                      >
                        {r_type}
                      </p>
                    </div>
                    <Handle
                      type="source"
                      position={Position.Right}
                      id={handleId}
                      style={{
                        top: "50%",
                        transform: "translateY(-50%)",
                        right: "-15px",
                        width: 0,
                        height: 10,
                        visibility: "hidden",
                        cursor: "grab",
                      }}
                    />
                  </td>
                </tr>
              );
            },
          )}
        </tbody>
      </table>
    </div>
  );
};

function toFlow(schema) {
  const nodes = schema.entities.map((entity) => ({
    id: entity.name,
    type: "tableNode",
    data: {
      name: entity.name,
      desc: entity.desc,
      type: entity.type,
      fields: entity.fields,
      entities: schema.entities,
    },
    width: nodeWidth,
    height: nodeHeight,
  }));

  const edges = schema.relations.map((rel, idx) => {
    const [fromTable, fromColumn] = rel.from.split(".");
    const [toTable, toColumn] = rel.to.split(".");

    return {
      id: `e${idx}`,
      source: fromTable,
      sourceHandle: `${fromTable}-${fromColumn}`,
      target: toTable,
      targetHandle: `${toTable}-${toColumn}`,
      animated: true,
      style: { stroke: "#000", strokeWidth: 2 },
      label: rel.desc || "",
    };
  });

  return { nodes, edges };
}

async function elkLayout(nodes, edges) {
  const graph = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "org.eclipse.elk.mrtree",
      "elk.direction": "RIGHT",
      "elk.mrtree.direction": "RIGHT",
      "elk.spacing.nodeNode": "50",
      "elk.layered.spacing.nodeNodeBetweenLayers": "50",
      "elk.edgeRouting": "POLYLINE",
    },
    children: nodes.map((node) => ({
      id: node.id,
      width: node.width,
      height: node.height,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      type: "custom",
      sources: [edge.source],
      targets: [edge.target],
    })),
  };

  const layoutedGraph = await elk.layout(graph);
  console.log("All edges from ELK layout:", layoutedGraph.edges);

  // Проставляем позиции в узлы
  const layoutedEdgesWithBendPoints = layoutedGraph.edges.map((edge) => {
    const originalEdge = edges.find((e) => e.id === edge.id);
    const allBendPoints = (edge.sections || []).flatMap(
      (s) => s.bendPoints || [],
    );

    return {
      ...originalEdge,
      data: {
        ...originalEdge.data,
        bendPoints: allBendPoints,
      },
    };
  });

  // Обновляем позиции узлов
  const posNodes = nodes.map((node) => {
    const layoutNode = layoutedGraph.children.find((n) => n.id === node.id);
    return {
      ...node,
      position: { x: layoutNode.x, y: layoutNode.y },
    };
  });

  return { nodes: posNodes, edges: layoutedEdgesWithBendPoints };
}

const ERDiagramEditor = () => {
  const [inputText, setInputText] = useState(() => {
    return localStorage.getItem("inputText") || defaultInput;
  });
  const [elements, setElements] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const nodeTypes = { tableNode: TableNode };

  useEffect(() => {
    localStorage.setItem("inputText", inputText);
  }, [inputText]);

  useEffect(() => {
    if (inputText.trim() === "") {
      setElements({ nodes: [], edges: [] });
      return;
    }
    const timer = setTimeout(() => {
      setLoading(true);
      fetch("http://127.0.0.1:4765/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Ошибка сервера");
          return res.json();
        })
        .then(async (data) => {
          const { nodes, edges } = toFlow(data);

          const layouted = await elkLayout(nodes, edges);
          setElements(layouted);
          setError(null);
        })
        .catch((err) => {
          setError(err.message);
          setElements({ nodes: [], edges: [] });
        })
        .finally(() => setLoading(false));
    }, 500);

    return () => clearTimeout(timer);
  }, [inputText]);

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
      }}
    >
      <div
        style={{
          flexBasis: "33vw",
          maxWidth: "33vw",
          minWidth: "280px",
          background: "transparent",
          paddingTop: "2vh",
          paddingLeft: "2vh",
          paddingBottom: "2vh",
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
        }}
      >
        <textarea
          style={{
            background: "#fff",
            padding: "10px",
            border: "1.5px solid #666",
            borderRadius: "10px",
            width: "100%",
            height: "100%",
            fontSize: 16,
            resize: "none",
            boxSizing: "border-box",
          }}
          placeholder="Введите описание таблиц и связей..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
      </div>
      <div style={{ flex: 1 }}>
        {loading && <div>Загрузка...</div>}
        {error && <div style={{ color: "red" }}>Ошибка: {error}</div>}
        {console.log("Edges для ReactFlow:", elements.edges)}
        {!loading && !error && elements.nodes.length > 0 && (
          // <ArrowMarker />
          <ReactFlow
            nodes={elements.nodes}
            edges={elements.edges}
            nodeTypes={nodeTypes}
            fitView
            connectionLineType="default"
            nodesConnectable={false}
            edgesConnectable={false}
            onConnect={() => {}}
          >
            {/* <Background />*/}
            {/* <Controls />*/}
          </ReactFlow>
        )}
      </div>
    </div>
  );
};

export default ERDiagramEditor;
