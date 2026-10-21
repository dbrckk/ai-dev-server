This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
qualification/
  public-model-diagnostic-fix-20261020.json
```

# Files

## File: qualification/public-model-diagnostic-fix-20261020.json
```json
{
  "requested_model": "kilo-auto/free",
  "reported_model": "nvidia/nemotron-3.5-super-vl:free",
  "usage": {
    "prompt_tokens": 489,
    "completion_tokens": 1003,
    "total_tokens": 1492,
    "cost": 0,
    "is_byok": false,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 0,
      "audio_tokens": 0,
      "video_tokens": 0
    },
    "cost_details": {
      "upstream_inference_cost": 0,
      "upstream_inference_prompt_cost": 0,
      "upstream_inference_completions_cost": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 941,
      "image_tokens": 0,
      "audio_tokens": 0
    }
  },
  "finish_reason": "stop",
  "max_tokens": 1024,
  "max_attempts": 1,
  "source_sha256": "a5b11226be891f91d4ebe4633ad86aff6870ae7284f78da26e91732617463496",
  "patch_sha256": "522c1baf9a593f9797ede094d0142f92cf67cb2ae76c02339ffa20949ec966de",
  "schema_version": 1,
  "observed_on": "2026-10-20",
  "target_repository": "dbrckk/ai-dev-server",
  "target_visibility": "public",
  "target_path": "studio/production_os_live_diagnostics.py",
  "base_commit": "d28b09e",
  "transport": "existing core.API, fixed HTTPS Kilo public gateway, empty credential, one POST without retry",
  "free_preflight": "fresh catalog isFree=true and zero prompt/completion prices",
  "proposed_edit": {
    "old": "or len(fn.args.args) != 1 or fn.args.args[0].arg != \"value\"",
    "new": "or len(fn.args.args) != 1 or fn.args.args[0].arg != \"value\" or fn.args.args[0].annotation is not None"
  },
  "validation": {
    "before": "existing regression extended; annotated argument accepted and regression failed",
    "after": "23 tests and 20 subtests passed; exact proposed source edit applied",
    "hosted_ci": "pending"
  },
  "limits": [
    "model identity and cost are gateway-reported",
    "not a hosted Production-OS queue-to-worker run",
    "not sustained quota or arbitrary coding-quality proof",
    "no private content sent; no provider-generated executable code run"
  ]
}
```
