document.addEventListener("DOMContentLoaded", function() {
    let video = document.querySelector("#videoElement");
    let gestureResultDiv = document.getElementById('gestureResult'); // Reference to the result display div

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (error) {
                console.log("Something went wrong!", error);
                gestureResultDiv.textContent = "Error accessing webcam"; // Display error
            });
    }

    function sendFrame() {
        if (!video.videoWidth) return; // Check if the video is ready

        let canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        let data = canvas.toDataURL('image/jpeg');

        fetch('/process_frame/', {
            method: 'POST',
            body: JSON.stringify({'frame': data}),
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            gestureResultDiv.textContent = data.result; // Update the result display
        })
        .catch(error => {
            console.error('Fetch error:', error);
            gestureResultDiv.textContent = "Error processing frame"; // Display error
        });
    }

    setInterval(sendFrame, 10); // Adjust the interval as needed

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
