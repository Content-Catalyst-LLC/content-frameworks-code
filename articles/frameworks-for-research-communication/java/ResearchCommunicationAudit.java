public class ResearchCommunicationAudit {
    static double readiness(double claimSupport, double method, double uncertainty, double audience, double visual) {
        double score = 0.28 * claimSupport + 0.18 * method + 0.22 * uncertainty + 0.17 * audience + 0.15 * visual;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Research Communication Audit");
        System.out.printf("Full research communication readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial readiness example: %.3f%n", readiness(0.75, 1.0, 0.75, 0.75, 0.67));
        System.out.printf("Governance review example: %.3f%n", readiness(0.35, 0.0, 0.5, 0.5, 0.0));
    }
}
