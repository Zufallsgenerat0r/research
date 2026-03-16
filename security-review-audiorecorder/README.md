# Security Review: Dimowner/AudioRecorder

**Repository:** https://github.com/Dimowner/AudioRecorder
**Review Date:** 2026-03-16
**Reviewer:** Automated security analysis
**App Type:** Android audio recording application (Java/Kotlin)

---

## Executive Summary

AudioRecorder is an open-source Android app for recording, playing, and managing audio files. The app uses local-only storage with no network connectivity (INTERNET permission is commented out), which significantly reduces its attack surface. However, the review identified **4 Critical**, **8 High**, **8 Medium**, and several Low-severity security issues primarily related to insecure file handling, SQL injection, overly permissive component exports, and credential management.

The most urgent issues are the **overly broad FileProvider configuration** exposing the entire external storage, **SQL injection vulnerabilities** in the data layer, and **signing credentials committed to version control**.

---

## Severity Summary

| Severity | Count | Key Areas |
|----------|-------|-----------|
| Critical | 4 | FileProvider paths, SQL injection, keystore in VCS, signing credentials |
| High | 8 | Path traversal, unprotected broadcast receivers, intent spoofing, excessive logging, buffer issues, input validation |
| Medium | 8 | Unencrypted database/prefs, PendingIntent flags, race conditions, ProGuard bypass, lint config, file deletion |
| Low/Info | 5+ | Deprecated APIs, null checks, exposed email, duplicate permissions |

---

## Critical Findings

### C1. Overly Broad FileProvider Path Configuration
**File:** `app/src/main/res/xml/provider_paths.xml`
**CWE:** CWE-552 (Files or Directories Accessible to External Parties)

```xml
<external-path name="external_files" path="."/>
<external-files-path name="external_files" path="." />
<external-path name="AudioRecorder" path="/" />
```

The FileProvider configuration exposes the **entire external storage root** (`path="/"`). Any app that receives a content URI from this provider can potentially access arbitrary files on external storage. This is the most critical finding as it enables data exfiltration.

**Recommendation:** Restrict to specific subdirectories:
```xml
<external-files-path name="recordings" path="Recordings/" />
```

---

### C2. SQL Injection Vulnerabilities
**Files:** `LocalRepositoryImpl.java` (lines 130-160), `DataSource.java` (lines 178-212)
**CWE:** CWE-89 (SQL Injection)

Multiple methods use string concatenation in SQL queries with only naive single-quote escaping:

```java
// LocalRepositoryImpl.java - findRecordByPath()
path = path.replace("'", "''");  // Insufficient protection
List<Record> records = dataSource.getItems(COLUMN_PATH + " = '" + path + "'");

// DataSource.java - getRecords() - order parameter is user-controllable
Cursor cursor = queryLocal("SELECT * FROM " + tableName
    + " ORDER BY " + order       // Direct injection
    + " LIMIT " + AppConstants.DEFAULT_PER_PAGE
    + " OFFSET " + (page-1) * AppConstants.DEFAULT_PER_PAGE);
```

The `getItems(String where)` method accepts arbitrary WHERE clauses, and `getRecords()` accepts an unvalidated `order` parameter.

**Recommendation:** Use parameterized queries with `rawQuery(String, String[])` or Android's `query()` API with selection args.

---

### C3. Signing Credentials Committed to Version Control
**File:** `keystore.properties`
**CWE:** CWE-798 (Use of Hard-Coded Credentials)

```properties
storePassword=android
keyPassword=android
keyAlias=androiddebugkey
prodStorePassword=your_pass
prodKeyPassword=your_pass
prodKeyAlias=your_alias
```

The keystore properties file containing signing passwords is tracked in git. While the production values appear to be placeholders, the debug credentials are real. This file should never be in version control.

**Recommendation:** Add `keystore.properties` to `.gitignore`, use environment variables or CI/CD secrets for signing credentials, and rotate any exposed keys.

---

### C4. Debug Signing Credentials Hardcoded in build.gradle
**File:** `app/build.gradle` (lines 29-34)
**CWE:** CWE-798 (Use of Hard-Coded Credentials)

```gradle
signingConfigs {
    dev {
        storeFile file('key/debug/debug.keystore')
        storePassword 'android'
        keyAlias 'androiddebugkey'
        keyPassword 'android'
    }
}
```

While debug keystores are standard, hardcoding them in the build file checked into a public repository is poor practice.

---

## High Findings

### H1. Path Traversal in File Operations
**Files:** `FileUtil.java` (lines 535-564), `FileRepositoryImpl.java` (lines 192-214)
**CWE:** CWE-22 (Path Traversal)

File rename operations do not validate that the target path stays within the expected directory. The `renameFile()` method accepts untrusted names without canonicalization:

```java
public static boolean renameFile(File file, String newName, String extension) {
    File renamed = new File(file.getParentFile().getAbsolutePath()
        + File.separator + newName + AppConstants.EXTENSION_SEPARATOR + extension);
    // No validation that 'newName' doesn't contain "../"
}
```

