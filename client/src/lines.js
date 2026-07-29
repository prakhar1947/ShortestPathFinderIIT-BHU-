const Lines = (props) => {
const nodePositions = {
  1: { x: 630, y: 100 },
  2: { x: 724, y: 410 },
};
if (!props.dataPoint || !Array.isArray(props.dataPoint.path)) return null;
return(
    <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
        }}
      >
        {/* Draw lines between nodes in path */}
        {props.dataPoint.path.map((node, i) => {
          if (i === props.dataPoint.path.length - 1) return null;
          const from = nodePositions[props.dataPoint.path[i]];
          const to = nodePositions[props.dataPoint.path[i + 1]];
          return (
            <line
              key={i}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="red"
              strokeWidth="4"
            />
          );
        })}

        {/* Optional: Draw circles at nodes
        {path.map((node, i) => {
          const { x, y } = nodePositions[node];
          return <circle key={`circle-${i}`} cx={x} cy={y} r="6" fill="blue" />;
        })} */}
      </svg>
);
}

export default Lines;