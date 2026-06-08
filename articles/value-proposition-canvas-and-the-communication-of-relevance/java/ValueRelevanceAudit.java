public class ValueRelevanceAudit {
    static double score(double job, double pain, double gain, double evidence, double clarity, double ethics) {
        return (job + pain + gain + evidence + clarity + ethics) / 6.0;
    }

    static String classify(double score) {
        if (score >= 0.88) return "strong relevance";
        if (score >= 0.78) return "publishable with review";
        if (score >= 0.60) return "revise before publication";
        return "major relevance gap";
    }

    public static void main(String[] args) {
        double result = score(0.91, 0.84, 0.86, 0.76, 0.90, 0.88);
        System.out.printf("Value relevance score: %.3f%n", result);
        System.out.println(classify(result));
    }
}
