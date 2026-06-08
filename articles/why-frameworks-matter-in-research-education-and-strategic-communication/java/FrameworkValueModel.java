import java.util.ArrayList;
import java.util.List;

class FrameworkValue {
    private final String frameworkName;
    private final String domain;
    private final int comprehension;
    private final int comparison;
    private final int retention;
    private final int action;
    private final int governance;
    private final int evidenceIntegrity;
    private final int audienceFit;
    private final int ethicalSafety;

    FrameworkValue(String frameworkName, String domain, int comprehension, int comparison, int retention, int action, int governance, int evidenceIntegrity, int audienceFit, int ethicalSafety) {
        this.frameworkName = frameworkName;
        this.domain = domain;
        this.comprehension = comprehension;
        this.comparison = comparison;
        this.retention = retention;
        this.action = action;
        this.governance = governance;
        this.evidenceIntegrity = evidenceIntegrity;
        this.audienceFit = audienceFit;
        this.ethicalSafety = ethicalSafety;
    }

    int totalScore() {
        return comprehension + comparison + retention + action + governance + evidenceIntegrity + audienceFit + ethicalSafety;
    }

    boolean productReady() {
        return totalScore() >= 32 && evidenceIntegrity >= 4 && ethicalSafety >= 4;
    }

    String summary() {
        return frameworkName + " | " + domain + " | value score: " + totalScore() + " | product ready: " + productReady();
    }
}

public class FrameworkValueModel {
    public static void main(String[] args) {
        List<FrameworkValue> frameworks = new ArrayList<>();

        frameworks.add(new FrameworkValue("Research Communication Framework", "Research", 5, 4, 4, 3, 4, 5, 4, 5));
        frameworks.add(new FrameworkValue("Educational Scaffolding", "Education", 5, 3, 5, 4, 3, 4, 5, 4));
        frameworks.add(new FrameworkValue("Message House", "Strategic Communication", 4, 4, 4, 5, 3, 4, 5, 3));

        for (FrameworkValue framework : frameworks) {
            System.out.println(framework.summary());
        }
    }
}
