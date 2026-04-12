# APK Size Investigation: jellyfin-audio-player (Fintunes)

**Repository:** https://github.com/leinelissen/jellyfin-audio-player
**Date:** 2026-04-12
**Current APK size:** 120.7 MB (v2.4.6), 143.4 MB (v2.5.0-beta.2)
**Current AAB size:** 86.1 MB (v2.4.6)

## Tech Stack Overview

| Component | Value |
|-----------|-------|
| React Native | 0.83.1 |
| React | 19.2.3 |
| Architecture | New Architecture enabled (Fabric + TurboModules) |
| JS Engine | Hermes (enabled) |
| State Management | Redux Toolkit + Redux Persist |
| Navigation | React Navigation v7 (native-stack + bottom-tabs) |
| Styling | styled-components |
| Build System | Fastlane + Gradle |
| Error Tracking | Sentry |

## Executive Summary

The APK is extremely large (120-143 MB) primarily because:

1. **No ABI splits** -- native code for all 4 CPU architectures bundled into a single APK
2. **Skia rendering engine** -- adds ~14-16 MB per architecture for a single visual effect
3. **ProGuard/R8 disabled** -- Java/Kotlin code is not minified or shrunk
4. **Multiple heavy native modules** -- each duplicated 4x across architectures

With all recommended fixes, the APK could likely be reduced to **30-40 MB** for a single-architecture APK, or the AAB (used for Play Store) could deliver **~25-35 MB** per device.

---

## Detailed Findings

### 1. NO ABI SPLITS (Critical -- Estimated savings: 70-80%)

**File:** `android/gradle.properties` (line 28)
```properties
reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64
```

**File:** `android/app/build.gradle` -- No `splits` or `enableSeparateBuildPerCPUArchitecture` block exists.

The APK bundles native libraries for ALL four CPU architectures. Modern Android devices are almost exclusively arm64-v8a. The x86 and x86_64 architectures are only needed for emulators. Even armeabi-v7a (32-bit ARM) is becoming rare.

**Each architecture adds a full copy of:**
- React Native core + Hermes (~15-18 MB)
- Skia engine (~14-16 MB)
- Reanimated, gesture-handler, worklets, SVG, etc. (~4-6 MB)
- Total: ~33-40 MB per architecture

**With 4 architectures: ~130-160 MB of native code alone.**

**Fix:** Add ABI splits to `android/app/build.gradle`:
```gradle
android {
    splits {
        abi {
            reset()
            enable true
            universalApk false
            include "armeabi-v7a", "arm64-v8a"
            // Omit x86/x86_64 -- only needed for emulators
        }
    }
}
```

Or better yet, **publish as an AAB (Android App Bundle)** to the Play Store, which already happens for their `release` and `beta` Fastlane lanes. The `build` lane (used in CI) uses `assemble` which produces a universal APK. The GitHub release APK is therefore unnecessarily large.

For F-Droid / sideloading, produce per-ABI APKs.

### 2. SKIA RENDERING ENGINE (High Impact -- Estimated savings: ~14-16 MB per arch)

**Dependency:** `@shopify/react-native-skia` v2.4.14

**Usage:** Only ONE component -- `src/components/CoverImage.tsx` (line 3):
```typescript
import { Canvas, Blur, Image as SkiaImage, useImage, Offset, Mask, RoundedRect, Shadow } from '@shopify/react-native-skia';
```

This is used to render album cover images with blur effects, rounded corners, and shadows. The entire Skia rendering engine (a full 2D graphics library including SVG, text layout, animations via Skottie, paragraph layout, unicode support) is bundled for what is essentially:
- Image rendering with blur
- Rounded rectangle masking
- Drop shadows

The Skia postinstall script downloads prebuilt static libraries for 4 Android architectures:
- `skia-android-arm` (15.1 MB compressed)
- `skia-android-arm-64` (14.5 MB compressed)
- `skia-android-arm-x64` (16.3 MB compressed)
- `skia-android-arm-x86` (14.6 MB compressed)

