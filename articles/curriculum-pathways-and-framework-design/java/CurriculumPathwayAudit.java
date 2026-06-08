public class CurriculumPathwayAudit {
    static double readiness(double sequence, double objective, double accessibility, double feedback, double transfer) {
        double score = 0.22 * sequence + 0.22 * objective + 0.16 * accessibility + 0.18 * feedback + 0.22 * transfer;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Curriculum Pathway Audit");
        System.out.printf("Complete pathway readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial pathway readiness: %.3f%n", readiness(0.8, 0.75, 0.75, 0.67, 0.67));
        System.out.printf("Governance review example: %.3f%n", readiness(0.5, 0.4, 0.5, 0.33, 0.33));
    }
}
