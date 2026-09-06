# Folder Organization

This document explains the new organization of the `basic-strands-agent` folder.

## What Changed

### Before (Messy)
```
basic-strands-agent/
├── plugin-basics.py
├── custom-plugin-basics.py
├── custom-plugin-basics-fixed.py  ← Duplicate!
├── custom-plugin-counter-fixed.py ← Duplicate!
├── skills-from-files-fixed.py     ← Duplicate!
├── test-get-available-skills.py   ← Debug file
├── skills-debug.py                ← Debug file
├── PLUGINS_GUIDE.md
├── CUSTOM_PLUGIN_FIX.md
├── CUSTOM_PLUGINS_GUIDE.md        ← Duplicate!
└── ... 30+ files in root
```

### After (Organized)
```
basic-strands-agent/
├── README.md                   ← Main guide
├── examples/                   ← All examples
│   ├── 01-basics/             ← Start here
│   ├── 02-custom-plugins/     ← Build plugins
│   ├── 03-skills/             ← Skills
│   ├── 04-hooks/              ← Hooks
│   └── 05-session-management/ ← Persistence
├── skills/                     ← Example skills
├── utils/                      ← Reusable code
└── docs/                       ← Guides
```

---

## New Structure

### 📂 examples/
**Runnable code organized by topic**

- **01-basics/** - Start here! Basic plugins and agents
- **02-custom-plugins/** - Build your own plugins
- **03-skills/** - Specialized instructions
- **04-hooks/** - Direct event handling
- **05-session-management/** - Persist conversations

Each folder has its own README explaining what's inside.

### 📂 skills/
**Example skill definitions**

- `math-helper/` - Math tutor skill
- `email-writer/` - Email writing skill

Used by `examples/03-skills/skills-from-files.py`

### 📂 utils/
**Reusable components**

- `sqlite_session_manager.py` - Production-ready SQLite session manager

Copy these into your own projects!

### 📂 docs/
**Comprehensive guides**

- `plugins.md` - Complete plugin guide
- `hooks-vs-plugins.md` - Understand the difference
- `custom-plugins.md` - Build your own
- `skills.md` - Skills from scratch
- `skills-gotcha.md` - Common pitfalls
- `session-management.md` - Persistence

---

## Files Removed

### Duplicates Deleted:
- ❌ `custom-plugin-basics-fixed.py` → kept `custom-plugin-basics.py`
- ❌ `custom-plugin-counter-fixed.py` → kept `custom-plugin-counter.py`
- ❌ `skills-from-files-fixed.py` → kept `skills-from-files.py`
- ❌ `plugin-example-logger-proper.py` → redundant
- ❌ `CUSTOM_PLUGIN_FIX.md` → info merged into guides
- ❌ `CUSTOM_PLUGINS_GUIDE.md` → renamed to `docs/custom-plugins.md`

### Debug Files Deleted:
- ❌ `test-get-available-skills.py`
- ❌ `test-skills-loading.py`
- ❌ `skills-debug.py`
- ❌ `step1_simple_db.py`

### Redundant Examples Deleted:
- ❌ `plugin-example-logger.py` → kept `hook-example-logger.py`
- ❌ `plugin-example-user-context.py` → concept covered in other examples
- ❌ `session-manager-basic.py` → redundant

---

## Navigation

### Quick Start
1. Read: [README.md](README.md)
2. Run: `python examples/01-basics/plugin-basics.py`
3. Follow the learning path

### Finding Examples
- Examples by topic: `examples/`
- Each folder has a README
- Numbered for progression

### Finding Docs
- All guides: `docs/`
- Quick reference: [README.md](README.md)

---

## Benefits

### ✅ Clear Organization
- Examples in `examples/`
- Docs in `docs/`
- Utils in `utils/`

### ✅ No Duplicates
- One version of each file
- No `-fixed` versions
- No debug files

### ✅ Easy Navigation
- Numbered folders (01, 02, 03...)
- README in each folder
- Clear naming

### ✅ Progressive Learning
- Start with 01-basics
- Progress through folders
- Build on previous knowledge

### ✅ Easy to Find Things
- Examples: `examples/0X-topic/`
- Docs: `docs/topic.md`
- Utils: `utils/`

---

## File Count

**Before:** ~35 files in root (messy!)
**After:**
- Root: 1 file (README.md)
- Examples: 12 files (organized)
- Docs: 6 files
- Utils: 1 file

**Much cleaner!** 🎉

---

## Migration Guide

If you had bookmarks or scripts referencing old paths:

| Old Path | New Path |
|----------|----------|
| `./plugin-basics.py` | `examples/01-basics/plugin-basics.py` |
| `./custom-plugin-basics.py` | `examples/02-custom-plugins/custom-plugin-basics.py` |
| `./skills-from-files.py` | `examples/03-skills/skills-from-files.py` |
| `./PLUGINS_GUIDE.md` | `docs/plugins.md` |
| `./sqlite_session_manager.py` | `utils/sqlite_session_manager.py` |

---

## Maintenance

This structure is designed for:
- ✅ Easy to add new examples (just put in appropriate folder)
- ✅ Easy to update docs (all in `docs/`)
- ✅ Easy to find things (clear categories)
- ✅ Easy for beginners (numbered progression)

---

**Result:** A clean, organized, easy-to-navigate learning resource! 🚀
