import java.util.ArrayList;
import java.util.List;

class LearningArticle {
    final String slug;
    final String title;
    final String stage;
    final double orientation;
    final double prerequisites;
    final double examples;
    final double feedback;
    final double transfer;
    final double accessibility;
    final double loadPenalty;

    LearningArticle(String slug, String title, String stage, double orientation, double prerequisites, double examples, double feedback, double transfer, double accessibility, double loadPenalty) {
        this.slug = slug;
        this.title = title;
        this.stage = stage;
        this.orientation = orientation;
        this.prerequisites = prerequisites;
        this.examples = examples;
        this.feedback = feedback;
        this.transfer = transfer;
        this.accessibility = accessibility;
        this.loadPenalty = loadPenalty;
    }

    double scaffoldReadinessScore() {
        double score = 0.18 * orientation
            + 0.20 * prerequisites
            + 0.18 * examples
            + 0.16 * feedback
            + 0.18 * transfer
            + 0.10 * accessibility
            - loadPenalty;

        if (score < 0.0) {
            return 0.0;
        }
        if (score > 1.0) {
            return 1.0;
        }
        return score;
    }

    boolean needsGovernanceReview() {
        return scaffoldReadinessScore() < 0.78;
    }
}

public class EducationalScaffoldingModel {
    public static void main(String[] args) {
        List<LearningArticle> articles = new ArrayList<>();

        articles.add(new LearningArticle("educational-scaffolding-and-the-design-of-learning-systems", "Educational Scaffolding and the Design of Learning Systems", "method", 1, 1, 1, 1, 1, 1, 0));
        articles.add(new LearningArticle("frameworks-for-digital-knowledge-systems", "Frameworks for Digital Knowledge Systems", "application", 1, 1, 1, 0, 1, 0.75, 0.25));
        articles.add(new LearningArticle("curriculum-pathways-and-framework-design", "Curriculum Pathways and Framework Design", "transfer", 1, 0.5, 0, 0, 1, 0.5, 0.10));

        System.out.println("Educational Scaffolding Model");
        System.out.println("-----------------------------");

        for (LearningArticle article : articles) {
            System.out.printf(
                "%s | stage=%s | readiness=%.3f | review=%s%n",
                article.slug,
                article.stage,
                article.scaffoldReadinessScore(),
                article.needsGovernanceReview()
            );
        }
    }
}
