import java.util.ArrayList;
import java.util.List;

class ContentFramework {
    private final String name;
    private final String domain;
    private final String function;

    ContentFramework(String name, String domain, String function) {
        this.name = name;
        this.domain = domain;
        this.function = function;
    }

    String summary() {
        return name + " | " + domain + " | " + function;
    }
}

public class ContentFrameworkModel {
    public static void main(String[] args) {
        List<ContentFramework> frameworks = new ArrayList<>();
        frameworks.add(new ContentFramework("Pillar Page and Topic Cluster", "Digital Publishing", "Organizes related articles around a central explanatory hub"));
        frameworks.add(new ContentFramework("Message House", "Strategic Communication", "Structures central claims and proof points"));
        frameworks.add(new ContentFramework("Educational Scaffolding", "Education", "Sequences knowledge from foundational to advanced understanding"));

        for (ContentFramework framework : frameworks) {
            System.out.println(framework.summary());
        }
    }
}
