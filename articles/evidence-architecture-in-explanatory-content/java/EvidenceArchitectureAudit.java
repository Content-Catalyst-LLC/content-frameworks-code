public class EvidenceArchitectureAudit {
    static double readiness(double claimSupport, double sourceQuality, double uncertainty, double visualSupport, double reviewReadiness) {
        double score = 0.30 * claimSupport + 0.20 * sourceQuality + 0.20 * uncertainty + 0.12 * visualSupport + 0.18 * reviewReadiness;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Evidence Architecture Audit");
        System.out.printf("Complete evidence architecture readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial readiness example: %.3f%n", readiness(0.75, 0.75, 0.75, 0.75, 0.67));
        System.out.printf("Governance review example: %.3f%n", readiness(0.35, 0.45, 0.50, 0.25, 0.33));
    }
}
