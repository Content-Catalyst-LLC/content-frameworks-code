import java.util.ArrayList;
import java.util.List;

class PathwayArticle {
    private final String slug;
    private final String title;
    private final String articleRole;
    private final String pathwayRole;
    private final String readerState;
    private final int incomingLinks;
    private final int outgoingLinks;
    private final double metadataCompletion;
    private final boolean orientationReady;
    private final boolean bridgeReady;

    PathwayArticle(String slug, String title, String articleRole, String pathwayRole, String readerState,
                   int incomingLinks, int outgoingLinks, double metadataCompletion,
                   boolean orientationReady, boolean bridgeReady) {
        this.slug = slug;
        this.title = title;
        this.articleRole = articleRole;
        this.pathwayRole = pathwayRole;
        this.readerState = readerState;
        this.incomingLinks = incomingLinks;
        this.outgoingLinks = outgoingLinks;
        this.metadataCompletion = metadataCompletion;
        this.orientationReady = orientationReady;
        this.bridgeReady = bridgeReady;
    }

    int linkDegree() {
        return incomingLinks + outgoingLinks;
    }

    boolean isReady() {
        return metadataCompletion >= 0.85 && linkDegree() >= 2 && orientationReady && bridgeReady;
    }

    String summary() {
        return title + " | role: " + articleRole + " | pathway role: " + pathwayRole
            + " | reader state: " + readerState
            + " | link degree: " + linkDegree()
            + " | metadata: " + metadataCompletion
            + " | ready: " + isReady();
    }
}

public class NarrativePathwayModel {
    public static void main(String[] args) {
        List<PathwayArticle> records = new ArrayList<>();

        records.add(new PathwayArticle("pillar-pages-and-topic-clusters", "Pillar Pages and Topic Clusters", "pillar", "architecture", "beginner", 3, 5, 1.0, true, true));
        records.add(new PathwayArticle("narrative-pathways-and-knowledge-architecture", "Narrative Pathways and Knowledge Architecture", "method", "pathway_design", "practitioner", 4, 6, 1.0, true, true));
        records.add(new PathwayArticle("taxonomy-design-for-content-frameworks", "Taxonomy Design for Content Frameworks", "method", "taxonomy_design", "editor", 1, 1, 0.0, false, false));

        for (PathwayArticle record : records) {
            System.out.println(record.summary());
        }
    }
}
