package example.p2psearch;

/** Two measurements: success rate and average hops. */
public class SearchStats {
	private static int ok, fail;
	private static long hops;

	public static synchronized void recordSuccess(int hopCount) { ok++; hops += hopCount; }
	public static synchronized void recordFailure() { fail++; }
	public static synchronized void reset() { ok = 0; fail = 0; hops = 0; }

	public static int getTotalSearches() { return ok + fail; }
	public static double getSuccessRate() { int t = ok + fail; return t == 0 ? 0 : (double) ok / t; }
	public static double getAverageHops() { return ok == 0 ? 0 : (double) hops / ok; }
	public static int getSuccessCount() { return ok; }
}
