public class CommunicationResponseAudit {
    static double readiness(double coverage, double support, double balance, double audienceFit, double governance, double ethics) {
        double score = 0.22 * coverage + 0.22 * support + 0.16 * balance + 0.16 * audienceFit + 0.14 * governance + 0.10 * ethics;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Communication Response Audit");
        System.out.printf("Complete response readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial response readiness: %.3f%n", readiness(0.71, 0.80, 0.90, 1.0, 0.75, 1.0));
        System.out.printf("Governance review example: %.3f%n", readiness(0.33, 0.20, 0.45, 0.33, 0.25, 0.25));
    }
}
