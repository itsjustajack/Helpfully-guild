# Make Pocket smarter with 14 free projects

> **Jack's answers, 10 Nov:** no voice (typing is fine); PC model is qwen2.5:7b; the phone needs a model that runs on it. **Final phone pick after a second check: Qwen3-4B-Instruct-2507 Q4_K_M (2.5 GB, Apache-2.0).** Qwen's own table shows Qwen3.5-2B (non-thinking) at IFEval 61.2, below today's Llama-3.2-3B at 77.4, while Qwen3-4B-2507 scores 83.4 ([Qwen card](https://huggingface.co/Qwen/Qwen3.5-0.8B), [unsloth GGUF](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF), [Llama figure](https://insiderllm.com/guides/best-models-under-3b-parameters/)). It never 'thinks out loud', loads in Pocket's current llama.cpp, and fits the S23 FE's 8 GB. It is likely about a third slower than today's model (estimated); if too slow, fall back to Qwen3.5-2B. The model section below is kept for the record only.

Bottom line: the biggest win for the least work is a **newer, smaller phone model** (Qwen3.5-2B or Gemma 4 E2B, both Apache-2.0 GGUFs that the existing llama.cpp helper should load) plus a **one-tap "get the phone AI" download** modelled on PocketPal AI. After that, the best additions are helpers that **find the right note** (chromem-go with Ollama embeddings on the PC), a **tray icon, pop-up hotkey and Windows reminders** on the PC, **speaking a brain dump** (sherpa-onnx or whisper.cpp), and a safe **phone-to-PC share by file or QR code** built mostly from Pocket's own code. Every pick below has a permissive licence (MIT, Apache-2.0, BSD, ISC or MPL-2.0), is actively kept, needs no API key and runs offline. Confidence is **medium**: licences, upkeep and features were read from each project's own pages, but nothing was built or speed-tested on Jack's Galaxy S23 FE or RTX 3060. The method was the deep-research-plus skill: four parallel researchers, one per angle, with notes in `notes/`.

Already picked for 1.4 and not repeated here: olebedev/when, rrule-go, goldmark, strutil, Lucide.

## A newer model will help the phone more than a faster engine

