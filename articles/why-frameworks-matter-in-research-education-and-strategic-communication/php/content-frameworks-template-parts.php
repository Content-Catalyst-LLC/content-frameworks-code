<?php
/**
 * WordPress-oriented helper snippets for Content Frameworks articles.
 */

function cc_content_framework_series_strip($previous_url, $previous_title, $map_url, $next_url, $next_title) {
    return '<nav class="cc-series-strip" aria-label="Content Frameworks series navigation">'
        . '<div class="cc-series-strip-label">Continue the Content Frameworks Series</div>'
        . '<div class="cc-series-strip-grid">'
        . '<a class="cc-series-strip-item" href="' . esc_url($previous_url) . '"><span class="cc-series-strip-meta">← Previous Article</span><span class="cc-series-strip-title">' . esc_html($previous_title) . '</span></a>'
        . '<a class="cc-series-strip-item cc-series-strip-center" href="' . esc_url($map_url) . '"><span class="cc-series-strip-meta">◆ Article Map</span><span class="cc-series-strip-title">Content Frameworks</span></a>'
        . '<a class="cc-series-strip-item cc-series-strip-right" href="' . esc_url($next_url) . '"><span class="cc-series-strip-meta">Next Article →</span><span class="cc-series-strip-title">' . esc_html($next_title) . '</span></a>'
        . '</div>'
        . '</nav>';
}
