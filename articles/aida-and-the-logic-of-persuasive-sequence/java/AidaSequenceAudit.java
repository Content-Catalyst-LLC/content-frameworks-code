public class AidaSequenceAudit {
    static double readiness(double attention, double interest, double desire, double action, double ethics) {
        double score = 0.18 * attention + 0.20 * interest + 0.22 * desire + 0.20 * action + 0.20 * ethics;
        if (score < 0.0) return 0.0;
        if (score > 1.0) return 1.0;
        return score;
    }

    public static void main(String[] args) {
        System.out.println("AIDA Sequence Audit");
        System.out.printf("Complete AIDA readiness: %.3f%n", readiness(1.0, 1.0, 1.0, 1.0, 1.0));
        System.out.printf("Partial AIDA readiness: %.3f%n", readiness(1.0, 0.75, 0.67, 0.75, 1.0));
        System.out.printf("Governance review example: %.3f%n", readiness(0.33, 0.33, 0.33, 0.67, 0.25));
    }
}
