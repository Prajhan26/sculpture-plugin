# Sculpture Plugin

## What This Project Is
A Claude Code plugin that removes AI capabilities instead of restricting them.
"We don't build agents. We sculpt them."

Inspired by the Kailasa Temple — carved from a single mountain by removing 
200,000 tons of rock. We start with a full AI and remove what's not needed.

## Core Philosophy
- Absence of capability = proof of innocence
- Rules can be ignored. Removed capabilities cannot.
- Less is more secure. Less is cheaper. Less is focused.

## Project Structure
- commands/ → user-facing commands (/sculpture)
- agents/ → sculptor agent (guides what to remove)
- skills/ → knowledge base (subtractive AI concepts)
- .claude-plugin/ → plugin metadata
- SPEC.md → full specification
- CLAUDE.md → this file

## How To Work On This Project
- Always read SPEC.md before making changes
- Don't add complexity — this project is about subtraction
- Every new feature must answer: "does this need to exist?"
- Keep commands simple, agents smart, skills deep

## Current Status
- Files placed ✅
- SPEC written ✅
- WAT structure → in progress
- Testing → pending

## What You Should Never Do
- Don't add tools that aren't in SPEC.md
- Don't change plugin.json structure without updating README
- Don't skip the sculptor agent flow