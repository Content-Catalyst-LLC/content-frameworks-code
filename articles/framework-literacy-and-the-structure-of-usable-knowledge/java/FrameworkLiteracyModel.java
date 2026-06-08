import java.util.ArrayList;
import java.util.List;

class FrameworkLiteracyRecord {
    private final String name;
    private final String domain;
    private final int assumptionAwareness;
    private final int blindSpotRecognition;
    private final int boundaryClarity;
    private final int useConditionClarity;
    private final int evidenceAlignment;
    private final int ethicalSafety;
    private final int audienceFit;
    private final int domainFit;
    private final int adaptability;
    private final int governanceReadiness;

    FrameworkLiteracyRecord(String name, String domain, int assumptionAwareness, int blindSpotRecognition,
                            int boundaryClarity, int useConditionClarity, int evidenceAlignment,
                            int ethicalSafety, int audienceFit, int domainFit, int adaptability,
                            int governanceReadiness) {
        this.name = name;
        this.domain = domain;
        this.assumptionAwareness = assumptionAwareness;
        this.blindSpotRecognition = blindSpotRecognition;
        this.boundaryClarity = boundaryClarity;
        this.useConditionClarity = useConditionClarity;
        this.evidenceAlignment = evidenceAlignment;
        this.ethicalSafety = ethicalSafety;
        this.audienceFit = audienceFit;
        this.domainFit = domainFit;
        this.adaptability = adaptability;
        this.governanceReadiness = governanceReadiness;
    }

    int literacyScore() {
        return assumptionAwareness + blindSpotRecognition + boundaryClarity + useConditionClarity
            + evidenceAlignment + ethicalSafety + audienceFit + domainFit + adaptability + governanceReadiness;
    }

    boolean readyForUse() {
        return literacyScore() >= 40
            && blindSpotRecognition >= 4
            && useConditionClarity >= 4
            && evidenceAlignment >= 4
            && ethicalSafety >= 4
            && governanceReadiness >= 4;
    }

    String summary() {
        return name + " | " + domain + " | literacy score: " + literacyScore()
            + " | ready for framework-literate use: " + readyForUse();
    }
}

public class FrameworkLiteracyModel {
    public static void main(String[] args) {
        List<FrameworkLiteracyRecord> records = new ArrayList<>();

        records.add(new FrameworkLiteracyRecord("Research Communication Framework", "Research", 5, 5, 5, 5, 5, 5, 4, 5, 4, 5));
        records.add(new FrameworkLiteracyRecord("Message House", "Strategic Communication", 4, 3, 4, 3, 4, 3, 5, 4, 3, 3));
        records.add(new FrameworkLiteracyRecord("Article Map", "Digital Publishing", 5, 4, 5, 5, 4, 5, 4, 5, 5, 5));

        for (FrameworkLiteracyRecord record : records) {
            System.out.println(record.summary());
        }
    }
}
