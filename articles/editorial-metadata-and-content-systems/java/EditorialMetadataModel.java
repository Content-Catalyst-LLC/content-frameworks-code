import java.util.ArrayList;
import java.util.List;

class EditorialMetadataRecord {
    final String slug;
    final String title;
    final String status;
    final String articleType;
    final int completedFields;
    final int requiredFields;
    final boolean repositoryPathAligned;
    final boolean footerNavigationValid;

    EditorialMetadataRecord(String slug, String title, String status, String articleType, int completedFields, int requiredFields, boolean repositoryPathAligned, boolean footerNavigationValid) {
        this.slug = slug;
        this.title = title;
        this.status = status;
        this.articleType = articleType;
        this.completedFields = completedFields;
        this.requiredFields = requiredFields;
        this.repositoryPathAligned = repositoryPathAligned;
        this.footerNavigationValid = footerNavigationValid;
    }

    double completionRate() {
        return requiredFields == 0 ? 1.0 : (double) completedFields / requiredFields;
    }

    boolean readyForPublication() {
        return completionRate() >= 0.90 && repositoryPathAligned && footerNavigationValid;
    }
}

public class EditorialMetadataModel {
    public static void main(String[] args) {
        List<EditorialMetadataRecord> records = new ArrayList<>();

        records.add(new EditorialMetadataRecord("editorial-metadata-and-content-systems", "Editorial Metadata and Content Systems", "published", "technical", 25, 25, true, true));
        records.add(new EditorialMetadataRecord("taxonomy-design-for-content-frameworks", "Taxonomy Design for Content Frameworks", "planned", "methodological", 16, 25, true, true));
        records.add(new EditorialMetadataRecord("frameworks-for-digital-knowledge-systems", "Frameworks for Digital Knowledge Systems", "published", "technical", 22, 25, true, true));

        System.out.println("Editorial Metadata Model");
        System.out.println("------------------------");

        for (EditorialMetadataRecord record : records) {
            System.out.printf(
                "%s | status=%s | type=%s | completion=%.3f | ready=%s%n",
                record.slug,
                record.status,
                record.articleType,
                record.completionRate(),
                record.readyForPublication()
            );
        }
    }
}
