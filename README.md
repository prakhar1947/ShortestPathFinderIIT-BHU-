
# Shortest-Path-Finder

A brief description of what this project does and who it's for

**Shortest Path Finder** is a full-stack web application that solves the classic graph theory problem of finding the optimal route between two points. The application represents a real-world campus map as a weighted graph with nodes (locations) and computes the shortest path using Dijkstra's algorithm.

## Features

- displays the shortest distance between source and destination.
- displays shortest path one must take to reach destintion with minimum distance

## API Reference

#### Get shortest distance between node A and node B 

```http
  GET /shortd/<string:A>/<string:B>
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `source` | `string` | **Required**|
| `destination` | `string` |     **Required**      |




## Tech Stack

**Client:** React

**Server:** Flask, Python

# Pre install
```
Node > 20
python
pip
```

#Start server
```
cd server
pip install -r requirements.txt
python server.py
```
#Start Client
```
cd client
npm install
npm start
```
