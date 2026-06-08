public class JTBDContentAudit {
    static double readiness(
        double jobClarity,
        double contentFit,
        double evidence,
        double outcome,
        double agency,
        double governance
    ) {
        double score = 0.24 * jobClarity + 0.22 * contentFit + 0.20 * evidence + 0.14 * outcome + 0.10 * agency + 0.10 * governance;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Jobs to Be Done Content Audit");
        System.out.printf("Complete JTBD readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial JTBD readiness: %.3f%n", readiness(0.75, 0.75, 0.80, 0.67, 1.0, 0.75));
        System.out.printf("Governance review example: %.3f%n", readiness(0.25, 0.25, 0.20, 0.0, 0.0, 0.0));
    }
}
