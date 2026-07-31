import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../result.css";

const Result = () => {
  const location = useLocation();
  const navigate = useNavigate();

  if (!location.state) {
    return (
      <div className="result-page">
        <h1>No Route Selected</h1>

        <button
          className="back-btn"
          onClick={() => navigate("/")}
        >
          ← Back
        </button>
      </div>
    );
  }

  const { data } = location.state;

  const distance = data.totalDis;
  const path = data.path;
  const source = data.from;
  const destination = data.to;

  // Estimated Times
  const walkingTime = Math.ceil(distance / 80);
  const cycleTime = Math.ceil(distance / 200);
  const bikeTime = Math.ceil(distance / 500);

  return (
    <div className="result-page">

      <h1 className="title">
        🧭 IIT (BHU) Smart Navigator
      </h1>

      

      <div className="result-card">

        <h2>Route Details</h2>

        <div className="route-info">

          <div className="info-box">
            <span>📍 Source</span>
            <h3>{source}</h3>
          </div>

          <div className="info-box">
            <span>🎯 Destination</span>
            <h3>{destination}</h3>
          </div>

        </div>

        <div className="distance-card">
          <h2>Total Distance</h2>
          <h1>{distance} m</h1>
        </div>

        <div className="time-container">

          <div className="time-card walk">
            <h3>🚶 Walking</h3>
            <h2>{walkingTime} min</h2>
          </div>

          <div className="time-card cycle">
            <h3>🚲 Cycle</h3>
            <h2>{cycleTime} min</h2>
          </div>

          <div className="time-card bike">
            <h3>🏍 Bike</h3>
            <h2>{bikeTime} min</h2>
          </div>

        </div>

        <div className="path-card">

          <h2>Shortest Path</h2>

          <div className="path-display">

            {path.map((node, index) => (
              <span key={index}>
                {node}
                {index !== path.length - 1 && " ➜ "}
              </span>
            ))}

          </div>

        </div>

        <button
          className="back-btn"
          onClick={() => navigate("/")}
        >
          ← Back to Home
        </button>

      </div>

    </div>
  );
};

export default Result;