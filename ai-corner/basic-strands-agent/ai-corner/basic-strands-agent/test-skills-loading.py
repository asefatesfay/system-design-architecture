"""
Test: Check if skills are loading from files
"""

from strands import Agent, AgentSkills
import os
from pathlib import Path

print("\n" + "=" * 60)
print("Testing Skills Loading from Files")
print("=" * 60 + "\n")

# Check current directory
print(f"📁 Current directory: {os.getcwd()}")
print(f"📁 Skills path: {Path('./skills').absolute()}")

print("\n" + "-" * 60 + "\n")

# List what's in skills directory
skills_dir = Path("./skills")
if skills_dir.exists():
    print("📂 Contents of ./skills/:")
    for item in skills_dir.iterdir():
        if item.is_dir():
            print(f"   📁 {item.name}/")
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                print(f"      ✅ SKILL.md exists")
                # Read first line to check format
                with open(skill_file) as f:
                    first_line = f.readline().strip()
                    print(f"      First line: {first_line}")
            else:
                print(f"      ❌ SKILL.md missing")
else:
    print("❌ ./skills/ directory doesn't exist!")

print("\n" + "-" * 60 + "\n")

# Try to load
print("🔄 Attempting to load skills...")
try:
    plugin = AgentSkills(skills="./skills/")
    print("✅ Plugin created successfully")

    # Check if it's callable/awaitable
    print(f"   Plugin type: {type(plugin)}")

    # Try to get skills
    try:
        skills = plugin.get_available_skills()
        print(f"✅ get_available_skills() returned: {type(skills)}")
        print(f"   Number of skills: {len(skills)}")

        if len(skills) > 0:
            print("\n📚 Skills found:")
            for skill in skills:
                print(f"   • {skill.name}: {skill.description}")
        else:
            print("\n⚠️  No skills found (empty list)")

    except Exception as e:
        print(f"❌ Error calling get_available_skills(): {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Error creating plugin: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("If you see 'No skills found', use the working example instead:")
print("  python skills-working-example.py")
print("=" * 60)