These contain: libskia.a, libsvg.a, libskshaper.a, libskparagraph.a, libskunicode_core.a, libskunicode_icu.a, libskottie.a, libsksg.a, libjsonreader.a, libpathops.a

**Fix options:**
- **Replace with React Native's built-in capabilities:** Use `react-native-fast-image` (already a dependency!) with CSS-like `borderRadius`, plus `react-native-blur` (already a dependency!) for the blur effect. Shadow can be done with `react-native-shadow-2` (also already a dependency!) or platform shadow APIs.
- **Use `expo-blur` or `@react-native-community/blur`** for the blur effect, which are much lighter.
- If Skia is truly needed, explore `@aspect-build/rules_js` or custom Skia builds with only the needed features compiled in.

### 3. PROGUARD/R8 DISABLED (Medium Impact -- Estimated savings: 5-15 MB)

**File:** `android/app/build.gradle` (line 64)
```gradle
def enableProguardInReleaseBuilds = false
```

**Line 122:**
```gradle
minifyEnabled enableProguardInReleaseBuilds
```

With ProGuard/R8 disabled, all Java/Kotlin bytecode from ALL dependencies is included in the APK without shrinking, optimization, or obfuscation. This includes unused classes from React Native, navigation, Redux, and all other Java/Kotlin libraries.

**Fix:** Enable R8 minification:
```gradle
def enableProguardInReleaseBuilds = true
```

Note: The existing `proguard-rules.pro` file is essentially empty (only comments). You will need to add keep rules for libraries that use reflection. Start with:
```proguard
# React Native
-keep class com.facebook.react.** { *; }
-keep class com.facebook.hermes.** { *; }
-keep class com.facebook.jni.** { *; }

# Track Player
-keep class com.doublesymmetry.** { *; }

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}
```

### 4. LARGE PLACEHOLDER IMAGES (Low Impact -- Estimated savings: ~1.5 MB)

**Files:**
- `src/assets/images/empty-album-dark.png` -- 1,028,961 bytes (1 MB)
- `src/assets/images/empty-album-light.png` -- 947,892 bytes (926 KB)

These are placeholder images shown when no album art is available. Nearly 2 MB for placeholder images is excessive.

**Fix:**
- Compress with tools like `pngquant` or `optipng` -- could reduce by 50-80%
- Consider using vector (SVG) placeholders instead
- Or generate programmatically with a gradient/icon

### 5. DUPLICATE FONT FILE (Very Low Impact -- Estimated savings: ~785 KB)

**Files:**
- `src/assets/fonts/Inter-VariableFont_slnt,wght.ttf` (785 KB)
- `android/app/src/main/assets/fonts/Inter-VariableFont_slnt,wght.ttf` (785 KB)

The font is duplicated. The `react-native.config.js` asset linking points to `src/assets/fonts/`, while the Android copy may be manual.

**Fix:**
- Remove the duplicate in `android/app/src/main/assets/fonts/`
- Or subset the font to only include used weights/characters using `fonttools`

### 6. UNUSED / UNDERUSED DEPENDENCIES (Low-Medium Impact)

| Dependency | Issue | Action |
|-----------|-------|--------|
| `react-native-shadow-2` | Zero imports in source code | Remove entirely |
| `lodash` (1.7 MB) | Only 6 functions used (xor, intersection, shuffle, debounce, chunk, groupBy) | Replace with `lodash-es` or individual `lodash.debounce` packages, or use native JS alternatives |
| `react-airplay` | Only used in iOS-specific file (`Casting.ios.tsx`) | Verify it's not auto-linked on Android; if so, exclude from Android build |
| `react-native-collapsible` | Used once (Sentry settings) | Consider inline replacement |
| `react-native-webview` | Used once (CredentialGenerator for server auth) | Acceptable, but heavy for single use |

### 7. STYLED-COMPONENTS RUNTIME OVERHEAD (Low Impact on APK, High on Runtime)

