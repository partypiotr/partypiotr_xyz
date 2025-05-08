<?php
header("Content-Type: application/json");

$conn = new mysqli("mysql-partypiotr.alwaysdata.net", "410961", "LigmaBalls", "partypiotr_website");

if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

$sql = "SELECT textbox FROM text LIMIT 1";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    echo json_encode(["textbox" => $row["textbox"]]);
} else {
    echo json_encode(["error" => "No data found"]);
}

$conn->close();
?>