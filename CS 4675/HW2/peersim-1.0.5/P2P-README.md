# CS 4675 HW2 – P2P Search (PeerSim)

Toy P2P search: 5+ peers, 5 keyword "files" per peer, two measurements (success rate, average hops).

## What’s in this repo

- **Source:** `src/example/p2psearch/` — P2PSearchProtocol, SearchObserver, SearchStats, SearchReporter
- **Config:** `example/config-p2psearch.txt`
- **Jars:** `peersim-1.0.5.jar`, `jep-2.3.0.jar`, `djep-1.0.0.jar` (PeerSim + deps)

## How to run

1. Compile the P2P example:
   ```bash
   javac -cp "peersim-1.0.5.jar:jep-2.3.0.jar:djep-1.0.0.jar" -d build src/example/p2psearch/*.java
   ```

2. Run the simulator:
   ```bash
   java -cp "peersim-1.0.5.jar:jep-2.3.0.jar:djep-1.0.0.jar:build" peersim.Simulator example/config-p2psearch.txt
   ```

You should see "P2P Search Measurements" with success rate and average hops at the end.
