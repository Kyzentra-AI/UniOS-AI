"""
UniOS Content Sanitizer
Cleans and standardizes generated lesson content, LaTeX math formatting, and physical units
to prevent broken rendering, unparsed LaTeX macros (like \\text{}), and malformed symbols on mobile/web clients.
"""

import re


def sanitize_math_and_latex(content: str) -> str:
    """
    Sanitizes raw/broken LaTeX math expressions so they render cleanly on mobile cards
    and web markdown renderers without raw \\text{} macros, stray commas, or broken units.
    
    Transforms:
      • $u = 20 , \\text{m/s}$     ->  • u = 20 m/s
      • $a = -5 , \\text{m/s}^2$   ->  • a = -5 m/s²
      • $v = 0 , \\text{m/s}$      ->  • v = 0 m/s
      • $t = ?$                   ->  • t = ?
      • $s = ?$                   ->  • s = ?
    """
    if not content:
        return content

    # 1. Replace \text{unit}^2 or \text{unit}^{2} with Unicode superscripts
    content = re.sub(r'\\text\{([^}]+)\}\^\{?2\}?', r'\1²', content)
    content = re.sub(r'\\text\{([^}]+)\}\^\{?3\}?', r'\1³', content)

    # 2. Replace any other \text{...} with its plain inner text
    content = re.sub(r'\\text\{([^}]+)\}', r'\1', content)

    # 3. Clean up commas or backslash commas used before units inside math blocks
    # e.g. '$u = 20 , m/s$' or '$u = 20 \, m/s$' -> '$u = 20$ m/s' or 'u = 20 m/s'
    def clean_inline_math(match):
        inner = match.group(1).strip()
        # Clean stray math spacing commas or backslashes before units: ', m/s' or '\, m/s'
        inner = re.sub(r'\s*[,|\\]+\s*([a-zA-Z/²³°]+)$', r' \1', inner)
        
        # If pattern is variable = value unit, e.g. 'u = 20 m/s' or 'a = -5 m/s²'
        m = re.match(r'^([a-zA-Z]\s*=\s*[\-0-9\.]+)\s+([a-zA-Z/²³°%]+)$', inner)
        if m:
            var_val, unit = m.groups()
            return f"{var_val} {unit}"
        
        # If it's a simple variable equality with question mark like '$t = ?$', simplify to 't = ?'
        if re.match(r'^[a-zA-Z]\s*=\s*\?$', inner):
            return inner
        
        return f"${inner}$"

    # Match inline math like $...$ but not display math $$...$$
    content = re.sub(r'(?<!\$)\$([^$\n]+)\$(?!\$)', clean_inline_math, content)

    # 4. Clean up display math $$...$$ if it has \text or stray commas
    def clean_display_math(match):
        inner = match.group(1).strip()
        inner = re.sub(r'\\text\{([^}]+)\}', r'\1', inner)
        inner = re.sub(r'\s*[,|\\]+\s*', ' ', inner)
        return f"$${inner}$$"

    content = re.sub(r'\$\$([^$]+)\$\$', clean_display_math, content)

    # 5. Clean any lingering triple single quotes
    content = content.replace("'''python", "```python").replace("'''", "```")

    return content
