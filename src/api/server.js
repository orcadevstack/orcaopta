const express = require("express");
const app = express();
app.use(express.json());

const { spawn } = require("child_process");

function callPython(module, func, records, res) {
    const py = spawn("python", ["src/api/python_bridge.py", module, func, JSON.stringify(records)]);

    py.stdout.on("data", data => res.json(JSON.parse(data.toString())));
    py.stderr.on("data", err => console.error(err.toString()));
}

app.post("/anomaly", (req, res) => {
    callPython("anomaly_detection", "predict", req.body.records, res);
});

app.post("/forecast", (req, res) => {
    callPython("forecasting", "predict", req.body.records, res);
});

app.post("/resource-opt", (req, res) => {
    callPython("resource_optimization", "predict", req.body.records, res);
});

app.post("/autoscale", (req, res) => {
    callPython("autoscaling", "predict", req.body.records, res);
});

app.listen(8000, () => console.log("Node API running on port 8000"));
