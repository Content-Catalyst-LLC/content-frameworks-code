<?php
/**
 * Why Content Frameworks Matter Today Catalyst Canvas renderer.
 *
 * This lightweight helper is designed for WordPress-style environments where
 * generated Canvas JSON files may be rendered into article companion blocks.
 */

function cc_content_framework_value_load_json($path) {
    if (!file_exists($path)) {
        return array(
            'ok' => false,
            'error' => 'File not found: ' . $path,
            'data' => array()
        );
    }

    $raw = file_get_contents($path);
    $data = json_decode($raw, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        return array(
            'ok' => false,
            'error' => json_last_error_msg(),
            'data' => array()
        );
    }

    return array(
        'ok' => true,
        'error' => '',
        'data' => $data
    );
}

function cc_content_framework_value_render_card_list($cards) {
    if (!is_array($cards) || count($cards) === 0) {
        return '<p>No Content Framework Value Canvas cards are available.</p>';
    }

    $html = '<div class="cc-canvas-card-list">';

    foreach ($cards as $card) {
        $title = htmlspecialchars($card['title'] ?? 'Untitled content framework value item', ENT_QUOTES, 'UTF-8');
        $description = htmlspecialchars($card['description'] ?? '', ENT_QUOTES, 'UTF-8');
        $html .= '<article class="cc-canvas-card content-framework-value-card">';
        $html .= '<h3>' . $title . '</h3>';
        $html .= '<p>' . $description . '</p>';
        $html .= '</article>';
    }

    $html .= '</div>';

    return $html;
}
