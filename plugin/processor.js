// Globals 
var timestamps
const api_url = 'https://647d075137a1e3aa310d6a291dbfe679.serveo.net/api/search'

// Wait for the video element to load
function waitForVideo() {
    const video = document.querySelector('video');
    if (video) {
        console.log("[YouTube Tracker] Video found.");
        console.log("[YouTube Tracker]:", window.location.href);

        const params = new URLSearchParams();
        params.append('link', window.location.href);

        fetch(api_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params.toString()
        }).then(response => response.json())
            .then(data => {
                console.log('[YouTube Tracker] POST request responded with:', data);
                timestamps = data;
            }).catch(error => {
                console.error("[YouTube Tracker] POST request error:", error);
            });

        trackVideo(video);

    } else {
        setTimeout(waitForVideo, 1000);
    }
}

function trackVideo(video) {
    setInterval(() => {
        const currentTime = video.currentTime;
        console.log("[YouTube Tracker] Current Time:", currentTime);

        const curTime = document.querySelector('video').currentTime;
        var nextTime;
        for (let i = 0; i < timestamps.length - 1; i++) {
            // Currently Not Labelled For Skipping
            if (timestamps[i].timestamp > curTime && (timestamps[i].label == 0)) {
                return;
            }

            if ((timestamps[i].label == 1) && (timestamps[i + 1].timestamp > curTime)) {
                console.log('[Youtube Tracker] searching from, ', timestamps[i].timestamp)
                // Find next timestamp label that is 0
                for (let j = i; j < timestamps.length; j++) {
                    if (timestamps[j].label == 0) {
                        nextTime = timestamps[j].timestamp;
                        document.querySelector('video').currentTime = nextTime
                        return;
                    }
                }
            }
        }
    }, 5000); // Log every 5 seconds
}

waitForVideo();
