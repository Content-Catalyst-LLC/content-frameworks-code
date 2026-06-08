import java.util.ArrayList;
import java.util.List;

class TaxonomyAssignmentRecord {
    private final String slug;
    private final String title;
    private final int primaryCategoryCount;
    private final int secondaryCategoryCount;
    private final int tagCount;
    private final double taxonomyMetadataCompletion;
    private final boolean published;

    TaxonomyAssignmentRecord(String slug, String title, int primaryCategoryCount, int secondaryCategoryCount,
                             int tagCount, double taxonomyMetadataCompletion, boolean published) {
        this.slug = slug;
        this.title = title;
        this.primaryCategoryCount = primaryCategoryCount;
        this.secondaryCategoryCount = secondaryCategoryCount;
        this.tagCount = tagCount;
        this.taxonomyMetadataCompletion = taxonomyMetadataCompletion;
        this.published = published;
    }

    boolean assignmentReady() {
        return primaryCategoryCount == 1 && tagCount <= 8 && taxonomyMetadataCompletion >= 0.85;
    }

    String reviewStatus() {
        if (!published) {
            return "planned";
        }
        return assignmentReady() ? "ready" : "review required";
    }

    String summary() {
        return title
            + " | primary categories: " + primaryCategoryCount
            + " | secondary categories: " + secondaryCategoryCount
            + " | tags: " + tagCount
            + " | taxonomy metadata: " + taxonomyMetadataCompletion
            + " | status: " + reviewStatus();
    }
}

public class TaxonomyDesignModel {
    public static void main(String[] args) {
        List<TaxonomyAssignmentRecord> records = new ArrayList<>();

        records.add(new TaxonomyAssignmentRecord(
            "taxonomy-design-for-content-frameworks",
            "Taxonomy Design for Content Frameworks",
            1,
            1,
            6,
            1.0,
            true
        ));

        records.add(new TaxonomyAssignmentRecord(
            "internal-linking-as-framework-infrastructure",
            "Internal Linking as Framework Infrastructure",
            1,
            1,
            4,
            0.875,
            false
        ));

        for (TaxonomyAssignmentRecord record : records) {
            System.out.println(record.summary());
        }
    }
}
