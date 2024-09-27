# Generate the Graph

We use a React wrapper for Sigma.js for the graph. 
For the layout algorithm, we useForceAtlas2 from the package graphology.

## Structure

```
-- graph
    |-- dev-app        app for experimenting with the graph and layout algorithm
    |-- functions      functions to create the graph and layout
```

### Generate the data

To generate the final graph data, run:

```bash
npm run generate
```
This generates the graph and runs the layout algorithm on it.
The result is saved to the folder `assets` of the dev-skill-tree app.

### Develop

If you want to experiment with the graph or the layout algorithm, you can do so in the [dev-app](./dev-app).
To start it, run:

```bash
npm run dev
```
