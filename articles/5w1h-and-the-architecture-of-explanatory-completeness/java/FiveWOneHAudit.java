public class FiveWOneHAudit {
    static double readiness(double coverage, double support, double balance, double audienceFit, double governance) {
        double score = 0.24 * coverage + 0.26 * support + 0.16 * balance + 0.16 * audienceFit + 0.18 * governance;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("5W1H Explanatory Completeness Audit");
        System.out.printf("Complete readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial readiness: %.3f%n", readiness(0.83, 0.80, 0.90, 1.0, 0.75));
        System.out.printf("Governance review example: %.3f%n", readiness(0.33, 0.20, 0.45, 0.33, 0.25));
    }
}
