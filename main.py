from moviepy.editor import *
import reddit, screenshot, time, subprocess, random, configparser, sys, math, youtube_API
from os import listdir
from os.path import isfile, join

def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if (len(sys.argv) == 2):
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        script = reddit.getContent(outputDir, postOptionCount)
    fileName = script.getFileName()

    # show id of the post
    print(f"Post ID: {script.postId}")


    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)

    #get background music 
    bgMusicDir = config["General"]["BackgroundMusicDirectory"]
    bgMusicFiles = [f for f in listdir(bgMusicDir) if isfile(join(bgMusicDir, f))]
    bgMusicCount = len(bgMusicFiles)
    bgMusicIndex = random.randint(0, bgMusicCount-1)
    bgMusic = AudioFileClip(f"{bgMusicDir}/{bgMusicFiles[bgMusicIndex]}")


    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)
    bgIndex = random.randint(0, bgCount-1)
    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4", 
        audio=False).subclip(0, script.getDuration())
    w, h = backgroundVideo.size

    def __createClip(screenShotFile, audioClip, marginSize):
        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
            ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    clips.append(__createClip(script.titleSCFile, script.titleAudioClip, marginSize))
    for comment in script.frames:
        clips.append(__createClip(comment.screenShotFile, comment.audioClip, marginSize))

    # Merge clips into single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))
    bgMusic = bgMusic.subclip(0, script.getDuration())
    combined_audio = CompositeAudioClip([contentOverlay.audio.volumex(0.5), bgMusic.volumex(0.2)])

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay], 
        size=backgroundVideo.size).set_audio(combined_audio)
    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4"
    final.write_videofile(
        outputFile, 
        codec = 'mpeg4',
        threads = threads, 
        bitrate = bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

    # Preview in VLC for approval before uploading
    if (config["General"].getboolean("PreviewBeforeUpload")):
        vlcPath = config["General"]["VLCPath"]
        p = subprocess.Popen([vlcPath, outputFile])
    # Upload to YouTube when enter y
    print("Upload to YouTube? (y/n)")
    if (input() == "y"):
        youtube_API.upload_video(outputFile, script.title)
        print("Video uploaded to YouTube!")
    else:
        print("Video not uploaded to YouTube!")

    #cleanup
    # delete all screenshots and audio files created
    
    

    print("Video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")

    screenshotDir = "Screenshots"
    audioDir = "Voiceovers"

    for f in listdir(screenshotDir):
        if isfile(join(screenshotDir, f)):
            os.remove(join(screenshotDir, f))

    for f in listdir(audioDir):
        if isfile(join(audioDir, f)):
            os.remove(join(audioDir, f))



    
    
    

if __name__ == "__main__":
    createVideo()