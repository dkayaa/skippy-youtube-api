// Globals 
var timestamps
const api_url = 'https://86b3a6376391576e6c6111b618b49ddc.serveo.net/api/search'
const api_test_url = 'https://86b3a6376391576e6c6111b618b49ddc.serveo.net/api/test'


// Wait for the video element to load
function waitForVideo() {
    const video = document.querySelector('video');
    if (video) {
        console.log("[YouTube Tracker] Video found.");
        console.log("[YouTube Tracker]:", window.location.href);

        fetch(api_test_url, {
            method: 'GET'
        }).then(response => response.json())
            .then(data => {
                console.log('[YouTube Tracker] GET request responded with:', data);
            }).catch(error => {
                console.error("[YouTube Tracker] GET request error:", error);
            });


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

        trackTime(video);

    } else {
        setTimeout(waitForVideo, 1000);
    }
}

function trackTime(video) {
    setInterval(() => {
        const currentTime = video.currentTime;
        console.log("[YouTube Tracker] Current Time:", currentTime);
        // You could also send this data to a server or localStorage

        const curTime = document.querySelector('video').currentTime;
        var nextTime;
        for (let i = 0; i < timestamps.length - 1; i++) {
            // Currently Not Labelled For Skipping
            if (timestamps[i].timestamp > curTime && (timestamps[i].label == 0)) {
                return;
            }

            if ((timestamps[i].label == 1) && (timestamps[i + 1].timestamp > curTime)) {
                //if ((i == timestamps.length - 1) || (timestamps[i + 1].timestamp > curTime)) {
                console.log('[Youtube Tracker] searching from, ', timestamps[i].timestamp)
                //find next timestamp label that is 0
                for (let j = i; j < timestamps.length; j++) {
                    if (timestamps[j].label == 0) {
                        nextTime = timestamps[j].timestamp;
                        document.querySelector('video').currentTime = nextTime
                        return;
                    }
                }
                //}
            }
        }
        //document.querySelector('video').currentTime = 90
    }, 5000); // Log every 5 seconds
}

waitForVideo();
