import java.util.ArrayList;
import java.util.List;

class HistoricalFrameworkRecord {
    private final String name;
    private final String lineage;
    private final String domain;
    private final boolean transferredAcrossDomains;
    private final double governanceScore;
    private final String riskSeverity;

    HistoricalFrameworkRecord(String name, String lineage, String domain, boolean transferredAcrossDomains, double governanceScore, String riskSeverity) {
        this.name = name;
        this.lineage = lineage;
        this.domain = domain;
        this.transferredAcrossDomains = transferredAcrossDomains;
        this.governanceScore = governanceScore;
        this.riskSeverity = riskSeverity;
    }

    boolean requiresReview() {
        return governanceScore < 0.80 || "high".equals(riskSeverity) || ("medium".equals(riskSeverity) && transferredAcrossDomains);
    }

    String summary() {
        return name + " | lineage: " + lineage + " | domain: " + domain
            + " | governance: " + governanceScore + " | requires review: " + requiresReview();
    }
}

public class FrameworkHistoryModel {
    public static void main(String[] args) {
        List<HistoricalFrameworkRecord> records = new ArrayList<>();

        records.add(new HistoricalFrameworkRecord("Classical Rhetorical Arrangement", "rhetorical", "Communication", true, 1.0, "medium"));
        records.add(new HistoricalFrameworkRecord("AIDA", "advertising_persuasive_sequence", "Advertising", true, 0.6, "high"));
        records.add(new HistoricalFrameworkRecord("Information Architecture", "information_architecture", "Digital Publishing", true, 1.0, "low"));

        for (HistoricalFrameworkRecord record : records) {
            System.out.println(record.summary());
        }
    }
}
