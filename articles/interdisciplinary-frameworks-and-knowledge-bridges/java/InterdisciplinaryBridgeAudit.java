public class InterdisciplinaryBridgeAudit {
    static double readiness(double translation, double evidence, double method, double audience, double governance) {
        double score = 0.22 * translation + 0.24 * evidence + 0.18 * method + 0.18 * audience + 0.18 * governance;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Interdisciplinary Bridge Audit");
        System.out.printf("Complete bridge readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial bridge readiness: %.3f%n", readiness(0.75, 0.75, 0.67, 0.75, 0.67));
        System.out.printf("Governance review example: %.3f%n", readiness(0.40, 0.35, 0.33, 0.50, 0.33));
    }
}
