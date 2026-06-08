<?php
function cc_responsible_persuasion_label($score) {
    $score = floatval($score);
    if ($score >= 0.78) return 'ready';
    if ($score >= 0.60) return 'review';
    return 'needs support';
}
