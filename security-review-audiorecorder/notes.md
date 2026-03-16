# Security Review Notes: AudioRecorder

## Project Info
- **Repository:** https://github.com/Dimowner/AudioRecorder
- **Language:** Java/Kotlin (Android)
- **Date:** 2026-03-16

## Approach
1. Cloned the repository to /tmp for analysis
2. Ran parallel security reviews covering:
   - Android manifest & build configuration
   - Data storage & file handling
   - IPC, services & component security
   - Audio recording/playback code, utilities, and dependencies

## Key Files Examined
- `AndroidManifest.xml` - permissions, exported components, provider config
- `app/build.gradle` - SDK versions, signing config, dependencies, ProGuard
- `keystore.properties` - signing credentials (checked into git!)
- `provider_paths.xml` - FileProvider path configuration
- `LocalRepositoryImpl.java` / `DataSource.java` - SQL queries
- `FileUtil.java` / `FileRepositoryImpl.java` - file operations
- `PrefsImpl.java` - SharedPreferences storage
- `SQLiteHelper.java` - database schema
- `RecordingService.java` / `PlaybackService.java` / `DecodeService.kt` / `MoveRecordsService.kt` - services
- `RecordingWidget.kt` - widget and broadcast receivers
- `AudioRecorder.java` / `WavRecorder.java` / `ThreeGpRecorder.java` - recording engines
- `AudioDecoder.java` - audio decoding
- `AndroidUtils.java` - utility functions with file sharing
- `DownloadManager.kt` - file download/export
- `AppRecorderImpl.java` - recording orchestration
- `FileBrowserPresenter.java` - file browser
- `TransparentRecordingActivity.kt` - transparent recording UI
- `Injector.java` - dependency injection / singletons
- `AppConstants.java` - app constants

## Notable Findings Summary
- 4 Critical issues (FileProvider paths, SQL injection, keystore in git, signing creds exposed)
- 8+ High issues (path traversal, unprotected receivers, intent spoofing, excessive logging, buffer issues)
- 8+ Medium issues (unencrypted DB/prefs, PendingIntent flags, race conditions, lint config)
- Several Low/Info issues (deprecated APIs, missing null checks, exposed email)

## Positive Observations
- INTERNET permission is commented out (no network access)
- All services are marked `android:exported="false"`
- SDK versions are current (compileSdk 34, targetSdk 34)
- Dependencies are up-to-date with no known CVEs
- Firebase/analytics are disabled (commented out)
- Scoped storage properly handled for Android 10+
- Release builds use minify and shrinkResources

## Tools Used
- git clone for repo fetch
- Manual code review of all critical files
- Pattern analysis for SQL injection, path traversal, logging, etc.
