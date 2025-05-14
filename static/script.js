function downloadVideo() {
    let url = document.getElementById("videoUrl").value;
    let status = document.getElementById("status");

    if (!url) {
        status.innerHTML = "Please enter a video URL!";
        status.style.color = "red";
        return;
    }

    fetch("/download", {
        method: "POST",
        body: JSON.stringify({ url: url }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            status.innerHTML = `❌ ${data.error}`;
            status.style.color = "red";
        } else {
            status.innerHTML = `✅ ${data.message}`;
            status.style.color = "green";
        }
    })
    .catch(error => {
        status.innerHTML = "❌ Error downloading video!";
        status.style.color = "red";
    });
}
