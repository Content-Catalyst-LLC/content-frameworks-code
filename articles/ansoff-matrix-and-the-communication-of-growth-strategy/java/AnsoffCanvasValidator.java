import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Lightweight Java smoke validator for Ansoff Matrix Catalyst Canvas outputs.
 * This intentionally uses only the Java standard library.
 */
public class AnsoffCanvasValidator {
    public static void main(String[] args) throws IOException {
        Path manifest = Path.of("canvas", "canvas_manifest.json");
        Path cards = Path.of("canvas", "canvas_cards.json");
        Path queue = Path.of("canvas", "governance_queue.json");

        requireFile(manifest);
        requireFile(cards);
        requireFile(queue);

        String manifestText = Files.readString(manifest);
        if (!manifestText.contains("\"ansoff_canvas\"")) {
            throw new IllegalStateException("Manifest does not identify ansoff_canvas.");
        }

        System.out.println("Ansoff Canvas Java validation passed.");
    }

    private static void requireFile(Path path) {
        if (!Files.exists(path)) {
            throw new IllegalStateException("Required file missing: " + path);
        }
    }
}
