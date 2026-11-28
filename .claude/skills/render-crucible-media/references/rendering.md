# Rendering commands

Run these commands from the repository root.

```powershell
node scripts/render-media.mjs --kind image --scene nature --backend gpu --preset high --output artifacts/nature.png
node scripts/render-media.mjs --kind image --scene object --backend cpu --preset cpu --output artifacts/object-cpu.png
node scripts/render-media.mjs --kind stills --scene film --backend gpu --preset balanced --output artifacts/stills/frame.png
node scripts/score.mjs
node scripts/render-media.mjs --kind video --scene film --backend gpu --preset balanced --encoder gpu --output artifacts/critical.mp4
```

The available scenes are `object`, `nature`, `film`, `motion`, `view2d`, `assets`, `modeling` and `file` (`--scene file --config <scene.json>`; `--config`, `--camera` and `--root` need it).
GPU rendering selects hardware WebGL through Chrome. CPU rendering requests ANGLE SwiftShader.
The CPU exporter verifies that the selected backend reports SwiftShader.

| Preset | Dimensions | Samples | FPS | Target budget |
| --- | --- | ---: | ---: | ---: |
| `preview` | 960 × 540 | 2 | 24 | 256 MiB |
| `balanced` | 1280 × 720 | 4 | 24 | 384 MiB |
| `high` | 1920 × 1080 | 4 | 24 | 512 MiB |
| `cpu` | 640 × 360 | 1 | 12 | 192 MiB |

The memory planner includes color/depth targets, resolve storage, staging frames, shadows and uploaded geometry.
The browser context remains an additional allocation outside that estimate.
The offline exporter uses one capture frame at a time.
It disposes the previous scene before uploading the next scene.

`--memory` controls the target budget. `--width`, `--height`, `--fps` and `--duration` override preset values.
For object images, `--assembly 1` explodes the model. The default value `0` assembles it.

Each option requires a value. Dimensions range from 64 to 4096 pixels.
Memory ranges from 32 to 1024 MiB (8192 for `--scene file`, which defaults to the budget in its config). Duration ranges from 0.1 to 240 seconds, and `--fps` from 1 to 60.
The limits of MCP render jobs are a different set: see `limits-and-checks.md`.

`--encoder` is `auto` (the default for the GPU backend: NVENC when the probe finds it, else libx264), `cpu` or `gpu`, independently of the renderer backend.
`--encoder gpu` requires NVENC; a failed encoder stops the export and reports its error. The renderer does not silently replace a failed hardware export with a lower-quality output.

Video capture cost (measured on an RTX 3060 at 1280x720 on a loaded machine, 20 s of the film, 480 frames, NVENC).
Screenshots (`--capture jpeg`) cost 28.8 ms a frame to capture and 7.4 ms to draw, 21.5 s for the clip.
Every report has `stageTimings.captureSeconds` and `renderSeconds`.
`--capture auto`, the default for video, uses WebCodecs and falls back to screenshots (never raw readback, which is slower) when the browser cannot hardware encode the size or `--encoder cpu` or `--backend cpu` is requested. `--capture webcodecs` fails instead of falling back, `--capture jpeg` and `--capture png` keep screenshots, and `--capture raw` keeps the `readPixels` and WebSocket path as opt in. The hardware encoder is the browser's, so the bitstream can differ between machines and drivers even though the frames are deterministic, which is why `--encoder cpu` keeps libx264 on screenshots.
Why WebCodecs is the default (measured on one RTX 3060, 1280 by 720, the 4,488 frame film, one evening): in-page encoding took 20.6 s in all (draw 2.0 ms and capture 2.2 ms a frame), screenshots 139.6 s, and raw `readPixels` over a WebSocket 405.1 s, because moving 3.7 MB of pixels to Node cost 27 to 52 ms a frame. Only 5 to 60 kB of encoded chunks a frame cross the socket, and `ffmpeg -c copy` muxes them with the audio. The output is BT.709 limited range.
A decoded raw frame matches the PNG seek of the same time at 41.0 dB PSNR on SwiftShader (`npm run smoke:capture-parity`).

`scripts/score.mjs` generates the original film score.
The `--audio <path>` option selects an existing score.
Only `film` selects the CRITICAL score automatically.
Do not use movie dialogue, footage or music without authorization.

```powershell
ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames,color_space:format=duration,size -of json artifacts/critical.mp4
```

Inspect the sidecar `<output>.json` for backend, estimated allocation, process memory, frame queue and graphics errors.
The process guard stops Node above 512 MiB and sampled browser JavaScript heap above 256 MiB.
Heap samples do not establish peak browser RSS or total VRAM use.

## Animation, shorts and assets

```powershell
node scripts/render-media.mjs --kind video --scene motion --aspect portrait --backend gpu --encoder gpu --output artifacts/short.mp4
node scripts/render-media.mjs --kind image --scene view2d --aspect square --backend cpu --preset cpu --output artifacts/poster.png
node scripts/render-media.mjs --kind video --scene assets --asset model.glb --start 0 --duration 2 --output artifacts/model.mp4
```

`--aspect` accepts `landscape`, `portrait` or `square`. Explicit width and height override preset dimensions.
`--start` selects the first video sample. A scene duration limits the selected range.
`--asset` accepts a local GLB of at most 32 MiB and requires `--scene assets`.
The importer reports unsupported features before capture.

A reusable viewer exposes `window.__scene = { renderer, renderAt, duration, pause }`.
The exporter prioritizes this interface and samples absolute scene time.
The JSON report includes negotiated HDR and MSAA capabilities, alongside estimated allocation.
