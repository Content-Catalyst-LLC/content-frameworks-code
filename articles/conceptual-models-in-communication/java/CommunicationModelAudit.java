public class CommunicationModelAudit {
    static double readiness(double elements, double relationships, double audience, double feedback, double evidence, double domain, double penalty) {
        double score = 0.25 * elements + 0.15 * relationships + 0.20 * audience + 0.15 * feedback + 0.15 * evidence + 0.10 * domain - penalty;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Communication Model Audit");
        System.out.printf("Transactional Meaning Model readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 0.67, 1.0, 0.0));
        System.out.printf("Systems Communication Model readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.10));
        System.out.printf("Persuasive Sequence Model readiness: %.3f%n", readiness(0.80, 0.45, 0.50, 0.0, 0.0, 0.65, 0.25));
    }
}
