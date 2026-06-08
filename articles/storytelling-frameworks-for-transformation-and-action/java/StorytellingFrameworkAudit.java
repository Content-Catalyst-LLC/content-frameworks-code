public class StorytellingFrameworkAudit {
    static double readiness(
        double completeness,
        double evidence,
        double agency,
        double transformation,
        double governance,
        double ethics
    ) {
        double score = 0.24 * completeness + 0.22 * evidence + 0.18 * agency + 0.16 * transformation + 0.12 * governance + 0.08 * ethics;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("Storytelling Framework Audit");
        System.out.printf("Complete storytelling readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial storytelling readiness: %.3f%n", readiness(0.83, 0.80, 1.0, 0.67, 0.75, 1.0));
        System.out.printf("Governance review example: %.3f%n", readiness(0.33, 0.20, 0.33, 0.25, 0.25, 0.25));
    }
}
