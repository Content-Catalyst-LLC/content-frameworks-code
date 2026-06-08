public class PersuasiveRiskAudit {
    static double responsibleScore(
        double agency,
        double evidence,
        double governance,
        double accessibility,
        double pressure,
        double vulnerability,
        double darkPattern
    ) {
        double score = 0.24 * agency + 0.24 * evidence + 0.18 * governance + 0.14 * accessibility - 0.12 * pressure - 0.08 * vulnerability - 0.10 * darkPattern;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Persuasive Framework Ethical-Risk Audit");
        System.out.printf("Responsible persuasion example: %.3f%n", responsibleScore(1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0));
        System.out.printf("High-stakes public CTA example: %.3f%n", responsibleScore(1.0, 1.0, 1.0, 1.0, 0.0, 0.25, 0.0));
        System.out.printf("Dark-pattern risk example: %.3f%n", responsibleScore(0.0, 0.25, 0.0, 0.0, 1.0, 1.0, 1.0));
    }
}
