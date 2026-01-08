# Steam Auto Shutdown Downloader

This application is designed for users who download large Steam games overnight due to slow internet speeds and don’t want to leave their computer running after the download is finished.

The app uses the **Steam Web API** to monitor the installation size of a selected game and automatically shuts down the computer once the download is complete.

## How It Works

1. The user provides a **Steam API Key**.
2. The application tracks the target game's installation directory size.
3. While the game is downloading, the app continuously checks the folder size.
4. When the folder size reaches the expected install size, the download is considered complete.
5. The application then shuts down the computer using a system command:shutdown /s /t <seconds>
