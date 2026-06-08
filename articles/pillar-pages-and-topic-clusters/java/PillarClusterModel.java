import java.util.ArrayList;
import java.util.List;

class PillarClusterArticle {
    private final String slug;
    private final String title;
    private final String cluster;
    private final String status;
    private final String role;
    private final int incomingLinks;
    private final int outgoingLinks;
    private final double metadataCompletion;

    PillarClusterArticle(String slug, String title, String cluster, String status, String role,
                         int incomingLinks, int outgoingLinks, double metadataCompletion) {
        this.slug = slug;
        this.title = title;
        this.cluster = cluster;
        this.status = status;
        this.role = role;
        this.incomingLinks = incomingLinks;
        this.outgoingLinks = outgoingLinks;
        this.metadataCompletion = metadataCompletion;
    }

    int linkDegree() {
        return incomingLinks + outgoingLinks;
    }

    boolean isReady() {
        return "published".equals(status) && metadataCompletion >= 0.85 && linkDegree() >= 2;
    }

    String summary() {
        return title + " | role: " + role + " | cluster: " + cluster
            + " | link degree: " + linkDegree()
            + " | metadata: " + metadataCompletion
            + " | ready: " + isReady();
    }
}

public class PillarClusterModel {
    public static void main(String[] args) {
        List<PillarClusterArticle> records = new ArrayList<>();

        records.add(new PillarClusterArticle("pillar-pages-and-topic-clusters", "Pillar Pages and Topic Clusters", "Knowledge Architecture", "published", "pillar", 4, 8, 1.0));
        records.add(new PillarClusterArticle("narrative-pathways-and-knowledge-architecture", "Narrative Pathways and Knowledge Architecture", "Knowledge Architecture", "published", "method", 2, 2, 1.0));
        records.add(new PillarClusterArticle("taxonomy-design-for-content-frameworks", "Taxonomy Design for Content Frameworks", "Knowledge Architecture", "planned", "method", 1, 1, 0.0));

        for (PillarClusterArticle record : records) {
            System.out.println(record.summary());
        }
    }
}
