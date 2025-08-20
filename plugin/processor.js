// Globals 
var timestamps;
var api_url = '';
const api_path = '/api/search';

// Load server URL from storage
setInterval(() => {
    const storage = (typeof browser !== "undefined") ? browser.storage.sync : chrome.storage.sync;

    storage.get('server').then((result) => {
        var api_url_old = api_url;
        api_url = result.server || 'No Server URL Set';
        if (api_url !== api_url_old) {
            console.log("[YouTube Tracker] API URL updated:", api_url);
            postServer(video_ref);
        }
    });
}, 1000); // Check every second

function waitForVideo() {
    const video = document.querySelector('video');
    if (video) {
        video_ref = window.location.href;

        console.log("[YouTube Tracker] Video found.");
        console.log("[YouTube Tracker]:", video_ref);

        postServer(video_ref);
        trackVideo(video);

    } else {
        setTimeout(waitForVideo, 10000);
    }
}

function postServer(link) {
    const params = new URLSearchParams();
    params.append('link', video_ref);

    fetch(api_url + api_path, {
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
}

function trackVideo(video) {
    setInterval(() => {
        const currentTime = video.currentTime;

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
