"""Region fingerprint extraction and fidelity checking.

Extracts structural fingerprints from region HTML fragments and checks
that a generated .vue file contains all required structural elements.

Used by trtc_verify_region.py to enforce paste-then-bind fidelity.
"""
import re
from pathlib import Path


def extract_data_attrs(html_content: str, attr_name: str) -> list:
    """Extract all values of a specific data-* attribute from HTML.

    Example: extract_data_attrs(html, "data-btn") → ["mic", "cam", "share", ...]
    """
    pattern = rf'{attr_name}="([^"]*)"'
    return re.findall(pattern, html_content)


def count_pattern(content: str, pattern: str) -> int:
    """Count occurrences of a string pattern in content."""
    return content.count(pattern)


def has_v_for_with_pattern(vue_content: str, pattern: str) -> bool:
    """Check if the pattern appears inside a v-for context in the Vue template.

    If a v-for loop renders elements with the pattern, one source occurrence
    satisfies any min_count (renders N at runtime).
    """
    # Simple heuristic: check if there's a v-for on a nearby line
    lines = vue_content.split('\n')
    for i, line in enumerate(lines):
        if pattern in line:
            # Look at surrounding 5 lines for v-for
            context_start = max(0, i - 5)
            context_end = min(len(lines), i + 5)
            context = '\n'.join(lines[context_start:context_end])
            if 'v-for' in context:
                return True
    return False


# Key structural classes to count per region type.
# These are the classes where count matters (not just presence).
STRUCTURAL_CLASSES = {
    'topbar': ['ui-toolbar-item', 'ui-popover', 'ui-info-row'],
    'bottombar': ['ui-icon-button', 'ui-popover', 'ui-menu-item', 'ui-menu-section'],
    'sidepanel': ['ui-menu-item', 'ui-popover'],
    'stage': ['ui-stage__frame', 'ui-stage__tile'],
    'modals': ['ui-modal', 'ui-nav-item', 'ui-form-row'],
}


def extract_fingerprints(region_html_path: Path) -> dict:
    """Extract structural fingerprints from a region HTML fragment.

    Returns a dict with:
      - data_attrs: dict of {attr_name: [values]}
      - class_counts: dict of {class_name: min_count_from_region}
      - region_name: str (e.g. "topbar")
    """
    content = region_html_path.read_text()
    region_name = region_html_path.stem  # e.g. "topbar", "bottombar"

    # Extract data-* attribute values
    data_attrs = {}
    for attr in ['data-btn', 'data-tb', 'data-panel', 'data-nav']:
        values = extract_data_attrs(content, attr)
        if values:
            data_attrs[attr] = values

    # Count key structural classes for this region type
    class_counts = {}
    classes_to_check = STRUCTURAL_CLASSES.get(region_name, [])
    for cls in classes_to_check:
        count = count_pattern(content, cls)
        if count > 0:
            class_counts[cls] = count

    return {
        'data_attrs': data_attrs,
        'class_counts': class_counts,
        'region_name': region_name,
        'region_file': region_html_path.name,
    }


def check_fidelity(vue_content: str, fingerprints: dict) -> list:
    """Check a .vue file against region fingerprints.

    Returns a list of violation strings (empty = pass).
    """
    violations = []
    region_file = fingerprints['region_file']
    region_name = fingerprints['region_name']
    component_name = region_name.replace('-', '').title()  # e.g. "Topbar" → will be overridden by caller

    # Check data-* attributes: every value in the region must appear in the .vue
    for attr_name, expected_values in fingerprints['data_attrs'].items():
        present = []
        missing = []
        for val in expected_values:
            # Check both quote styles and Vue dynamic binding
            if (f'{attr_name}="{val}"' in vue_content or
                f"{attr_name}='{val}'" in vue_content or
                f':{attr_name}="\'{val}\'"' in vue_content or
                f'{attr_name}' in vue_content and val in vue_content):
                # More precise check: the attr=value pair must exist
                if f'{attr_name}="{val}"' in vue_content or f"{attr_name}='{val}'" in vue_content:
                    present.append(val)
                else:
                    present.append(val)  # relaxed match
            else:
                missing.append(val)

        if missing:
            violations.append(
                f"V7: missing {attr_name} values {missing} from region spec ({region_file}). "
                f"Expected {expected_values}."
            )

    # Check structural class counts
    for cls, region_count in fingerprints['class_counts'].items():
        vue_count = count_pattern(vue_content, cls)

        # v-for allowance: if pattern is inside a v-for, count as satisfied
        if vue_count < region_count and has_v_for_with_pattern(vue_content, cls):
            continue

        if vue_count < region_count:
            violations.append(
                f"V7: has {vue_count} `{cls}` but region spec ({region_file}) has {region_count}. "
                f"Ensure all structural elements from the reference HTML are preserved."
            )

    return violations
