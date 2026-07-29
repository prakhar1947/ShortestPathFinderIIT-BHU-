import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../home.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:5010";

const Home = () => {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [nodesLoading, setNodesLoading] = useState(true);
  const [nodes, setNodes] = useState({});
  const [fetchError, setFetchError] = useState(null);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const response = await fetch(`${API_BASE}/nodes`);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();
        setNodes(data);
        setFetchError(null);
      } catch (err) {
        console.error("Fetch Error:", err);
        setFetchError(
          "Could not connect to the server. Please start the Flask backend on port 5010."
        );
      } finally {
        setNodesLoading(false);
      }
    };

    fetchNodes();
  }, []);

  const sortedEntries = Object.entries(nodes).sort((a, b) =>
    a[1].localeCompare(b[1])
  );

  const onsubmitHandler = async (e) => {
    e.preventDefault();

    const source = e.target.source.value;
    const destination = e.target.destination.value;

    if (!source || !destination) {
      setFormError("Please select both a source and a destination.");
      return;
    }
    if (source === destination) {
      setFormError("Source and destination cannot be the same.");
      return;
    }
    setFormError("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/shortd/${source}/${destination}`
      );

      const jsonData = await response.json();

      navigate("/result", {
        state: {
          data: jsonData,
        },
      });
    } catch (err) {
      console.error(err);
      setFormError("Failed to fetch route. Is the server running?");
    }

    setLoading(false);
  };

  return (
    <div className="mainContainer">

      <div className="projectHeader">
        IIT (BHU) Smart Navigator
      </div>

      <div className="Maps">
        <img
          className="satMap"
          src="/Maps/campus.jpg"
          alt="Campus"
        />
      </div>

      <div className="formInput">

        {fetchError && (
          <div className="errorBanner">
            ⚠️ {fetchError}
          </div>
        )}

        {nodesLoading ? (
          <div className="loadingMsg">⏳ Loading campus locations...</div>
        ) : (
          <form onSubmit={onsubmitHandler} className="formGroup">

            <div className="sourceForm">
              <label>Source</label>
              <select
                name="source"
                defaultValue=""
                className="sourceInput"
                disabled={!!fetchError}
              >
                <option value="">Select Source</option>
                {sortedEntries.map(([slug, name]) => (
                  <option key={slug} value={slug}>
                    {name}
                  </option>
                ))}
              </select>
            </div>

            <div className="destinationForm">
              <label>Destination</label>
              <select
                name="destination"
                defaultValue=""
                className="destinationInput"
                disabled={!!fetchError}
              >
                <option value="">Select Destination</option>
                {sortedEntries.map(([slug, name]) => (
                  <option key={slug} value={slug}>
                    {name}
                  </option>
                ))}
              </select>
            </div>

            {formError && (
              <div className="formErrorMsg">⚠️ {formError}</div>
            )}

            <button className="formButton" disabled={loading || !!fetchError}>
              {loading ? "Finding Route..." : "Find Shortest Route"}
            </button>

          </form>
        )}

      </div>

    </div>
  );
};

export default Home;