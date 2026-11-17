# Aseprite Action Viewer v0.5.8.5

Source-only Viewport Quick Inspector update.

## Added

- Right-click Player, NPC, or PROP sprites to open one compact runtime inspector.
- Left-click runtime actor selection and left-drag runtime repositioning with
  camera/zoom-aware world conversion; thresholded right drag keeps camera pan.
- Topmost selection based on actual actor draw order and current frame bounds.
- Scrollable eight-row tag selector with wheel, scroll indicator, keyboard
  navigation, and modern/legacy wheel capture before viewport zoom.
- Current-tag/full-sequence and Once/Repeat visual preview combinations.
- Isolated Player/NPC preview that pauses gameplay/AI actions and movement without
  resetting runtime state; actual death/destruction still takes priority.
- Draggable, clamped inspector header with session-only manual position retention.
- NPC spawn/despawn/death, PROP place/despawn/destruction, Player reset to the
  existing spawn position, and navigation to existing detailed settings.
- Content-sized Player/NPC/PROP panels with 10px bottom padding and retained,
  resize-aware manual positioning.
- Korean/English labels, tooltips, stale-target cleanup, and automated tests.

## Safety

- Forced preview is a separate runtime-only animation track. It does not alter
  normal animation/AI state or generate damage, projectiles, or attack hitboxes.
- Inspector and preview fields are not serialized to project/settings JSON.
- Existing NPC death and PROP destruction handlers remain the terminal-action
  source of truth.
- No PyInstaller build, EXE, ZIP, signing, Aseprite CLI operation, commit, tag,
  or push was performed. Existing v0.5.8.4 distribution artifacts are unchanged.