Similarly, `AudioRecorder.java` accepts `outputFile` paths without validation in `startRecording()`.

**Recommendation:** Validate all file paths using canonical path comparison against allowed directories.

---

### H2. Unprotected Broadcast Receivers
**File:** `AndroidManifest.xml` (lines 115-120)
**CWE:** CWE-925 (Improper Verification of Intent by Broadcast Receiver)

Six broadcast receivers are declared without `android:exported="false"` or permission protection:

```xml
<receiver android:name=".WidgetReceiver" />
<receiver android:name=".app.RecordingService$StopRecordingReceiver" />
<receiver android:name=".app.PlaybackService$StopPlaybackReceiver" />
<receiver android:name=".app.DownloadService$StopDownloadReceiver" />
<receiver android:name=".app.DecodeService$StopDecodeReceiver" />
<receiver android:name=".app.moverecords.MoveRecordsService$StopMoveRecordsReceiver" />
```

Any app on the device can send broadcasts to stop active recordings, stop playback, or trigger widget actions. The `StopRecordingReceiver` is particularly concerning as it allows a malicious app to silently terminate an active recording.

**Recommendation:** Add `android:exported="false"` to all receivers, or use `LocalBroadcastManager`/explicit intents.

---

### H3. Intent Action Spoofing in Services
**Files:** `RecordingService.java` (lines 193-227), `PlaybackService.java` (lines 121-147), `DecodeService.kt` (lines 104-124), `MoveRecordsService.kt` (lines 97-113)
**CWE:** CWE-927 (Use of Implicit Intent for Sensitive Communication)

While services are marked `exported="false"`, they accept intent actions without permission verification. Combined with the exported widget receiver, this creates a chain where:
1. Malicious app sends broadcast to `WidgetReceiver`
2. `WidgetReceiver` starts `RecordingService` with record action
3. Recording starts/stops without user interaction

The `MoveRecordsService` is also concerning as it accepts arbitrary record ID arrays, potentially allowing unauthorized file operations.

---

### H4. Excessive Logging of Sensitive Information
**Files:** `FileUtil.java`, `AudioDecoder.java`, `FileRepositoryImpl.java`, and others
**CWE:** CWE-532 (Insertion of Sensitive Information into Log File)

Multiple locations log file paths, audio parameters, and error details:

```java
Log.d(LOG_TAG, "createFile path = " + path.getAbsolutePath() + " fileName = " + fileName);
Timber.v("old File: " + file.getAbsolutePath());
Timber.v("new File: " + renamed.getAbsolutePath());
Timber.e(e, "sampleRate = " + sampleRate + " channelCount = " + channelCount);
```

This exposes recording locations, filenames, and internal state through logcat.

**Recommendation:** Remove or guard all file path logging behind BuildConfig.DEBUG checks. Use `Timber.plant()` only in debug builds.

---

### H5. ProGuard Keep-All Rule Defeats Obfuscation
**File:** `app/proguard-rules.pro` (line 23)

```
-keep class com.dimowner.audiorecorder.** { *; }
```

This rule keeps all classes and members with original names, completely defeating the purpose of code obfuscation. Combined with `-keepattributes SourceFile,LineNumberTable`, the release APK is essentially unobfuscated.

**Recommendation:** Use targeted keep rules only for classes that require reflection or serialization.

---

### H6. Insecure Temporary File Creation
**File:** `FileUtil.java` (lines 378-408)
**CWE:** CWE-377 (Insecure Temporary File)

Files are created with user-supplied names using `File.createNewFile()` which does not provide atomic creation with restricted permissions. No use of `File.createTempFile()`.

---

### H7. Missing Input Validation in Audio Recording
**Files:** `AudioRecorder.java` (lines 67-100), `WavRecorder.java` (lines 87-139)
**CWE:** CWE-20 (Improper Input Validation)

Recording parameters (sample rate, bitrate, channel count, output file path) are accepted without bounds checking. The `WavRecorder` also has a potential buffer indexing issue when `bufferSize` is odd.

---

### H8. Exported Widget Receiver Without Permission
**File:** `AndroidManifest.xml` (lines 36-46)

```xml
<receiver android:name=".RecordingWidget" android:exported="true">
```

The recording widget is exported without permission protection, enabling broadcast injection attacks.

---

## Medium Findings

### M1. Unencrypted SQLite Database
**File:** `SQLiteHelper.java`
**CWE:** CWE-311 (Missing Encryption of Sensitive Data)

The `records.db` database stores recording metadata (file paths, timestamps, durations, waveform data as BLOBs) without encryption. On rooted devices or via backup extraction, all recording metadata is accessible in plaintext.

**Recommendation:** Consider using SQLCipher for database encryption.

---

### M2. Unencrypted SharedPreferences
**File:** `PrefsImpl.java`
**CWE:** CWE-311

