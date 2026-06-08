<?php
function cc_communication_model_readiness_label($score) {
    $score = floatval($score);
    if ($score >= 0.78) return 'ready';
    if ($score >= 0.60) return 'review';
    return 'needs support';
}