Used in 48 files across the codebase. `styled-components` includes a CSS parser and runtime template processing. For React Native, consider migrating to:
- `StyleSheet.create()` (zero overhead)
- `nativewind` / Tailwind-based approach
- `tamagui` (compile-time optimization)

This affects JS bundle size more than APK size but still contributes.

### 8. SENTRY (Medium -- Consider Build-time Impact)

`@sentry/react-native` (28 MB npm package) includes native SDKs and source map tooling. The `sentry.gradle` plugin is conditionally included:

**File:** `android/app/build.gradle` (lines 57-59)
```gradle
if (System.getenv("DISABLE_SENTRY_SOURCEMAP_UPLOAD") != "true") {
    apply from: "../../node_modules/@sentry/react-native/sentry.gradle"
}
```

Sentry's native Android SDK adds native crash handling code. This is a legitimate dependency but should be verified that debug symbols and source maps aren't accidentally included in the release APK.

---

## Prioritized Action Plan

### Tier 1: Quick Wins (Estimated combined savings: 70-90 MB on APK)

| # | Action | Estimated Savings | Effort |
|---|--------|-------------------|--------|
| 1 | **Enable ABI splits** or build per-architecture APKs for sideloading | 70-80% of APK size | Low |
| 2 | **Enable ProGuard/R8** | 5-15 MB | Low-Medium |
| 3 | **Remove react-native-shadow-2** (unused) | Negligible directly, cleaner deps | Trivial |

### Tier 2: Significant Refactoring (Estimated additional savings: 14-16 MB per arch)

| # | Action | Estimated Savings | Effort |
|---|--------|-------------------|--------|
| 4 | **Replace @shopify/react-native-skia** with lighter alternatives | ~14-16 MB per arch | High |
| 5 | **Compress placeholder images** | ~1.5 MB | Low |
| 6 | **Replace full lodash with individual functions** | ~0.5-1 MB JS bundle | Low-Medium |

### Tier 3: Long-term Optimization

| # | Action | Estimated Savings | Effort |
|---|--------|-------------------|--------|
| 7 | **Subset Inter font** to only needed weights | ~400-600 KB | Medium |
| 8 | **Audit styled-components** usage, consider lighter alternative | JS bundle reduction | High |
| 9 | **Limit architectures** to arm64-v8a only (drop armeabi-v7a for newer min SDK) | ~33-40 MB | Low (policy decision) |
| 10 | **Review Sentry** configuration for debug symbol stripping | Variable | Low |

---

## Expected Results After Optimization

### Current State
- Universal APK: **120-143 MB** (all 4 architectures)

### After Tier 1 (ABI splits + ProGuard)
- Per-architecture APK: **30-40 MB** each
- AAB download size (Play Store): **~25-35 MB** per device

### After Tier 1 + 2 (remove Skia + compress assets)
- Per-architecture APK: **18-28 MB** each
- AAB download size (Play Store): **~15-22 MB** per device

### Comparison
- Typical audio player app: 15-30 MB
- Spotify: ~40 MB (but vastly more features)

---

## Appendix: File Locations Referenced

| File | Key Finding |
|------|------------|
| `android/app/build.gradle:64` | ProGuard disabled |
| `android/app/build.gradle:79-126` | No ABI splits configured |
| `android/gradle.properties:28` | All 4 architectures enabled |
| `android/gradle.properties:39` | Hermes enabled (good) |
| `android/gradle.properties:35` | New Architecture enabled |
| `package.json:28` | @shopify/react-native-skia dependency |
| `src/components/CoverImage.tsx:3` | Only Skia usage |
| `src/assets/images/empty-album-dark.png` | 1 MB placeholder |
| `src/assets/images/empty-album-light.png` | 926 KB placeholder |
| `android/app/proguard-rules.pro` | Empty ProGuard rules |
| `android/app/src/main/AndroidManifest.xml` | Clean, no unnecessary permissions |
