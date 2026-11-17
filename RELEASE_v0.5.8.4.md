# Aseprite Action Viewer v0.5.8.4

Status: **Internal with-examples candidate; automated checks passed**

## Hotfix scope

- F9 restores Player HP without changing position, scene objects, key mappings,
  project data, or settings. The app shortcut is blocked during active input,
  key binding, and modal confirmation.
- A finite 480ms recovery orbit FX reuses the existing particle system and is
  bounded to twelve active recovery particles.
- NPC attack preparation and recovery tags no longer create authored or
  fallback hitboxes. The existing 35–60% damage window is calculated inside
  mapped damaging tag durations.
- Read-only inspection confirmed the reported fixture uses
  `ThrustForward_Ready` (frames 29–38) and `ThrustForward` (39–47).
- `Icon.ico` remains the executable resource. `Icon.png` is bundled as onefile
  runtime data and loaded through `pygame.display.set_icon()` before window
  creation. Windows receives the stable AppUserModelID
  `ToastSource.AsepriteActionViewer`.

## Automated validation

- Source `py_compile`, `--check`, `--check-sidebar-ui`, and `git diff --check`:
  passed.
- All 86 test modules passed independently: 429 tests, one optional real
  SporeHeart fixture integration skipped.
- PyInstaller 6.21.0 build: passed with standard Tcl/Tk hooks.
- Frozen check: exit 0, Tcl/Tk 8.6.12, runtime icon available.
- Frozen sidebar check: exit 0.
- EXE size: 19,607,852 bytes.
- EXE SHA-256:
  `3BF37DDDE0C1666E133D0EE1F2DA9D1118F4F92CD5799A392097CC83D67CC233`

## Package policy

The company-internal ZIP contains:

- `ase_viewer.exe`
- `README.md`
- `MANUAL_TEST_CHECKLIST.md`
- `RELEASE_v0.5.8.4.md`
- `resources/examples/**`

It excludes project/settings JSON, user resources, source, tests, caches,
`.git`, quarantine, and prior build/release output. The authoritative ZIP hash
is external in the companion `.sha256` file because an archive cannot contain
its own final hash.

Workspace package record:

- ZIP: `ase_viewer_v0.5.8.4_with_examples.zip`
- Size: 22,085,231 bytes
- SHA-256:
  `2532C273C4CF9930CF882EF1F84CAE55C9A97479A69123431560B1299EDEC2D2`

## Unsigned build notice

이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/내부 배포용 빌드입니다.
Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가 표시될 수 있습니다.
동반 `.sha256` 파일로 ZIP을 확인한 뒤 실행해 주세요.

This is an unsigned internal/test build. Windows may show an Unknown Publisher
or SmartScreen warning. Verify the ZIP with its companion `.sha256` file.

No code signing, Aseprite CLI, full GUI automation, commit, tag, push, or
release publication was performed.

## Post-build source polish pending next build

The current source has a later build-free polish that is **not included** in
the existing v0.5.8.4 ZIP/EXE:

- Regenerated `Icon.ico` from the user-replaced 1024×1024 RGBA `Icon.png`.
- PNG SHA-256:
  `A28F575ED0A82B04972A62349423A1A5C46B558EB4AA30E26161881A5951D3D8`
- ICO SHA-256:
  `D6E6670F0BDD41A9F5E20430E0B74176DC39E6B1B9A89C021DF8970977851EE8`
- Shortened each damage-capable NPC tag window from local 35–60% to local
  0–25%, with a capped 40ms minimum for very short tags.
- `ThrustForward_Ready` remains no-damage; `ThrustForward` becomes active at
  its start and inactive after its early window.

No PyInstaller build or ZIP was created for this source polish. Confirm the
new ICO and timing behavior in the next feature/bugfix build.
