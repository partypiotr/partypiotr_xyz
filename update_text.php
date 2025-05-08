<?php
header("Content-Type: application/json");

$conn = new mysqli("mysql-partypiotr.alwaysdata.net", "410961", "LigmaBalls", "partypiotr_website");

if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

$data = json_decode(file_get_contents('php://input'), true);

if (!isset($data["newText"])) {
    echo json_encode(["error" => "Missing new text"]);
    exit;
}

$newText = $conn->real_escape_string($data["newText"]);
$sql = "UPDATE text SET textbox = '$newText' LIMIT 1";

if ($conn->query($sql) === TRUE) {
    echo json_encode(["status" => "success"]);
} else {
    echo json_encode(["error" => "Update failed: " . $conn->error]);
}

$conn->close();
?>