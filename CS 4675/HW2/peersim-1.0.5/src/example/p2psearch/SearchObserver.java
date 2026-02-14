package example.p2psearch;

import peersim.config.*;
import peersim.core.*;
import peersim.edsim.EDSimulator;

/** Schedules random searches at time 0. */
public class SearchObserver implements Control {

	private final int pid;
	private final int numQueries;
	private static String[] keywords;

	public SearchObserver(String prefix) {
		pid = Configuration.getPid(prefix + ".protocol");
		numQueries = Configuration.getInt(prefix + ".numqueries", 20);
		if (keywords == null) {
			String name = Configuration.lookupPid(pid);
			String kw = Configuration.getString("protocol." + name + ".keywords", "jazz,piano,blues,rock,classical");
			keywords = kw.split(",");
			for (int i = 0; i < keywords.length; i++) keywords[i] = keywords[i].trim();
		}
	}

	public boolean execute() {
		SearchStats.reset();
		int n = Network.size();
		if (n == 0) return false;
		for (int i = 0; i < numQueries; i++) {
			Node node = Network.get(CommonState.r.nextInt(n));
			if (!node.isUp()) continue;
			String kw = keywords[CommonState.r.nextInt(keywords.length)];
			EDSimulator.add(0, new P2PSearchProtocol.SearchQuery(kw, node, 0), node, pid);
		}
		return false;
	}
}
