import java.util.ArrayList;
import java.util.List;

class FrameworkQuality {
    private final String name;
    private final String domain;
    private final int clarity;
    private final int coherence;
    private final int transferability;
    private final int adaptability;
    private final int explanatoryDepth;
    private final int domainFit;
    private final int audienceFit;
    private final int evidenceAlignment;
    private final int ethicalSafety;
    private final int governability;

    FrameworkQuality(String name, String domain, int clarity, int coherence, int transferability, int adaptability,
                     int explanatoryDepth, int domainFit, int audienceFit, int evidenceAlignment,
                     int ethicalSafety, int governability) {
        this.name = name;
        this.domain = domain;
        this.clarity = clarity;
        this.coherence = coherence;
        this.transferability = transferability;
        this.adaptability = adaptability;
        this.explanatoryDepth = explanatoryDepth;
        this.domainFit = domainFit;
        this.audienceFit = audienceFit;
        this.evidenceAlignment = evidenceAlignment;
        this.ethicalSafety = ethicalSafety;
        this.governability = governability;
    }

    int qualityScore() {
        return clarity + coherence + transferability + adaptability + explanatoryDepth
            + domainFit + audienceFit + evidenceAlignment + ethicalSafety + governability;
    }

    double readinessScore() {
        return (evidenceAlignment + ethicalSafety + governability) / 3.0;
    }

    String maturityLevel() {
        int score = qualityScore();
        if (score >= 44 && readinessScore() >= 4.0) {
            return "product-ready";
        } else if (score >= 36) {
            return "strong but review";
        } else if (score >= 28) {
            return "developing";
        }
        return "not ready";
    }

    String summary() {
        return name + " | " + domain + " | quality score: " + qualityScore()
            + " | readiness: " + String.format("%.2f", readinessScore())
            + " | maturity: " + maturityLevel();
    }
}

public class FrameworkQualityModel {
    public static void main(String[] args) {
        List<FrameworkQuality> frameworks = new ArrayList<>();

        frameworks.add(new FrameworkQuality("Research Communication Framework", "Research", 5, 5, 4, 4, 5, 5, 4, 5, 5, 4));
        frameworks.add(new FrameworkQuality("Message House", "Strategic Communication", 4, 4, 4, 3, 3, 4, 5, 4, 3, 3));
        frameworks.add(new FrameworkQuality("Article Map", "Digital Publishing", 5, 5, 5, 4, 4, 5, 4, 4, 5, 5));

        for (FrameworkQuality framework : frameworks) {
            System.out.println(framework.summary());
        }
    }
}
