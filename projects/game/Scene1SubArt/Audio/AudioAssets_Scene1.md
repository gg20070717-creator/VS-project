# Scene1 SubArt Audio Deliverables

## Scope
From `game/计划表(1).xlsx`, the Scene1 (BloodyWolfHighSchool) sub-art audio tasks are:
- Bird ambience
- Stream water ambience
- Reading ambience
- Excavator digging ambience
- Pen/pencil friction on paper
- Exam paper page turning

## Naming Rule Applied
- English names only
- Type prefix used: `SFX_`
- CamelCase naming after prefix

## Local Files (Ready)
Directory: `game/Scene1SubArt/Audio/Mixkit`

1. `SFX_BirdsChirpingMorning.mp3`
- Task mapping: Bird ambience (`鸟鸣`)
- Source title: Morning birds
- Source URL: https://mixkit.co/free-sound-effects/bird/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/2472/2472-preview.mp3
- Size: 6,547,966 bytes

2. `SFX_StreamWaterFlowRiver.mp3`
- Task mapping: Stream water ambience (`流水声`)
- Source title: River water flowing
- Source URL: https://mixkit.co/free-sound-effects/rivers/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/2454/2454-preview.mp3
- Size: 5,552,581 bytes

3. `SFX_SchoolReadingVoices.mp3`
- Task mapping: Reading ambience (`读书声`)
- Source title: Children voices in school
- Source URL: https://mixkit.co/free-sound-effects/children/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/2254/2254-preview.mp3
- Size: 3,733,831 bytes

4. `SFX_ExcavatorDiggingAmbience.mp3`
- Task mapping: Excavator digging (`挖掘机挖掘音`)
- Source title: Construction place and bulldozer ambiance
- Source URL: https://mixkit.co/free-sound-effects/construction/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/800/800-preview.mp3
- Size: 3,009,052 bytes

5. `SFX_PencilWritingOnPaper.mp3`
- Task mapping: Pen/pencil friction (`纸笔摩擦声`)
- Source title: Writing pencil
- Source URL: https://mixkit.co/free-sound-effects/write/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/3194/3194-preview.mp3
- Size: 49,001 bytes

6. `SFX_ExamPaperPageTurn.mp3`
- Task mapping: Exam paper page turn (`试卷翻页声`)
- Source title: Paper magazine paging
- Source URL: https://mixkit.co/free-sound-effects/paper/
- Direct file URL: https://assets.mixkit.co/active_storage/sfx/1100/1100-preview.mp3
- Size: 214,011 bytes

## License and Usage
- Library: Mixkit Sound Effects
- License page: https://mixkit.co/license/#sfxFree
- Reported allowed usage includes: video games, commercial projects, educational projects.
- Restriction note: do not redistribute source files as standalone stock assets.

## Integration Notes for Unreal (per project规范.md)
- Put final imported assets into project `Content/Audio/...` module folder.
- Keep module-based folder structure and English naming.
- If moving imported `.uasset` files later, do it inside Unreal Editor (not in file explorer).
