import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class LinkEdge {
    final String source;
    final String target;
    final String relationshipType;

    LinkEdge(String source, String target, String relationshipType) {
        this.source = source;
        this.target = target;
        this.relationshipType = relationshipType;
    }
}

public class InternalLinkGraphModel {
    public static void main(String[] args) {
        List<LinkEdge> links = new ArrayList<>();
        links.add(new LinkEdge("content-frameworks", "internal-linking-as-framework-infrastructure", "topic_cluster"));
        links.add(new LinkEdge("internal-linking-as-framework-infrastructure", "pillar-pages-and-topic-clusters", "prerequisite"));
        links.add(new LinkEdge("internal-linking-as-framework-infrastructure", "content-audits-and-framework-governance", "governance"));
        links.add(new LinkEdge("pillar-pages-and-topic-clusters", "internal-linking-as-framework-infrastructure", "method"));

        Map<String, Integer> incoming = new HashMap<>();
        Map<String, Integer> outgoing = new HashMap<>();

        for (LinkEdge edge : links) {
            outgoing.put(edge.source, outgoing.getOrDefault(edge.source, 0) + 1);
            incoming.put(edge.target, incoming.getOrDefault(edge.target, 0) + 1);
        }

        System.out.println("Internal Link Graph Model");
        for (String slug : outgoing.keySet()) {
            int outCount = outgoing.getOrDefault(slug, 0);
            int inCount = incoming.getOrDefault(slug, 0);
            System.out.println(slug + " | incoming=" + inCount + " | outgoing=" + outCount + " | total=" + (inCount + outCount));
        }
    }
}
