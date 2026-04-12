APK size for the "jellyfin-audio-player" (Fintunes) app has increased by approximately 40 MB across six releases, largely due to bundling native code for all CPU architectures (no ABI splits), inclusion of the heavy Skia rendering engine for minimal graphical effects, and disabled code shrinking/minification (ProGuard/R8). The universal APK currently ranges from 120–143 MB, but with targeted optimizations—such as enabling ABI splits, replacing Skia with lighter alternatives, compressing assets, and trimming unused dependencies—the app could achieve a per-architecture APK size of 18–28 MB or an AAB download of 15–22 MB per user. The investigation outlines actionable steps for immediate and long-term improvement, providing specific build system and dependency changes that would bring the app in line with typical audio player apps. Repository details and further reference: [GitHub Repository](https://github.com/leinelissen/jellyfin-audio-player), [React Native documentation](https://reactnative.dev/docs/signed-apk-android).

**Key Findings:**
- No ABI splits: All architectures' native code included (accounts for ~70-80% APK size).
- Skia rendering engine: Adds ~14–16 MB per architecture, used for basic UI effects.
- Disabled ProGuard/R8: Leads to bloated Java/Kotlin bytecode.
- Unused/duplicate assets & fonts: Unneeded files add several MB.
- Removing Skia and enabling ABI splits are the highest-impact steps.
