import json, os, requests, ffmpeg, datetime, sys

print("Checking messages for voice messages...")
voiceMessages = []
folder = sys.argv[1]
exportFolder = sys.argv[2]
channelFolders = os.listdir(folder)
audioTypes = ["ogg", "m4a", "mp3", "wav", "aac"]
for channelFolder in channelFolders:
    if channelFolder != "index.json" or channelFolder != ".DS_Store":
        messageFileLocation = folder + "/" + channelFolder + "/messages.json"
        if os.path.exists(messageFileLocation):
            with open(messageFileLocation) as file:
                messages = json.load(file)
                for message in messages:
                    if message["Attachments"]:
                        for attachment in message["Attachments"].split(" "):
                            originalName = attachment.split("/")[-1].split("?")[0]
                            for audioType in audioTypes:
                                if originalName.endswith(audioType):
                                    voiceMessages.append(
                                        {
                                            "url": attachment,
                                            "date": message["Timestamp"],
                                            "channel": channelFolder,
                                            "originalName": originalName, 
                                            "id": message["ID"]
                                        }
                                    )
print("Finished")

print(f"Downloading & Converting {len(voiceMessages)} Voice Messages")

for voiceMessage in voiceMessages:
    fileName = f"{exportFolder}/discord {voiceMessage["channel"]} m{voiceMessage["id"]} {voiceMessage["originalName"]}"
    newFileName = f"{fileName}.m4a"
    with open(fileName, "wb") as file:
        fail = False
        if not (os.path.exists(newFileName)):
            voiceContents = requests.get(voiceMessage["url"])
            file.write(voiceContents.content)
            try:
                if not fileName.endswith("m4a"):
                    ffmpeg.input(fileName).output(newFileName).run()
                else:
                    with open(newFileName, "wb") as file2:
                        file2.write(voiceContents.content)
            except:
                fail = True
        if not fail:
            os.remove(fileName)
            date, time = voiceMessage["date"].split(" ")
            year, month, day = date.split("-")
            hour, minute, second = time.split(":")
            time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            timestamp = time.timestamp()
            os.utime(newFileName, (timestamp, timestamp))