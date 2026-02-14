package example.p2psearch;

import peersim.config.*;
import peersim.core.*;
import peersim.edsim.EDProtocol;
import peersim.transport.Transport;
import peersim.config.FastConfig;
import java.util.*;

/** Each peer has 5 "files" (keywords). Forwards search to a neighbor or replies if found. */
public class P2PSearchProtocol implements EDProtocol {

	private static String[] keywordPool;
	private static int ttl = 10;
	private static final int FILES = 5;
	private List<String> files = new ArrayList<String>();

	public P2PSearchProtocol(String prefix) {
		if (keywordPool == null) {
			String kw = Configuration.getString(prefix + ".keywords", "jazz,piano,blues,rock,classical");
			keywordPool = kw.split(",");
			for (int i = 0; i < keywordPool.length; i++) keywordPool[i] = keywordPool[i].trim();
			ttl = Configuration.getInt(prefix + ".ttl", 10);
		}
	}

	public Object clone() {
		try {
			P2PSearchProtocol p = (P2PSearchProtocol) super.clone();
			p.files = new ArrayList<String>();
			for (int i = 0; i < FILES && keywordPool.length > 0; i++)
				p.files.add(keywordPool[CommonState.r.nextInt(keywordPool.length)]);
			return p;
		} catch (CloneNotSupportedException e) { throw new RuntimeException(e); }
	}

	public void processEvent(Node node, int pid, Object event) {
		if (event instanceof SearchResponse) {
			SearchStats.recordSuccess(((SearchResponse) event).hopCount);
			return;
		}
		if (!(event instanceof SearchQuery)) return;
		SearchQuery q = (SearchQuery) event;

		if (files.contains(q.keyword)) {
			Transport tr = (Transport) node.getProtocol(FastConfig.getTransport(pid));
			tr.send(node, q.origin, new SearchResponse(q.hopCount + 1), pid);
			return;
		}
		if (q.hopCount >= ttl) { SearchStats.recordFailure(); return; }

		Linkable link = (Linkable) node.getProtocol(FastConfig.getLinkable(pid));
		if (link.degree() == 0) { SearchStats.recordFailure(); return; }
		Node neighbor = link.getNeighbor(CommonState.r.nextInt(link.degree()));
		if (!neighbor.isUp()) { SearchStats.recordFailure(); return; }

		Transport tr = (Transport) node.getProtocol(FastConfig.getTransport(pid));
		tr.send(node, neighbor, new SearchQuery(q.keyword, q.origin, q.hopCount + 1), pid);
	}

	public static class SearchQuery {
		final String keyword;
		final Node origin;
		final int hopCount;
		SearchQuery(String keyword, Node origin, int hopCount) {
			this.keyword = keyword; this.origin = origin; this.hopCount = hopCount;
		}
	}

	public static class SearchResponse {
		final int hopCount;
		SearchResponse(int hopCount) { this.hopCount = hopCount; }
	}
}
