import java.util.ArrayList;
import java.util.List;

class StructureTypeRecord {
    private final String name;
    private final String declaredType;
    private final String observedType;
    private final double governanceCompletion;
    private final String riskSeverity;

    StructureTypeRecord(String name, String declaredType, String observedType, double governanceCompletion, String riskSeverity) {
        this.name = name;
        this.declaredType = declaredType;
        this.observedType = observedType;
        this.governanceCompletion = governanceCompletion;
        this.riskSeverity = riskSeverity;
    }

    boolean typeMatches() {
        return declaredType.equals(observedType);
    }

    boolean governanceReady() {
        return governanceCompletion >= 0.85 && !"high".equals(riskSeverity);
    }

    String reviewStatus() {
        if (!typeMatches()) {
            return "type mismatch review required";
        }
        if (!governanceReady()) {
            return "governance review required";
        }
        return "ready for managed use";
    }

    String summary() {
        return name + " | declared: " + declaredType + " | observed: " + observedType
            + " | governance: " + governanceCompletion + " | status: " + reviewStatus();
    }
}

public class StructureTypeModel {
    public static void main(String[] args) {
        List<StructureTypeRecord> records = new ArrayList<>();

        records.add(new StructureTypeRecord("Content Framework Article Map", "framework", "framework", 1.0, "low"));
        records.add(new StructureTypeRecord("Content Audit Sheet", "template", "method", 0.71, "medium"));
        records.add(new StructureTypeRecord("AI Outline Prompt", "template", "framework", 0.0, "high"));

        for (StructureTypeRecord record : records) {
            System.out.println(record.summary());
        }
    }
}
