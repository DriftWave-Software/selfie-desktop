# Selfie Desktop App

A feature-rich Flutter selfie application that allows users to take customized selfies with camera adjustments, background images, timers, and photo filters.

## Features

- **Camera Controls**: Adjust brightness and contrast of the camera in real-time
- **Background Image**: Set custom background images (similar to virtual backgrounds in Google Meet)
- **Timer Functionality**: Set 3, 5, or 10-second timers for taking photos
- **Multiple Shots**: Automatically take 4 consecutive shots with timer
- **Image Filters**: Apply various filters to captured images
- **Image Gallery**: View and edit captured images

## How to Use

### Camera Controls
- Use sliders to adjust brightness and contrast
- Select timer duration from preset values
- Tap the camera button to take a photo
- Use timer button to take a photo with countdown
- Use the 4-shots button to take multiple consecutive photos

### Background Image
- Tap the image icon in the app bar
- Select an image from your gallery to use as background
- Toggle the background on/off using the same button

### Photo Filters
- After taking photos, tap on any thumbnail in the bottom gallery
- Choose from available filters in the popup panel
- Tap 'Apply' to apply the selected filter
- Tap 'Cancel' to discard changes

## Requirements

- Flutter SDK: ^3.8.1
- Camera permissions
- Storage permissions

## Installation

```bash
git clone https://github.com/yourusername/selfie-desktop.git
cd selfie-desktop
flutter pub get
flutter run
```

## Dependencies

- camera: ^0.10.5+5
- image_picker: ^1.0.4
- path_provider: ^2.1.1
- photofilters: ^3.0.1
- and more (see pubspec.yaml for full list)
