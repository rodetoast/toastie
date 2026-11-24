# ase_viewer 개발 현황

확인일 2026-11-24 · 기본 브랜치 `main` · [개발 브랜치](https://github.com/rodetoast/toastie/tree/codex/migration-checkpoint-20261117) · [조사 기준 소스 커밋](https://github.com/rodetoast/toastie/commit/0d5a7d114c0bedb645c2f3cfaa57ca8c0e9aeee1)

애니메이터가 Aseprite 애니메이션을 액션·물리·전투 상황에서 확인합니다.

- 제품 표시명 **ase_viewer** · 런처 app_id `ase-viewer`
- 기술 구성 Python, Pygame, PyInstaller
- 구현 기능 Aseprite 애니메이션 재생과 캐릭터 동작·전투 효과 검수

## 배포 상태

**0.5.8.4** · `0.5.8.4-team-3bf37dd` · `ase-viewer--0.5.8.4-team-3bf37dd.zip` (onefile) · 실행 파일 `ase_viewer.exe`. [Rod 운영 카탈로그](https://github.com/rodetoast/creative-group-releases/releases/tag/rodetoast-catalog-000015)

소스 저장소의 독립 Latest Release는 확인되지 않았습니다.

## 개발과 검증

0.5.8.5 개발 소스에 Viewport Quick Inspector를 추가했습니다. 운영은 0.5.8.4입니다.

**알려진 제약과 미검증** 0.5.8.5 Windows 후보 및 현재 호스트 연동은 미검증입니다.

이번 확인에서는 원격 Git과 공개 서명 카탈로그를 대조했습니다. 기능 시험과 패키징은 기존 보고서의 범위를 따릅니다.

## 패키징과 다음 단계

README의 --check 및 ase_viewer.spec에 따른 빌드 절차를 따릅니다. [공통 배포 절차](https://github.com/rodetoast/southpaw-development-hub/blob/main/docs/RELEASE_GUIDE.md)

**다음 단계** 기존 노트에 남은 0.5.8.5 빌드와 실제 Aseprite 연동을 확인합니다.

[README.md](https://github.com/rodetoast/toastie/blob/0d5a7d114c0bedb645c2f3cfaa57ca8c0e9aeee1/README.md) · [ase_viewer.spec](https://github.com/rodetoast/toastie/blob/0d5a7d114c0bedb645c2f3cfaa57ca8c0e9aeee1/ase_viewer.spec) · [RELEASE_v0.5.8.5.md](https://github.com/rodetoast/toastie/blob/0d5a7d114c0bedb645c2f3cfaa57ca8c0e9aeee1/RELEASE_v0.5.8.5.md) · [개발 허브 요약](https://github.com/rodetoast/southpaw-development-hub/blob/main/projects/ase-viewer.md)
