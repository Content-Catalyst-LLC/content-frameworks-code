from pathlib import Path
import sys
ARTICLE_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ARTICLE_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))
from content_framework_canvas.cli import main
raise SystemExit(main(["--article-root", str(ARTICLE_ROOT)]))
