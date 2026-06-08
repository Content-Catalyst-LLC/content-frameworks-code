public class PasBabSequenceAudit {
    static double readiness(double currentState, double stakes, double transformation, double bridge, double ethics) {
        double score = 0.20 * currentState + 0.20 * stakes + 0.20 * transformation + 0.20 * bridge + 0.20 * ethics;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("PAS/BAB Sequence Audit");
        System.out.printf("Complete PAS/BAB readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial PAS/BAB readiness: %.3f%n", readiness(1.0, 1.0, 0.67, 0.75, 1.0));
        System.out.printf("Governance review example: %.3f%n", readiness(0.33, 0.33, 0.33, 0.33, 0.25));
    }
}
