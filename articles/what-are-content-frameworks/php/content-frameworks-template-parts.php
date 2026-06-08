<?php
/**
 * WordPress-oriented helper snippets for Content Frameworks articles.
 */

function cc_content_framework_footer_nav($previous_url, $previous_label, $map_url, $next_url, $next_label) {
    $previous = '<a class="cc-footer-nav-button disabled" aria-disabled="true">← Series Start</a>';

    if (!empty($previous_url) && !empty($previous_label)) {
        $previous = '<a class="cc-footer-nav-button" href="' . esc_url($previous_url) . '">← ' . esc_html($previous_label) . '</a>';
    }

    return '<nav class="cc-article-footer-nav" aria-label="Content Frameworks article navigation">'
        . $previous
        . '<a class="cc-footer-nav-button" href="' . esc_url($map_url) . '">Content Frameworks Article Map</a>'
        . '<a class="cc-footer-nav-button" href="' . esc_url($next_url) . '">' . esc_html($next_label) . ' →</a>'
        . '</nav>';
}
