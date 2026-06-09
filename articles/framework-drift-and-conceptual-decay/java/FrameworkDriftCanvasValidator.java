import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Lightweight Java smoke validator for Framework Drift and Conceptual Decay Catalyst Canvas outputs.
 * This intentionally uses only the Java standard library.
 */
public class FrameworkDriftCanvasValidator {
    public static void main(String[] args) throws IOException {
        Path manifest = Path.of("canvas", "canvas_manifest.json");
        Path cards = Path.of("canvas", "canvas_cards.json");
        Path queue = Path.of("canvas", "governance_queue.json");

        requireFile(manifest);
        requireFile(cards);
        requireFile(queue);

        String manifestText = Files.readString(manifest);
        if (!manifestText.contains("\"framework_drift_canvas\"")) {
            throw new IllegalStateException("Manifest does not identify framework_drift_canvas.");
        }

        System.out.println("Framework Drift Canvas Java validation passed.");
    }

    private static void requireFile(Path path) {
        if (!Files.exists(path)) {
            throw new IllegalStateException("Required file missing: " + path);
        }
    }
}