Google's own LiteRT-LM figures show a phone's graphics chip mostly speeds up **reading the prompt (4–7× faster)**, while **writing the answer stays about the same** ([LiteRT-LM overview](https://developers.google.com/edge/litert-lm/overview)). No source showed any engine beating plain CPU on the Exynos 2200 that most S23 FE phones carry. So the cheapest fix for Pip feeling "stupid" on the phone is the model, not the engine.

| Pick | What it adds | Licence | Kept up? |
|---|---|---|---|
| **Qwen3.5-2B GGUF (Q4_K_M)** | Newer and smaller (1.28 GB vs 2 GB today); turn its "think first" mode off ([HF](https://huggingface.co/NobodyWho/Qwen_Qwen3.5-2B-GGUF)) | Apache-2.0 | 2026 model |
| **ggml-org/gemma-4-E2B-it-GGUF** | Google's newest small model, no login needed, 2.84 GB at Q4_0 ([HF](https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF)) | Apache-2.0 ([Google](https://opensource.googleblog.com/2026/03/gemma-4-expanding-the-gemmaverse-with-apache-20.html)) | 2026 model |
| **a-ghorbani/pocketpal-ai** (borrow the design) | One button, one fixed file, size warning on mobile data, resumes a broken download, checks the file isn't corrupt, then offline for good | MIT, 9.1k stars, pushed 2026-11-09 | Yes |
| **google-ai-edge/LiteRT-LM** (trial later) | Optional faster engine with graphics/AI-chip use and CPU fallback; needs its own model format | Apache-2.0, pushed 2026-11-10 | Yes |

A download button needs Pocket's first Android permission (internet). Android grants it at install without asking, but it breaks today's "no permissions at all" rule, so Jack should say yes first. The alternative is shipping the model inside a ~2 GB APK. No head-to-head scores exist for these models on task-splitting, so the build should test both against 20–30 of Jack's real brain dumps (**estimated** best approach).

## Helpers can find the right note, not just the newest

| Pick | What it adds | Licence | Notes |
|---|---|---|---|
| **philippgille/chromem-go** | Bots pick the notes that match the question, using Ollama's embed endpoint on the PC; saves to one file | MPL-2.0, 1,076 stars, pushed 2026-09-06 | Pure Go, no other deps, go 1.21 |
| **sahilm/fuzzy** | Finds tasks and notes even with typos (also the phone's fallback, with a hand-written keyword ranker) | MIT, 1,454 stars, pushed 2026-06-24 | Pure Go |

Rejected: bleve (needs go 1.25, ~37 deps, a folder index) and Ollama's own Go client, which reads `OLLAMA_HOST` and could route round Pocket's local-only rule.

## The PC can stay ready without a background service

| Pick | What it adds | Licence | Notes |
|---|---|---|---|
| **fyne-io/systray** | Tray icon: close the window, Pocket stays ready so reminders can fire | Apache-2.0, pushed 2026-10-24 | Windows code uses x/sys only; must be tested beside the WebView2 window loop |
| **golang.design/x/hotkey** | One key press anywhere opens Capture | MIT, pushed 2026-09-26 | go 1.24, one small dep |
| **git.sr.ht/~jackmordaunt/go-toast/v2** | Real Windows reminder pop-ups that open Pocket when clicked | MIT/Unlicense | Last release seen 2025-01; avoid go-toast/toast, which runs PowerShell with ExecutionPolicy Bypass for every pop-up |
| **arran4/golang-ical** | "Add to calendar": export tasks with dates to an .ics file | Apache-2.0, pushed 2026-10-18 | Pure Go |

Single-instance lock and start-with-Windows are about 30 lines each with x/sys, so write them rather than add a library (**estimated**).

## Talking and photos are possible offline, with one licence trap

The maintained Piper voices and espeak-ng are **GPL-3.0**, which would force Pocket's code open. **k2-fsa/sherpa-onnx** (Apache-2.0, 15.8k stars, pushed 2026-11-10) removed espeak-ng and piper-phonemize in its 2.0.0 release, so it is the clean route for both listening and reading answers aloud, with Go and Android bindings. **ggml-org/whisper.cpp** (MIT, 55k stars) is the alternative that fits the llama.cpp build Pocket already has and can use the RTX 3060; models run from 75 MiB (tiny) to 466 MiB (small). Moonshine models (MIT for English) give live words as you talk, run inside sherpa-onnx.

For "photo of a list or screenshot into a brain dump", **RapidAI/RapidOCR** (Apache-2.0, pushed 2026-11-10) uses PaddleOCR's models; **tesseract** (Apache-2.0) is the simple fallback. None of them reads handwriting well.

Speaking on the phone needs the microphone permission, so this also needs Jack's yes. No speed figures exist for the S23 FE.

## Phone-to-PC sharing is mostly Pocket's own code

automerge-go needs cgo, which breaks the phone's pure-Go core, so the merge should be ~100 lines of Pocket's own Go: keep the newer copy of each item by its existing id, use a change counter rather than the clock, and keep small markers for deleted items (**estimated**). Libraries that help around it:

| Pick | What it adds | Licence |
|---|---|---|
| **FiloSottile/age** | Locks a share file with the safety word | BSD-3-Clause, 24k stars (current version needs go 1.25) |
| **yeqown/go-qrcode** | PC shows a pairing QR code (or a few tasks) | MIT, pushed 2026-08-06 |
| **cozmo/jsQR** | Phone reads that QR from a photo or screenshot, offline, no camera permission | Apache-2.0, pushed 2026-05-15 |

One QR code holds only about 2–3 KB, so it suits pairing and a handful of tasks, not a whole save.

## Small screen add-ons and ideas worth copying

**SortableJS** (MIT, 31k stars) for drag-to-reorder tasks, **DOMPurify** (Apache-2.0/MPL-2.0, 17.5k stars) to keep Bot and pasted text safe to show, and **canvas-confetti** (ISC) for a gentle burst when the day is done (worker mode off for the strict CSP, off in Calm mode and for reduced motion). Phone buzz should use Android's own `performHapticFeedback`, which needs no permission.

Ideas, not code: Goblin Tools' **"break it down more" with a 1–3 chilli setting** for how small the steps are; Super Productivity's (MIT) **short focus timer with a gentle break nudge**; an **energy check-in that makes Today lighter** on low days. Tasks.org (GPL) and Vikunja (AGPL) are ideas only.

## Key uncertainties

Nothing here was run on Jack's devices. Unknown: real speed of any model or engine on the S23 FE, whether the tray, hotkey and WebView2 window share one Go process cleanly, each individual voice model's licence, go-toast's recent upkeep (sr.ht was blocked), and whether `navigator.vibrate` needs a permission. Three good libraries (age's newest version, kaptinlin/jsonrepair, Ollama's client) need a newer Go than Pocket's 1.24, so the build would need a Go upgrade or an older release.

## Conclusion

Two of the best picks change Pocket's "no permissions" promise (internet for the model download, microphone for voice), so those need Jack's yes before building. Everything else fits his rules as they stand and can go straight into 1.4 or 1.5, in this order: newer phone model, find-the-right-note, tray plus hotkey plus reminders, calendar export, then voice, photos and phone-to-PC sharing.
