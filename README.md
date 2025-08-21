![image](./images/title.png)
## What ?
A browser plugin that uses AI text classification to detect and scrub advertisement content from Youtube videos in real-time. 
## Why ? 
Improve the Youtube user experience by automatically skipping those in-video ad reads that were going to be skipped anyway. 
## How ? 
When a user navigates to a Youtube video URL, a request is sent to the backend server to execute the following; the back-end first retrieves the relevant audio transcript and timestamps, leveraging the python's `youtube-transcript-api` library. The transcript undergoes a preprocessing step whereby it is split into overlapping text chunks. Each chunk is then processed by a text-classification model. Specifically, we leverage the pretrained `distilbert-base-uncased` model, fine tuned on a manually curated dataset of 3K+ labelled samples, to employ binary classification for each text chunk as either an advertisement or not. 

## Local Setup 
The plugin and server can be deployed for local use.
- Deploy the project containers using the setup script `cd server; bash run.sh`
- Copy the serveo.net url forwarding traffic to the server. It should be of the form `https://xxx.serveo.net`
- Navigate to the browser*, type `about:debugging#/runtime/this-firefox`
- Click `Load Temporary Add-on` and select `manifest.json` 
- Navigate to the plugin configuration menu and paste the serveo url and hit save.

*Currently only supports Firefox

## Training Data
An indicative training sample is provided below 
```
 {
        "text": "very high quality protein with just 150 calories if you would like to try David you can go to david.com huberman again the link is david.com huberman today's episode is also brought To Us by eight sleep eight sleep makes Smart mattress covers with cooling Heating and sleep tracking capacity now I've spoken before on this podcast about the critical need for us to get adequate amounts of quality sleep each night now one of the best ways to ensure a great night's sleep is to ensure that the temperature of your sleeping environment is correct and that's because in order to fall and stay deeply asleep your body temperature actually has to drop by about 1 to 3° and in order to wake up feeling refreshed and energized your body",
        
        "start": 236.799,
        
        "label": 1
}
```