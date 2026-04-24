#!/usr/bin/env python3
"""
Automatically organize TORQ-e folder structure.
Run this once to move all files to their proper folders.
"""

import os
import shutil
from pathlib import Path

# Base paths
TORQUE_ROOT = Path(__file__).parent
TESTE_ROSA = TORQUE_ROOT / "Teste Rosa"

# Create new folder structure
FOLDERS = {
    'docs': TORQUE_ROOT / 'docs',
    'docs_journeys': TORQUE_ROOT / 'docs' / 'journeys',
    'branding': TORQUE_ROOT / 'branding',
    'branding_logo': TORQUE_ROOT / 'branding' / 'logo',
    'code': TORQUE_ROOT / 'code',
    'code_backend': TORQUE_ROOT / 'code' / 'backend',
    'code_specs': TORQUE_ROOT / 'code' / 'specs',
}

# File mapping: source_file -> destination_folder_key
FILE_MOVES = {
    # Architecture & design docs → docs/
    'ARCHITECTURE_BUSINESS_ANALYST.md': 'docs',
    'ARCHITECTURE_TECHNICAL.md': 'docs',
    'DATABASE_README.md': 'docs',
    'ENV_CONFIG_AND_MOCKING.md': 'docs',
    'TEST_CASES_COMPREHENSIVE.md': 'docs',
    'READING_ENGINE_SOURCES_ROADMAP.md': 'docs',
    'THE_INFRASTRUCTURE_OF_ERASURE.md': 'docs',

    # Journey blueprints → docs/journeys/
    'UMID_JOURNEY_BLUEPRINT.txt': 'docs_journeys',
    'UPID_JOURNEY_BLUEPRINT.txt': 'docs_journeys',
    'UHWP_JOURNEY_BLUEPRINT.txt': 'docs_journeys',
    'USHI_JOURNEY_BLUEPRINT.txt': 'docs_journeys',
    'UBADA_JOURNEY_BLUEPRINT.txt': 'docs_journeys',

    # Specifications → code/specs/
    'UMID_SPECIFICATION.txt': 'code_specs',
    'UPID_SPECIFICATION.txt': 'code_specs',
    'UHWP_SPECIFICATION.txt': 'code_specs',
    'USHI_SPECIFICATION.txt': 'code_specs',
    'UBADA_SPECIFICATION.txt': 'code_specs',

    # Backend code → code/backend/
    'torq_e_backend.py': 'code_backend',
    'torq_e_mcp_server.py': 'code_backend',
    'requirements_torq_e.txt': 'code_backend',
    '.env.template': 'code_backend',
    'Procfile': 'code_backend',

    # Branding files → branding/
    'BRANDING.md': 'branding',
    'FAVICON_SETUP.md': 'branding',
    'QUICK_SETUP.md': 'branding',
    'generate_favicon.py': 'branding',

    # Logo → branding/logo/
    'TdST.png': 'branding_logo',
}

print("🗂️  TORQ-e Folder Organization Script")
print("=" * 60)

# Step 1: Create all folders
print("\n📁 Creating folder structure...\n")
for folder_key, folder_path in FOLDERS.items():
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {folder_path.relative_to(TORQUE_ROOT)}")

# Step 2: Move files
print("\n📦 Moving files to their homes...\n")

moved_count = 0
failed_count = 0

for filename, dest_key in FILE_MOVES.items():
    source = TESTE_ROSA / filename
    destination_folder = FOLDERS[dest_key]
    destination = destination_folder / filename

    if source.exists():
        try:
            shutil.move(str(source), str(destination))
            print(f"   ✅ {filename} → {destination_folder.name}/")
            moved_count += 1
        except Exception as e:
            print(f"   ❌ {filename} - ERROR: {str(e)}")
            failed_count += 1
    else:
        print(f"   ⚠️  {filename} - NOT FOUND (skipped)")

# Step 3: Clean up empty Teste Rosa folder
print("\n🧹 Cleanup...\n")
if TESTE_ROSA.exists():
    # Check if folder is now empty (except hidden files)
    remaining_files = [f for f in TESTE_ROSA.iterdir() if not f.name.startswith('.')]
    if not remaining_files:
        try:
            shutil.rmtree(TESTE_ROSA)
            print(f"   ✅ Removed empty Teste Rosa folder")
        except Exception as e:
            print(f"   ⚠️  Could not remove Teste Rosa: {e}")
    else:
        print(f"   ⚠️  Teste Rosa folder still contains {len(remaining_files)} files")
        print(f"      (This is fine if you want to keep it)")

# Final summary
print("\n" + "=" * 60)
print(f"✨ ORGANIZATION COMPLETE!")
print("=" * 60)
print(f"\n📊 Results:")
print(f"   • Files moved: {moved_count}")
if failed_count > 0:
    print(f"   • Errors: {failed_count}")
print(f"\n📂 New structure:")
print(f"   TORQ-e/")
print(f"   ├── docs/")
print(f"   │   ├── [Architecture & design docs]")
print(f"   │   └── journeys/")
print(f"   │       └── [5 journey blueprints]")
print(f"   │")
print(f"   ├── branding/")
print(f"   │   ├── [Branding guidelines]")
print(f"   │   ├── generate_favicon.py")
print(f"   │   └── logo/")
print(f"   │       └── TdST.png")
print(f"   │")
print(f"   └── code/")
print(f"       ├── backend/")
print(f"       │   └── [Backend Python files]")
print(f"       └── specs/")
print(f"           └── [5 specification files]")
print(f"\n✅ Done! Your TORQ-e project is now organized.")