All preferences (record counter, active record ID, migration timestamps, recording settings) are stored in plaintext SharedPreferences. While individually low-risk, they reveal user recording patterns.

**Recommendation:** Use `EncryptedSharedPreferences` for sensitive values.

---

### M3. Missing `android:allowBackup="false"`
**File:** `AndroidManifest.xml`

The `android:allowBackup` attribute is not set, defaulting to `true`. This allows all app data (including recordings database and preferences) to be extracted via ADB backup.

**Recommendation:** Add `android:allowBackup="false"` to the `<application>` tag.

---

### M4. PendingIntent Flags on Pre-Android M Devices
**Files:** `RecordingService.java`, `PlaybackService.java`, `DecodeService.kt`, `MoveRecordsService.kt`

`AppConstants.PENDING_INTENT_FLAGS` uses `FLAG_IMMUTABLE` only on Android M+. Pre-M devices receive mutable PendingIntents (flag value 0), which are vulnerable to intent tampering.

---

### M5. World-Readable Recording Storage
**Files:** `FileUtil.java`, `DownloadManager.kt`
**CWE:** CWE-276 (Incorrect Default Permissions)

Recordings stored in public directories (`Environment.getExternalStoragePublicDirectory()`) and exported downloads are readable by any app. Audio recordings are inherently sensitive data.

---

### M6. Improper File Deletion (Trash)
**File:** `LocalRepositoryImpl.java` (lines 312-352), `FileRepositoryImpl.java` (lines 164-170)

"Deleted" files are only renamed with a `.del` extension. They remain recoverable on disk. No secure wiping is performed.

---

### M7. Race Conditions in Timer/Thread Synchronization
**File:** `AppRecorderImpl.java` (lines 343-374)
**CWE:** CWE-362

Shared variables (`durationMills`, `updateTime`) are accessed from Timer threads without synchronization or volatile declarations.

---

### M8. Lint Errors Don't Abort Build
**File:** `app/build.gradle` (lines 77-79)

```gradle
lintOptions { abortOnError false }
```

Security-related lint warnings are silently ignored during builds.

---

## Low / Informational Findings

| Finding | Location | Note |
|---------|----------|------|
| Duplicate POST_NOTIFICATIONS permission | AndroidManifest.xml | Lines 4 and 19 |
| Exposed developer email | AppConstants.java:38 | `dmitriy.ponomarenko.ua@gmail.com` |
| Null pointer risk in FileUtil.deleteRecursive | FileUtil.java | `file.list()` can return null |
| Deprecated API usage | FileUtil.java, AudioRecorder.java | `getExternalStorageDirectory()` deprecated in API 29 |
| No file integrity checks on import | FileBrowserPresenter.java | Imported audio files not validated |

---

## Positive Security Observations

1. **No network access** - INTERNET permission is commented out, eliminating remote attack vectors
2. **Services properly unexported** - All services have `android:exported="false"`
3. **Current SDK versions** - compileSdk 34, targetSdk 34
4. **Up-to-date dependencies** - No known CVEs in declared dependencies
5. **Firebase/analytics disabled** - No tracking or telemetry code active
6. **Scoped storage support** - Proper handling for Android 10+
7. **Release build optimizations** - minifyEnabled and shrinkResources are enabled
8. **FileProvider used for sharing** - Content URIs used instead of `file://` URIs (though config is too broad)

---

## Remediation Priority

### Immediate (P0) - Before Next Release
1. Restrict `provider_paths.xml` to app-specific directories only
2. Replace all raw SQL with parameterized queries (or migrate to Room)
3. Remove `keystore.properties` from git and add to `.gitignore`
4. Add `android:exported="false"` to all broadcast receivers
5. Add `android:allowBackup="false"` to manifest

### High Priority (P1)
6. Implement canonical path validation for all file operations
7. Remove/guard file path logging in production builds
8. Refine ProGuard rules to actually obfuscate code
9. Validate all intent extras and recording parameters
10. Protect widget receiver with permission

### Medium Priority (P2)
11. Encrypt SQLite database with SQLCipher
12. Use EncryptedSharedPreferences for sensitive values
13. Fix thread synchronization in AppRecorderImpl
14. Use unique PendingIntent request codes
15. Enable strict lint checking

### Low Priority (P3)
16. Implement secure file deletion (overwrite before delete)
17. Add file integrity validation on import
18. Replace deprecated API calls
19. Fix null pointer edge cases in FileUtil

---

## Conclusion

AudioRecorder is a well-structured Android app with a minimal attack surface due to its offline-only nature. However, it has significant local security weaknesses - particularly in file access control (FileProvider), data layer security (SQL injection), and component protection (broadcast receivers). The most impactful changes would be restricting the FileProvider paths, parameterizing SQL queries, and marking all broadcast receivers as non-exported. These three changes alone would address the majority of the critical and high-severity findings.
