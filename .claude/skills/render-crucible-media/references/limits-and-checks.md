# Limits and checks

## Server options (the user sets them, not the job)

| Option | Meaning |
|---|---|
| `--backend gpu` or `cpu` | gpu is the default and fast; cpu is SwiftShader, for machines without hardware WebGL, much slower. |
| `--memory <32..4096>` | Render-target budget in MiB, default 192, at most half of the machine's RAM. It also sets the job memory guard (Node RSS max(512, budget + 128) MiB; browser heap max(256, two thirds of budget) MiB) and the native tracer allowance. A 1920x1080 frame needs about 175 MiB at 4 samples (measured), so use 256 for it and more for textured scenes. |
| `--jobs <abs dir>` | Private store for job files. Required for any job. |
| `--ffmpeg <abs path>` | Needed for MP4 when ffmpeg is not on PATH. |
| `--audio <abs dir>` | The folder `settings.audio.file` names a file from. |
| `--gpu-queue <abs exe or JSON array>` and `--gpu-queue-wait` | Optional queue command that looks, reviews, bakes and render jobs wait for before they take the GPU, so the server can share a card. |

`scene_capabilities` reports the backend, memory, job limits and the job UUIDs it holds after a restart. Check it
before you promise a size or a sound track.

## Job limits

- Width and height 64 to 1920 each (an image job up to 3840, at most 3840x2160), within the memory budget. A square frame fits up to 1440 for stills and video
  and 2880 for an image. A video or stills job that does not fit is reduced, and an image job larger than 1920x1080 is refused with the --memory it needs; the result reports
  the actual dimensions, so say them. `metrics.report.fallbacks` says when a frame was cut.
- Video: at most 60 s and 900 frames (60 s needs 15 fps or less), even dimensions, shots up to 64 and 60 s total. A stills job writes 2 to 300 frames
  (`stillCount`, default 8).
- Time allowed: 60 s plus 2 s per frame (more above 1024x576), at most 30 minutes, counted from when the render starts. The wait behind other calls
  (and a shared GPU queue) is bounded apart, at 5 minutes. A job over its deadline under a shared GPU fails with advice to submit again. A path traced job has its own
  `maxSeconds` per frame.
- Output files of one job: 128 MiB in all, 12 MiB a frame (48 MiB for `png16` or `exr`); a job over it fails with that limit.
- Placed assets and `.67vg` grid files of one scene count together toward a 64 MiB cap; a scene over it fails with the cap message.
- A job leases the single preview renderer. While it runs, `scene_create`, `scene_create_asset`, `scene_apply`, `mesh_edit`, `mesh_stack`, `scene_look`,
  `scene_review`, `scene_checkpoint`, `scene_restore`, `scene_release_checkpoint`, `scene_export_glb`, `scene_export_web`, `scene_dispose` and `scene_render_submit`
  fail with the running job's ID and frame count; call `scene_render_status` with that `jobId`, or `scene_render_cancel`. Inspection, recipe export and the
  job tools stay available. Plan one job at a time.

## Check the result

1. `scene_render_result` lists files; SHA-256 hashes come with `response_format: "detailed"`. Compare `metrics` frame count and duration with what you asked.
2. Look at one frame: the PNG itself, or for video a still of the same `motion.start` (the timeline seek gives the same
   pixels as the frame inside the video).
3. For video, verify with ffprobe when it is installed:
   `ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration,size -of json <file>`.
4. With audio, read `metrics.sync` (`differenceSeconds` under 0.05). It proves alignment, not that the sound is good.
5. For a path-traced film, measure flicker before anyone sees it. A still can look clean while the film shimmers: OIDN
   leaves slow blotches that change every frame. Take one second of frames and compute the mean absolute temporal
   second difference `|f[t+1] - 2 f[t] + f[t-1]|` in 8-bit grey. Smooth camera motion cancels in it; noise stays. A
   still-looking film scores about 1. Above 2, fix it before showing anyone: blend each denoised frame into the
   reprojected history of the frames before it (first-hit depth and the two cameras). More samples alone did not fix
   it in a room lit through one window: 1024 spp still scored 2.
6. A path traced still from `backend: "native"` can differ from the raster look: put a `draft` still of the same scene beside it before trusting either. Open reports:
   an `environment.skyMap` sun may sit near world -z instead of along `sunDirection` (codepawl/cook#65), and a native trace of an unlit night scene may ignore
   environment lighting and exposure and render bright (#1833). If the two stills disagree on the sun or the exposure, say so and file the issue.
7. The framebuffer figure is an allocation model, not total VRAM, and Node and browser heap samples do not cover every
   allocation. Report them as estimates.

## Speed

Capture cost dominates video. `metrics.captureSeconds` and `renderSeconds` show where the time went. Hardware
`nvenc` encoding in the page was measured about 7 times faster than screenshots on one RTX 3060 (1280x720, 4,488 frames:
20.6 s against 139.6 s); that is one machine, so measure before you promise a time. Machine load changes timings, so
report a range, not one number.
