import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Lightweight Java smoke validator for Strategic Foresight and Scenario Thinking Catalyst Canvas outputs.
 * This intentionally uses only the Java standard library.
 */
public class StrategicForesightCanvasValidator {
    public static void main(String[] args) throws IOException {
        Path manifest = Path.of("canvas", "canvas_manifest.json");
        Path cards = Path.of("canvas", "canvas_cards.json");
        Path queue = Path.of("canvas", "governance_queue.json");

        requireFile(manifest);
        requireFile(cards);
        requireFile(queue);

        String manifestText = Files.readString(manifest);
        if (!manifestText.contains("\"strategic_foresight_canvas\"")) {
            throw new IllegalStateException("Manifest does not identify strategic_foresight_canvas.");
        }

        System.out.println("Strategic Foresight Canvas Java validation passed.");
    }

    private static void requireFile(Path path) {
        if (!Files.exists(path)) {
            throw new IllegalStateException("Required file missing: " + path);
        }
    }
}
