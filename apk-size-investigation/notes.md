# APK Size Investigation Notes - jellyfin-audio-player (Fintunes)

## Investigation Process

### Step 1: Clone and initial file examination
- Cloned https://github.com/leinelissen/jellyfin-audio-player (shallow clone)
- Examined: package.json, android/app/build.gradle, android/build.gradle, android/gradle.properties,
  babel.config.js, metro.config.js, app.json, AndroidManifest.xml, react-native.config.js, Podfile

### Step 2: Confirmed APK sizes from GitHub releases
- v2.5.0-beta.2: 143.4 MB APK
- v2.5.0-beta.1: 128.0 MB APK
- v2.4.6: 120.7 MB APK, 86.1 MB AAB
- v2.4.5: 114.1 MB APK
- v2.4.4: 103.5 MB APK
- Trend: APK has been growing significantly with each release

### Step 3: Key findings from config files

#### ABI Splits: NOT enabled
- No `enableSeparateBuildPerCPUArchitecture` found anywhere
- No `splits { abi { ... } }` block in build.gradle
- `reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64` in gradle.properties
  means ALL FOUR architectures are bundled into a single universal APK
- This is the #1 reason for the bloated APK

#### ProGuard/R8: DISABLED
- `def enableProguardInReleaseBuilds = false` on line 64 of android/app/build.gradle
- This means Java/Kotlin bytecode is NOT minified or shrunk
- Unused Java classes from libraries remain in the APK

#### Hermes: ENABLED (good)
- `hermesEnabled=true` in gradle.properties
- This is actually better than JSC for bundle size

#### New Architecture: ENABLED
- `newArchEnabled=true` -- using Fabric/TurboModules
- This can add some native code overhead but is the modern path

### Step 4: Heavy native dependencies identified

Modules with C++/native code (CMakeLists.txt present):
1. **@shopify/react-native-skia** -- THE biggest contributor. Downloads ~60 MB of prebuilt
   Skia static libraries (libskia.a + support libs) across 4 architectures. Each arch's
   Skia libs are ~14-16 MB compressed. Only used in ONE component (CoverImage.tsx) for
   blur effects and rounded images.
2. **react-native-reanimated** -- 5.5 MB npm module, has native C++ code
3. **react-native-gesture-handler** -- native C++ code
4. **react-native-svg** -- 4.4 MB npm module, has native JNI code
5. **react-native-screens** -- native code
6. **react-native-worklets** -- native C++ code
7. **react-native-nitro-modules** -- native C++ code
8. **@iternio/react-native-auto-play** -- native C++ code (Android Auto)
9. **react-native-safe-area-context** -- native JNI code

Modules without their own native code (Java/Kotlin only or JS-only):
- react-native-track-player (Java/Kotlin, no C++ cmake)
- @d11/react-native-fast-image (Java, no cmake)
- react-native-webview (Java, no cmake)
- @sbaiahmed1/react-native-blur (Java, no cmake)
- @sentry/react-native (uses Java SDK, 28 MB npm but mostly JS/tooling)

### Step 5: Asset analysis
- Font: Inter-VariableFont (785 KB) duplicated in both src/assets/fonts/ and android/app/src/main/assets/fonts/
- Images: empty-album-dark.png (1 MB) and empty-album-light.png (926 KB) -- large placeholder images
- SVG icons: ~37 SVG files in src/assets/icons/ (small, good)
- App launcher icons: standard set across density buckets (~154 KB total)
- docs/ and fastlane/ images are NOT included in APK (not a concern)

### Step 6: JS dependency analysis
- **lodash**: full package imported (1.7 MB npm), only uses xor, intersection, shuffle, debounce, chunk, groupBy
- **styled-components**: used in 48 files, adds runtime overhead and bundle size
- **react-native-shadow-2**: listed as dependency but NOT imported anywhere in src/
- **date-fns**: used with tree-shakeable imports (good)
- **@reduxjs/toolkit**: 6.9 MB npm, large but essential for state management

### Step 7: Unused/questionable dependencies
- **react-native-shadow-2**: zero imports found -- dead dependency
- **react-airplay**: only used in iOS file (Casting.ios.tsx) -- may still be linked on Android
- **react-native-collapsible**: only used once (Sentry settings accordion)

### Key Learning
The universal APK bundles native code for 4 CPU architectures. Each architecture gets its own
copy of Hermes, React Native core libs, Skia, Reanimated, and other native modules. Skia alone
is ~14-16 MB per architecture. With 4 architectures, that's ~60 MB just for Skia.
