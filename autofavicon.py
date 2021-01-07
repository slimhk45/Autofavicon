import os

import favicon
import requests
from urllib.parse import urlparse
from PIL import Image

from send2trash import send2trash


# typically user folder and start menu
myDirs = input('Folder pathes to show icons in (separated by ;): ')
myDirs = myDirs.split(';')

iconDir = input('\n Icon folder path: ')


# list all internet shortcuts in the given folders

shortcuts = []

for myDir in myDirs:
    for (root, subdirs, files) in os.walk(myDir):
        for file in files:
            if file.endswith('.url'):
                shortcuts.append(os.path.join(root, file))

print('\nInternet shortcuts found: ', shortcuts)


iconsToKeep = []

for shortcut in shortcuts:

    with open(shortcut, 'r') as text:
        data = text.readlines()
    print('\nThe following shortcut will be processed:', data)

    targetPath = False
    iconFile = False

    for i in range(len(data)):
        if 'URL' == data[i][:3]:
            targetPath == True
            targetPath = data[i].split('=')[1]
        elif 'IconFile' == data[i][:8]:
            iconFile = True
            iconPath = data[i].split('=')[1]
        else:
            continue

    if targetPath == False:
        print('The shortcut located at ' + shortcut +
              ' is not associated with a website anymore ! Please add an URL to the shortcut again or delete it.\n')
        continue
    if iconFile == False:

        # download the website favicon

        hostName = urlparse(targetPath).netloc

        icons = favicon.get('https://' + hostName)
        print('Icons found: ', icons)

        icon = icons[0]
        for i in range(len(icons)):
            if 'favicon' in icons[i].url.lower():
                icon = icons[i]
                break
            else:
                continue

        downloadPath = os.path.join(iconDir, hostName + '.' + icon.format)
        response = requests.get(icon.url, stream=True)

        with open(downloadPath, 'wb') as img:
            for chunk in response.iter_content(1024):
                img.write(chunk)
        print(icon.url + ' downloaded to ' + downloadPath)

        # convert the favicon to icon file format if necessary

        if not(downloadPath.endswith('.ico')):

            iconPath = downloadPath + '.ico'

            img = Image.open(downloadPath)
            img.save(iconPath, format='ICO', sizes=[(32, 32)])
            send2trash(downloadPath)
        else:
            iconPath = downloadPath

        print('Icon downloaded to ' + iconPath)

        # associate the shortcut to its favicon

        data.append('IconFile=' + iconPath +
                    '\nIconIndex=0\nHotKey=0\nIDList=')

        with open(shortcut, 'w') as text:
            text.writelines(data)

        print('Icon successfully associated to the shortcut:', data)
    else:
        print('Shortcut already associated to ' + iconPath)

    # prepare the removal of unassigned icons
    iconsToKeep.append(iconPath)


# remove unassigned icons and refresh file explorer view

iconsToDelete = []

for file in os.listdir(iconDir):
    filePath = os.path.join(iconDir, file)
    if file.endswith('.ico') and (filePath not in iconsToKeep):
        iconsToDelete.append(filePath)

print('\nList of unassociated icons that will be deleted:', iconsToDelete)

for filePath in iconsToDelete:
    send2trash(filePath)
    print('\n' + file + ' successfuly deleted')

os.system('taskkill /F /IM explorer.exe & start explorer')
