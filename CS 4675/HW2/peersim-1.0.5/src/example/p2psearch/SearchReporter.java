package example.p2psearch;

import peersim.core.Control;

/** Prints the two measurements at end of run. */
public class SearchReporter implements Control {

	public SearchReporter(String prefix) { }

	public boolean execute() {
		int total = SearchStats.getTotalSearches();
		if (total == 0) { System.out.println("No searches run."); return false; }
		System.out.println("=== P2P Search Measurements ===");
		System.out.println("1. Success rate: " + SearchStats.getSuccessRate() + " (" + SearchStats.getSuccessCount() + "/" + total + ")");
		System.out.println("2. Avg hops: " + SearchStats.getAverageHops());
		return false;
	}
}
