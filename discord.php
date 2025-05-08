<?php
// process.php

$webhook_url = 'https://discord.com/api/webhooks/1366848000474874056/vjMfmUmENrA51ixmb3PJT1UOsjCxvJcN2jJmALZDFNq3BCewtvBQKZqJTZnEuxqE9twP';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Accept raw UTF-8 input
    $name = trim($_POST['name']);
    $message = trim($_POST['message']);

    // Prepare payload
    $data = [
        'username' => $name,
        'content' => $message
    ];

    // JSON_UNESCAPED_UNICODE preserves emojis and special characters
    $json = json_encode($data, JSON_UNESCAPED_UNICODE);

    // Send to Discord
    $ch = curl_init($webhook_url);
    curl_setopt_array($ch, [
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $json,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true
    ]);

    $response = curl_exec($ch);
    curl_close($ch);
    header('Location: index.html');
} else {
    echo 'Invalid request method.';
}
?>
