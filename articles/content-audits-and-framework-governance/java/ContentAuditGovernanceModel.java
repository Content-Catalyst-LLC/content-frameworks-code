import java.util.ArrayList;
import java.util.List;

class ContentAuditRecord {
    final String slug;
    final String status;
    final double metadataScore;
    final double linkScore;
    final double evidenceScore;
    final double freshnessScore;
    final double governanceScore;
    final double accessibilityScore;

    ContentAuditRecord(String slug, String status, double metadataScore, double linkScore, double evidenceScore, double freshnessScore, double governanceScore, double accessibilityScore) {
        this.slug = slug;
        this.status = status;
        this.metadataScore = metadataScore;
        this.linkScore = linkScore;
        this.evidenceScore = evidenceScore;
        this.freshnessScore = freshnessScore;
        this.governanceScore = governanceScore;
        this.accessibilityScore = accessibilityScore;
    }

    double frameworkHealthScore() {
        return 0.20 * metadataScore
            + 0.18 * linkScore
            + 0.20 * evidenceScore
            + 0.17 * freshnessScore
            + 0.15 * governanceScore
            + 0.10 * accessibilityScore;
    }

    boolean needsGovernanceReview() {
        return "published".equals(status) && frameworkHealthScore() < 0.78;
    }
}

public class ContentAuditGovernanceModel {
    public static void main(String[] args) {
        List<ContentAuditRecord> records = new ArrayList<>();

        records.add(new ContentAuditRecord("content-audits-and-framework-governance", "published", 1.0, 1.0, 1.0, 1.0, 1.0, 1.0));
        records.add(new ContentAuditRecord("what-makes-a-powerful-content-framework", "published", 0.5, 0.4, 0.8, 0.6, 0.5, 0.3));
        records.add(new ContentAuditRecord("editorial-metadata-and-content-systems", "planned", 0.0, 0.1, 0.0, 0.0, 0.25, 0.0));

        System.out.println("Content Audit Governance Model");
        System.out.println("--------------------------------");

        for (ContentAuditRecord record : records) {
            System.out.printf(
                "%s | status=%s | health=%.3f | review=%s%n",
                record.slug,
                record.status,
                record.frameworkHealthScore(),
                record.needsGovernanceReview()
            );
        }
    }
}
