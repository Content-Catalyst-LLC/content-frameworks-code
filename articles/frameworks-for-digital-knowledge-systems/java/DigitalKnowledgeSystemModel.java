import java.util.ArrayList;
import java.util.List;

class DigitalKnowledgeRecord {
    private final String slug;
    private final String title;
    private final String cluster;
    private final String contentType;
    private final String articleRole;
    private final double metadataCompletion;
    private final int linkDegree;
    private final double repositoryReadiness;
    private final boolean taxonomyReady;
    private final boolean reviewCurrent;

    DigitalKnowledgeRecord(String slug, String title, String cluster, String contentType, String articleRole,
                           double metadataCompletion, int linkDegree, double repositoryReadiness,
                           boolean taxonomyReady, boolean reviewCurrent) {
        this.slug = slug;
        this.title = title;
        this.cluster = cluster;
        this.contentType = contentType;
        this.articleRole = articleRole;
        this.metadataCompletion = metadataCompletion;
        this.linkDegree = linkDegree;
        this.repositoryReadiness = repositoryReadiness;
        this.taxonomyReady = taxonomyReady;
        this.reviewCurrent = reviewCurrent;
    }

    double systemHealthScore() {
        double linkScore = Math.min(linkDegree / 4.0, 1.0);
        double taxonomyScore = taxonomyReady ? 1.0 : 0.0;
        double reviewScore = reviewCurrent ? 1.0 : 0.0;
        return (metadataCompletion + linkScore + repositoryReadiness + taxonomyScore + reviewScore) / 5.0;
    }

    boolean requiresReview() {
        return systemHealthScore() < 0.75 || metadataCompletion < 0.85 || linkDegree < 2 || !taxonomyReady;
    }

    String summary() {
        return title + " | cluster: " + cluster
            + " | type: " + contentType
            + " | role: " + articleRole
            + " | health: " + String.format("%.3f", systemHealthScore())
            + " | requires review: " + requiresReview();
    }
}

public class DigitalKnowledgeSystemModel {
    public static void main(String[] args) {
        List<DigitalKnowledgeRecord> records = new ArrayList<>();

        records.add(new DigitalKnowledgeRecord(
            "frameworks-for-digital-knowledge-systems",
            "Frameworks for Digital Knowledge Systems",
            "Knowledge Architecture",
            "article",
            "technical",
            1.0,
            8,
            1.0,
            true,
            true
        ));

        records.add(new DigitalKnowledgeRecord(
            "taxonomy-design-for-content-frameworks",
            "Taxonomy Design for Content Frameworks",
            "Knowledge Architecture",
            "article",
            "method",
            0.0,
            1,
            0.0,
            true,
            false
        ));

        for (DigitalKnowledgeRecord record : records) {
            System.out.println(record.summary());
        }
    }
}
